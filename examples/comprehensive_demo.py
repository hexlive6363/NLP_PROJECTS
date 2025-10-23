#!/usr/bin/env python3
"""
Comprehensive demonstration of SelfIndex capabilities.
Shows all major features including different index types, query modes, and metrics.
"""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import SelfIndex
from src.utils.data_loader import DatasetManager
from src.metrics import FunctionalMetrics


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def demo_index_types():
    """Demonstrate different index types."""
    print_section("DEMO 1: Different Index Types")
    
    # Load sample data
    data_manager = DatasetManager()
    documents = data_manager.get_mixed_dataset(news_count=30, wiki_count=30)
    
    versions = [
        ("1.1000", "Boolean Index"),
        ("2.1000", "Word Count Index"),
        ("3.1000", "TF-IDF Index")
    ]
    
    for version, name in versions:
        print(f"\n{name} (v{version}):")
        print("-" * 40)
        
        index = SelfIndex(version=version)
        
        # Add documents
        for doc in documents:
            index.add_document(doc)
        
        index.finalize()
        
        # Get statistics
        stats = index.get_statistics()
        print(f"Documents: {stats['document_count']}")
        print(f"Vocabulary: {stats['vocabulary_size']}")
        print(f"Total postings: {stats['total_postings']}")
        
        # Test search
        results = index.search("artificial intelligence machine learning", top_k=3)
        print(f"\nTop 3 results for 'artificial intelligence machine learning':")
        
        if results and isinstance(results[0], tuple):
            for doc_id, score in results[:3]:
                print(f"  Doc {doc_id}: {score:.4f}")
        else:
            print(f"  Found {len(results)} matching documents")


def demo_boolean_queries():
    """Demonstrate boolean query capabilities."""
    print_section("DEMO 2: Boolean Query Operators")
    
    # Create index
    index = SelfIndex(version="1.1000")
    
    # Add sample documents
    documents = [
        "Python is a programming language used for data science",
        "Machine learning is a subset of artificial intelligence",
        "Java is a programming language for enterprise applications",
        "Data science combines programming and statistics",
        "Python is popular for machine learning and AI",
    ]
    
    for i, doc in enumerate(documents):
        index.add_document(doc)
        print(f"Doc {i}: {doc}")
    
    index.finalize()
    
    # Test different boolean queries
    queries = [
        ('"python" AND "programming"', "AND: Both terms must be present"),
        ('"python" OR "java"', "OR: Either term can be present"),
        ('"programming" AND NOT "java"', "NOT: Exclude documents with 'java'"),
        ('("machine learning" OR "data science") AND "python"', "Complex: Using parentheses"),
    ]
    
    print("\nQuery Results:")
    print("-" * 40)
    
    for query, description in queries:
        print(f"\n{description}")
        print(f"Query: {query}")
        results = index.search(query, use_boolean=True)
        print(f"Matching documents: {sorted(results) if results else []}")


def demo_query_processing_modes():
    """Demonstrate different query processing modes."""
    print_section("DEMO 3: Query Processing Modes (TAAT vs DAAT)")
    
    # Load data
    data_manager = DatasetManager()
    documents = data_manager.get_mixed_dataset(news_count=50, wiki_count=50)
    
    modes = [
        ("3.1000", "Basic (no specific mode)"),
        ("3.1001", "Term-at-a-Time (TAAT)"),
        ("3.1002", "Document-at-a-Time (DAAT)"),
    ]
    
    test_query = "artificial intelligence machine learning data science"
    
    for version, name in modes:
        print(f"\n{name} (v{version}):")
        print("-" * 40)
        
        index = SelfIndex(version=version)
        
        # Add documents
        start_time = time.time()
        for doc in documents:
            index.add_document(doc)
        index.finalize()
        index_time = time.time() - start_time
        
        # Test query
        start_time = time.time()
        results = index.search(test_query, top_k=5)
        query_time = time.time() - start_time
        
        print(f"Index time: {index_time:.4f}s")
        print(f"Query time: {query_time*1000:.2f}ms")
        print(f"Top 5 results:")
        for doc_id, score in results[:5]:
            print(f"  Doc {doc_id}: {score:.4f}")


def demo_compression():
    """Demonstrate compression methods."""
    print_section("DEMO 4: Compression Methods")
    
    # Load data
    data_manager = DatasetManager()
    documents = data_manager.get_mixed_dataset(news_count=50, wiki_count=50)
    
    compression_modes = [
        ("3.1000", "No Compression"),
        ("3.1100", "Simple Compression (Gap Encoding)"),
        ("3.1200", "Library Compression (zlib)"),
    ]
    
    for version, name in compression_modes:
        print(f"\n{name} (v{version}):")
        print("-" * 40)
        
        index = SelfIndex(version=version)
        
        # Add documents
        for doc in documents:
            index.add_document(doc)
        index.finalize()
        
        # Get statistics
        stats = index.get_statistics()
        print(f"Vocabulary size: {stats['vocabulary_size']}")
        print(f"Total postings: {stats['total_postings']}")
        
        if 'compression_ratio' in stats:
            print(f"Compression ratio: {stats['compression_ratio']:.2f}x")


