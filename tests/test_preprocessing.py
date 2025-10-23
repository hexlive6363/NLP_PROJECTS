"""
Unit tests for text preprocessing module.
"""

import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.preprocessing import TextPreprocessor


class TestTextPreprocessor(unittest.TestCase):
    """Test cases for TextPreprocessor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.preprocessor = TextPreprocessor(
            use_stemming=True,
            remove_stopwords=True,
            lowercase=True
        )
    
    def test_basic_preprocessing(self):
        """Test basic text preprocessing."""
        text = "Hello World! This is a test."
        result = self.preprocessor.preprocess(text)
        
        # Should be lowercase, no stopwords, stemmed
        self.assertIsInstance(result, list)
        self.assertIn('hello', result)
        self.assertIn('world', result)
        self.assertIn('test', result)
        # Stopwords should be removed
        self.assertNotIn('is', result)
        self.assertNotIn('a', result)
    
    def test_stemming(self):
        """Test stemming functionality."""
        text = "running runs runner"
        result = self.preprocessor.preprocess(text)
        
        # All forms should stem to similar roots
        self.assertEqual(len(result), 3)
        # Check that stemming occurred (all should be similar)
        # PorterStemmer stems these to 'run'
        unique_stems = set(result)
        # Should have reduced variety (1 or 2 unique stems)
        self.assertLessEqual(len(unique_stems), 2)
    
    def test_preprocessing_with_positions(self):
        """Test preprocessing that preserves positions."""
        text = "Python is a programming language"
        result = self.preprocessor.preprocess_with_positions(text)
        
        self.assertIsInstance(result, list)
        self.assertTrue(all(isinstance(item, tuple) for item in result))
        self.assertTrue(all(len(item) == 2 for item in result))
        
        # Check positions are sequential
        positions = [pos for _, pos in result]
        self.assertTrue(all(positions[i] < positions[i+1] for i in range(len(positions)-1)))
    
    def test_punctuation_removal(self):
        """Test that punctuation is removed."""
        text = "Hello, World! How are you?"
        result = self.preprocessor.preprocess(text)
        
        # No punctuation should remain
        self.assertNotIn(',', result)
        self.assertNotIn('!', result)
        self.assertNotIn('?', result)
    
    def test_empty_text(self):
        """Test handling of empty text."""
        result = self.preprocessor.preprocess("")
        self.assertEqual(result, [])
    
    def test_no_stopwords_removal(self):
        """Test preprocessing without stopword removal."""
        preprocessor = TextPreprocessor(remove_stopwords=False)
        text = "This is a test"
        result = preprocessor.preprocess(text)
        
        # Stopwords should be present
        self.assertIn('is', result)
        self.assertIn('a', result)
    
    def test_no_stemming(self):
        """Test preprocessing without stemming."""
        preprocessor = TextPreprocessor(use_stemming=False)
        text = "running runs"
        result = preprocessor.preprocess(text)
        
        # Should keep original forms
        self.assertIn('running', result)
        self.assertIn('runs', result)


if __name__ == '__main__':
    unittest.main()
