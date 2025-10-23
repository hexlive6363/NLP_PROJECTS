"""
Main SelfIndex class that provides a unified interface for indexing and querying.
"""

import os
from typing import List, Dict, Any, Set, Tuple, Optional
from ..preprocessing import TextPreprocessor
from ..index.factory import IndexFactory
from ..query.boolean_query import QueryProcessor
from ..query.ranking_query import (
    TermAtATimeProcessor,
    DocumentAtATimeProcessor,
    OptimizedTAATProcessor,
    OptimizedDAATProcessor
)
from ..utils.compression import CompressionWrapper
from ..metrics import MetricsCollector, QueryTimer


class SelfIndex:
    """
    Unified interface for the self-implemented inverted index.
    Supports multiple index types, datastores, compression, and query processing modes.
    """
    
    def __init__(self, version: str = "1.1000", **kwargs):
        """
        Initialize SelfIndex.
        
        Args:
            version: Version string (format: x.yziq)
            **kwargs: Additional arguments for specific components
        """
        self.version = version
        self.version_info = IndexFactory.parse_version(version)
        
        # Initialize preprocessor
        self.preprocessor = TextPreprocessor(
            use_stemming=kwargs.get('use_stemming', True),
            remove_stopwords=kwargs.get('remove_stopwords', True),
            lowercase=kwargs.get('lowercase', True)
        )
        
        # Create index
        self.index = IndexFactory.create_index(version, **kwargs)
        
        # Initialize compression wrapper if needed
        self.compression = None
        if self.version_info['compression_type'] > 0:
            self.compression = CompressionWrapper(
                self.index,
                self.version_info['compression_type']
            )
        
        # Initialize query processor
        self._init_query_processor()
        
        # Metrics collector
        self.metrics = MetricsCollector()
        
        # Document storage
        self.doc_id_counter = 0
        self.doc_texts = {}
    
    def _init_query_processor(self):
        """Initialize appropriate query processor based on version."""
        query_type = self.version_info['query_type']
        optimization = self.version_info['optimization_type']
        
        # Boolean query processor (for operators)
        self.boolean_processor = QueryProcessor(self.index, self.preprocessor)
        
        # Ranking query processor
        if query_type == 1:  # TAAT
            if optimization == 1:
                self.ranking_processor = OptimizedTAATProcessor(self.index, self.preprocessor)
            else:
                self.ranking_processor = TermAtATimeProcessor(self.index, self.preprocessor)
        elif query_type == 2:  # DAAT
            if optimization == 1:
                self.ranking_processor = OptimizedDAATProcessor(self.index, self.preprocessor)
            else:
                self.ranking_processor = DocumentAtATimeProcessor(self.index, self.preprocessor)
        else:
            # Default to TAAT
            self.ranking_processor = TermAtATimeProcessor(self.index, self.preprocessor)
    
    def add_document(self, text: str, doc_id: Optional[int] = None) -> int:
        """
        Add a document to the index.
        
        Args:
            text: Document text
            doc_id: Optional document ID (auto-generated if not provided)
            
        Returns:
            Document ID
        """
        if doc_id is None:
            doc_id = self.doc_id_counter
            self.doc_id_counter += 1
        
        # Store document text
        self.doc_texts[doc_id] = text
        
        # Preprocess with positions
        terms_with_positions = self.preprocessor.preprocess_with_positions(text)
        
        if not terms_with_positions:
            return doc_id
        
        # Extract terms and positions
        terms = [t[0] for t in terms_with_positions]
        positions = [t[1] for t in terms_with_positions]
        
        # Add to index
        with QueryTimer(self.metrics, 'index'):
            self.index.add_document(doc_id, terms, positions)
        
        return doc_id
    
    def add_documents(self, documents: List[str]) -> List[int]:
        """
        Add multiple documents to the index.
        
        Args:
            documents: List of document texts
            
        Returns:
            List of document IDs
        """
        doc_ids = []
        
        for doc in documents:
            doc_id = self.add_document(doc)
            doc_ids.append(doc_id)
        
        return doc_ids
    
    def finalize(self):
        """
        Finalize the index after all documents are added.
        Computes IDF values and applies compression if enabled.
        """
        # Finalize index (compute IDF, etc.)
        self.index.finalize_index()
        
        # Apply compression if enabled
        if self.compression:
            self.compression.compress()
        
        # Build skip pointers if optimization is enabled
        if (self.version_info['optimization_type'] == 1 and
            hasattr(self.ranking_processor, 'build_skip_pointers')):
            self.ranking_processor.build_skip_pointers()
    
    def search(self, query: str, top_k: int = 10, use_boolean: bool = None) -> List[Any]:
        """
        Search the index with a query.
        
        Args:
            query: Query string
            top_k: Number of top results to return (for ranking queries)
            use_boolean: Force boolean query mode (auto-detect if None)
            
        Returns:
            List of results (format depends on query type)
        """
        # Auto-detect boolean query
        if use_boolean is None:
            use_boolean = any(op in query.upper() for op in ['AND', 'OR', 'NOT', 'PHRASE'])
        
        with QueryTimer(self.metrics, 'query'):
            if use_boolean:
                # Boolean query - returns set of doc IDs
                result_set = self.boolean_processor.process_query(query)
                return list(result_set)
            else:
                # Ranking query - returns ranked list
                ranked_results = self.ranking_processor.process_query(query, top_k)
                return ranked_results
    
    def get_document(self, doc_id: int) -> Optional[str]:
        """
        Get document text by ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document text or None if not found
        """
        return self.doc_texts.get(doc_id)
    
    def save(self, path: str):
        """
        Save index to disk.
        
        Args:
            path: Path to save the index
        """
        # Create directory if needed
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
        
        # Save index
        self.index.save(path)
        
        # Save document texts separately
        import pickle
        doc_path = path + '.docs'
        with open(doc_path, 'wb') as f:
            pickle.dump({
                'doc_texts': self.doc_texts,
                'doc_id_counter': self.doc_id_counter,
                'version': self.version
            }, f)
        
        # Save compression data if applicable
        if self.compression:
            comp_path = path + '.comp'
            with open(comp_path, 'wb') as f:
                pickle.dump(self.compression.compressed_index, f)
    
    def load(self, path: str):
        """
        Load index from disk.
        
        Args:
            path: Path to load the index from
        """
        # Load index
        self.index.load(path)
        
        # Load document texts
        import pickle
        doc_path = path + '.docs'
        if os.path.exists(doc_path):
            with open(doc_path, 'rb') as f:
                data = pickle.load(f)
                self.doc_texts = data['doc_texts']
                self.doc_id_counter = data['doc_id_counter']
        
        # Load compression data if applicable
        if self.compression:
            comp_path = path + '.comp'
            if os.path.exists(comp_path):
                with open(comp_path, 'rb') as f:
                    self.compression.compressed_index = pickle.load(f)
        
        # Reinitialize query processor
        self._init_query_processor()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get index statistics.
        
        Returns:
            Dictionary with statistics
        """
        stats = self.index.get_statistics()
        
        # Add compression stats if applicable
        if self.compression:
            stats['compression_ratio'] = self.compression.get_compression_ratio()
        
        # Add metrics
        stats['latency'] = self.metrics.get_latency_statistics()
        stats['memory'] = self.metrics.get_memory_footprint()
        
        return stats
    
    def get_version_description(self) -> str:
        """
        Get human-readable version description.
        
        Returns:
            Description string
        """
        return IndexFactory.get_version_description(self.version)
