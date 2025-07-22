from trie.prefix_trie import PrefixTrie
import re

def show_predict_menu():
    print("""
Predict/Restore Text
1. Load trie from file    (~)
2. Display trie           (#)
3. List all matches       ($)
4. Restore single word    (?)
5. Restore full text      (&)
6. Restore best matches   (@)
7. Help                   (!)
8. Back to Main           (\\)
""")

def _extract(tok: str):
    """Strip leading/trailing punctuation (but keep ‘*’) → return (pre, core, post)."""
    # [^\w\*] = anything that is NOT a word-char or a '*'
    m = re.match(r"^([^\w\*]*)([\w\*]+)([^\w\*]*)$", tok)
    return m.groups() if m else ("", tok, "")

def _process_all(tok: str, trie: PrefixTrie) -> str:
    pre, core, post = _extract(tok)
    core_l = core.lower()
    if "*" in core_l:
        matches = trie.wildcard_match(core_l)
        matches.sort(key=lambda w: trie.get_frequency(w), reverse=True)
        return f"{pre}{matches}{post}"
    return tok

def _process_best(tok: str, trie: PrefixTrie) -> str:
    pre, core, post = _extract(tok)
    core_l = core.lower()
    if "*" in core_l:
        best = trie.best_match(core_l)
        if best:
            # preserve casing
            if core.isupper():
                best = best.upper()
            elif core[0].isupper():
                best = best.capitalize()
            return f"{pre}<{best}>{post}"
    return tok

def _apply_restore(in_path: str, out_path: str, trie: PrefixTrie, processor):
    """Read each token from in_path, process with `processor`, write to out_path."""
    with open(in_path, 'r', encoding='utf-8') as fin, \
         open(out_path, 'w', encoding='utf-8') as fout:
        for line in fin:
            parts = [processor(tok, trie) for tok in line.rstrip("\n").split()]
            fout.write(" ".join(parts) + "\n")

def run_predict_cli(trie: PrefixTrie):
    while True:
        show_predict_menu()
        choice = input("Select option: ").strip()

        if choice in ['1', '~']:
            # load word,frequency file
            while True:
                raw = input("Input file (word,frequency) [\\ to cancel]: ").strip()
                if raw == '\\':
                    print("Load cancelled.")
                    break
                path = raw.strip('"').strip("'")
                try:
                    trie.load_from_word_freq_file(path)
                    print(f"Keywords loaded from {path} into trie.")
                    break
                except FileNotFoundError:
                    print(f"File not found: {path}. Try again.")
                except Exception as e:
                    print(f"Error: {e}")
                    break

        elif choice in ['2', '#']:
            words = trie.list_words()
            if words:
                print("Keywords in trie:")
                for w in words:
                    print("  ", w)
            else:
                print("(Trie is empty)")

        elif choice in ['3', '$']:
            patt = input("Wildcard pattern (use '*'): ").strip().lower()
            matches = trie.wildcard_match(patt)
            matches.sort(key=lambda w: trie.get_frequency(w), reverse=True)
            print(",".join(f"[{w},{trie.get_frequency(w)}]" for w in matches) if matches else "")

        elif choice in ['4', '?']:
            raw = input("Wildcard pattern (use '*'): ").strip()
            pre, core, post = _extract(raw)
            if "*" not in core:
                print("No wildcard detected.")
            else:
                best = trie.best_match(core.lower())
                if best:
                    # reapply casing
                    if core.isupper():
                        best = best.upper()
                    elif core[0].isupper():
                        best = best.capitalize()
                    print(f'Restored keyword "{pre}{best}{post}"')
                else:
                    print("No match found.")

        elif choice in ['5', '&']:
            in_f = input("Input file: ").strip()
            out_f = input("Output file: ").strip()
            try:
                _apply_restore(in_f, out_f, trie, _process_all)
                print(f"All matches restored and saved to {out_f}")
            except Exception as e:
                print("Error:", e)

        elif choice in ['6', '@']:
            in_f = input("Input file: ").strip()
            out_f = input("Output file: ").strip()
            try:
                _apply_restore(in_f, out_f, trie, _process_best)
                print(f"Best matches restored and saved to {out_f}")
            except Exception as e:
                print("Error:", e)

        elif choice in ['7', '!']:
            continue  # will reprint menu

        elif choice in ['8', '\\']:
            break

        else:
            print("Invalid choice; enter '!' for help.")
