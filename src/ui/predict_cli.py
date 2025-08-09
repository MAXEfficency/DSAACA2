from trie.prefix_trie import PrefixTrie
import re


def show_predict_menu():
    print(r"""
----------------------------------------------------------------
Predict/Restore Text Commands:
  '~', '#', '$', '?', '&', '@', '!', '\'
----------------------------------------------------------------
~                     (read keywords from file to make Trie)
#                     (display Trie)
$ra*nb*w              (list all possible matching keywords)
?ra*nb*w              (restore a word using best keyword match)
&                     (restore a text using all matching keywords)
@                     (restore a text using best keyword matches)
!                     (print instructions)
\                     (exit)
----------------------------------------------------------------
""")


def _prompt_filepath(prompt: str, must_exist: bool = False) -> str | None:
    """
    Prompt the user for a filepath.
    If must_exist=True, keep asking until a file is found or user cancels with '\\'.
    If must_exist=False, return the entered path or None if cancelled.
    """
    while True:
        raw = input(f"{prompt} [\\ to cancel]: ").strip()
        if raw == '\\':
            return None
        path = raw.strip('"').strip("'")
        if must_exist:
            try:
                open(path, 'r').close()
                return path
            except FileNotFoundError:
                print(f"File not found: {path}. Please try again.")
            except Exception as e:
                print(f"Error accessing file: {e}")
                return None
        else:
            return path


def _extract(tok: str):
    """Strip leading/trailing punctuation (but keep '*') → return (pre, core, post)."""
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
    show_predict_menu()
    while True:
        cmd = input("> ").strip()
        if not cmd:
            continue

        op = cmd[0]
        arg = cmd[1:].strip()  # pattern for $ / ?, otherwise usually empty

        # ~ : load keywords (word,frequency) from file
        if op == '~':
            path = _prompt_filepath("Please enter input file", must_exist=True)
            if not path:
                print("Load cancelled.")
            else:
                try:
                    trie.load_from_word_freq_file(path)
                    print(f"Keywords loaded from {path} into trie.")
                except Exception as e:
                    print(f"Error loading keywords: {e}")

        # # : display trie (ASCII)
        elif op == '#':
            trie.print_trie()

        # $<pattern> : list all matches ranked by freq
        elif op == '$':
            if not arg:
                print("Usage: $<pattern-with-*>   e.g. $ca*")
                continue
            patt = arg.lower()
            matches = trie.wildcard_match(patt)
            matches.sort(key=lambda w: trie.get_frequency(w), reverse=True)
            print(",".join(f"[{w},{trie.get_frequency(w)}]" for w in matches) if matches else "")

        # ?<pattern> : best match for a single word
        elif op == '?':
            if not arg:
                print("Usage: ?<pattern-with-*>   e.g. ?ca*")
                continue
            pre, core, post = _extract(arg)
            if "*" not in core:
                print("No wildcard detected.")
            else:
                best = trie.best_match(core.lower())
                if best:
                    if core.isupper():
                        best = best.upper()
                    elif core[0].isupper():
                        best = best.capitalize()
                    print(f'Restored keyword "{pre}{best}{post}"')
                else:
                    print("No match found.")

        # & : restore a whole text (all matches)
        elif op == '&':
            in_f = _prompt_filepath("Please enter input file", must_exist=True)
            if not in_f:
                print("Restore cancelled.")
                continue
            out_f = _prompt_filepath("Please enter output file")
            if not out_f:
                print("Restore cancelled.")
                continue
            try:
                _apply_restore(in_f, out_f, trie, _process_all)
                print(f"All matches restored and saved to {out_f}")
            except Exception as e:
                print(f"Error during restore: {e}")

        # @ : restore a whole text (best matches)
        elif op == '@':
            in_f = _prompt_filepath("Please enter input file", must_exist=True)
            if not in_f:
                print("Restore cancelled.")
                continue
            out_f = _prompt_filepath("Please enter output file")
            if not out_f:
                print("Restore cancelled.")
                continue
            try:
                _apply_restore(in_f, out_f, trie, _process_best)
                print(f"Best matches restored and saved to {out_f}")
            except Exception as e:
                print(f"Error during restore: {e}")

        # ! : reprint instructions
        elif op == '!':
            show_predict_menu()

        # \ : exit to main
        elif op == '\\':
            break

        else:
            print("Unknown command. Enter '!' for help.")