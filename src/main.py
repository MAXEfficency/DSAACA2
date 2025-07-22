# main.py

from trie.prefix_trie import PrefixTrie
from ui.construct_cli import run_construct_cli
from ui.predict_cli import run_predict_cli  

def show_main_menu():
    print("""
Main Menu
1. Construct/Edit Trie
2. Predict/Restore Text
3. Extra Feature 1
4. Extra Feature 2
5. Extra Feature 3
6. Extra Feature 4
7. Exit
""")

def main():
    trie = PrefixTrie()

    while True:
        show_main_menu()
        choice = input("Select option: ").strip()

        if choice == '1':
            # hand off control to your Construct/Edit panel
            run_construct_cli(trie)

        elif choice == '2':
            # hand off control to your Predict/Restore panel
            run_predict_cli(trie)

        elif choice in ['3','4','5','6']:
            print("Extra feature coming soon!")  # replace with your feature calls

        elif choice in ['7', 'exit', 'q', 'quit']:
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please select 1–7.")

if __name__ == "__main__":
    main()
