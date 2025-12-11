import asyncio
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# Add backend path to sys.path
sys.path.append(os.path.join(os.getcwd(), "backend/app/priority_core"))
from model_router import UnifiedModelRouter

MAX_FILE_ATTEMPTS = 3
FOLLOW_UP_INSTRUCTIONS = [
    "Highlight the exact lines that still fail verification, mention the rule IDs, and make incremental edits strictly around those locations.",
    "Apply a minimal diff only around the remaining failing lines; keep unrelated sections untouched and avoid reformatting the whole file.",
]

RULE_HISTORY_CACHE: dict[str, dict] = {}


def _format_issue_summary(issues: list[dict]) -> str:
    if not issues:
        return "No issue details available."
    lines = []
    for issue in issues[:5]:
        line = issue.get("line", "?")
        rule = issue.get("rule", "unknown")
        message = issue.get("message", "No message")
        lines.append(f"Line {line} (Rule: {rule}): {message}")
    return "; ".join(lines)


def _hash_content(content: str | bytes) -> str:
    hasher = hashlib.sha256()
    if isinstance(content, str):
        content = content.encode("utf-8")
    hasher.update(content)
    return hasher.hexdigest()


def _issue_signature(issue: dict) -> str:
    return "|".join(
        [
            str(issue.get("rule", "unknown")),
            str(issue.get("line", "?")),
            issue.get("message", "")[:128],
        ]
    )


def _clear_failure_history(file_path: str) -> None:
    RULE_HISTORY_CACHE.pop(file_path, None)


def _register_failure_history(
    file_path: str, issues: list[dict], content_hash: str
) -> str:
    if not issues:
        entry = RULE_HISTORY_CACHE.setdefault(
            file_path,
            {"rules": {}, "last_content_hash": content_hash, "last_issues": []},
        )
        entry["last_content_hash"] = content_hash
        entry["last_issues"] = []
        return ""

    entry = RULE_HISTORY_CACHE.setdefault(
        file_path,
        {"rules": {}, "last_content_hash": "", "last_issues": []},
    )
    guidance_parts = []
    for issue in issues:
        rule = issue.get("rule", "unknown")
        snippet = issue.get("line_text", "").strip()
        message = issue.get("message", "No message")
        rules = entry["rules"]
        record = rules.setdefault(
            rule, {"last_signature": "", "consecutive": 0, "last_message": ""}
        )
        signature = _issue_signature(issue)
        if record["last_signature"] == signature:
            record["consecutive"] += 1
        else:
            record["consecutive"] = 1
        record["last_signature"] = signature
        record["last_message"] = message
        if record["consecutive"] >= 2:
            guidance_parts.append(
                f"Rule {rule} keeps failing; keep the existing logic near '{snippet or 'the highlighted section'}' "
                "and adjust only the guarded block to satisfy the rule without reworking the entire function."
            )
        else:
            guidance_parts.append(
                f"You failed on rule {rule} because {message}; avoid the prior edit by focusing changes around '{snippet or 'the affected lines'}'."
            )
    entry["last_content_hash"] = content_hash
    entry["last_issues"] = issues
    return " ".join(guidance_parts)


def _run_detectors(path: str) -> tuple[int | None, list[dict]]:
    """
    Run both tscanner and opti_scanner to gather all code issues (lint + performance).
    """
    all_issues = []

    # 1. Run tscanner (Linting)
    try:
        t_res = subprocess.run(
            ["tscanner", "check", path, "--format", "json"],
            capture_output=True,
            text=True,
        )
        if t_res.returncode == 0 or t_res.stdout:
            try:
                v_data = json.loads(t_res.stdout)
                if isinstance(v_data, dict):
                    v_files = v_data.get("files", [])
                    if v_files:
                        all_issues.extend(v_files[0].get("issues", []))
            except json.JSONDecodeError:
                pass
    except Exception:
        pass

    # 2. Run opti_scanner (Performance/Modernization)
    # Import directly since we are in the same repo.
    try:
        sys.path.append(os.path.join(os.getcwd(), "tools"))
        import importlib

        import opti_scanner

        # Force reload to pick up any rule changes (59 rules as of Dec 2025)
        importlib.reload(opti_scanner)

        # Scan
        file_path = Path(path)
        opt_findings = opti_scanner.scan_file(file_path)

        # Convert to tscanner-like format for the LLM
        for f in opt_findings:
            all_issues.append(
                {
                    "rule": f["rule_id"],
                    "line": f["line"],
                    "message": f"{f['suggestion']} (Priority: {f['priority']})",
                    "line_text": f["code"],
                }
            )

    except ImportError:
        pass  # opti_scanner not found or broken
    except Exception as e:
        print(f"OptiScanner failed: {e}")

    return len(all_issues), all_issues


