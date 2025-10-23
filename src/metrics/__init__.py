"""
Performance metrics collection for indexing and querying.
Includes latency, throughput, memory footprint, and functional metrics.
"""

import time
import psutil
import os
import numpy as np
from typing import List, Dict, Any, Tuple
from collections import defaultdict


class MetricsCollector:
    """Collects and tracks performance metrics."""
    
    def __init__(self):
        """Initialize metrics collector."""
        self.query_latencies = []
        self.index_latencies = []
        self.memory_snapshots = []
        self.start_memory = None
        self.process = psutil.Process(os.getpid())
    
    def start_memory_tracking(self):
        """Start tracking memory usage."""
        self.start_memory = self.process.memory_info().rss / (1024 * 1024)  # MB
    
    def record_memory_snapshot(self, label: str = ""):
        """
        Record current memory usage.
        
        Args:
            label: Label for this snapshot
        """
        memory_mb = self.process.memory_info().rss / (1024 * 1024)
        self.memory_snapshots.append((label, memory_mb))
    
    def get_memory_footprint(self) -> Dict[str, float]:
        """
        Get memory footprint statistics.
        
        Returns:
            Dictionary with memory statistics
        """
        if not self.memory_snapshots:
            return {}
        
        memories = [m[1] for m in self.memory_snapshots]
        
        return {
            'min_memory_mb': min(memories),
            'max_memory_mb': max(memories),
            'avg_memory_mb': np.mean(memories),
            'current_memory_mb': memories[-1],
            'snapshots': self.memory_snapshots
        }
    
    def record_query_latency(self, latency: float):
        """
        Record query latency.
        
        Args:
            latency: Query latency in seconds
        """
        self.query_latencies.append(latency)
    
    def record_index_latency(self, latency: float):
        """
        Record indexing latency.
        
        Args:
            latency: Indexing latency in seconds
        """
        self.index_latencies.append(latency)
    
    def get_latency_statistics(self) -> Dict[str, Any]:
        """
        Get latency statistics including p95 and p99.
        
        Returns:
            Dictionary with latency statistics
        """
        if not self.query_latencies:
            return {'query_latencies': {}, 'index_latencies': {}}
        
        query_stats = {}
        if self.query_latencies:
            query_stats = {
                'mean': np.mean(self.query_latencies),
                'median': np.median(self.query_latencies),
                'min': np.min(self.query_latencies),
                'max': np.max(self.query_latencies),
                'p95': np.percentile(self.query_latencies, 95),
                'p99': np.percentile(self.query_latencies, 99),
                'std': np.std(self.query_latencies),
                'count': len(self.query_latencies)
            }
        
        index_stats = {}
        if self.index_latencies:
            index_stats = {
                'mean': np.mean(self.index_latencies),
                'median': np.median(self.index_latencies),
                'min': np.min(self.index_latencies),
                'max': np.max(self.index_latencies),
                'p95': np.percentile(self.index_latencies, 95),
                'p99': np.percentile(self.index_latencies, 99),
                'std': np.std(self.index_latencies),
                'count': len(self.index_latencies)
            }
        
        return {
            'query_latencies': query_stats,
            'index_latencies': index_stats
        }
    
    def calculate_throughput(self, duration: float, operation_type: str = 'query') -> float:
        """
        Calculate throughput (operations per second).
        
        Args:
            duration: Total duration in seconds
            operation_type: Type of operation ('query' or 'index')
            
        Returns:
            Throughput in operations per second
        """
        if operation_type == 'query':
            count = len(self.query_latencies)
        else:
            count = len(self.index_latencies)
        
        if duration == 0:
            return 0.0
        
        return count / duration
    
    def reset(self):
        """Reset all metrics."""
        self.query_latencies = []
        self.index_latencies = []
        self.memory_snapshots = []
        self.start_memory = None


