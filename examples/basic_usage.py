#!/usr/bin/env python3
"""
Example script demonstrating basic usage of SelfIndex.
Creates indexes with different versions and tests queries.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import SelfIndex
from src.utils.data_loader import DatasetManager


def main():
    """Run basic example."""
    print("=" * 80)
    print("SelfIndex Basic Example")
    print("=" * 80)
    
    # Load sample data
    print("\n1. Loading sample data...")
    data_manager = DatasetManager()
    documents = data_manager.get_mixed_dataset(news_count=20, wiki_count=20)
    print(f"   Loaded {len(documents)} documents")
    
    # Create different index versions
    versions = [
        ("1.1000", "Boolean index with pickle storage"),
        ("2.1000", "Word count index with pickle storage"),
        ("3.1000", "TF-IDF index with pickle storage"),
    ]
    
    for version, description in versions:
        print(f"\n2. Creating index version {version}")
        print(f"   Description: {description}")
        
        # Create index
        index = SelfIndex(version=version)
        
        # Add documents
        print("   Adding documents...")
        for doc in documents:
            index.add_document(doc)
        
        # Finalize index
        print("   Finalizing index...")
        index.finalize()
        
        # Get statistics
        stats = index.get_statistics()
        print(f"   Statistics:")
        print(f"     - Documents: {stats['document_count']}")
        print(f"     - Vocabulary size: {stats['vocabulary_size']}")
        print(f"     - Total postings: {stats['total_postings']}")
        
        # Test queries
        print("\n3. Testing queries...")
        
        # Simple query
        query1 = "artificial intelligence"
        print(f"\n   Query: '{query1}'")
        results = index.search(query1, top_k=5)
        
        if isinstance(results, list) and results and isinstance(results[0], tuple):
            # Ranked results
            print(f"   Top 5 results:")
            for doc_id, score in results[:5]:
                print(f"     Doc {doc_id}: score={score:.4f}")
        else:
            print(f"   Found {len(results)} documents")
        
        # Boolean query
        query2 = '"machine learning" AND "artificial intelligence"'
        print(f"\n   Boolean query: '{query2}'")
        try:
            results = index.search(query2, use_boolean=True)
            print(f"   Found {len(results)} documents")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Save index
        print("\n4. Saving index...")
        save_path = f"indices/example_{version.replace('.', '_')}.pkl"
        os.makedirs("indices", exist_ok=True)
        index.save(save_path)
        print(f"   Saved to {save_path}")
        
        # Get metrics
        latency_stats = stats.get('latency', {})
        if latency_stats.get('query_latencies'):
            query_stats = latency_stats['query_latencies']
            print(f"\n5. Query Performance:")
            print(f"   - Mean latency: {query_stats['mean']*1000:.2f} ms")
            print(f"   - P95 latency: {query_stats['p95']*1000:.2f} ms")
            print(f"   - P99 latency: {query_stats['p99']*1000:.2f} ms")
    
    print("\n" + "=" * 80)
    print("Example completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