def _verify_candidate_content(
    candidate: str, suffix: str
) -> tuple[int | None, list[dict]]:
    temp = None
    try:
        temp = tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False)
        temp.write(candidate)
        temp.close()
        return _run_detectors(temp.name)
    finally:
        if temp and os.path.exists(temp.name):
            os.unlink(temp.name)


def _extract_code_block(content: str) -> str | None:
    lines = content.splitlines()
    in_block = False
    block = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_block = not in_block
            continue
        if in_block:
            block.append(line)
    if block:
        return "\n".join(block)
    return None


def _apply_search_replace(original_content: str, patch_text: str) -> str | None:
    """
    Applies strict SEARCH/REPLACE blocks.
    Format:
    <<<< SEARCH
    ...lines...
    ====
    ...lines...
    >>>>
    """
    import re

    # Pattern to capture SEARCH and REPLACE blocks
    # Flags: Dotall to match newlines, Multiline for anchors if needed
    pattern = re.compile(r"<<<< SEARCH\n(.*?)\n====\n(.*?)\n>>>>", re.DOTALL)

    matches = list(pattern.finditer(patch_text))
    if not matches:
        return None

    new_content = original_content
    # Apply changes in reverse order if we were doing offsets, but here we do string replacement.
    # String replacement is risky if multiple identical blocks exist.
    # Better to just do .replace(search, replace, 1) assuming sequential?
    # Actually, for reliability, let's assume one block per issue or distinct enough content.

    for match in matches:
        search_block = match.group(1)
        replace_block = match.group(2)

        # Determine if search block exists
        if search_block in new_content:
            new_content = new_content.replace(search_block, replace_block, 1)
        else:
            # Try loose matching (strip whitespace)
            if search_block.strip() in new_content:
                # This is tricky without exact positions.
                # Fallback: Don't apply ambiguous patches
                return None
            return None

    return new_content


def _build_prompt(
    issues_text: str,
    file_content: str,
    attempt: int,
    failure_note: str,
    suffix: str,
    rule_guidance: str = "",
) -> str:
    base = (
        "You are an expert code refactoring agent. Fix the issues below using a SEARCH/REPLACE block.\n"
        "Reduce token usage by only returning the changed lines. Do NOT return the full file.\n\n"
        "RULE CONTEXT (Dec 2025 Standards):\n"
        "- OPT-PERF-PY-*: perflint anti-patterns (dict iterator, list comprehension, dotted imports)\n"
        "- OPT-RES-*: Research bot findings (match statements, asyncio.to_thread, memoryview)\n"
        "- OPT-IO-*: File safety (use atomic_open for writes)\n"
        "- OPT-RES-*: Resilience (wrap external calls in CircuitBreaker)\n"
    )

    prompt = (
        f"{base}\n"
        f"ISSUES:\n{issues_text}\n\n"
        f"FILE CONTENT:\n```{suffix}\n{file_content}\n```\n\n"
        "Return the fix using this EXACT format:\n"
        "```\n"
        "<<<< SEARCH\n"
        "[Exact lines to be replaced from the original file]\n"
        "====\n"
        "[New corrected lines]\n"
        ">>>>\n"
        "```\n"
        "If multiple changes are needed, provide multiple blocks. Copy the SEARCH lines exactly from the input."
    )

    if attempt > 1 and failure_note:
        idx = min(attempt - 2, len(FOLLOW_UP_INSTRUCTIONS) - 1)
        prompt += f"\n\nPREVIOUS ATTEMPT {attempt - 1} FAILED: {failure_note}. {FOLLOW_UP_INSTRUCTIONS[idx]}"

    if rule_guidance:
        prompt += f"\n\nRULE GUIDANCE: {rule_guidance}"

    return prompt


