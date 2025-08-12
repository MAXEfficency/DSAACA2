# ui/construct_cli.py
from trie.prefix_trie import PrefixTrie

def show_instructions():
    print(r"""
Construct/Edit Trie Commands:
  +<word>        (add a keyword, default freq=1)
  -<word>        (delete a keyword)
  ?<word>        (search for a keyword)
  #              (display Trie)
  @              (write Trie display to file)
  ~              (load keywords from file)
  =              (dump keywords (word,frequency) to file)
  !              (print these instructions)
  \              (exit back to Main Menu)
""")

def _prompt_filepath(prompt: str, must_exist: bool = False) -> str | None:
    """
    Same behavior as in Predict:
      - prompts for a path
      - if must_exist, keeps asking until a file is found or user cancels with '\'
      - returns None on cancel
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

def run_construct_cli(trie: PrefixTrie):
    show_instructions()
    while True:
        cmd = input(">").strip()
        if not cmd:
            continue

        op, arg = cmd[0], cmd[1:].strip()

        if op == '+':
            if not arg:
                print("Usage: +<keyword>")
                continue
            trie.insert(arg, 1)
            print(f"Added '{arg}' (1).")

        elif op == '-':
            if not arg:
                print("Usage: -<keyword>")
                continue
            deleted = trie.delete(arg)
            print(f"Deleted '{arg}'." if deleted else f"Keyword \"{arg}\" is not found")

        elif op == '?':
            if not arg:
                print("Usage: ?<keyword>")
                continue
            found = trie.search(arg)
            print(f"Keyword \"{arg}\" is found" if found else f"Keyword \"{arg}\" is not found")

        elif op == '#':
            trie.print_trie()

        elif op == '@':
            path = _prompt_filepath("Please enter output filename")
            if not path:
                print("Save cancelled."); continue
            try:
                trie.save_display_to_file(path)   # ASCII view
                print(f"Trie display saved to {path}")
            except Exception as e:
                print(f"Error saving trie: {e}")

        elif op == '~':
            # NEW: prompt like Predict does
            path = _prompt_filepath("Please enter input file (word,frequency)", must_exist=True)
            if not path:
                print("Load cancelled."); continue
            try:
                trie.load_from_word_freq_file(path)
                print(f"Keywords loaded from {path} into trie.")
            except Exception as e:
                print(f"Error loading keywords: {e}")

        elif op == '=':
            # NEW: prompt like Predict does
            path = _prompt_filepath("Please enter output file")
            if not path:
                print("Dump cancelled."); continue
            try:
                trie.save_to_file(path)  # word,frequency dump
                print(f"Dumped {len(trie.list_words())} keywords to {path}")
            except Exception as e:
                print(f"Error dumping keywords: {e}")

        elif op == '!':
            show_instructions()

        elif op == '\\':
            break

        else:
            print("Unknown command. Enter '!' for help.")
