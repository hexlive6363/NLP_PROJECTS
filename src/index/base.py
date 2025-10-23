"""
Base inverted index implementation with support for versioning.
"""

import math
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional, Any
from abc import ABC, abstractmethod


class InvertedIndex(ABC):
    """Base class for inverted index implementations."""
    
    def __init__(self, version: str = "1.1000"):
        """
        Initialize inverted index.
        
        Args:
            version: Version string in format x.yziq where:
                x = type of index (1=boolean, 2=word counts, 3=TF-IDF)
                y = datastore (1=pickle/JSON, 2=PostgreSQL, 3=RocksDB, 4=Redis)
                z = compression (0=none, 1=simple, 2=library)
                i = optimization (0=no skipping, 1=with skipping)
                q = query processing (0=basic, 1=TAAT, 2=DAAT)
        """
        self.version = version
        self.index: Dict[str, Any] = defaultdict(list)
        self.document_count = 0
        self.documents: Dict[int, str] = {}
        self.doc_lengths: Dict[int, int] = {}
        self.avg_doc_length = 0
        
        # Parse version
        parts = version.split('.')
        if len(parts) >= 2:
            self.index_type = int(parts[0])  # x: 1=boolean, 2=counts, 3=TF-IDF
            if len(parts[1]) >= 1:
                self.datastore_type = int(parts[1][0])  # y
            if len(parts[1]) >= 2:
                self.compression_type = int(parts[1][1])  # z
            if len(parts[1]) >= 3:
                self.optimization_type = int(parts[1][2])  # i
            if len(parts[1]) >= 4:
                self.query_type = int(parts[1][3])  # q
        else:
            self.index_type = 1
            self.datastore_type = 1
            self.compression_type = 0
            self.optimization_type = 0
            self.query_type = 0
    
    def add_document(self, doc_id: int, terms: List[str], positions: List[int] = None):
        """
        Add a document to the index.
        
        Args:
            doc_id: Document ID
            terms: List of terms in the document
            positions: Optional list of positions for each term
        """
        self.document_count += 1
        self.doc_lengths[doc_id] = len(terms)
        
        # Update average document length
        self.avg_doc_length = sum(self.doc_lengths.values()) / len(self.doc_lengths)
        
        if self.index_type == 1:  # Boolean index with positions
            self._add_boolean_index(doc_id, terms, positions)
        elif self.index_type == 2:  # Word count index
            self._add_count_index(doc_id, terms, positions)
        elif self.index_type == 3:  # TF-IDF index
            self._add_tfidf_index(doc_id, terms, positions)
    
    def _add_boolean_index(self, doc_id: int, terms: List[str], positions: List[int] = None):
        """Add document to boolean index."""
        term_positions = defaultdict(list)
        
        if positions is None:
            positions = list(range(len(terms)))
        
        for term, pos in zip(terms, positions):
            term_positions[term].append(pos)
        
        for term, pos_list in term_positions.items():
            # Store as (doc_id, positions)
            self.index[term].append((doc_id, pos_list))
    
    def _add_count_index(self, doc_id: int, terms: List[str], positions: List[int] = None):
        """Add document to count-based index."""
        term_counts = defaultdict(int)
        term_positions = defaultdict(list)
        
        if positions is None:
            positions = list(range(len(terms)))
        
        for term, pos in zip(terms, positions):
            term_counts[term] += 1
            term_positions[term].append(pos)
        
        for term in term_counts:
            # Store as (doc_id, count, positions)
            self.index[term].append((doc_id, term_counts[term], term_positions[term]))
    
    def _add_tfidf_index(self, doc_id: int, terms: List[str], positions: List[int] = None):
        """Add document to TF-IDF index."""
        term_counts = defaultdict(int)
        term_positions = defaultdict(list)
        
        if positions is None:
            positions = list(range(len(terms)))
        
        for term, pos in zip(terms, positions):
            term_counts[term] += 1
            term_positions[term].append(pos)
        
        doc_length = len(terms)
        
        for term in term_counts:
            tf = term_counts[term] / doc_length if doc_length > 0 else 0
            # Store as (doc_id, tf, count, positions)
            self.index[term].append((doc_id, tf, term_counts[term], term_positions[term]))
    
    def finalize_index(self):
        """
        Finalize index after all documents are added.
        Compute IDF values for TF-IDF index.
        """
        if self.index_type == 3:  # TF-IDF
            self._compute_idf()
    
    def _compute_idf(self):
        """Compute IDF values for all terms."""
        self.idf_values = {}
        
        for term, postings in self.index.items():
            df = len(postings)  # Document frequency
            idf = math.log((self.document_count + 1) / (df + 1))
            self.idf_values[term] = idf
    
    def get_postings(self, term: str) -> List[Any]:
        """
        Get postings list for a term.
        
        Args:
            term: Search term
            
        Returns:
            List of postings (format depends on index type)
        """
        return self.index.get(term, [])
    
    def get_document_ids(self, term: str) -> Set[int]:
        """
        Get set of document IDs containing the term.
        
        Args:
            term: Search term
            
        Returns:
            Set of document IDs
        """
        postings = self.get_postings(term)
        
        if not postings:
            return set()
        
        # Extract doc_id (always the first element)
        return {posting[0] for posting in postings}
    
    def get_term_positions(self, term: str, doc_id: int) -> List[int]:
        """
        Get positions of term in a document.
        
        Args:
            term: Search term
            doc_id: Document ID
            
        Returns:
            List of positions
        """
        postings = self.get_postings(term)
        
        for posting in postings:
            if posting[0] == doc_id:
                # Position is always the last element
                return posting[-1]
        
        return []
    
    def get_vocabulary_size(self) -> int:
        """Get the size of the vocabulary."""
        return len(self.index)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get index statistics."""
        total_postings = sum(len(postings) for postings in self.index.values())
        
        return {
            'version': self.version,
            'document_count': self.document_count,
            'vocabulary_size': self.get_vocabulary_size(),
            'total_postings': total_postings,
            'avg_doc_length': self.avg_doc_length,
            'index_type': self.index_type,
            'datastore_type': self.datastore_type,
            'compression_type': self.compression_type,
            'optimization_type': self.optimization_type,
            'query_type': self.query_type
        }
    
    @abstractmethod
    def save(self, path: str):
        """Save index to disk."""
        pass
    
    @abstractmethod
    def load(self, path: str):
        """Load index from disk."""
        pass
