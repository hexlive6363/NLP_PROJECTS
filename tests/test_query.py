"""
Unit tests for query processing modules.
"""

import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import SelfIndex
from src.query.boolean_query import QueryLexer, QueryParser, QueryProcessor


class TestQueryLexer(unittest.TestCase):
    """Test cases for QueryLexer."""
    
    def test_simple_term(self):
        """Test lexing a simple term."""
        lexer = QueryLexer('"hello"')
        tokens = lexer.tokenize()
        
        self.assertEqual(len(tokens), 2)  # TERM + EOF
        self.assertEqual(tokens[0].value, 'hello')
    
    def test_and_query(self):
        """Test lexing AND query."""
        lexer = QueryLexer('"hello" AND "world"')
        tokens = lexer.tokenize()
        
        # TERM, AND, TERM, EOF
        self.assertEqual(len(tokens), 4)
    
    def test_or_query(self):
        """Test lexing OR query."""
        lexer = QueryLexer('"hello" OR "world"')
        tokens = lexer.tokenize()
        
        self.assertEqual(len(tokens), 4)
    
    def test_not_query(self):
        """Test lexing NOT query."""
        lexer = QueryLexer('NOT "hello"')
        tokens = lexer.tokenize()
        
        self.assertEqual(len(tokens), 3)  # NOT, TERM, EOF
    
    def test_parentheses(self):
        """Test lexing with parentheses."""
        lexer = QueryLexer('("hello" AND "world")')
        tokens = lexer.tokenize()
        
        # LPAREN, TERM, AND, TERM, RPAREN, EOF
        self.assertEqual(len(tokens), 6)
    
    def test_complex_query(self):
        """Test lexing complex query."""
        lexer = QueryLexer('("hello" AND "world") OR NOT "goodbye"')
        tokens = lexer.tokenize()
        
        # Should tokenize without error
        self.assertGreater(len(tokens), 0)


class TestQueryParser(unittest.TestCase):
    """Test cases for QueryParser."""
    
    def test_simple_term_parsing(self):
        """Test parsing a simple term."""
        lexer = QueryLexer('"hello"')
        tokens = lexer.tokenize()
        parser = QueryParser(tokens)
        ast = parser.parse()
        
        self.assertEqual(ast[0], 'TERM')
        self.assertEqual(ast[1], 'hello')
    
    def test_and_query_parsing(self):
        """Test parsing AND query."""
        lexer = QueryLexer('"hello" AND "world"')
        tokens = lexer.tokenize()
        parser = QueryParser(tokens)
        ast = parser.parse()
        
        self.assertEqual(ast[0], 'AND')
    
    def test_or_query_parsing(self):
        """Test parsing OR query."""
        lexer = QueryLexer('"hello" OR "world"')
        tokens = lexer.tokenize()
        parser = QueryParser(tokens)
        ast = parser.parse()
        
        self.assertEqual(ast[0], 'OR')
    
    def test_not_query_parsing(self):
        """Test parsing NOT query."""
        lexer = QueryLexer('NOT "hello"')
        tokens = lexer.tokenize()
        parser = QueryParser(tokens)
        ast = parser.parse()
        
        self.assertEqual(ast[0], 'NOT')
    
    def test_precedence(self):
        """Test operator precedence."""
        lexer = QueryLexer('"a" OR "b" AND "c"')
        tokens = lexer.tokenize()
        parser = QueryParser(tokens)
        ast = parser.parse()
        
        # AND has higher precedence than OR
        # Should parse as: "a" OR ("b" AND "c")
        self.assertEqual(ast[0], 'OR')
        self.assertEqual(ast[2][0], 'AND')


class TestQueryProcessor(unittest.TestCase):
    """Test cases for QueryProcessor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.index = SelfIndex(version="1.1000")
        self.docs = [
            "Python is a programming language",
            "Machine learning uses Python",
            "Data science involves programming",
            "Java is also a programming language"
        ]
        
        for doc in self.docs:
            self.index.add_document(doc)
        
        self.index.finalize()
    
    def test_simple_query(self):
        """Test simple term query."""
        results = self.index.search('"python"', use_boolean=True)
        
        self.assertIsInstance(results, list)
        # Should find documents with "python"
        self.assertGreater(len(results), 0)
    
    def test_and_query(self):
        """Test AND query."""
        results = self.index.search('"python" AND "programming"', use_boolean=True)
        
        self.assertIsInstance(results, list)
        # Should find documents with both terms
    
    def test_or_query(self):
        """Test OR query."""
        results = self.index.search('"python" OR "java"', use_boolean=True)
        
        self.assertIsInstance(results, list)
        # Should find documents with either term
        self.assertGreater(len(results), 0)
    
    def test_not_query(self):
        """Test NOT query."""
        # This might return empty or all docs depending on whether
        # the term exists
        results = self.index.search('NOT "xyz123"', use_boolean=True)
        
        self.assertIsInstance(results, list)
    
    def test_complex_query(self):
        """Test complex query with multiple operators."""
        results = self.index.search(
            '("python" OR "java") AND "programming"',
            use_boolean=True
        )
        
        self.assertIsInstance(results, list)


class TestRankingQueries(unittest.TestCase):
    """Test cases for ranking queries."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.index = SelfIndex(version="3.1001")  # TF-IDF with TAAT
        self.docs = [
            "Python is a popular programming language for data science",
            "Machine learning is a subset of artificial intelligence",
            "Python is used in machine learning and data science",
            "Data science combines statistics and programming",
            "Artificial intelligence includes machine learning"
        ]
        
        for doc in self.docs:
            self.index.add_document(doc)
        
        self.index.finalize()
    
    def test_ranked_search(self):
        """Test ranked search returns scored results."""
        results = self.index.search("python machine learning", top_k=3)
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        
        # Check results are tuples of (doc_id, score)
        for result in results:
            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 2)
            self.assertIsInstance(result[0], int)  # doc_id
            self.assertIsInstance(result[1], float)  # score
    
    def test_score_ordering(self):
        """Test that results are ordered by score."""
        results = self.index.search("data science", top_k=5)
        
        if len(results) > 1:
            # Scores should be in descending order
            scores = [score for _, score in results]
            self.assertEqual(scores, sorted(scores, reverse=True))
    
    def test_top_k_limit(self):
        """Test that top_k limits results."""
        k = 2
        results = self.index.search("programming", top_k=k)
        
        # Should return at most k results
        self.assertLessEqual(len(results), k)


if __name__ == '__main__':
    unittest.main()
