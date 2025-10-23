# SelfIndex Usage Guide

This guide provides detailed instructions on using the SelfIndex system.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Index Versions](#index-versions)
3. [Creating and Using Indexes](#creating-and-using-indexes)
4. [Query Types](#query-types)
5. [Performance Metrics](#performance-metrics)
6. [Data Loading](#data-loading)
7. [Advanced Features](#advanced-features)

## Quick Start

### Basic Example

```python
from src import SelfIndex

# Create a TF-IDF index
index = SelfIndex(version="3.1000")

# Add documents
documents = [
    "Python is a programming language",
    "Machine learning uses Python",
    "Data science involves programming"
]

for doc in documents:
    index.add_document(doc)

# Finalize (compute TF-IDF, etc.)
index.finalize()

# Search
results = index.search("python programming", top_k=5)
print(results)

# Save for later use
index.save("indices/my_index.pkl")
```

## Index Versions

The version string follows the format: `x.yziq`

### Components

- **x (Index Type)**:
  - `1`: Boolean index (document IDs and positions)
  - `2`: Word count index (with term frequencies)
  - `3`: TF-IDF index (with TF-IDF scoring)

- **y (Datastore)**:
  - `1`: Pickle/JSON (local files)
  - `2`: PostgreSQL with GIN index
  - `3`: RocksDB
  - `4`: Redis

- **z (Compression)**:
  - `0`: No compression
  - `1`: Simple gap encoding + variable byte encoding
  - `2`: Library-based compression (zlib)

- **i (Optimization)**:
  - `0`: No optimization
  - `1`: With skipping pointers

- **q (Query Processing)**:
  - `0`: Basic query processing
  - `1`: Term-at-a-Time (TAAT)
  - `2`: Document-at-a-Time (DAAT)

### Example Versions

- `1.1000`: Boolean index, pickle storage, no compression, basic queries
- `3.1112`: TF-IDF, pickle, simple compression, skipping pointers, DAAT
- `3.2001`: TF-IDF, PostgreSQL, no compression, no optimization, TAAT
- `2.3200`: Word count, RocksDB, library compression, no optimization, DAAT

## Creating and Using Indexes

### Different Index Types

#### Boolean Index (x=1)

```python
index = SelfIndex(version="1.1000")
# Good for: presence/absence queries, boolean operations
# Stores: document IDs and term positions
```

#### Word Count Index (x=2)

```python
index = SelfIndex(version="2.1000")
# Good for: basic ranking by term frequency
# Stores: document IDs, term counts, positions
```

#### TF-IDF Index (x=3)

```python
index = SelfIndex(version="3.1000")
# Good for: relevance-based ranking
# Stores: document IDs, TF scores, counts, positions
# Best for: most search applications
```

### Using Different Datastores

#### Pickle Storage (y=1)

```python
index = SelfIndex(version="3.1000")
# Pros: Simple, fast for small datasets, portable
# Cons: Memory-intensive, no concurrent access
```

#### PostgreSQL (y=2)

```python
index = SelfIndex(
    version="3.2000",
    connection_params={
        'host': 'localhost',
        'database': 'inverted_index',
        'user': 'postgres',
        'password': 'your_password'
    }
)
# Pros: Scalable, supports concurrent access, ACID guarantees
# Cons: Requires PostgreSQL server, more setup
```

#### RocksDB (y=3)

```python
index = SelfIndex(
    version="3.3000",
    db_path="indices/my_rocksdb"
)
# Pros: Fast, embedded, good for large datasets
# Cons: Requires RocksDB library, more complex
```

#### Redis (y=4)

```python
index = SelfIndex(
    version="3.4000",
    redis_params={
        'host': 'localhost',
        'port': 6379,
        'db': 0
    }
)
# Pros: Fast, in-memory, supports distributed setup
# Cons: Requires Redis server, data in RAM
```

### Compression

#### No Compression (z=0)

```python
index = SelfIndex(version="3.1000")
# Fastest access, largest storage
```

#### Simple Compression (z=1)

```python
index = SelfIndex(version="3.1100")
# Gap encoding + variable byte encoding
# Good compression ratio with fast decompression
```

#### Library Compression (z=2)

```python
index = SelfIndex(version="3.1200")
# Uses zlib for maximum compression
# Best compression ratio, slower access
```

## Query Types

### Ranked Queries (Default)

Used when no boolean operators are present:

```python
results = index.search("machine learning", top_k=10)
# Returns: [(doc_id, score), (doc_id, score), ...]
```

### Boolean Queries

Use boolean operators for precise matching:

```python
# AND - both terms must be present
results = index.search('"machine" AND "learning"', use_boolean=True)

# OR - either term must be present
results = index.search('"python" OR "java"', use_boolean=True)

# NOT - term must not be present
results = index.search('"programming" AND NOT "java"', use_boolean=True)

# PHRASE - terms must appear in sequence
results = index.search('PHRASE "machine learning"', use_boolean=True)

# Complex queries with parentheses
results = index.search(
    '("machine learning" OR "data science") AND "python"',
    use_boolean=True
)
```

### Operator Precedence

From highest to lowest:
1. PHRASE
2. NOT
3. AND
4. OR

Example: `"a" OR "b" AND "c"` is parsed as `"a" OR ("b" AND "c")`

## Performance Metrics

### Collecting Metrics

```python
index = SelfIndex(version="3.1000")

# Add documents and search...
for doc in documents:
    index.add_document(doc)

index.finalize()

# Run queries
for query in test_queries:
    results = index.search(query, top_k=10)

# Get statistics
stats = index.get_statistics()

# Access latency metrics
latency = stats['latency']
print(f"Mean query time: {latency['query_latencies']['mean']*1000:.2f}ms")
print(f"P95 query time: {latency['query_latencies']['p95']*1000:.2f}ms")
print(f"P99 query time: {latency['query_latencies']['p99']*1000:.2f}ms")

# Memory metrics
memory = stats['memory']
print(f"Max memory: {memory['max_memory_mb']:.2f}MB")
```

### Comparing Versions

```python
versions = ["1.1000", "2.1000", "3.1000", "3.1001", "3.1002"]

results = {}
for version in versions:
    index = SelfIndex(version=version)
    
    # Index documents
    for doc in documents:
        index.add_document(doc)
    index.finalize()
    
    # Test queries
    for query in test_queries:
        index.search(query, top_k=10)
    
    # Collect stats
    results[version] = index.get_statistics()
```

## Data Loading

### Using Sample Data

```python
from src.utils.data_loader import DatasetManager

manager = DatasetManager()

# Get mixed sample data
documents = manager.get_mixed_dataset(news_count=50, wiki_count=50)

# Index the data
index = SelfIndex(version="3.1000")
for doc in documents:
    index.add_document(doc)
index.finalize()
```

### Loading News Data

```python
from src.utils.data_loader import NewsDataLoader

loader = NewsDataLoader(data_path="data/news.jsonl")
docs = loader.load_from_file(limit=1000)

texts = [loader.extract_text(doc) for doc in docs]
```

### Loading Wikipedia Data

```python
from src.utils.data_loader import WikiDataLoader

loader = WikiDataLoader(split="20231101.en")
texts = loader.load(limit=1000)
```

## Advanced Features

### Custom Preprocessing

```python
from src.preprocessing import TextPreprocessor

# Custom preprocessing options
preprocessor = TextPreprocessor(
    use_stemming=False,  # Don't stem
    remove_stopwords=False,  # Keep stopwords
    lowercase=True  # Convert to lowercase
)

# Use with index
index = SelfIndex(version="3.1000")
# Note: SelfIndex creates its own preprocessor
# To use custom preprocessing, preprocess documents before adding:
for doc in documents:
    terms = preprocessor.preprocess(doc)
    preprocessed_text = ' '.join(terms)
    index.add_document(preprocessed_text)
```

### Functional Metrics

```python
from src.metrics import FunctionalMetrics

# For evaluation
retrieved_docs = {1, 2, 3, 4, 5}  # Retrieved by query
relevant_docs = {2, 3, 6, 7}  # Actually relevant

# Calculate metrics
precision = FunctionalMetrics.precision(retrieved_docs, relevant_docs)
recall = FunctionalMetrics.recall(retrieved_docs, relevant_docs)
f1 = FunctionalMetrics.f1_score(retrieved_docs, relevant_docs)

print(f"Precision: {precision:.2f}")
print(f"Recall: {recall:.2f}")
print(f"F1: {f1:.2f}")

# For ranked results
ranked_results = [1, 2, 3, 4, 5]
avg_precision = FunctionalMetrics.average_precision(ranked_results, relevant_docs)
print(f"Average Precision: {avg_precision:.2f}")
```

### Query Processing Modes

#### Term-at-a-Time (TAAT)

```python
index = SelfIndex(version="3.1001")
# Processes one term at a time, accumulating scores
# Pros: Simple, memory-efficient
# Cons: May be slower for long queries
```

#### Document-at-a-Time (DAAT)

```python
index = SelfIndex(version="3.1002")
# Processes one document at a time across all terms
# Pros: Faster for short queries, better cache locality
# Cons: Requires more memory for posting lists
```

#### With Optimization

```python
index = SelfIndex(version="3.1011")
# Adds skipping pointers for faster intersection
# Pros: Much faster for large indexes
# Cons: Slightly more memory
```

### Persistence and Loading

```python
# Save index
index.save("indices/my_index.pkl")

# Load later
loaded_index = SelfIndex(version="3.1000")
loaded_index.load("indices/my_index.pkl")

# Continue using
results = loaded_index.search("query", top_k=10)
```

## Best Practices

1. **Choose the right index type**:
   - Use Boolean (x=1) for exact matching only
   - Use TF-IDF (x=3) for most relevance-based search

2. **Finalize after adding all documents**:
   ```python
   for doc in documents:
       index.add_document(doc)
   index.finalize()  # Important!
   ```

3. **Use appropriate datastore**:
   - Pickle for small datasets (<10k docs)
   - PostgreSQL for scalability and concurrency
   - RocksDB for large datasets with single process

4. **Enable compression for large datasets**:
   - Use simple compression (z=1) for good balance
   - Use library compression (z=2) for maximum space savings

5. **Use TAAT (q=1) for long queries, DAAT (q=2) for short queries**

6. **Enable optimization (i=1) for large indexes**

## Troubleshooting

### Import Errors

Make sure you're in the project root and have installed dependencies:
```bash
pip install -r requirements.txt
```

### Database Connection Errors

For PostgreSQL/Redis, ensure the server is running and credentials are correct.

### Memory Issues

For large datasets:
- Use compression (z=1 or z=2)
- Use database storage (y=2, y=3, or y=4) instead of pickle
- Process in batches

### Slow Queries

- Enable optimization (i=1)
- Use appropriate query processor (q=1 or q=2)
- Consider using compression (may improve I/O)

## Examples

See the `examples/` directory for complete working examples:

- `basic_usage.py`: Introduction to SelfIndex
- `test_versions.py`: Comprehensive version comparison

Run examples:
```bash
python3 examples/basic_usage.py
python3 examples/test_versions.py
```

## Testing

Run all tests:
```bash
python3 run_tests.py
```

Run specific test modules:
```bash
python3 -m unittest tests.test_preprocessing
python3 -m unittest tests.test_index
python3 -m unittest tests.test_query
```
