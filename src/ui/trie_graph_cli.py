from features.trie_graph import show_trie_graph

def preview_trie_map(trie):
    prefix = input("Prefix (blank = whole trie): ").strip()
    word = input("Word to highlight (optional, must start with prefix): ").strip()
    word = word if word else None
    show_trie_graph(trie, prefix=prefix, word=word)