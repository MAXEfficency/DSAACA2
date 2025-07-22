from .trie_node import TrieNode
import pickle

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
        # accumulate frequency if word re-inserted
        node.frequency += frequency

    def delete(self, word: str) -> bool:
        """Delete a word from the trie. Return True if deleted."""

        def _delete(node: TrieNode, word: str, depth: int) -> bool:
            if depth == len(word):
                # word not present
                if not node.is_end:
                    return False
                # unmark end and decide if node should be pruned
                node.is_end = False
                return len(node.children) == 0
            char = word[depth]
            child = node.children.get(char)
            if not child:
                return False
            # recurse
            should_prune = _delete(child, word, depth + 1)
            if should_prune:
                # remove the child reference
                del node.children[char]
                # prune this node if it's not end-of-word and has no other children
                return not node.is_end and len(node.children) == 0
            return False

        # kick off recursion from root
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
                # try every possible child
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
        """Serialize the entire trie to disk using pickle."""
        with open(filepath, 'wb') as f:
            pickle.dump(self.root, f)

    def load_from_file(self, filepath: str) -> None:
        """Load a trie from disk (clears current trie)."""
        with open(filepath, 'rb') as f:
            self.root = pickle.load(f)

    def load_from_word_freq_file(self, filepath: str) -> None:
        """
        Load keywords + frequencies from a text file (word,frequency per line),
        clearing any existing data in the trie.
        """
        from .trie_node import TrieNode
        self.root = TrieNode()  # reset
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
        (using '?' for single-character wildcards) based on highest frequency.
        """
        matches = self.wildcard_match(pattern)
        best_word: str | None = None
        best_freq = -1

        for word in matches:
            node = self.root
            # traverse to the node for this word
            for char in word:
                node = node.children[char]
            # compare frequency
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
