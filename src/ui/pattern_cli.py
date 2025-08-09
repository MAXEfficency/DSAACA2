# src/ui/pattern_cli.py
from __future__ import annotations
from typing import List, Tuple
from features.pattern import glob_match, is_glob_pattern

def _print_results(matches: List[Tuple[str, int]], max_rows: int | None = None) -> None:
    if not matches:
        print("No matches.")
        return
    print(f"Found {len(matches)} match(es).")
    rows = matches if max_rows is None else matches[:max_rows]
    for i, (w, f) in enumerate(rows, 1):
        print(f"{i:>3}. {w}  (freq={f})")
    if max_rows is not None and len(matches) > max_rows:
        print(f"... and {len(matches) - max_rows} more.")

def _restore_tokens(tokens: List[str], trie, interactive: bool) -> List[str]:
    restored: List[str] = []
    for tok in tokens:
        if is_glob_pattern(tok):
            matches = glob_match(trie, tok, top_k=5)
            if not matches:
                restored.append(tok)
                continue
            if interactive:
                print(f"\nPattern: {tok}")
                _print_results(matches, max_rows=None)
                choice = input("Pick # to replace, 0 to keep original, or Enter for top-1: ").strip()
                if choice == "":
                    restored.append(matches[0][0])
                else:
                    try:
                        n = int(choice)
                        if n == 0:
                            restored.append(tok)
                        elif 1 <= n <= len(matches):
                            restored.append(matches[n - 1][0])
                        else:
                            print("Invalid number, keeping original.")
                            restored.append(tok)
                    except ValueError:
                        print("Invalid input, keeping original.")
                        restored.append(tok)
            else:
                # auto mode: take top-1
                restored.append(matches[0][0])
        else:
            restored.append(tok)
    return restored

def run_pattern_cli(trie) -> None:
    """
    Advanced Pattern Search (Glob+)
    1) Find matches for a pattern
    2) Restore a line (interactive)
    3) Restore a line (auto, top-1)
    4) Back to main
    """
    while True:
        print("\n" + "-" * 44)
        print("Advanced Pattern Search (Glob+)")
        print("1. Find matches for a pattern")
        print("2. Restore a line (interactive picks)")
        print("3. Restore a line (auto: pick top-1)")
        print("4. Back to main")
        choice = input("Enter choice: ").strip()

        if choice == '1':
            pat = input("Enter Glob+ pattern: ").strip()
            try:
                topk_raw = input("Enter top_k (blank for all): ").strip()
                top_k = int(topk_raw) if topk_raw else None
            except ValueError:
                print("Invalid top_k, showing all.")
                top_k = None
            try:
                matches = glob_match(trie, pat, top_k=top_k)
                _print_results(matches, max_rows=None)
            except ValueError as e:
                print(f"Pattern error: {e}")

        elif choice == '2':
            line = input("Enter a line (patterns may include ?, *, [...]): ").rstrip("\n")
            tokens = line.split()
            try:
                out_tokens = _restore_tokens(tokens, trie, interactive=True)
                print("\nRestored line:")
                print(" ".join(out_tokens))
            except ValueError as e:
                print(f"Pattern error: {e}")

        elif choice == '3':
            line = input("Enter a line (patterns may include ?, *, [...]): ").rstrip("\n")
            tokens = line.split()
            try:
                out_tokens = _restore_tokens(tokens, trie, interactive=False)
                print("\nAuto-restored line (top-1 per pattern):")
                print(" ".join(out_tokens))
            except ValueError as e:
                print(f"Pattern error: {e}")

        elif choice == '4':
            break
        else:
            print("Invalid choice. Please select 1–4.")
