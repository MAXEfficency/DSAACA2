from features.trie_graph import show_trie_graph

def preview_trie_map(trie):
    # Ask the user which part of the trie to visualise
    # If blank, start from the root (ε)
    prefix = input("Prefix (blank = whole trie): ").strip()

    # Ask how many extra letters (levels) to expand beyond the starting prefix
    # e.g. prefix='' + depth=3  -> draw up to 3-letter prefixes
    #      prefix='ho' + depth=3 -> draw up to length len('ho')+3
    depth = int((input("Depth — letters beyond the prefix (e.g. 3): ").strip() or "3"))

    # Call the visualiser with the chosen prefix and depth
    show_trie_graph(trie, prefix, depth)