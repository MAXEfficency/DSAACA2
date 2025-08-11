# features/trie_stats.py
# Dataset-centric Top-5 trie stats. No external imports.

# Expected trie API:
#   trie.root.children : dict[char -> node]
#   node.is_end : bool
#   node.frequency : int

def _walk_paths(trie):
    stack = [("", trie.root, 0)]
    while stack:
        path, node, depth = stack.pop()
        yield path, node, depth
        for ch, child in node.children.items():
            stack.append((path + ch, child, depth + 1))

def _postorder(root):
    a = [root]; b = []
    while a:
        n = a.pop(); b.append(n)
        for c in n.children.values():
            a.append(c)
    b.reverse()
    return b

def _subtree_word_count(root):
    # node -> number of word-ends in subtree
    count = {}
    for node in _postorder(root):
        total = 1 if getattr(node, "is_end", False) else 0
        for child in node.children.values():
            total += count[child]
        count[node] = total
    return count

def compute_stats(trie, top_k=5):
    # pass 1: collect vocabulary + lengths + frequencies
    vocab = []  # (word, freq)
    length_sum = 0
    min_len = None
    max_len = 0
    shortest_word = ""
    longest_word = ""

    for path, node, depth in _walk_paths(trie):
        if getattr(node, "is_end", False):
            f = getattr(node, "frequency", 0)
            vocab.append((path, f))
            length_sum += depth
            if min_len is None or depth < min_len:
                min_len = depth
                shortest_word = path
            if depth > max_len:
                max_len = depth
                longest_word = path

    vocab_size = len(vocab)
    avg_word_len = (length_sum / vocab_size) if vocab_size else 0.0

    # average & median frequency
    if vocab_size:
        freqs = [f for _, f in vocab]
        total_tokens = 0
        for v in freqs:
            total_tokens += v
        avg_frequency = total_tokens / vocab_size
        freqs.sort()
        mid = vocab_size // 2
        median_frequency = freqs[mid] if vocab_size % 2 == 1 else (freqs[mid - 1] + freqs[mid]) / 2
    else:
        avg_frequency = 0.0
        median_frequency = 0.0

    if min_len is None:
        min_len = 0
        shortest_word = "-"

    # pass 2: prefix coverage (word-count per prefix)
    subtree_words = _subtree_word_count(trie.root)

    path_of = {}
    for path, node, _ in _walk_paths(trie):
        path_of[node] = path

    prefix_counts = []
    for node, p in path_of.items():
        if p != "":
            prefix_counts.append((p, subtree_words[node]))

    # top lists + most/least frequent words
    vocab.sort(key=lambda x: (-x[1], x[0]))
    prefix_counts.sort(key=lambda x: (-x[1], x[0]))

    if vocab_size:
        most_word, most_freq = vocab[0]
        least_word, least_freq = vocab[-1]
    else:
        most_word, most_freq = "-", 0
        least_word, least_freq = "-", 0

    return {
        "dataset": {
            "vocab_size": vocab_size,
            "avg_word_length": round(avg_word_len, 3),
            "shortest_word": shortest_word,
            "longest_word": longest_word or "-",
            "avg_frequency": round(avg_frequency, 3),
            "median_frequency": median_frequency,
            "most_frequent": (most_word, most_freq),
            "least_frequent": (least_word, least_freq)
        },
        "top": {
            "words_by_frequency": vocab[:top_k],
            "prefixes_by_word_count": prefix_counts[:top_k]
        }
    }

def pretty_print(stats):
    d = stats["dataset"]
    t = stats["top"]

    top_prefixes = t["prefixes_by_word_count"]
    top_words = t["words_by_frequency"]

    def fmt_num(n):
        try:
            n = float(n)
            return f"{int(n):,}" if n.is_integer() else f"{n:,.3f}"
        except:
            return str(n)

    width = 74
    bar = "+" + "-" * (width - 2) + "+"

    def center(text):
        pad = max(0, width - 2 - len(text))
        left = pad // 2
        right = pad - left
        print("|" + " " * left + text + " " * right + "|")

    print(bar); center("Trie Stats"); print(bar)
    center("Vocab: " + fmt_num(d["vocab_size"]) +
           " | AvgLen: " + f"{d['avg_word_length']:.3f}")
    center("Longest: " + d["longest_word"] +
           " | Shortest: " + d["shortest_word"])
    mf_w, mf_c = d["most_frequent"]; lf_w, lf_c = d["least_frequent"]
    center("MostFreq: " + str(mf_w) + " (" + fmt_num(mf_c) + ")" +
           " | LeastFreq: " + str(lf_w) + " (" + fmt_num(lf_c) + ")")
    center("AvgFreq: " + fmt_num(d["avg_frequency"]) +
           " | MedianFreq: " + fmt_num(d["median_frequency"]))
    print(bar)
    center("Top 5 prefixes (by word count)"); print(bar)
    for i, (pfx, cnt) in enumerate(top_prefixes, 1):
        print("| " + str(i) + ") " + str(pfx).ljust(24) + fmt_num(cnt).rjust(24) + " |")
    print(bar)
    center("Top 5 words (by frequency)"); print(bar)
    for i, (w, f) in enumerate(top_words, 1):
        print("| " + str(i) + ") " + str(w).ljust(24) + fmt_num(f).rjust(24) + " |")
    print(bar)