async def _adaptive_fix_file(
    router: UnifiedModelRouter,
    file_path: str,
    original_content: str,
    issues: list[dict],
) -> tuple[bool, str, int | None, str]:
    issue_summary = "\n".join(
        [
            f"- {i.get('line', '?')} (Rule: {i.get('rule', 'unknown')}): "
            f"{i.get('message', 'No message')} | Code: {i.get('line_text', '').strip()}"
            for i in issues
        ]
    )
    failure_note = "initial pass"
    best_issue_count = len(issues)
    suffix = Path(file_path).suffix.lstrip(".") or "txt"

    for attempt in range(1, MAX_FILE_ATTEMPTS + 1):
        prompt = _build_prompt(
            issue_summary, original_content, attempt, failure_note, suffix
        )
        response = await router.query(prompt, force_model="gpt-oss:latest")
        fixed = response.get("content", "")
        candidate = _extract_code_block(fixed) or fixed

        if not candidate.strip():
            failure_note = f"model returned empty content on attempt {attempt}"
            continue

        issue_count, _ = _verify_candidate_content(candidate, f".{suffix}")
        if issue_count is None:
            failure_note = f"verification failed on attempt {attempt}"
            continue

        if issue_count < best_issue_count:
            return True, candidate, issue_count, ""

        failure_note = f"issue count stayed at {issue_count}"

    return False, original_content, best_issue_count, failure_note


