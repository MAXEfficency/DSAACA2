class TrieNode:
    def __init__(self):
        # child characters → TrieNode
        self.children: dict[str, TrieNode] = {}
        # marks end of a complete word
        self.is_end: bool = False
        # frequency count for word-restoration ranking
        self.frequency: int = 0