class FunctionalMetrics:
    """Calculates functional metrics like precision, recall, and ranking measures."""
    
    @staticmethod
    def precision(retrieved: set, relevant: set) -> float:
        """
        Calculate precision.
        
        Args:
            retrieved: Set of retrieved document IDs
            relevant: Set of relevant document IDs
            
        Returns:
            Precision score
        """
        if not retrieved:
            return 0.0
        
        return len(retrieved & relevant) / len(retrieved)
    
    @staticmethod
    def recall(retrieved: set, relevant: set) -> float:
        """
        Calculate recall.
        
        Args:
            retrieved: Set of retrieved document IDs
            relevant: Set of relevant document IDs
            
        Returns:
            Recall score
        """
        if not relevant:
            return 0.0
        
        return len(retrieved & relevant) / len(relevant)
    
    @staticmethod
    def f1_score(retrieved: set, relevant: set) -> float:
        """
        Calculate F1 score.
        
        Args:
            retrieved: Set of retrieved document IDs
            relevant: Set of relevant document IDs
            
        Returns:
            F1 score
        """
        prec = FunctionalMetrics.precision(retrieved, relevant)
        rec = FunctionalMetrics.recall(retrieved, relevant)
        
        if prec + rec == 0:
            return 0.0
        
        return 2 * (prec * rec) / (prec + rec)
    
    @staticmethod
    def average_precision(ranked_results: List[int], relevant: set) -> float:
        """
        Calculate average precision for a ranked list.
        
        Args:
            ranked_results: List of document IDs in ranked order
            relevant: Set of relevant document IDs
            
        Returns:
            Average precision score
        """
        if not relevant or not ranked_results:
            return 0.0
        
        precisions = []
        relevant_count = 0
        
        for i, doc_id in enumerate(ranked_results, 1):
            if doc_id in relevant:
                relevant_count += 1
                precision_at_i = relevant_count / i
                precisions.append(precision_at_i)
        
        if not precisions:
            return 0.0
        
        return sum(precisions) / len(relevant)
    
    @staticmethod
    def mean_average_precision(queries_results: List[Tuple[List[int], set]]) -> float:
        """
        Calculate mean average precision across multiple queries.
        
        Args:
            queries_results: List of (ranked_results, relevant_set) tuples
            
        Returns:
            Mean average precision score
        """
        if not queries_results:
            return 0.0
        
        aps = [
            FunctionalMetrics.average_precision(results, relevant)
            for results, relevant in queries_results
        ]
        
        return np.mean(aps)
    
    @staticmethod
    def ndcg(ranked_results: List[int], relevance_scores: Dict[int, float], k: int = None) -> float:
        """
        Calculate Normalized Discounted Cumulative Gain (NDCG).
        
        Args:
            ranked_results: List of document IDs in ranked order
            relevance_scores: Dictionary mapping doc_id to relevance score
            k: Consider only top-k results (None for all)
            
        Returns:
            NDCG score
        """
        if not ranked_results or not relevance_scores:
            return 0.0
        
        if k is not None:
            ranked_results = ranked_results[:k]
        
        # Calculate DCG
        dcg = 0.0
        for i, doc_id in enumerate(ranked_results, 1):
            rel = relevance_scores.get(doc_id, 0)
            dcg += (2 ** rel - 1) / np.log2(i + 1)
        
        # Calculate IDCG (Ideal DCG)
        ideal_ranking = sorted(relevance_scores.values(), reverse=True)[:len(ranked_results)]
        idcg = 0.0
        for i, rel in enumerate(ideal_ranking, 1):
            idcg += (2 ** rel - 1) / np.log2(i + 1)
        
        if idcg == 0:
            return 0.0
        
        return dcg / idcg
    
    @staticmethod
    def reciprocal_rank(ranked_results: List[int], relevant: set) -> float:
        """
        Calculate reciprocal rank.
        
        Args:
            ranked_results: List of document IDs in ranked order
            relevant: Set of relevant document IDs
            
        Returns:
            Reciprocal rank score
        """
        for i, doc_id in enumerate(ranked_results, 1):
            if doc_id in relevant:
                return 1.0 / i
        
        return 0.0
    
    @staticmethod
    def mean_reciprocal_rank(queries_results: List[Tuple[List[int], set]]) -> float:
        """
        Calculate mean reciprocal rank across multiple queries.
        
        Args:
            queries_results: List of (ranked_results, relevant_set) tuples
            
        Returns:
            Mean reciprocal rank score
        """
        if not queries_results:
            return 0.0
        
        rrs = [
            FunctionalMetrics.reciprocal_rank(results, relevant)
            for results, relevant in queries_results
        ]
        
        return np.mean(rrs)


class QueryTimer:
    """Context manager for timing operations."""
    
    def __init__(self, metrics_collector: MetricsCollector, operation_type: str = 'query'):
        """
        Initialize query timer.
        
        Args:
            metrics_collector: MetricsCollector instance
            operation_type: Type of operation ('query' or 'index')
        """
        self.metrics_collector = metrics_collector
        self.operation_type = operation_type
        self.start_time = None
    
    def __enter__(self):
        """Start timing."""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timing and record latency."""
        end_time = time.time()
        latency = end_time - self.start_time
        
        if self.operation_type == 'query':
            self.metrics_collector.record_query_latency(latency)
        else:
            self.metrics_collector.record_index_latency(latency)
