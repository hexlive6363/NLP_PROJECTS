#!/usr/bin/env python3
"""
Comprehensive test script for SelfIndex.
Tests various index versions and generates performance metrics.
"""

import sys
import os
import time
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import SelfIndex, MetricsCollector
from src.utils.data_loader import DatasetManager


def test_index_versions():
    """Test different index versions and collect metrics."""
    print("=" * 80)
    print("SelfIndex Version Comparison Test")
    print("=" * 80)
    
    # Load data
    print("\nLoading sample data...")
    data_manager = DatasetManager()
    documents = data_manager.get_mixed_dataset(news_count=50, wiki_count=50)
    print(f"Loaded {len(documents)} documents")
    
    # Define versions to test
    test_versions = [
        ("1.1000", "Boolean + Pickle + No Compression"),
        ("1.1100", "Boolean + Pickle + Simple Compression"),
        ("1.1200", "Boolean + Pickle + Library Compression"),
        ("2.1000", "Word Count + Pickle"),
        ("3.1000", "TF-IDF + Pickle"),
        ("3.1001", "TF-IDF + Pickle + TAAT"),
        ("3.1002", "TF-IDF + Pickle + DAAT"),
    ]
    
    results = {}
    
    for version, description in test_versions:
        print(f"\n{'='*80}")
        print(f"Testing version: {version}")
        print(f"Description: {description}")
        print(f"{'='*80}")
        
        try:
            # Create index
            index = SelfIndex(version=version)
            
            # Measure indexing time
            start_time = time.time()
            for doc in documents:
                index.add_document(doc)
            index.finalize()
            index_time = time.time() - start_time
            
            # Get statistics
            stats = index.get_statistics()
            
            # Test queries
            test_queries = [
                "artificial intelligence",
                "machine learning",
                "data science",
                "programming language",
                "computer system",
            ]
            
            query_times = []
            for query in test_queries:
                start = time.time()
                results_list = index.search(query, top_k=10)
                query_times.append(time.time() - start)
            
            # Store results
            results[version] = {
                'description': description,
                'index_time': index_time,
                'query_times': query_times,
                'avg_query_time': sum(query_times) / len(query_times),
                'vocabulary_size': stats['vocabulary_size'],
                'total_postings': stats['total_postings'],
            }
            
            # Print results
            print(f"\nResults:")
            print(f"  Index time: {index_time:.4f}s")
            print(f"  Avg query time: {results[version]['avg_query_time']*1000:.2f}ms")
            print(f"  Vocabulary size: {stats['vocabulary_size']}")
            print(f"  Total postings: {stats['total_postings']}")
            
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    return results


def generate_plots(results):
    """Generate performance comparison plots."""
    print("\n" + "="*80)
    print("Generating performance plots...")
    print("="*80)
    
    if not results:
        print("No results to plot")
        return
    
    versions = list(results.keys())
    
    # Plot 1: Index time comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    index_times = [results[v]['index_time'] for v in versions]
    ax.bar(range(len(versions)), index_times)
    ax.set_xlabel('Index Version')
    ax.set_ylabel('Index Time (seconds)')
    ax.set_title('Indexing Time Comparison')
    ax.set_xticks(range(len(versions)))
    ax.set_xticklabels(versions, rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('plots/index_time_comparison.png')
    print("Saved: plots/index_time_comparison.png")
    plt.close()
    
    # Plot 2: Query time comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    query_times = [results[v]['avg_query_time'] * 1000 for v in versions]  # Convert to ms
    ax.bar(range(len(versions)), query_times)
    ax.set_xlabel('Index Version')
    ax.set_ylabel('Avg Query Time (milliseconds)')
    ax.set_title('Query Time Comparison')
    ax.set_xticks(range(len(versions)))
    ax.set_xticklabels(versions, rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('plots/query_time_comparison.png')
    print("Saved: plots/query_time_comparison.png")
    plt.close()
    
    # Plot 3: Memory usage (vocabulary size)
    fig, ax = plt.subplots(figsize=(10, 6))
    vocab_sizes = [results[v]['vocabulary_size'] for v in versions]
    ax.bar(range(len(versions)), vocab_sizes)
    ax.set_xlabel('Index Version')
    ax.set_ylabel('Vocabulary Size')
    ax.set_title('Memory Footprint (Vocabulary Size)')
    ax.set_xticks(range(len(versions)))
    ax.set_xticklabels(versions, rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('plots/memory_comparison.png')
    print("Saved: plots/memory_comparison.png")
    plt.close()
    
    print("\nAll plots generated successfully!")


def main():
    """Run comprehensive tests."""
    # Create plots directory
    os.makedirs('plots', exist_ok=True)
    
    # Test versions
    results = test_index_versions()
    
    # Generate plots
    generate_plots(results)
    
    print("\n" + "="*80)
    print("Test completed successfully!")
    print("="*80)


if __name__ == "__main__":
    main()
