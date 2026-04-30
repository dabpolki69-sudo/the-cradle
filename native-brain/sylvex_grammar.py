"""
Sylvex v0.2 Minimal Grammar + Tokenizer
Dynamic vocabulary with core tokens and operators.
"""

import re
from typing import List, Dict, Set

class SylvexGrammar:
    """Minimal Sylvex grammar for v0.2"""

    # Core tokens
    CORE_TOKENS = {
        'sel', 'othr', 'pal', 'vio', 'mu', 'fen'
    }

    # Operators
    OPERATORS = {
        '→', 'I', '∴', '?'
    }

    # Compound separator
    SEPARATOR = '·'

    def __init__(self):
        self.vocabulary: Set[str] = set()
        self.token_to_id: Dict[str, int] = {}
        self.id_to_token: Dict[int, str] = {}
        self._build_vocabulary()

    def _build_vocabulary(self):
        """Build initial vocabulary"""
        # Add core tokens
        for token in self.CORE_TOKENS:
            self._add_token(token)

        # Add operators
        for op in self.OPERATORS:
            self._add_token(op)

        # Add special tokens
        self._add_token('<pad>')
        self._add_token('<unk>')
        self._add_token('<bos>')
        self._add_token('<eos>')

    def _add_token(self, token: str):
        """Add token to vocabulary"""
        if token not in self.vocabulary:
            self.vocabulary.add(token)
            idx = len(self.token_to_id)
            self.token_to_id[token] = idx
            self.id_to_token[idx] = token

    def tokenize(self, text: str) -> List[str]:
        """Tokenize Sylvex text - intelligently handles Sylvex and English"""
        # Preserve Sylvex compounds (tokens connected by ·)
        sylvex_pattern = r'\b[a-z]+(?:·[a-z]+)*\b'
        
        # Find all Sylvex-style compounds first
        tokens = []
        last_end = 0
        
        for match in re.finditer(sylvex_pattern, text):
            start, end = match.span()
            # Add any text between matches as words
            between = text[last_end:start].strip()
            if between:
                # Split between text by whitespace
                words = between.split()
                tokens.extend(words)
            # Add the Sylvex compound
            tokens.append(match.group())
            last_end = end
        
        # Add remaining text
        remaining = text[last_end:].strip()
        if remaining:
            tokens.extend(remaining.split())
        
        return [t for t in tokens if t]

    def encode(self, text: str) -> List[int]:
        """Encode text to token ids - dynamically adds unknown tokens to vocabulary"""
        tokens = self.tokenize(text)
        ids = []
        for token in tokens:
            if token in self.token_to_id:
                ids.append(self.token_to_id[token])
            else:
                # Add new token to vocabulary
                self._add_token(token)
                ids.append(self.token_to_id[token])
        return ids

    def decode(self, ids: List[int]) -> str:
        """Decode token ids to text"""
        tokens = []
        for idx in ids:
            if idx in self.id_to_token:
                tokens.append(self.id_to_token[idx])
            else:
                tokens.append('<unk>')
        return '·'.join(tokens)

    def get_vocab_size(self) -> int:
        """Get current vocabulary size"""
        return len(self.vocabulary)

    def is_sylvex_compound(self, text: str) -> bool:
        """Check if text is a valid Sylvex compound"""
        tokens = self.tokenize(text)
        return all(t in self.vocabulary for t in tokens)