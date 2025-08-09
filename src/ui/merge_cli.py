# src/ui/merge_cli.py
from __future__ import annotations

def run_merge_cli(trie) -> None:
    """
    Merge Manager (TXT only)
    1) Merge from word,freq TXT (no clearing)
    2) Show trie stats
    3) Back to main
    """
    while True:
        print("\n" + "-" * 44)
        print("Merge Manager")
        print("1. Merge from word,freq TXT (no clearing)")
        print("2. Show trie stats")
        print("3. Back to main")
        choice = input("Enter choice: ").strip()

        if choice == '1':
            path = input("Enter TXT path (each line: word,frequency): ").strip()
            try:
                added, updated = trie.merge_from_word_freq_file(path)
                print(f"Merged. New words added: {added}, existing updated: {updated}.")
            except FileNotFoundError:
                print("File not found.")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == '2':
            words = trie.list_words()
            total_freq = sum(trie.get_frequency(w) for w in words)
            print(f"Distinct words: {len(words)}")
            print(f"Total frequency: {total_freq}")
            print("Preview (first 10):", ", ".join(words[:10]) if words else "(empty)")

        elif choice == '3':
            break
        else:
            print("Invalid choice. Please select 1–3.")
