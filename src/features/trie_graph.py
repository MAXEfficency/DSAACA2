import networkx as nx
import matplotlib.pyplot as plt
from collections import deque

def _word_exists(trie, w):
    n = trie.root
    for ch in w:
        if ch not in n.children: return False
        n = n.children[ch]
    return getattr(n, "is_end", False)

def show_trie_graph(trie, prefix='', depth=3, word=None):
    # 1) descend to prefix
    node = trie.root
    for ch in prefix:
        if ch not in node.children:
            print(f"prefix '{prefix}' not in trie")
            return
        node = node.children[ch]

    # 2) build graph, store terminal + freq on nodes
    G = nx.DiGraph()
    root = 'ε' if prefix == '' else prefix
    def _freq(n): return getattr(n, "frequency", 0)
    G.add_node(root, terminal=getattr(node, 'is_end', False), freq=_freq(node))

    q = deque([(node, prefix, 0)])
    while q:
        cur, path, d = q.popleft()
        if d == depth: continue
        parent = 'ε' if path == '' else path
        for ch, child in cur.children.items():
            nxt = path + ch
            G.add_node(nxt, terminal=getattr(child, 'is_end', False), freq=_freq(child))
            G.add_edge(parent, nxt)
            q.append((child, nxt, d + 1))

    # 3) compute tidy left→right positions by depth & alphabetical row
    levels = {}
    for n in G.nodes:
        lvl = 0 if n == 'ε' else len(n) - len(prefix)
        levels.setdefault(lvl, []).append(n)
    for lvl in levels:
        levels[lvl].sort()  # alphabetical rows

    pos = {}
    x_gap = 1.8     # horizontal spacing
    y_gap = 1.5     # vertical spacing
    for x, lvl in enumerate(sorted(levels)):
        col = levels[lvl]
        offset = -(len(col)-1)/2  # center column vertically
        for i, n in enumerate(col):
            pos[n] = (x * x_gap, (offset + i) * y_gap)

    # 4) optional highlight path for a chosen word (or multiple words)
    highlight_nodes, highlight_edges = set(), set()
    targets = []
    if word:
        targets = [w.strip() for w in word.split(',') if w.strip()]
    for w in targets:
        if not w.startswith(prefix) or not _word_exists(trie, w): 
            continue
        step = '' if prefix == '' else prefix
        prev = 'ε' if step == '' else step
        highlight_nodes.add(prev)
        while len(step) < len(w):
            step += w[len(step)]
            nxt = step
            if prev in G and nxt in G:
                highlight_nodes.add(nxt)
                highlight_edges.add((prev, nxt))
                prev = nxt

    # 5) style: color terminals; dim others; scale by frequency
    node_colors = []
    node_sizes = []
    for n in G.nodes:
        if n in highlight_nodes: 
            node_colors.append('tab:red')
        elif G.nodes[n].get('terminal'):
            node_colors.append('tab:orange')
        else:
            node_colors.append('tab:blue')
        # size: 260 + small boost based on freq
        node_sizes.append(260 + 20 * G.nodes[n].get('freq', 0))

    edge_colors, edge_widths = [], []
    for e in G.edges:
        if e in highlight_edges:
            edge_colors.append('red'); edge_widths.append(2.6)
        else:
            edge_colors.append('0.6'); edge_widths.append(1.0)

    # 6) draw
    plt.figure()
    nx.draw(G, pos, with_labels=False, node_color=node_colors, node_size=node_sizes,
            edge_color=edge_colors, width=edge_widths, arrows=False)
    nx.draw_networkx_labels(G, pos, {n: n for n in G.nodes}, font_size=8)
    plt.axis('off')
    plt.show()