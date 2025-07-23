# main.py

from trie.prefix_trie import PrefixTrie
from ui.construct_cli import run_construct_cli
from ui.predict_cli import run_predict_cli

def show_main_menu():
    border = "*" * 60
    print(border)
    print("*  ST1507 DSAA: Predictive Text Editor (using tries)".ljust(59) + "*")
    print("*  - Done by: Thomas San (2415831) & Tee Lin Kai (2415464)".ljust(59) + "*")
    print("*  - Class DAAA/FT/2A/02".ljust(59) + "*")
    print(border)
    print()
    print("Please select your choice ('1','2','3','4','5','6','7'):")
    print("1. Construct/Edit Trie")
    print("2. Predict/Restore Text")
    print("-" * 44)
    print("3. Extra Feature One (Thomas San):")
    print("4. Extra Feature Two (Thomas San):")
    print("-" * 44)
    print("5. Extra Feature One (Tee Lin Kai):")
    print("6. Extra Feature Two (Tee Lin Kai):")
    print("-" * 44)
    print("7. Exit")
    print("Enter choice: ", end="")

def main():
    trie = PrefixTrie()
    while True:
        show_main_menu()
        choice = input().strip()

        if choice == '1':
            run_construct_cli(trie)

        elif choice == '2':
            run_predict_cli(trie)

        elif choice in ['3', '4']:
            print("Feature under construction (Thomas San).")

        elif choice in ['5', '6']:
            print("Feature under construction (Tee Lin Kai).")

        elif choice in ['7', 'exit', 'q', 'quit']:
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please select 1–7.")

if __name__ == "__main__":
    main()
