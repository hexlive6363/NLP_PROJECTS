# NLP_PROJECTS - SelfIndex Implementation

A custom inverted index implementation (SelfIndex-v1.0) with support for multiple index types, datastores, compression methods, and query processing engines.

## Project Structure

```
NLP_PROJECTS/
├── src/
│   ├── index/          # Index implementations
│   ├── datastore/      # Storage backends (pickle, PostgreSQL, RocksDB, Redis)
│   ├── query/          # Query processors (Boolean, TAAT, DAAT)
│   ├── preprocessing/  # Text preprocessing utilities
│   ├── metrics/        # Performance metrics collection
│   └── utils/          # Utilities (compression, data loading)
├── examples/           # Example scripts
├── tests/             # Unit tests
├── data/              # Data files (not in repo)
├── indices/           # Saved indices (not in repo)
└── plots/             # Generated plots (not in repo)
```

## Features

### Index Types (x parameter)
- **x=1**: Boolean index with document IDs and position IDs
- **x=2**: Word count-based ranking index
- **x=3**: TF-IDF scoring index

### Datastore Options (y parameter)
- **y=1**: Pickle/JSON (local storage)
- **y=2**: PostgreSQL with GIN index
- **y=3**: RocksDB
- **y=4**: Redis

### Compression Methods (z parameter)
- **z=0**: No compression
- **z=1**: Simple gap encoding with variable byte encoding
- **z=2**: Library-based compression (zlib)

### Query Processing (q parameter)
- **q=0**: Basic query processing
- **q=1**: Term-at-a-Time (TAAT)
- **q=2**: Document-at-a-Time (DAAT)

### Optimization (i parameter)
- **i=0**: No optimization
- **i=1**: With skipping pointers

## Version Format

Versions follow the format: `x.yziq`

Example: `3.1112` means:
- x=3: TF-IDF index
- y=1: Pickle storage
- z=1: Simple compression
- i=1: With skipping pointers
- q=2: DAAT query processing

## Installation

```bash
# Clone the repository
git clone https://github.com/hexlive6363/NLP_PROJECTS.git
cd NLP_PROJECTS

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
```

## Quick Start

### Basic Usage

```python
from src import SelfIndex

# Create a TF-IDF index with pickle storage
index = SelfIndex(version="3.1000")

# Add documents
documents = [
    "Python is a high-level programming language.",
    "Machine learning is a subset of artificial intelligence.",
    "Natural language processing deals with text analysis."
]

for doc in documents:
    index.add_document(doc)

# Finalize the index
index.finalize()

# Search
results = index.search("machine learning", top_k=5)
print(results)

# Boolean query
results = index.search('"machine learning" AND "artificial"', use_boolean=True)
print(results)

# Save index
index.save("indices/my_index.pkl")

# Load index
index.load("indices/my_index.pkl")
```

### Running Examples

```bash
# Basic usage example
python examples/basic_usage.py

# Version comparison test
python examples/test_versions.py
```

## Boolean Query Syntax

Supports the following operators:

- **AND**: Both terms must be present
- **OR**: Either term must be present
- **NOT**: Term must not be present
- **PHRASE**: Terms must appear in sequence
- **()**: Grouping with parentheses

**Operator Precedence** (highest to lowest):
1. PHRASE
2. NOT
3. AND
4. OR

**Example Queries**:
```
"machine learning"
"Python" AND "programming"
("data science" OR "machine learning") AND NOT "statistics"
PHRASE "artificial intelligence"
```

## Performance Metrics

The system automatically collects:

1. **Latency Metrics**: p95, p99 percentiles for query and index operations
2. **Throughput**: Queries per second
3. **Memory Footprint**: RAM usage during operations
4. **Functional Metrics**: Precision, recall, F1, MAP, NDCG, MRR

Example:
```python
stats = index.get_statistics()
print(stats['latency'])
print(stats['memory'])
```

## Data Sources

The system supports:

1. **News Data**: From webz.io (load from JSON/JSONL files)
2. **Wiki Data**: From HuggingFace datasets (20231101.en split)

```python
from src.utils.data_loader import DatasetManager

manager = DatasetManager()

# Load news data
news_texts = manager.load_dataset('news', limit=100)

# Load wiki data
wiki_texts = manager.load_dataset('wiki', limit=100)

# Load mixed dataset
mixed_texts = manager.get_mixed_dataset(news_count=50, wiki_count=50)
```

## Testing

```bash
# Run all tests (when implemented)
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_index.py
```

## Advanced Features

### Compression

```python
# Create index with simple compression
index = SelfIndex(version="3.1100")

# Create index with library compression
index = SelfIndex(version="3.1200")

# Check compression ratio
stats = index.get_statistics()
print(f"Compression ratio: {stats.get('compression_ratio', 1.0)}")
```

### Query Processing Modes

```python
# Term-at-a-Time
index_taat = SelfIndex(version="3.1001")

# Document-at-a-Time
index_daat = SelfIndex(version="3.1002")

# With optimization
index_optimized = SelfIndex(version="3.1011")
```

### Database Backends

```python
# PostgreSQL
index_pg = SelfIndex(
    version="3.2000",
    connection_params={
        'host': 'localhost',
        'database': 'inverted_index',
        'user': 'postgres',
        'password': 'postgres'
    }
)

# RocksDB
index_rocks = SelfIndex(version="3.3000", db_path="indices/rocksdb_index")

# Redis
index_redis = SelfIndex(
    version="3.4000",
    redis_params={'host': 'localhost', 'port': 6379, 'db': 0}
)
```

## Contributing

This is an educational project for understanding information retrieval systems.

## License

MIT License

## Assignment Context

This implementation fulfills the requirements for the Information Retrieval course assignment, specifically:

- ✅ Text preprocessing with stemming and stopword removal
- ✅ Custom inverted index implementation (SelfIndex-v1.0)
- ✅ Multiple index types (Boolean, Word Count, TF-IDF)
- ✅ Multiple datastore options (Pickle, PostgreSQL, RocksDB, Redis)
- ✅ Compression methods (simple and library-based)
- ✅ Query processing engines (TAAT and DAAT)
- ✅ Boolean query support (AND, OR, NOT, PHRASE operators)
- ✅ Performance metrics collection (latency, throughput, memory)
- ✅ Index persistence and loading
- ✅ Support for news and wiki datasets