async def run_smart_fixer():
    print("🔧 Smart Fixer: Initializing...")

    # 1. Safety First: Git Branch
    print("🛡️  Safety Check: Creating isolated git branch...")
    timestamp = int(time.time())
    branch_name = f"autofix-run-{timestamp}"
    try:
        subprocess.run(["git", "checkout", "-b", branch_name], check=True)
        print(
            f"🌿 Created branch '{branch_name}'. You can 'git checkout main' to undo ALL changes."
        )
    except subprocess.CalledProcessError:
        print("❌ Could not create branch. Check if your git status is clean.")
        return

    # 2. Run tscanner (Linting)
    print("🔍 Scanning codebase (Linting + Performance)...")
    file_map = {}

    # A. tscanner
    try:
        result = subprocess.run(
            ["tscanner", "check", "--format", "json"], capture_output=True, text=True
        )
        if result.returncode == 0 or result.stdout:
            try:
                t_data = json.loads(result.stdout)
                if isinstance(t_data, dict):
                    # Filter tscanner results with our Global Ignore List
                    try:
                        sys.path.append(os.path.join(os.getcwd(), "tools"))
                        import opti_scanner

                        ignore_dirs = opti_scanner.GLOBAL_IGNORE_DIRS
                        ignore_exts = opti_scanner.IGNORE_EXTENSIONS
                    except ImportError:
                        # Fallback defaults if opti_scanner is missing (unlikely)
                        ignore_dirs = {"node_modules", "venv", ".git", "04_ARCHIVE"}
                        ignore_exts = {".bak"}

                    for f in t_data.get("files", []):
                        fpath = Path(f["file"])

                        # 1. Check Extensions
                        if fpath.suffix in ignore_exts:
                            continue

                        # 2. Check Directories (Path Parts)
                        parts = fpath.parts
                        if any(bad in parts for bad in ignore_dirs):
                            continue

                        file_map[f["file"]] = f["issues"]
            except json.JSONDecodeError:
                pass
    except Exception as e:
        print(f"⚠️ tscanner warning: {e}")

    # B. opti_scanner (Performance)
    try:
        sys.path.append(os.path.join(os.getcwd(), "tools"))
        import opti_scanner

        # Reload rules just in case
        root_dir = Path(os.getcwd())

        for root, dirs, files in os.walk(root_dir):
            root_path = Path(root)
            # Prune directories
            dirs[:] = [d for d in dirs if d not in opti_scanner.GLOBAL_IGNORE_DIRS]
            if any(part in opti_scanner.GLOBAL_IGNORE_DIRS for part in root_path.parts):
                continue

            for file in files:
                if file.endswith(".py"):
                    full_path = root_path / file
                    rel_path = str(full_path.relative_to(root_dir))

                    # Skip tools themselves
                    if full_path.name in [
                        "opti_scanner.py",
                        "smart_fixer.py",
                        "resilience.py",
                    ]:
                        continue

                    try:
                        findings = opti_scanner.scan_file(full_path)
                        if findings:
                            current_list = file_map.setdefault(rel_path, [])
                            for f in findings:
                                # Normalize to tscanner format
                                current_list.append(
                                    {
                                        "rule": f["rule_id"],
                                        "line": f["line"],
                                        "message": f"{f['suggestion']} (Priority: {f['priority']})",
                                        "line_text": f["code"],
                                    }
                                )
                    except Exception as e:
                        print(f"⚠️ Error scanning {rel_path}: {e}")

    except Exception as e:
        print(f"⚠️ opti_scanner warning: {e}")

    # Reconstruct scan_data
    scan_data = {"files": [], "summary": {"total_issues": 0}}
    for fname, issues in file_map.items():
        if issues:
            scan_data["files"].append({"file": fname, "issues": issues})
            scan_data["summary"]["total_issues"] += len(issues)

    if not scan_data["files"]:
        print("✅ No issues found.")
        return

    total_issues = scan_data["summary"]["total_issues"]
    print(f"⚠️ Found {total_issues} issues in {len(scan_data['files'])} files.")

    # 3. Initialize Router
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.getenv("OPENROUTER_API_KEY", "dummy_local_key")
    router = UnifiedModelRouter(api_key=api_key)

    # 4. Process each file
    files_fixed = 0
    files_reverted = 0
    max_files = 100

    for idx, file_data in enumerate(scan_data["files"]):
        if idx >= max_files:
            print(f"🛑 Reached limit of {max_files} files. Stopping batch.")
            break

        file_path = file_data["file"]
        issues = file_data["issues"]
        initial_issue_count = len(issues)

        print(f"\n📂 Processing {file_path} ({initial_issue_count} issues)...")

        try:
            full_path = Path(os.getcwd()) / file_path
            content = full_path.read_text(encoding="utf-8")
            suffix = full_path.suffix.lstrip(".") or "txt"

            issue_summary = "\n".join(
                [
                    f"- {i.get('line', '?')} (Rule: {i.get('rule', 'unknown')}): "
                    f"{i.get('message', 'No message')} | Code: {i.get('line_text', '').strip()}"
                    for i in issues
                ]
            )

            prompt = _build_prompt(issue_summary, content, 1, "", suffix)
            # Query the fast coding model
            response = await router.query(prompt, force_model="gpt-oss:latest")
            fixed_content = response.get("content", "")

            # --- Apply and Verify (First Pass) ---
            success, new_issues_count, failure_details = await apply_and_verify(
                router,
                file_path,
                full_path,
                content,
                fixed_content,
                initial_issue_count,
            )

            if success:
                _clear_failure_history(file_path)
                files_fixed += 1
                continue

            # --- Self-Correction Retry ---
            print(f"🔄 Attempting self-correction for {file_path}...")
            candidate_text = full_path.read_text(encoding="utf-8")
            candidate_hash = _hash_content(candidate_text)
            guidance = _register_failure_history(
                file_path, failure_details, candidate_hash
            )
            failure_note = (
                f"{new_issues_count} issues remain after verification"
                if new_issues_count is not None
                else "verification returned no issue count"
            )

            history_entry = RULE_HISTORY_CACHE.get(file_path)
            current_issues = history_entry["last_issues"] if history_entry else []
            if not current_issues or (
                history_entry
                and history_entry.get("last_content_hash") != candidate_hash
            ):
                _, current_issues = _run_detectors(str(full_path))
                if history_entry:
                    history_entry["last_content_hash"] = candidate_hash
                    history_entry["last_issues"] = current_issues

            if current_issues:
                retry_issues_text = "\n".join(
                    [
                        f"- Line {i['line']}: {i['message']} (Rule: {i['rule']})\n  Code: {i['line_text']}"
                        for i in current_issues
                    ]
                )

                retry_prompt = _build_prompt(
                    retry_issues_text,
                    content,
                    2,
                    failure_note,
                    suffix,
                    guidance,
                )
                response_retry = await router.query(
                    retry_prompt, force_model="gpt-oss:latest"
                )
                fixed_content_retry = response_retry.get("content", "")

                (
                    success_retry,
                    final_issues_count,
                    final_issues,
                ) = await apply_and_verify(
                    router,
                    file_path,
                    full_path,
                    content,
                    fixed_content_retry,
                    initial_issue_count,
                )

                if success_retry:
                    print("✅ Self-correction succeeded!")
                    _clear_failure_history(file_path)
                    files_fixed += 1
                else:
                    retry_candidate_text = full_path.read_text(encoding="utf-8")
                    retry_candidate_hash = _hash_content(retry_candidate_text)
                    _register_failure_history(
                        file_path, final_issues, retry_candidate_hash
                    )
                    print("❌ Self-correction failed. Reverting safely.")
                    full_path.write_text(content, encoding="utf-8")
                    _clear_failure_history(file_path)
                    files_reverted += 1
            else:
                print("⚠️ Could not diagnose failure. Reverting.")
                full_path.write_text(content, encoding="utf-8")
                _clear_failure_history(file_path)
                files_reverted += 1

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")

    print(
        f"\n🎉 Run Complete. Fixed: {files_fixed}, Reverted/Skipped: {files_reverted}"
    )
    print(f"👉 To keep changes: git merge {branch_name}")
    print(f"👉 To discard: git checkout main && git branch -D {branch_name}")


