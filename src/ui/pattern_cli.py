from __future__ import annotations
from typing import List, Tuple
from features.pattern import glob_match, is_glob_pattern
import re

_CORE_CHARS = r"A-Za-z0-9\?\*\[\]-"

GLOB_HELP = r"""
How to use Advanced Pattern Search (Glob+)

Syntax:
  ?        exactly one character          (e.g., th??  → this, that)
  *        zero or more characters        (e.g., h*se  → house, horse)
  [abc]    one character from the set     (e.g., b[ae]t → bat, bet)
  [a-z]    one character in a range       (e.g., co[l-n]or → color, conor)

Notes:
  • Case-sensitive: use the same case as your trie words.
  • Results are ranked by frequency (highest first).
"""
def _split_token(tok: str) -> tuple[str, str, str]:
    """
    Split token into (pre, core, post), where core may include Glob+ chars.
    Examples:
      'th**,'   -> ('', 'th**', ',')
      '"H*se."' -> ('"', 'H*se', '."')
      'word'    -> ('', 'word', '')
    """
    # pre:     any chars NOT in core set
    # core:    one or more chars from core set
    # post:    any chars NOT in core set
    m = re.match(rf"^([^{_CORE_CHARS}]*)([{_CORE_CHARS}]+)([^{_CORE_CHARS}]*)$", tok)
    return m.groups() if m else ("", tok, "")

def _apply_casing(orig: str, repl: str) -> str:
    """
    Preserve casing style of 'orig' in 'repl':
      - ALL CAPS -> upper()
      - First letter capitalized -> capitalize()
      - else -> as-is
    """
    if orig.isupper():
        return repl.upper()
    if orig[:1].isupper() and (len(orig) == 1 or orig[1:].islower()):
        return repl.capitalize()
    return repl

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
        pre, core, post = _split_token(tok)
        # only treat the core as a pattern, not punctuation
        if is_glob_pattern(core):
            # case-insensitive match by lowercasing the core pattern
            pat = core.lower()
            matches = glob_match(trie, pat, top_k=5)
            if not matches:
                restored.append(tok)
                continue

            def pick_word(idx: int) -> str:
                chosen = matches[idx][0]  # raw word from trie (likely lowercase)
                chosen = _apply_casing(core, chosen)
                return f"{pre}{chosen}{post}"

            if interactive:
                print(f"\nPattern: {core}")
                _print_results(matches, max_rows=None)
                choice = input("Pick # to replace, 0 to keep original, or Enter for top-1: ").strip()
                if choice == "":
                    restored.append(pick_word(0))
                else:
                    try:
                        n = int(choice)
                        if n == 0:
                            restored.append(tok)
                        elif 1 <= n <= len(matches):
                            restored.append(pick_word(n - 1))
                        else:
                            print("Invalid number, keeping original.")
                            restored.append(tok)
                    except ValueError:
                        print("Invalid input, keeping original.")
                        restored.append(tok)
            else:
                restored.append(pick_word(0))  # auto: top-1, keep casing & punctuation
        else:
            restored.append(tok)
    return restored

def _apply_restore_file(in_path: str, out_path: str, trie, interactive: bool) -> None:
    """Read full text line-by-line, restore tokens that look like Glob+ patterns, write output file."""
    with open(in_path, 'r', encoding='utf-8') as fin, open(out_path, 'w', encoding='utf-8') as fout:
        for line in fin:
            tokens = line.rstrip("\n").split()
            out_tokens = _restore_tokens(tokens, trie, interactive=interactive)
            fout.write(" ".join(out_tokens) + "\n")

def run_pattern_cli(trie) -> None:
    """
    Advanced Pattern Search (Glob+)
    1) Helper (How this feature works)
    2) Find matches for a pattern
    3) Restore a text (interactive picks)
    4) Restore a text (auto: pick top-1)
    5) Back to main
    """
    while True:
        print("\n" + "-" * 44)
        print("Advanced Pattern Search (Glob+)")
        print("1. Helper (How this feature works)")
        print("2. Find matches for a pattern")
        print("3. Restore a text (interactive picks)")
        print("4. Restore a text (auto: pick top-1)")
        print("5. Back to main")
        choice = input("Enter choice: ").strip()

        if choice == '1':
            print(GLOB_HELP)

        elif choice == '2':
            print(GLOB_HELP)
            pat = input("Enter Glob+ pattern: ").strip()
            if not pat:
                print("No pattern entered."); continue
            top_k = None
            topk_raw = input("Enter top_k (blank for all): ").strip()
            if topk_raw:
                try:
                    top_k = int(topk_raw)
                    if top_k <= 0:
                        print("top_k must be positive; showing all."); top_k = None
                except ValueError:
                    print("Invalid top_k; showing all."); top_k = None
            try:
                matches = glob_match(trie, pat.lower(), top_k=top_k)  # <-- case-insensitive
                _print_results(matches, max_rows=None)
            except ValueError as e:
                print(f"Pattern error: {e}")

        elif choice == '3':
            in_f = input("Input file path: ").strip()
            out_f = input("Output file path: ").strip()
            if not in_f or not out_f:
                print("Cancelled."); continue
            try:
                _apply_restore_file(in_f, out_f, trie, interactive=True)
                print(f"Interactive restore complete → {out_f}")
            except FileNotFoundError:
                print("File not found.")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == '4':
            in_f = input("Input file path: ").strip()
            out_f = input("Output file path: ").strip()
            if not in_f or not out_f:
                print("Cancelled."); continue
            try:
                _apply_restore_file(in_f, out_f, trie, interactive=False)
                print(f"Auto restore (top-1) complete → {out_f}")
            except FileNotFoundError:
                print("File not found.")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == '5':
            break
        else:
            print("Invalid choice. Please select 1–5.")