def demo_metrics():
    """Demonstrate performance metrics collection."""
    print_section("DEMO 5: Performance Metrics")
    
    # Create index
    index = SelfIndex(version="3.1001")
    
    # Load data
    data_manager = DatasetManager()
    documents = data_manager.get_mixed_dataset(news_count=50, wiki_count=50)
    
    print("\nIndexing documents...")
    for doc in documents:
        index.add_document(doc)
    index.finalize()
    
    # Run multiple queries to collect metrics
    print("Running test queries...")
    test_queries = [
        "artificial intelligence",
        "machine learning",
        "data science programming",
        "natural language processing",
        "computer vision deep learning",
        "neural networks",
        "python programming",
        "database systems",
        "web development",
        "cloud computing"
    ]
    
    for query in test_queries:
        results = index.search(query, top_k=10)
    
    # Get statistics
    stats = index.get_statistics()
    
    print("\nPerformance Metrics:")
    print("-" * 40)
    
    # Latency metrics
    latency = stats.get('latency', {})
    if latency.get('query_latencies'):
        ql = latency['query_latencies']
        print(f"\nQuery Latency:")
        print(f"  Mean: {ql['mean']*1000:.2f}ms")
        print(f"  Median: {ql['median']*1000:.2f}ms")
        print(f"  P95: {ql['p95']*1000:.2f}ms")
        print(f"  P99: {ql['p99']*1000:.2f}ms")
        print(f"  Min: {ql['min']*1000:.2f}ms")
        print(f"  Max: {ql['max']*1000:.2f}ms")
    
    if latency.get('index_latencies'):
        il = latency['index_latencies']
        print(f"\nIndexing Latency:")
        print(f"  Mean per doc: {il['mean']*1000:.2f}ms")
        print(f"  Total docs: {il['count']}")
    
    # Memory metrics
    memory = stats.get('memory', {})
    if memory:
        print(f"\nMemory Usage:")
        print(f"  Current: {memory.get('current_memory_mb', 0):.2f}MB")
        print(f"  Max: {memory.get('max_memory_mb', 0):.2f}MB")
        print(f"  Avg: {memory.get('avg_memory_mb', 0):.2f}MB")


def demo_functional_metrics():
    """Demonstrate functional metrics (precision, recall, etc.)."""
    print_section("DEMO 6: Functional Metrics (Precision, Recall, etc.)")
    
    # Simulate query results
    print("\nExample: Evaluating search quality")
    print("-" * 40)
    
    retrieved_docs = {1, 2, 3, 4, 5, 6, 7, 8}
    relevant_docs = {2, 3, 5, 9, 10}
    
    print(f"Retrieved documents: {sorted(retrieved_docs)}")
    print(f"Relevant documents: {sorted(relevant_docs)}")
    
    precision = FunctionalMetrics.precision(retrieved_docs, relevant_docs)
    recall = FunctionalMetrics.recall(retrieved_docs, relevant_docs)
    f1 = FunctionalMetrics.f1_score(retrieved_docs, relevant_docs)
    
    print(f"\nMetrics:")
    print(f"  Precision: {precision:.3f} ({int(precision*len(retrieved_docs))}/{len(retrieved_docs)} relevant)")
    print(f"  Recall: {recall:.3f} ({len(retrieved_docs & relevant_docs)}/{len(relevant_docs)} found)")
    print(f"  F1 Score: {f1:.3f}")
    
    # Ranked results
    print("\nFor ranked results:")
    ranked_results = [1, 2, 3, 4, 5, 6, 7, 8]
    ap = FunctionalMetrics.average_precision(ranked_results, relevant_docs)
    rr = FunctionalMetrics.reciprocal_rank(ranked_results, relevant_docs)
    
    print(f"  Average Precision: {ap:.3f}")
    print(f"  Reciprocal Rank: {rr:.3f}")


def demo_persistence():
    """Demonstrate saving and loading indexes."""
    print_section("DEMO 7: Index Persistence")
    
    # Create and save index
    print("\n1. Creating and saving index...")
    index = SelfIndex(version="3.1000")
    
    documents = [
        "Python is a programming language",
        "Machine learning is a branch of AI",
        "Data science involves statistics"
    ]
    
    for doc in documents:
        index.add_document(doc)
    
    index.finalize()
    
    save_path = "indices/demo_index.pkl"
    os.makedirs("indices", exist_ok=True)
    index.save(save_path)
    print(f"   Saved to: {save_path}")
    
    # Load index
    print("\n2. Loading saved index...")
    loaded_index = SelfIndex(version="3.1000")
    loaded_index.load(save_path)
    print("   Loaded successfully!")
    
    # Test loaded index
    print("\n3. Testing loaded index...")
    results = loaded_index.search("python programming", top_k=3)
    print(f"   Query results: {results}")
    
    stats = loaded_index.get_statistics()
    print(f"   Documents in loaded index: {stats['document_count']}")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 80)
    print(" SelfIndex Comprehensive Demo")
    print(" Showcasing all major features and capabilities")
    print("=" * 80)
    
    try:
        demo_index_types()
        demo_boolean_queries()
        demo_query_processing_modes()
        demo_compression()
        demo_metrics()
        demo_functional_metrics()
        demo_persistence()
        
        print("\n" + "=" * 80)
        print(" Demo completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