async def apply_and_verify(
    router, file_path, full_path, original_content, new_content_raw, initial_count
):
    candidate_content = None

    # 1. Try Patch Method
    patch_result = _apply_search_replace(original_content, new_content_raw)
    if patch_result and patch_result != original_content:
        candidate_content = patch_result
        print("⚡ Applied patch successfully (Token Savings Mode).")

    # 2. Hybrid Fallback: Check for Full File Code Block
    elif "```" in new_content_raw:
        lines = new_content_raw.split("\n")
        code_lines = []
        in_block = False
        for line in lines:
            if line.strip().startswith("```"):
                if in_block:
                    break  # Stop at first block end
                in_block = True
                continue
            if in_block:
                code_lines.append(line)

        # Check if the block looks like a SEARCH block start? No, _apply_search_replace would have caught it.
        # This assumes the model ignored instructions and sent full file.
        if code_lines:
            potential_full = "\n".join(code_lines)
            # Heuristic: If it's roughly the same size as original, it's likely a full file
            if 0.5 < len(potential_full) / len(original_content) < 1.5:
                candidate_content = potential_full
                print("⚠️ Model returned full file (Legacy Mode).")

    if candidate_content:
        # Sanity check
        if (
            len(candidate_content) > 10
            and abs(len(candidate_content) - len(original_content))
            < len(original_content) * 0.5
        ):
            # Write
            full_path.write_text(candidate_content, encoding="utf-8")

            # Verify (TScanner + OptiScanner)

            # A. Check OptiScanner Findings
            opti_issues = 0
            try:
                import opti_scanner

                findings = opti_scanner.scan_file(full_path)
                opti_issues = len(findings)
            except Exception:
                pass

            # B. Check TScanner
            # Note: tscanner might not pick up the new file content immediately if it caches?
            # Assuming subprocess run is fresh.
            verify_res = subprocess.run(
                ["tscanner", "check", file_path, "--format", "json"],
                capture_output=True,
                text=True,
            )
            try:
                v_data = json.loads(verify_res.stdout)
                if isinstance(v_data, list):
                    # v_files is not available here, this path seems wrong or old tscanner behavior?
                    # Let's assume standard tscanner json output structure: {"files": [...], ...}
                    v_issues = 0
                else:
                    v_files = v_data.get("files", [])
                    issue_list = v_files[0]["issues"] if v_files else []
                    v_issues = len(issue_list)

                total_remaining = v_issues + opti_issues

                if total_remaining < initial_count:
                    print(f"✅ Verified: {initial_count} -> {total_remaining} issues.")
                    return (
                        True,
                        total_remaining,
                        issue_list,
                    )  # ignoring opti issue list merge for now
                else:
                    print(
                        f"⚠️ Verification Failed: {total_remaining} issues remaining (Opti: {opti_issues}, TScanner: {v_issues})."
                    )
                    return False, total_remaining, issue_list
            except json.JSONDecodeError:
                print("⚠️ Scan error. Assuming partial success.")
                return True, 0, []
        else:
            print("⚠️ Safety Rejection: Size mismatch.")
            return False, initial_count, []

    return False, initial_count, []


if __name__ == "__main__":
    try:
        asyncio.run(run_smart_fixer())
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user.")
    except Exception as e:
        print(f"\n❌ Fatal Error: {e}")
