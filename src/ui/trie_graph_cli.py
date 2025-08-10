from features.trie_graph import show_trie_graph

def preview_trie_map(trie):
    prefix = input("Prefix (blank = whole trie): ").strip()
    depth = int((input("Depth — letters beyond the prefix (e.g. 3): ").strip() or "3"))
    word = input("Word to highlight (optional, must start with prefix): ").strip()
    word = word if word else None
    show_trie_graph(trie, prefix=prefix, depth=depth, word=word)