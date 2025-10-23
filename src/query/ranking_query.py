"""
Advanced query processing engines: Term-at-a-Time (TAAT) and Document-at-a-Time (DAAT).
"""

import math
from typing import Dict, List, Set, Tuple
from collections import defaultdict


class TermAtATimeProcessor:
    """
    Term-at-a-Time (TAAT) query processor.
    Processes one term at a time, accumulating scores.
    """
    
    def __init__(self, index, preprocessor):
        """
        Initialize TAAT processor.
        
        Args:
            index: InvertedIndex instance
            preprocessor: TextPreprocessor instance
        """
        self.index = index
        self.preprocessor = preprocessor
    
    def process_query(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        """
        Process query and return ranked results.
        
        Args:
            query: Query string
            top_k: Number of top results to return
            
        Returns:
            List of (doc_id, score) tuples, sorted by score
        """
        # Preprocess query
        query_terms = self.preprocessor.preprocess(query)
        
        if not query_terms:
            return []
        
        # Accumulator for document scores
        scores = defaultdict(float)
        
        # Process each term
        for term in query_terms:
            postings = self.index.get_postings(term)
            
            if not postings:
                continue
            
            # Get IDF for the term
            idf = self._get_idf(term)
            
            # Add scores for each document
            for posting in postings:
                doc_id = posting[0]
                
                if self.index.index_type == 3:  # TF-IDF
                    tf = posting[1]
                    score = tf * idf
                elif self.index.index_type == 2:  # Word count
                    count = posting[1]
                    # Normalize by document length
                    doc_length = self.index.doc_lengths.get(doc_id, 1)
                    tf = count / doc_length
                    score = tf * idf
                else:  # Boolean
                    score = idf
                
                scores[doc_id] += score
        
        # Sort by score and return top-k
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_results[:top_k]
    
    def _get_idf(self, term: str) -> float:
        """Calculate IDF for a term."""
        if hasattr(self.index, 'idf_values') and term in self.index.idf_values:
            return self.index.idf_values[term]
        
        # Calculate on-the-fly
        df = len(self.index.get_postings(term))
        if df == 0:
            return 0.0
        
        return math.log((self.index.document_count + 1) / (df + 1))


class DocumentAtATimeProcessor:
    """
    Document-at-a-Time (DAAT) query processor.
    Processes one document at a time across all query terms.
    More efficient for short queries.
    """
    
    def __init__(self, index, preprocessor):
        """
        Initialize DAAT processor.
        
        Args:
            index: InvertedIndex instance
            preprocessor: TextPreprocessor instance
        """
        self.index = index
        self.preprocessor = preprocessor
    
    def process_query(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        """
        Process query and return ranked results.
        
        Args:
            query: Query string
            top_k: Number of top results to return
            
        Returns:
            List of (doc_id, score) tuples, sorted by score
        """
        # Preprocess query
        query_terms = self.preprocessor.preprocess(query)
        
        if not query_terms:
            return []
        
        # Get postings for all terms
        term_postings = {}
        term_idfs = {}
        
        for term in query_terms:
            postings = self.index.get_postings(term)
            if postings:
                term_postings[term] = postings
                term_idfs[term] = self._get_idf(term)
        
        if not term_postings:
            return []
        
        # Get all candidate documents
        candidate_docs = set()
        for postings in term_postings.values():
            candidate_docs.update(posting[0] for posting in postings)
        
        # Score each document
        scores = []
        
        for doc_id in candidate_docs:
            score = 0.0
            
            for term in term_postings:
                # Find posting for this document
                posting = self._find_posting(term_postings[term], doc_id)
                
                if posting:
                    if self.index.index_type == 3:  # TF-IDF
                        tf = posting[1]
                        score += tf * term_idfs[term]
                    elif self.index.index_type == 2:  # Word count
                        count = posting[1]
                        doc_length = self.index.doc_lengths.get(doc_id, 1)
                        tf = count / doc_length
                        score += tf * term_idfs[term]
                    else:  # Boolean
                        score += term_idfs[term]
            
            scores.append((doc_id, score))
        
        # Sort by score and return top-k
        sorted_results = sorted(scores, key=lambda x: x[1], reverse=True)
        return sorted_results[:top_k]
    
    def _find_posting(self, postings: List, doc_id: int):
        """Find posting for a specific document."""
        for posting in postings:
            if posting[0] == doc_id:
                return posting
        return None
    
    def _get_idf(self, term: str) -> float:
        """Calculate IDF for a term."""
        if hasattr(self.index, 'idf_values') and term in self.index.idf_values:
            return self.index.idf_values[term]
        
        # Calculate on-the-fly
        df = len(self.index.get_postings(term))
        if df == 0:
            return 0.0
        
        return math.log((self.index.document_count + 1) / (df + 1))


class OptimizedTAATProcessor(TermAtATimeProcessor):
    """
    Optimized TAAT with skipping pointers.
    """
    
    def __init__(self, index, preprocessor, skip_interval: int = 10):
        """
        Initialize optimized TAAT processor.
        
        Args:
            index: InvertedIndex instance
            preprocessor: TextPreprocessor instance
            skip_interval: Interval for skip pointers
        """
        super().__init__(index, preprocessor)
        self.skip_interval = skip_interval
        self.skip_pointers = {}
    
    def build_skip_pointers(self):
        """Build skip pointers for postings lists."""
        for term, postings in self.index.index.items():
            if len(postings) < self.skip_interval:
                continue
            
            skip_list = []
            for i in range(0, len(postings), self.skip_interval):
                if i + self.skip_interval < len(postings):
                    skip_list.append((i, i + self.skip_interval))
            
            if skip_list:
                self.skip_pointers[term] = skip_list


class OptimizedDAATProcessor(DocumentAtATimeProcessor):
    """
    Optimized DAAT with early termination.
    """
    
    def __init__(self, index, preprocessor, threshold: float = 0.5):
        """
        Initialize optimized DAAT processor.
        
        Args:
            index: InvertedIndex instance
            preprocessor: TextPreprocessor instance
            threshold: Score threshold for early termination
        """
        super().__init__(index, preprocessor)
        self.threshold = threshold
    
    def process_query(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        """
        Process query with early termination.
        
        Args:
            query: Query string
            top_k: Number of top results to return
            
        Returns:
            List of (doc_id, score) tuples, sorted by score
        """
        # Preprocess query
        query_terms = self.preprocessor.preprocess(query)
        
        if not query_terms:
            return []
        
        # Get postings for all terms
        term_postings = {}
        term_idfs = {}
        
        for term in query_terms:
            postings = self.index.get_postings(term)
            if postings:
                term_postings[term] = postings
                term_idfs[term] = self._get_idf(term)
        
        if not term_postings:
            return []
        
        # Sort terms by IDF (process high IDF terms first)
        sorted_terms = sorted(term_idfs.keys(), key=lambda t: term_idfs[t], reverse=True)
        
        # Get candidate documents from high IDF terms first
        candidate_docs = set()
        max_idf = max(term_idfs.values())
        
        for term in sorted_terms:
            if term_idfs[term] >= self.threshold * max_idf:
                candidate_docs.update(posting[0] for posting in term_postings[term])
            else:
                break
        
        # If no candidates, use all
        if not candidate_docs:
            for postings in term_postings.values():
                candidate_docs.update(posting[0] for posting in postings)
        
        # Score documents
        scores = []
        
        for doc_id in candidate_docs:
            score = 0.0
            
            for term in term_postings:
                posting = self._find_posting(term_postings[term], doc_id)
                
                if posting:
                    if self.index.index_type == 3:  # TF-IDF
                        tf = posting[1]
                        score += tf * term_idfs[term]
                    elif self.index.index_type == 2:  # Word count
                        count = posting[1]
                        doc_length = self.index.doc_lengths.get(doc_id, 1)
                        tf = count / doc_length
                        score += tf * term_idfs[term]
                    else:  # Boolean
                        score += term_idfs[term]
            
            scores.append((doc_id, score))
        
        # Sort by score and return top-k
        sorted_results = sorted(scores, key=lambda x: x[1], reverse=True)
        return sorted_results[:top_k]
