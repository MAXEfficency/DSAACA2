from trie.prefix_trie import PrefixTrie

def show_menu():
    print("""
Construct/Edit Trie
1. Add keyword      (+)
2. Delete keyword   (-)
3. Search keyword   (?)
4. Display trie     (#)
5. Save to file     (@)
6. Load from file   (~)
7. Dump keywords    (=)
8. Help             (!)
9. Back to Main     (\\)
""")

def run_construct_cli(trie: PrefixTrie):
    while True:
        show_menu()
        choice = input("Select option: ").strip()
        
        if choice in ['1', '+']:
            word = input("Word to add: ").strip()
            freq = int(input("Frequency: ").strip() or "1")
            trie.insert(word, freq)
            print(f"Added '{word}' ({freq}).")
        
        elif choice in ['2', '-']:
            word = input("Word to delete: ").strip()
            if trie.delete(word):
                print(f"Deleted '{word}'.")
            else:
                print(f"'{word}' not found.")
        
        elif choice in ['3', '?']:
            word = input("Word to search: ").strip()
            print("Found." if trie.search(word) else "Not found.")
        
        elif choice in ['4', '#']:
            # Display every word in the trie
            words = trie.list_words()
            if not words:
                print("(Trie is empty)")
            else:
                print("Keywords in trie:")
                for w in words:
                    print("  ", w)
        
        elif choice in ['5', '@']:
            path = input("Filepath to save: ").strip()
            trie.save_to_file(path)
            print(f"Trie saved to {path}.")
        
        elif choice in ['6', '~']:
            # Load keywords file, retry on error
            while True:
                raw = input("Filepath of keywords file (word,frequency.txt) [\\ to cancel]: ").strip()
                if raw == '\\':
                    print("Load cancelled.")
                    break
                # strip surrounding quotes if any
                path = raw.strip('"').strip("'")
                try:
                    trie.load_from_word_freq_file(path)
                    print(f"Keywords loaded from {path} into trie.")
                    break
                except FileNotFoundError:
                    print(f"File not found: {path}. Please try again.")
                except Exception as e:
                    print(f"Error loading file: {e}")
                    break
        
        elif choice in ['7', '=']:
            path = input("Filepath to dump keywords (word,frequency.txt): ").strip()
            words = trie.list_words()
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    for w in words:
                        freq = trie.get_frequency(w)
                        f.write(f"{w},{freq}\n")
                print(f"Dumped {len(words)} keywords with frequencies to {path}")
            except Exception as e:
                print("Error writing file:", e)
        
        elif choice in ['8', '!']:
            show_menu()
        
        elif choice in ['9', '\\']:
            break
        
        else:
            print("Invalid choice. Enter '!' for help.")
