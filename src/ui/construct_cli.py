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
  ~<filename>    (load keywords from file)
  =<filename>    (dump keywords (word,frequency) to file)
  !              (print these instructions)
  \              (exit back to Main Menu)
""")

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
            if found:
                print(f"Keyword \"{arg}\" is found")
            else:
                print(f"Keyword \"{arg}\" is not found")

        elif op == '#':
            trie.print_trie()

        elif op == '@':
            path = input("Please enter output filename: ").strip()
            if not path:
                print("Save cancelled.")
                continue
            try:
                trie.save_display_to_file(path)   # ASCII view
                print(f"Trie display saved to {path}")
            except Exception as e:
                print(f"Error saving trie: {e}")


        elif op == '~':
            if not arg:
                print("Usage: ~<filepath>")
                continue
            try:
                trie.load_from_word_freq_file(arg)
                print(f"Keywords loaded from {arg} into trie.")
            except FileNotFoundError:
                print(f"File not found: {arg}")
            except Exception as e:
                print(f"Error loading keywords: {e}")

        elif op == '=':
            if not arg:
                print("Usage: =<filepath>")
                continue
            try:
                trie.save_to_file(arg)            # word,frequency dump
                print(f"Dumped {len(trie.list_words())} keywords to {arg}")
            except Exception as e:
                print(f"Error dumping keywords: {e}")


        elif op == '!':
            show_instructions()

        elif op == '\\':
            break

        else:
            print("Unknown command. Enter '!' for help.")
