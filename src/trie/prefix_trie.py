from .trie_node import TrieNode
class PrefixTrie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str, frequency: int = 1) -> None:
        """Insert a word with its frequency into the trie."""
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
        node.frequency += frequency

    def delete(self, word: str) -> bool:
        """Delete a word from the trie. Return True if deleted."""
        def _delete(node: TrieNode, word: str, depth: int) -> bool:
            if depth == len(word):
                if not node.is_end:
                    return False
                node.is_end = False
                return len(node.children) == 0
            char = word[depth]
            child = node.children.get(char)
            if not child:
                return False
            should_prune = _delete(child, word, depth + 1)
            if should_prune:
                del node.children[char]
                return not node.is_end and len(node.children) == 0
            return False
        return _delete(self.root, word, 0)

    def search(self, word: str) -> bool:
        """Return True if the exact word is in the trie."""
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end

    def wildcard_match(self, pattern: str) -> list[str]:
        """
        Given a pattern with '*' as a single-character wildcard,
        return all matching words in the trie.
        """
        results: list[str] = []
        def _dfs(node: TrieNode, prefix: str, idx: int) -> None:
            if idx == len(pattern):
                if node.is_end:
                    results.append(prefix)
                return
            char = pattern[idx]
            if char == '*':
                for child_char, child_node in node.children.items():
                    _dfs(child_node, prefix + child_char, idx + 1)
            else:
                child = node.children.get(char)
                if not child:
                    return
                _dfs(child, prefix + char, idx + 1)
        _dfs(self.root, "", 0)
        return results

    def save_to_file(self, filepath: str) -> None:
        """Save words+frequencies as plain text: one 'word,freq' per line."""
        with open(filepath, "w", encoding="utf-8") as f:
            for w in self.list_words():
                f.write(f"{w},{self.get_frequency(w)}\n")
    def save_display_to_file(self, filepath: str) -> None:
        """Save the ASCII display of the trie (same as print_trie)."""
        with open(filepath, "w", encoding="utf-8") as f:
            for line in self.as_ascii():
                f.write(line + "\n")

    def load_from_file(self, filepath: str) -> None:
        """Load keywords+frequencies from a plain text file (word,frequency per line)."""
        self.load_from_word_freq_file(filepath)

    def load_from_word_freq_file(self, filepath: str) -> None:
        """
        Load keywords + frequencies from a text file (word,frequency per line),
        clearing any existing data in the trie.
        """
        from .trie_node import TrieNode
        self.root = TrieNode()
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(',')
                word = parts[0]
                try:
                    freq = int(parts[1])
                except (IndexError, ValueError):
                    freq = 1
                self.insert(word, frequency=freq)

    def best_match(self, pattern: str) -> str | None:
        """
        Return the single best match for a wildcard pattern
        (using '*' as the wildcard) based on highest frequency.
        """
        matches = self.wildcard_match(pattern)
        best_word: str | None = None
        best_freq = -1
        for word in matches:
            node = self.root
            for char in word:
                node = node.children[char]
            if node.frequency > best_freq:
                best_freq = node.frequency
                best_word = word
        return best_word

    def list_words(self) -> list[str]:
        """
        Return a list of every word stored in the trie.
        """
        results: list[str] = []
        def _dfs(node: TrieNode, prefix: str):
            if node.is_end:
                results.append(prefix)
            for char, child in node.children.items():
                _dfs(child, prefix + char)
        _dfs(self.root, "")
        return results

    def get_frequency(self, word: str) -> int:
        """Return the stored frequency of `word`, or 0 if it’s not in the trie."""
        node = self.root
        for char in word:
            if char not in node.children:
                return 0
            node = node.children[char]
        return node.frequency if node.is_end else 0
    
    def print_trie(self):
        for line in self.as_ascii():
            print(line)


    def as_ascii(self) -> list[str]:
        """
        Return the current trie as a list of ASCII lines,
        using the same format as print_trie().
        """
        lines: list[str] = []
        def _rec(node, prefix_str, level):
            indent = "." * level
            for ch in sorted(node.children):
                child = node.children[ch]
                if child.is_end:
                    lines.append(f"{indent}...>{prefix_str+ch}({child.frequency})*")
                if child.children:
                    lines.append(f"{indent}...[{prefix_str+ch}")
                    _rec(child, prefix_str+ch, level+1)
                    lines.append(f"{indent}...]")
        lines.append("[")
        _rec(self.root, "", 1)
        lines.append("]")
        return lines
    # --- Merge helpers -------------------------------------------------

    def merge_from_word_freq_file(self, filepath: str) -> tuple[int, int]:
        """
        Merge words from a word,freq TXT into the current trie (no clearing).
        Internally loads into a temporary trie and performs a fast structural merge.
        Returns (new_words_added, existing_words_updated).
        """
        tmp = PrefixTrie()              # same class, same module → safe to construct
        tmp.load_from_word_freq_file(filepath)
        return self.merge_trie(tmp)     # uses _merge_nodes/_clone_subtree/_count_words

    def merge_trie(self, other: "PrefixTrie") -> tuple[int, int]:
        """Merge `other` trie into this trie. Returns (added, updated)."""
        return self._merge_nodes(self.root, other.root)

    # --- Internal: recursive structural merge --------------------------

    def _merge_nodes(self, dst, src) -> tuple[int, int]:
        """
        Merge src subtree into dst subtree.
        Returns (new_words_added, existing_words_updated).
        """
        added = updated = 0

        # If src ends a word, add/accumulate at dst
        if getattr(src, "is_end", False):
            if getattr(dst, "is_end", False):
                dst.frequency += src.frequency
                updated += 1
            else:
                dst.is_end = True
                dst.frequency += src.frequency
                added += 1

        for ch, src_child in src.children.items():
            if ch not in dst.children:
                # Clone the entire subtree once (no shared refs)
                dst.children[ch] = self._clone_subtree(src_child)
                added += self._count_words(src_child)
            else:
                a, u = self._merge_nodes(dst.children[ch], src_child)
                added += a
                updated += u

        return added, updated

    def _clone_subtree(self, node):
        """Deep-copy a subtree so we don't share nodes across tries."""
        from .trie_node import TrieNode
        new = TrieNode()
        new.is_end = node.is_end
        new.frequency = node.frequency
        for ch, child in node.children.items():
            new.children[ch] = self._clone_subtree(child)
        return new

    def _count_words(self, node) -> int:
        """Count distinct words (end markers) in a subtree."""
        cnt = 1 if getattr(node, "is_end", False) else 0
        for child in node.children.values():
            cnt += self._count_words(child)
        return cnt
