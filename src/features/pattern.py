# src/features/pattern.py
from __future__ import annotations
from typing import List, Tuple, Set, Optional

Token = Tuple[str, object]  # ('LIT', 'c') | ('ANY', None) | ('STAR', None) | ('SET', frozenset({...}))

def is_glob_pattern(s: str) -> bool:
    # We only treat ?, *, [ as special now
    return any(ch in s for ch in ['?', '*', '['])

def _parse_charclass(pat: str, i: int) -> Tuple[frozenset[str], int]:
    """
    Parse a character class starting at pat[i-1] == '['.
    Supports sets [abc] and ranges [a-z]. No backslash escapes.
    Returns (set_of_chars, next_index_after_closing_bracket).
    """
    chars: Set[str] = set()
    j = i
    if j >= len(pat):
        raise ValueError("Unclosed character class '[' at end of pattern")

    first = True
    while j < len(pat):
        c = pat[j]
        if c == ']' and not first:
            return frozenset(chars), j + 1

        # range like a-z (only if there's something after '-')
        if j + 2 < len(pat) and pat[j + 1] == '-' and pat[j + 2] != ']':
            start, end = pat[j], pat[j + 2]
            s_ord, e_ord = sorted((ord(start), ord(end)))
            for code in range(s_ord, e_ord + 1):
                chars.add(chr(code))
            j += 3
            first = False
            continue

        # single char in the class
        chars.add(c)
        j += 1
        first = False

    raise ValueError("Unclosed character class '[' in pattern")

def _parse_pattern(pat: str) -> List[Token]:
    tokens: List[Token] = []
    i = 0
    while i < len(pat):
        c = pat[i]
        if c == '?':
            tokens.append(('ANY', None)); i += 1
        elif c == '*':
            tokens.append(('STAR', None)); i += 1
        elif c == '[':
            char_set, nxt = _parse_charclass(pat, i + 1)
            tokens.append(('SET', char_set)); i = nxt
        else:
            tokens.append(('LIT', c)); i += 1
    return tokens


def glob_match(trie, pattern: str, top_k: Optional[int] = None) -> List[Tuple[str, int]]:
    """
    Match words in `trie` against a Glob+ pattern.
    Returns list of (word, frequency), sorted by:
      1) higher frequency first, 2) alphabetical.
    If `top_k` is given, returns at most top_k results.
    """
    tokens = _parse_pattern(pattern)
    results: List[Tuple[str, int]] = []

    def dfs(node, ti: int, prefix: str) -> None:
        if ti == len(tokens):
            if getattr(node, "is_end", False):
                results.append((prefix, getattr(node, "frequency", 0)))
            return

        kind, payload = tokens[ti]

        if kind == 'LIT':
            nxt = node.children.get(payload)
            if nxt:
                dfs(nxt, ti + 1, prefix + payload)

        elif kind == 'ANY':  # '?'
            for ch, nxt in node.children.items():
                dfs(nxt, ti + 1, prefix + ch)

        elif kind == 'SET':  # [...]
            allowed = payload  # frozenset
            # Only follow allowed children actually present
            for ch in allowed:
                nxt = node.children.get(ch)
                if nxt:
                    dfs(nxt, ti + 1, prefix + ch)

        elif kind == 'STAR':  # '*'
            # Option A: consume zero characters
            dfs(node, ti + 1, prefix)
            # Option B: consume one character (stay on this STAR)
            for ch, nxt in node.children.items():
                dfs(nxt, ti, prefix + ch)

    dfs(trie.root, 0, "")

    # De-dup in case of accidental duplicates (shouldn't usually happen)
    best: dict[str, int] = {}
    for w, f in results:
        if w not in best or f > best[w]:
            best[w] = f

    sorted_items = sorted(best.items(), key=lambda x: (-x[1], x[0]))
    return sorted_items[:top_k] if top_k is not None else sorted_items
