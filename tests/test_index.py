"""
Unit tests for inverted index implementations.
"""

import unittest
import sys
import os
import tempfile
import shutil

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import SelfIndex
from src.index.factory import IndexFactory


class TestSelfIndex(unittest.TestCase):
    """Test cases for SelfIndex."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_docs = [
            "Python is a programming language",
            "Machine learning is a subset of artificial intelligence",
            "Data science involves statistics and programming",
            "Natural language processing uses machine learning",
            "Python is popular for data science and machine learning"
        ]
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_boolean_index_creation(self):
        """Test creation of boolean index."""
        index = SelfIndex(version="1.1000")
        
        for doc in self.test_docs:
            index.add_document(doc)
        
        index.finalize()
        
        stats = index.get_statistics()
        self.assertEqual(stats['document_count'], len(self.test_docs))
        self.assertGreater(stats['vocabulary_size'], 0)
    
    def test_word_count_index_creation(self):
        """Test creation of word count index."""
        index = SelfIndex(version="2.1000")
        
        for doc in self.test_docs:
            index.add_document(doc)
        
        index.finalize()
        
        stats = index.get_statistics()
        self.assertEqual(stats['document_count'], len(self.test_docs))
        self.assertEqual(stats['index_type'], 2)
    
    def test_tfidf_index_creation(self):
        """Test creation of TF-IDF index."""
        index = SelfIndex(version="3.1000")
        
        for doc in self.test_docs:
            index.add_document(doc)
        
        index.finalize()
        
        stats = index.get_statistics()
        self.assertEqual(stats['document_count'], len(self.test_docs))
        self.assertEqual(stats['index_type'], 3)
    
    def test_simple_search(self):
        """Test simple keyword search."""
        index = SelfIndex(version="3.1000")
        
        for doc in self.test_docs:
            index.add_document(doc)
        
        index.finalize()
        
        # Search for a term
        results = index.search("python", top_k=5)
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        
        # Results should be tuples of (doc_id, score)
        self.assertIsInstance(results[0], tuple)
        self.assertEqual(len(results[0]), 2)
    
    def test_boolean_search(self):
        """Test boolean query search."""
        index = SelfIndex(version="1.1000")
        
        for doc in self.test_docs:
            index.add_document(doc)
        
        index.finalize()
        
        # Boolean AND query
        results = index.search('"machine" AND "learning"', use_boolean=True)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        
        # Boolean OR query
        results = index.search('"python" OR "java"', use_boolean=True)
        self.assertGreater(len(results), 0)
    
    def test_save_and_load(self):
        """Test saving and loading index."""
        index = SelfIndex(version="3.1000")
        
        for doc in self.test_docs:
            index.add_document(doc)
        
        index.finalize()
        
        # Save index
        save_path = os.path.join(self.temp_dir, "test_index.pkl")
        index.save(save_path)
        
        # Load index
        loaded_index = SelfIndex(version="3.1000")
        loaded_index.load(save_path)
        
        # Verify loaded index
        stats = loaded_index.get_statistics()
        self.assertEqual(stats['document_count'], len(self.test_docs))
        
        # Test search on loaded index
        results = loaded_index.search("python", top_k=5)
        self.assertGreater(len(results), 0)
    
    def test_version_parsing(self):
        """Test version string parsing."""
        parsed = IndexFactory.parse_version("3.1112")
        
        self.assertEqual(parsed['index_type'], 3)
        self.assertEqual(parsed['datastore_type'], 1)
        self.assertEqual(parsed['compression_type'], 1)
        self.assertEqual(parsed['optimization_type'], 1)
        self.assertEqual(parsed['query_type'], 2)
    
    def test_get_document(self):
        """Test document retrieval."""
        index = SelfIndex(version="1.1000")
        
        doc_id = index.add_document(self.test_docs[0])
        
        retrieved = index.get_document(doc_id)
        self.assertEqual(retrieved, self.test_docs[0])
    
    def test_multiple_queries(self):
        """Test multiple queries for metrics collection."""
        index = SelfIndex(version="3.1000")
        
        for doc in self.test_docs:
            index.add_document(doc)
        
        index.finalize()
        
        # Run multiple queries
        queries = ["python", "machine learning", "data science"]
        for query in queries:
            index.search(query, top_k=5)
        
        # Check metrics were collected
        stats = index.get_statistics()
        latency = stats.get('latency', {})
        query_latencies = latency.get('query_latencies', {})
        
        if query_latencies:
            self.assertEqual(query_latencies.get('count', 0), len(queries))


class TestIndexFactory(unittest.TestCase):
    """Test cases for IndexFactory."""
    
    def test_create_boolean_index(self):
        """Test creating boolean index."""
        index = IndexFactory.create_index("1.1000")
        self.assertIsNotNone(index)
        self.assertEqual(index.index_type, 1)
    
    def test_create_tfidf_index(self):
        """Test creating TF-IDF index."""
        index = IndexFactory.create_index("3.1000")
        self.assertIsNotNone(index)
        self.assertEqual(index.index_type, 3)
    
    def test_version_description(self):
        """Test getting version description."""
        desc = IndexFactory.get_version_description("3.1112")
        self.assertIsInstance(desc, str)
        self.assertIn("TF-IDF", desc)


if __name__ == '__main__':
    unittest.main()
