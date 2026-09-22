#!/usr/bin/env python3
import os
import re
import json
import argparse
import subprocess


def get_keys_values_and_comments_from_file(file_path):
    """
    Extracts localization keys, values, and preceding source comments from a YAML file.
    Assumes standard Paradox localization format:
     key: "value"
     key:0 "value"
    Returns a dictionary: {key: {'value': value, 'comment': source_comment}}
    """
    data = {}
    prev_lines = []
    try:
        with open(file_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
            for line in f:
                line_str = line.strip()
                # Skip empty lines
                if not line_str:
                    prev_lines = []
                    continue
                # Collect comment lines
                if line_str.startswith('#'):
                    prev_lines.append(line_str)
                    continue
                
                # Check for key: "value" or key:0 "value" pattern
                if ':' in line_str:
                    parts = line_str.split(':', 1)
                    key_part = parts[0].strip()
                    value_part = parts[1].strip()
                    
                    # Basic validation
                    if key_part and not key_part.startswith('l_') and not key_part.startswith(' '):
                        value = value_part
                        first_q = value.find('"')
                        last_q = value.rfind('"')
                        if first_q != -1 and last_q > first_q:
                            value = value[first_q+1:last_q]
                        else:
                            ignore_index_match = re.search(r'^\d+\s+"', value)
                            if ignore_index_match:
                                value = value[ignore_index_match.end()-1:]
                            elif value.startswith('"'):
                                pass # Normal case
                            elif re.match(r'^\d+\s+', value):
                                # Case like: key:0 "value"
                                match = re.search(r'^\d+\s+(.*)', value)
                                if match:
                                    value = match.group(1)

                            if value.startswith('"') and value.endswith('"'):
                                value = value[1:-1]
                        
                        source_comment = None
                        if prev_lines:
                            # 1. Check for explicit "Original:" marker in preceding comments
                            for pl in reversed(prev_lines):
                                if "Original:" in pl:
                                    source_comment = pl.split("Original:", 1)[1].strip()
                                    break
                            # 2. Check for single-line comment directly above key (from apply_translations_v2)
                            if not source_comment and len(prev_lines) == 1:
                                c = prev_lines[0].lstrip('#').strip()
                                # Ignore banner / separator comment lines (e.g. ###, ---) and require Chinese characters
                                if not re.match(r'^[\s#=\-_*]+$', prev_lines[0]) and len(c) > 0 and re.search(r'[\u4e00-\u9fff]', c):
                                    source_comment = c

                        if source_comment and source_comment.startswith('"') and source_comment.endswith('"'):
                            source_comment = source_comment[1:-1]

                        data[key_part] = {
                            'value': value,
                            'comment': source_comment
                        }
                        prev_lines = []
                else:
                    prev_lines = []
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
    return data


def get_keys_and_values_from_file(file_path):
    """
    Extracts localization keys and their values from a YAML file.
    Returns a dictionary {key: value}
    """
    raw_data = get_keys_values_and_comments_from_file(file_path)
    return {k: v['value'] for k, v in raw_data.items()}


def get_changed_keys(commit_hash, cn_dir, details=False):
    """
    Returns a set of keys that have changed in the Chinese directory since the given commit.
    Ignores whitespace changes.
    """
    changed_keys = set()
    try:
        # Get list of changed files
        cmd = ["git", "diff", "--name-only", commit_hash, "HEAD", cn_dir]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        changed_files = [f for f in result.stdout.splitlines() if f.strip()]
        
        for file_path in changed_files:
            if not file_path.endswith('.yml'):
                continue
            
            # Get changes for this file, ignoring whitespace
            # -U0 avoids context lines, making parsing easier
            cmd_diff = ["git", "diff", "-w", "-U0", commit_hash, "HEAD", file_path]
            diff_result = subprocess.run(cmd_diff, capture_output=True, text=True)
            
            if diff_result.returncode != 0:
                if details:
                    print(f"Warning: Could not diff file {file_path}")
                continue

            for line in diff_result.stdout.splitlines():
                if line.startswith('+') and not line.startswith('+++'):
                    # This is an added/modified line
                    content = line[1:].strip()
                    if ':' in content and not content.startswith('#'):
                        parts = content.split(':', 1)
                        key = parts[0].strip()
                        # Basic validity check (matches logic in extracting keys)
                        if key and not key.startswith('l_'):
                            changed_keys.add(key)
                            
    except subprocess.CalledProcessError as e:
        print(f"Error running git diff: {e}")
    except Exception as e:
        print(f"Error processing git changes: {e}")
        
    return changed_keys


def main():
    parser = argparse.ArgumentParser(description="Check translation coverage.")
    parser.add_argument("-o", "--output", help="Output file path for missing/outdated translations in JSON format.")
    parser.add_argument("-c", "--commit", help="Git commit hash to compare against for finding outdated translations.")
    parser.add_argument("-l", "--lockfile", help="Path to translation lockfile (default: data/translation_lock.json).")
    parser.add_argument("--init-lock", action="store_true", help="Initialize/generate the lockfile from current translation status and exit.")
    parser.add_argument("-d", "--details", action="store_true", help="Show detailed warnings and list of missing/outdated keys.")
    args = parser.parse_args()

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    loc_dir = os.path.join(repo_root, "localisation")
    cn_dir = os.path.join(loc_dir, "simp_chinese")
    en_dir = os.path.join(loc_dir, "english")
    default_lockfile = os.path.join(repo_root, "data", "translation_lock.json")
    lockfile_path = args.lockfile if args.lockfile else default_lockfile

    if not os.path.exists(cn_dir):
        print(f"Error: Chinese localization directory not found at {cn_dir}")
        return

    # Map Chinese keys to (file_path, original_text)
    cn_keys_map = {} # key -> {'file': file_path, 'original': text}
    
    # Map English keys and their comments
    en_keys = set()
    en_comments = {} # key -> source_comment (extracted from YAML comments)

    # Get changed keys if commit hash is provided
    changed_keys = set()
    if args.commit:
        print(f"Calculating changes since commit {args.commit}...")
        changed_keys = get_changed_keys(args.commit, cn_dir, details=args.details)
        print(f"Found {len(changed_keys)} changed/new keys.")

    print(f"Scanning Chinese files in {cn_dir}...")
    for root, dirs, files in os.walk(cn_dir):
        for file in files:
            if file.endswith(".yml"):
                file_path = os.path.join(root, file)
                file_data = get_keys_and_values_from_file(file_path)
                rel_path = os.path.relpath(file_path, cn_dir)
                for key, value in file_data.items():
                    cn_keys_map[key] = {'file': rel_path, 'original': value}

    print(f"Scanning English files in {en_dir}...")
    if os.path.exists(en_dir):
        for root, dirs, files in os.walk(en_dir):
            for file in files:
                if file.endswith(".yml"):
                    file_path = os.path.join(root, file)
                    en_file_data = get_keys_values_and_comments_from_file(file_path)
                    for key, val_dict in en_file_data.items():
                        en_keys.add(key)
                        if val_dict.get('comment'):
                            en_comments[key] = val_dict['comment']
    else:
        if args.details:
            print(f"Warning: English localization directory not found at {en_dir}")

    # Handle --init-lock
    if args.init_lock:
        print(f"\nInitializing translation lockfile at {lockfile_path}...")
        lock_dict = {}
        for key, info in cn_keys_map.items():
            if key in en_keys:
                # Prioritize existing English comment as baseline original text; fallback to current Chinese text
                comment_text = en_comments.get(key)
                original_to_lock = comment_text if comment_text else info['original']
                lock_dict[key] = {
                    "original": original_to_lock,
                    "file": info['file']
                }
        os.makedirs(os.path.dirname(os.path.abspath(lockfile_path)), exist_ok=True)
        try:
            with open(lockfile_path, 'w', encoding='utf-8') as f:
                json.dump(lock_dict, f, ensure_ascii=False, indent=2)
            print(f"Successfully initialized lockfile with {len(lock_dict)} keys.")
            print(f"Lockfile saved to {lockfile_path}")
        except Exception as e:
            print(f"Error saving lockfile to {lockfile_path}: {e}")
        return

    # Load lockfile if available
    lock_data = {}
    has_lockfile = False
    if os.path.exists(lockfile_path):
        try:
            with open(lockfile_path, 'r', encoding='utf-8') as f:
                lock_data = json.load(f)
            has_lockfile = True
            print(f"Loaded translation lockfile from {lockfile_path} ({len(lock_data)} keys).")
        except Exception as e:
            if args.details:
                print(f"Warning: Could not read lockfile at {lockfile_path}: {e}")
    else:
        if args.lockfile:
            if args.details:
                print(f"Warning: Specified lockfile not found at {lockfile_path}. Falling back to English comments.")
        else:
            print(f"No lockfile found at {lockfile_path}. Falling back to English file comments.")

    total_cn_keys = len(cn_keys_map)
    missing_items = []
    
    # Track statistics
    stats = {
        'missing': 0,
        'outdated': 0,
        'empty': 0
    }

    for key, info in cn_keys_map.items():
        original_text = info['original']
        # Check if original text is empty or just whitespace
        if not original_text or original_text.strip() == "":
            if args.details:
                print(f"Warning: Key '{key}' in {info['file']} has empty original text.")
            missing_items.append({
                "file": info['file'],
                "key": key,
                "original": original_text,
                "status": "empty"
            })
            stats['empty'] += 1
            continue

        if key not in en_keys:
            missing_items.append({
                "file": info['file'],
                "key": key,
                "original": original_text,
                "status": "missing"
            })
            stats['missing'] += 1
        else:
            # Key exists in English. Check if original text has changed after translation.
            old_original = None
            is_outdated = False

            if has_lockfile and key in lock_data:
                lock_entry = lock_data[key]
                lock_orig = lock_entry.get("original") if isinstance(lock_entry, dict) else lock_entry
                if lock_orig is not None and original_text.strip() != lock_orig.strip():
                    is_outdated = True
                    old_original = lock_orig
            elif key in en_comments and en_comments[key]:
                comment_orig = en_comments[key]
                if original_text.strip() != comment_orig.strip():
                    is_outdated = True
                    old_original = comment_orig
            elif args.commit and key in changed_keys:
                is_outdated = True

            if is_outdated:
                item = {
                    "file": info['file'],
                    "key": key,
                    "original": original_text,
                    "new_original": original_text,
                    "status": "outdated"
                }
                if old_original is not None:
                    item["old_original"] = old_original
                missing_items.append(item)
                stats['outdated'] += 1

    total_eligible_keys = total_cn_keys - stats['empty']
    coverage = 0
    up_to_date_coverage = 0
    if total_eligible_keys > 0:
        coverage = (total_eligible_keys - stats['missing']) / total_eligible_keys * 100
        up_to_date_coverage = (total_eligible_keys - stats['missing'] - stats['outdated']) / total_eligible_keys * 100
    total_issues = len(missing_items)

    detection_methods = []
    if has_lockfile:
        detection_methods.append("Lockfile")
    if len(en_comments) > 0:
        detection_methods.append("Comments fallback")
    if args.commit:
        detection_methods.append(f"Git diff ({args.commit})")
    detection_str = " + ".join(detection_methods) if detection_methods else "None"

    print("\n" + "="*50)
    print("Translation Coverage Report")
    print("="*50)
    print(f"Total Chinese Keys: {total_cn_keys}")
    print(f"Keys with Empty Original: {stats['empty']} (excluded from coverage)")
    print(f"Total Eligible for Translation: {total_eligible_keys}")
    print(f"Total English Keys: {len(en_keys)}")
    print(f"Missing Translations: {stats['missing']}")
    print(f"Outdated Translations: {stats['outdated']} (Detection: {detection_str})")
    print(f"Coverage (ignoring outdated): {coverage:.2f}%")
    print(f"Up-to-date Coverage: {up_to_date_coverage:.2f}%")
    print("="*50)

    if total_issues > 0:
        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump([item for item in missing_items if not item.get("status")=="empty"], f, ensure_ascii=False, indent=4)
                print(f"\nReport written to {args.output}")
            except Exception as e:
                print(f"\nError writing to output file: {e}")

        if args.details:
            # Group by file and status
            items_by_file = {}
            for item in missing_items:
                fpath = item['file']
                if fpath not in items_by_file:
                    items_by_file[fpath] = []
                items_by_file[fpath].append(item)
            
            print("\nIssues found (grouped by source file):")
            for file in sorted(items_by_file.keys()):
                print(f"\n{file}:")
                for item in sorted(items_by_file[file], key=lambda x: x['key']):
                    status_tag = f"[{item['status'].upper()}]"
                    print(f"  - {status_tag} {item['key']}")


if __name__ == "__main__":
    main()
