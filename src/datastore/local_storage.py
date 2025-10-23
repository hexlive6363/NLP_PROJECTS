"""
Pickle/JSON based datastore implementation.
"""

import pickle
import json
import os
from typing import Any, Dict
from ..index.base import InvertedIndex


class PickleDatastore(InvertedIndex):
    """Inverted index using pickle for persistence."""
    
    def save(self, path: str):
        """
        Save index to disk using pickle.
        
        Args:
            path: Path to save the index
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        data = {
            'version': self.version,
            'index': dict(self.index),
            'document_count': self.document_count,
            'documents': self.documents,
            'doc_lengths': self.doc_lengths,
            'avg_doc_length': self.avg_doc_length,
            'idf_values': getattr(self, 'idf_values', {})
        }
        
        with open(path, 'wb') as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    def load(self, path: str):
        """
        Load index from disk using pickle.
        
        Args:
            path: Path to load the index from
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Index file not found: {path}")
        
        with open(path, 'rb') as f:
            data = pickle.load(f)
        
        self.version = data['version']
        self.index = data['index']
        self.document_count = data['document_count']
        self.documents = data['documents']
        self.doc_lengths = data['doc_lengths']
        self.avg_doc_length = data['avg_doc_length']
        
        if 'idf_values' in data:
            self.idf_values = data['idf_values']


class JSONDatastore(InvertedIndex):
    """Inverted index using JSON for persistence."""
    
    def save(self, path: str):
        """
        Save index to disk using JSON.
        
        Args:
            path: Path to save the index
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Convert to JSON-serializable format
        index_data = {}
        for term, postings in self.index.items():
            index_data[term] = [list(posting) for posting in postings]
        
        data = {
            'version': self.version,
            'index': index_data,
            'document_count': self.document_count,
            'documents': {str(k): v for k, v in self.documents.items()},
            'doc_lengths': {str(k): v for k, v in self.doc_lengths.items()},
            'avg_doc_length': self.avg_doc_length,
            'idf_values': getattr(self, 'idf_values', {})
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def load(self, path: str):
        """
        Load index from disk using JSON.
        
        Args:
            path: Path to load the index from
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Index file not found: {path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.version = data['version']
        
        # Convert back from JSON format
        self.index = {}
        for term, postings in data['index'].items():
            self.index[term] = [tuple(posting) for posting in postings]
        
        self.document_count = data['document_count']
        self.documents = {int(k): v for k, v in data['documents'].items()}
        self.doc_lengths = {int(k): v for k, v in data['doc_lengths'].items()}
        self.avg_doc_length = data['avg_doc_length']
        
        if 'idf_values' in data:
            self.idf_values = data['idf_values']
