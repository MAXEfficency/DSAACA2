import networkx as nx
import matplotlib.pyplot as plt
from collections import deque

def show_trie_graph(trie, prefix='', depth=3):
    # depth = number of extra letters expanded beyond `prefix`
    # e.g. prefix='' + depth=3 -> draw up to 3-letter prefixes
    #      prefix='ho' + depth=3 -> draw up to length len('ho')+3 (e.g. 'house')

    # 1) Walk down the trie to the node that matches `prefix`
    node = trie.root
    for ch in prefix:
        if ch not in node.children:
            print(f"prefix '{prefix}' not in trie")
            return
        node = node.children[ch]

    # 2) Build a NetworkX DiGraph of prefixes using BFS (bounded by `depth`)
    graph = nx.DiGraph()
    root = 'ε' if prefix == '' else prefix  # label the visual root
    graph.add_node(root)

    # queue holds (trie_node, current_prefix_string, letters_expanded)
    queue = deque([(node, prefix, 0)])
    while queue:
        cur, path, d = queue.popleft()

        # stop expanding once we've added `depth` letters beyond `prefix`
        if d == depth:
            continue

        parent = 'ε' if path == '' else path
        for ch, child in cur.children.items():
            nxt = path + ch # next prefix (path plus one letter)
            graph.add_node(nxt) # add node for that prefix
            graph.add_edge(parent, nxt) # connect parent prefix → child prefix
            queue.append((child, nxt, d + 1)) # explore one level deeper

    # 3) Lay out and draw (spring layout like Topic 6 examples)
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=False, node_size=320, arrows=False)

    # Show full prefixes as labels so completed words are obvious while debugging
    nx.draw_networkx_labels(graph, pos, {n: n for n in graph.nodes}, font_size=8)
    plt.show()