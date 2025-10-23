"""
Boolean query parser and processor.
Supports AND, OR, NOT, PHRASE operators with parentheses.
"""

import re
from typing import Set, List, Optional
from enum import Enum


class TokenType(Enum):
    """Token types for query parsing."""
    TERM = 1
    AND = 2
    OR = 3
    NOT = 4
    PHRASE = 5
    LPAREN = 6
    RPAREN = 7
    EOF = 8


class Token:
    """Token for query parsing."""
    def __init__(self, type: TokenType, value: str = ""):
        self.type = type
        self.value = value
    
    def __repr__(self):
        return f"Token({self.type}, {self.value})"


class QueryLexer:
    """Tokenizer for boolean queries."""
    
    def __init__(self, query: str):
        self.query = query
        self.pos = 0
    
    def peek(self) -> str:
        """Peek at current character without consuming."""
        if self.pos < len(self.query):
            return self.query[self.pos]
        return ''
    
    def advance(self) -> str:
        """Consume and return current character."""
        if self.pos < len(self.query):
            char = self.query[self.pos]
            self.pos += 1
            return char
        return ''
    
    def skip_whitespace(self):
        """Skip whitespace characters."""
        while self.peek().isspace():
            self.advance()
    
    def read_quoted_term(self) -> str:
        """Read a quoted term."""
        self.advance()  # Skip opening quote
        term = ""
        
        while self.peek() and self.peek() != '"':
            term += self.advance()
        
        if self.peek() == '"':
            self.advance()  # Skip closing quote
        
        return term
    
    def read_keyword(self) -> str:
        """Read a keyword (AND, OR, NOT, PHRASE)."""
        keyword = ""
        
        while self.peek() and self.peek().isalpha():
            keyword += self.advance()
        
        return keyword.upper()
    
    def tokenize(self) -> List[Token]:
        """Tokenize the query."""
        tokens = []
        
        while self.pos < len(self.query):
            self.skip_whitespace()
            
            if not self.peek():
                break
            
            char = self.peek()
            
            if char == '"':
                term = self.read_quoted_term()
                tokens.append(Token(TokenType.TERM, term))
            elif char == '(':
                self.advance()
                tokens.append(Token(TokenType.LPAREN))
            elif char == ')':
                self.advance()
                tokens.append(Token(TokenType.RPAREN))
            elif char.isalpha():
                keyword = self.read_keyword()
                
                if keyword == 'AND':
                    tokens.append(Token(TokenType.AND))
                elif keyword == 'OR':
                    tokens.append(Token(TokenType.OR))
                elif keyword == 'NOT':
                    tokens.append(Token(TokenType.NOT))
                elif keyword == 'PHRASE':
                    tokens.append(Token(TokenType.PHRASE))
                else:
                    # Treat as unquoted term
                    tokens.append(Token(TokenType.TERM, keyword.lower()))
            else:
                # Skip unknown characters
                self.advance()
        
        tokens.append(Token(TokenType.EOF))
        return tokens


