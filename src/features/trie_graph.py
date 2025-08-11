import networkx as nx
import matplotlib.pyplot as plt
from collections import deque

def _path_exists(trie, s):
    n = trie.root
    for ch in s:
        if ch not in n.children: return False
        n = n.children[ch]
    return True  # no is_end check

def _digits(x):
    try: x = int(x)
    except: return 1
    d = 1
    while x >= 10:
        x//=10; d+=1
    return d if d < 10 else 9

def _safe_size(freq):
    return 260 + 120*_digits(freq)   # old vibe, but log-ish so it won't explode

def show_trie_graph(trie, prefix='', word=None):
    # 1) descend to prefix
    node = trie.root
    for ch in prefix:
        if ch not in node.children:
            print(f"prefix '{prefix}' not in trie")
            return
        node = node.children[ch]

    # 2) build graph (whole subtree), store terminal + freq
    G = nx.DiGraph()
    root = '' if prefix == '' else prefix   # blank root label
    freq_of = lambda n: getattr(n, "frequency", 0)
    G.add_node(root, terminal=getattr(node, 'is_end', False), freq=freq_of(node))

    q = deque([(node, prefix)])
    while q:
        cur, path = q.popleft()
        parent = root if path == '' else path
        for ch, child in sorted(cur.children.items()):   # stable alphabetical rows
            nxt = path + ch
            G.add_node(nxt, terminal=getattr(child, 'is_end', False), freq=freq_of(child))
            G.add_edge(parent, nxt)
            q.append((child, nxt))

    # 3) tidy left→right positions by depth & alphabetical row
    levels = {}
    for n in G.nodes:
        lvl = 0 if n == root else len(n) - len(prefix)
        levels.setdefault(lvl, []).append(n)
    for lvl in levels: levels[lvl].sort()

    pos = {}
    x_gap = 1.8
    y_gap = 1.5
    for x, lvl in enumerate(sorted(levels)):
        col = levels[lvl]
        offset = -(len(col)-1)/2
        for i, n in enumerate(col):
            pos[n] = (x*x_gap, (offset+i)*y_gap)

    # 4) optional highlights
    hi_nodes, hi_edges = set(), set()
    if word:
        for w in [s.strip() for s in word.split(',') if s.strip()]:
            if not w.startswith(prefix) or not _path_exists(trie, w):
                continue
            step = prefix
            prev = root
            hi_nodes.add(prev)
            while len(step) < len(w):
                step += w[len(step)]
                if prev in G and step in G:
                    hi_nodes.add(step)
                    hi_edges.add((prev, step))
                    prev = step

    # 5) style (keep original colors; safe size)
    node_colors, node_sizes = [], []
    for n in G.nodes:
        if n in hi_nodes: node_colors.append('tab:red')
        elif G.nodes[n].get('terminal'): node_colors.append('tab:orange')
        else: node_colors.append('tab:blue')
        node_sizes.append(_safe_size(G.nodes[n].get('freq', 0)))

    edge_colors, edge_widths = [], []
    for e in G.edges:
        if e in hi_edges: edge_colors.append('red'); edge_widths.append(2.6)
        else: edge_colors.append('0.6'); edge_widths.append(1.0)

    # 6) draw (full screen; no tight_layout → no warning)
    plt.figure()
    plt.get_current_fig_manager().window.showMaximized() # one-liner fullscreen

    nx.draw(G, pos, with_labels=False, node_color=node_colors, node_size=node_sizes,
            edge_color=edge_colors, width=edge_widths, arrows=False)
    
    # labels: show the prefix in the first bubble if a prefix was typed
    labels = {}
    if prefix:                      # when user typed a prefix
        labels[root] = prefix       # put it in the first bubble
    for n in G.nodes:
        if n != root:
            labels[n] = n
    nx.draw_networkx_labels(G, pos, labels, font_size=8)

    plt.axis('off')
    plt.show()