class QueryParser:
    """Parser for boolean queries with operator precedence."""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def peek(self) -> Token:
        """Peek at current token."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token(TokenType.EOF)
    
    def advance(self) -> Token:
        """Consume and return current token."""
        token = self.peek()
        self.pos += 1
        return token
    
    def parse(self):
        """Parse the query into an AST."""
        return self.parse_or()
    
    def parse_or(self):
        """Parse OR expressions (lowest precedence)."""
        left = self.parse_and()
        
        while self.peek().type == TokenType.OR:
            self.advance()
            right = self.parse_and()
            left = ('OR', left, right)
        
        return left
    
    def parse_and(self):
        """Parse AND expressions."""
        left = self.parse_not()
        
        while self.peek().type == TokenType.AND:
            self.advance()
            right = self.parse_not()
            left = ('AND', left, right)
        
        return left
    
    def parse_not(self):
        """Parse NOT expressions."""
        if self.peek().type == TokenType.NOT:
            self.advance()
            expr = self.parse_phrase()
            return ('NOT', expr)
        
        return self.parse_phrase()
    
    def parse_phrase(self):
        """Parse PHRASE expressions (highest precedence)."""
        if self.peek().type == TokenType.PHRASE:
            self.advance()
            expr = self.parse_primary()
            return ('PHRASE', expr)
        
        return self.parse_primary()
    
    def parse_primary(self):
        """Parse primary expressions (terms and parentheses)."""
        token = self.peek()
        
        if token.type == TokenType.TERM:
            self.advance()
            return ('TERM', token.value)
        elif token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_or()
            
            if self.peek().type == TokenType.RPAREN:
                self.advance()
            
            return expr
        
        # Error: unexpected token
        return None


class QueryProcessor:
    """Process queries against an inverted index."""
    
    def __init__(self, index, preprocessor):
        """
        Initialize query processor.
        
        Args:
            index: InvertedIndex instance
            preprocessor: TextPreprocessor instance
        """
        self.index = index
        self.preprocessor = preprocessor
    
    def process_query(self, query: str) -> Set[int]:
        """
        Process a boolean query.
        
        Args:
            query: Query string
            
        Returns:
            Set of document IDs matching the query
        """
        # Tokenize and parse
        lexer = QueryLexer(query)
        tokens = lexer.tokenize()
        
        parser = QueryParser(tokens)
        ast = parser.parse()
        
        if ast is None:
            return set()
        
        # Evaluate the AST
        return self.evaluate(ast)
    
    def evaluate(self, node) -> Set[int]:
        """
        Evaluate an AST node.
        
        Args:
            node: AST node (tuple)
            
        Returns:
            Set of document IDs
        """
        if node is None:
            return set()
        
        operator = node[0]
        
        if operator == 'TERM':
            term = node[1]
            # Preprocess the term
            processed_terms = self.preprocessor.preprocess(term)
            
            if not processed_terms:
                return set()
            
            # Return documents containing the term
            return self.index.get_document_ids(processed_terms[0])
        
        elif operator == 'AND':
            left = self.evaluate(node[1])
            right = self.evaluate(node[2])
            return left & right
        
        elif operator == 'OR':
            left = self.evaluate(node[1])
            right = self.evaluate(node[2])
            return left | right
        
        elif operator == 'NOT':
            expr = self.evaluate(node[1])
            # Get all document IDs
            all_docs = set(range(self.index.document_count))
            return all_docs - expr
        
        elif operator == 'PHRASE':
            # For phrase queries, we need to check positions
            return self.evaluate_phrase(node[1])
        
        return set()
    
    def evaluate_phrase(self, node) -> Set[int]:
        """
        Evaluate a phrase query.
        
        Args:
            node: AST node
            
        Returns:
            Set of document IDs containing the phrase
        """
        if node[0] != 'TERM':
            return set()
        
        phrase = node[1]
        # Preprocess the phrase
        terms = self.preprocessor.preprocess(phrase)
        
        if len(terms) < 2:
            # Single term, just return documents containing it
            if terms:
                return self.index.get_document_ids(terms[0])
            return set()
        
        # Get documents containing all terms
        doc_sets = [self.index.get_document_ids(term) for term in terms]
        common_docs = set.intersection(*doc_sets) if doc_sets else set()
        
        # Check if terms appear in sequence
        result = set()
        
        for doc_id in common_docs:
            # Get positions for each term
            positions_list = [
                self.index.get_term_positions(term, doc_id)
                for term in terms
            ]
            
            # Check if there's a sequence
            if self._has_phrase_match(positions_list):
                result.add(doc_id)
        
        return result
    
    def _has_phrase_match(self, positions_list: List[List[int]]) -> bool:
        """
        Check if positions form a phrase (consecutive sequence).
        
        Args:
            positions_list: List of position lists for each term
            
        Returns:
            True if a phrase match is found
        """
        if not positions_list or not all(positions_list):
            return False
        
        # Check for consecutive positions
        for start_pos in positions_list[0]:
            current_pos = start_pos
            match = True
            
            for positions in positions_list[1:]:
                current_pos += 1
                if current_pos not in positions:
                    match = False
                    break
            
            if match:
                return True
        
        return False
