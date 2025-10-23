"""
Database-based datastore implementations (PostgreSQL, RocksDB, Redis).
"""

import json
import pickle
from typing import Any, Dict, List
from ..index.base import InvertedIndex


try:
    import psycopg2
    from psycopg2.extras import Json
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False


try:
    import rocksdb
    ROCKSDB_AVAILABLE = True
except ImportError:
    ROCKSDB_AVAILABLE = False


try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class PostgreSQLDatastore(InvertedIndex):
    """Inverted index using PostgreSQL with GIN index."""
    
    def __init__(self, version: str = "1.2000", connection_params: Dict[str, str] = None):
        """
        Initialize PostgreSQL datastore.
        
        Args:
            version: Version string
            connection_params: PostgreSQL connection parameters
        """
        if not PSYCOPG2_AVAILABLE:
            raise ImportError("psycopg2 is required for PostgreSQL datastore")
        
        super().__init__(version)
        
        # Default connection parameters
        self.connection_params = connection_params or {
            'host': 'localhost',
            'database': 'inverted_index',
            'user': 'postgres',
            'password': 'postgres'
        }
        
        self.conn = None
        self.table_name = f"index_{version.replace('.', '_')}"
    
    def _connect(self):
        """Establish database connection."""
        if self.conn is None or self.conn.closed:
            self.conn = psycopg2.connect(**self.connection_params)
    
    def _create_tables(self):
        """Create necessary tables with GIN index."""
        self._connect()
        cursor = self.conn.cursor()
        
        # Create main index table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                term VARCHAR(255) PRIMARY KEY,
                postings JSONB
            )
        """)
        
        # Create GIN index on postings
        cursor.execute(f"""
            CREATE INDEX IF NOT EXISTS {self.table_name}_gin_idx 
            ON {self.table_name} USING GIN (postings)
        """)
        
        # Create metadata table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.table_name}_meta (
                key VARCHAR(255) PRIMARY KEY,
                value JSONB
            )
        """)
        
        self.conn.commit()
        cursor.close()
    
    def save(self, path: str = None):
        """
        Save index to PostgreSQL database.
        
        Args:
            path: Not used (for interface compatibility)
        """
        self._create_tables()
        cursor = self.conn.cursor()
        
        # Clear existing data
        cursor.execute(f"DELETE FROM {self.table_name}")
        cursor.execute(f"DELETE FROM {self.table_name}_meta")
        
        # Insert index data
        for term, postings in self.index.items():
            postings_json = json.dumps([list(p) for p in postings])
            cursor.execute(
                f"INSERT INTO {self.table_name} (term, postings) VALUES (%s, %s)",
                (term, postings_json)
            )
        
        # Insert metadata
        metadata = {
            'version': self.version,
            'document_count': self.document_count,
            'documents': {str(k): v for k, v in self.documents.items()},
            'doc_lengths': {str(k): v for k, v in self.doc_lengths.items()},
            'avg_doc_length': self.avg_doc_length,
            'idf_values': getattr(self, 'idf_values', {})
        }
        
        for key, value in metadata.items():
            cursor.execute(
                f"INSERT INTO {self.table_name}_meta (key, value) VALUES (%s, %s)",
                (key, json.dumps(value))
            )
        
        self.conn.commit()
        cursor.close()
    
    def load(self, path: str = None):
        """
        Load index from PostgreSQL database.
        
        Args:
            path: Not used (for interface compatibility)
        """
        self._connect()
        cursor = self.conn.cursor()
        
        # Load metadata
        cursor.execute(f"SELECT key, value FROM {self.table_name}_meta")
        metadata = {row[0]: json.loads(row[1]) for row in cursor.fetchall()}
        
        self.version = metadata['version']
        self.document_count = metadata['document_count']
        self.documents = {int(k): v for k, v in metadata['documents'].items()}
        self.doc_lengths = {int(k): v for k, v in metadata['doc_lengths'].items()}
        self.avg_doc_length = metadata['avg_doc_length']
        
        if 'idf_values' in metadata:
            self.idf_values = metadata['idf_values']
        
        # Load index data
        cursor.execute(f"SELECT term, postings FROM {self.table_name}")
        self.index = {}
        for term, postings_json in cursor.fetchall():
            postings = json.loads(postings_json)
            self.index[term] = [tuple(p) for p in postings]
        
        cursor.close()
    
    def get_postings(self, term: str) -> List[Any]:
        """Get postings for a term from database."""
        if term in self.index:
            return self.index[term]
        
        self._connect()
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT postings FROM {self.table_name} WHERE term = %s",
            (term,)
        )
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            postings = json.loads(result[0])
            return [tuple(p) for p in postings]
        
        return []


class RocksDBDatastore(InvertedIndex):
    """Inverted index using RocksDB."""
    
    def __init__(self, version: str = "1.3000", db_path: str = None):
        """
        Initialize RocksDB datastore.
        
        Args:
            version: Version string
            db_path: Path to RocksDB database
        """
        if not ROCKSDB_AVAILABLE:
            raise ImportError("python-rocksdb is required for RocksDB datastore")
        
        super().__init__(version)
        
        self.db_path = db_path or f"indices/rocksdb_{version.replace('.', '_')}"
        self.db = None
    
    def _open_db(self):
        """Open RocksDB database."""
        if self.db is None:
            opts = rocksdb.Options()
            opts.create_if_missing = True
            opts.max_open_files = 300000
            opts.write_buffer_size = 67108864
            opts.max_write_buffer_number = 3
            opts.target_file_size_base = 67108864
            
            self.db = rocksdb.DB(self.db_path, opts)
    
    def save(self, path: str = None):
        """
        Save index to RocksDB.
        
        Args:
            path: Custom database path (optional)
        """
        if path:
            self.db_path = path
        
        self._open_db()
        
        # Write index data
        for term, postings in self.index.items():
            key = f"term:{term}".encode('utf-8')
            value = pickle.dumps(postings)
            self.db.put(key, value)
        
        # Write metadata
        metadata = {
            'version': self.version,
            'document_count': self.document_count,
            'documents': self.documents,
            'doc_lengths': self.doc_lengths,
            'avg_doc_length': self.avg_doc_length,
            'idf_values': getattr(self, 'idf_values', {})
        }
        
        self.db.put(b'meta:data', pickle.dumps(metadata))
    
    def load(self, path: str = None):
        """
        Load index from RocksDB.
        
        Args:
            path: Custom database path (optional)
        """
        if path:
            self.db_path = path
        
        self._open_db()
        
        # Load metadata
        meta_data = self.db.get(b'meta:data')
        if meta_data:
            metadata = pickle.loads(meta_data)
            self.version = metadata['version']
            self.document_count = metadata['document_count']
            self.documents = metadata['documents']
            self.doc_lengths = metadata['doc_lengths']
            self.avg_doc_length = metadata['avg_doc_length']
            
            if 'idf_values' in metadata:
                self.idf_values = metadata['idf_values']
        
        # Load index data
        self.index = {}
        it = self.db.iteritems()
        it.seek_to_first()
        
        for key, value in it:
            key_str = key.decode('utf-8')
            if key_str.startswith('term:'):
                term = key_str[5:]
                postings = pickle.loads(value)
                self.index[term] = postings
    
    def get_postings(self, term: str) -> List[Any]:
        """Get postings for a term from RocksDB."""
        if term in self.index:
            return self.index[term]
        
        self._open_db()
        key = f"term:{term}".encode('utf-8')
        value = self.db.get(key)
        
        if value:
            return pickle.loads(value)
        
        return []


class RedisDatastore(InvertedIndex):
    """Inverted index using Redis."""
    
    def __init__(self, version: str = "1.4000", redis_params: Dict[str, Any] = None):
        """
        Initialize Redis datastore.
        
        Args:
            version: Version string
            redis_params: Redis connection parameters
        """
        if not REDIS_AVAILABLE:
            raise ImportError("redis is required for Redis datastore")
        
        super().__init__(version)
        
        # Default Redis parameters
        self.redis_params = redis_params or {
            'host': 'localhost',
            'port': 6379,
            'db': 0
        }
        
        self.redis_client = None
        self.key_prefix = f"index_{version.replace('.', '_')}"
    
    def _connect(self):
        """Connect to Redis."""
        if self.redis_client is None:
            self.redis_client = redis.Redis(**self.redis_params)
    
    def save(self, path: str = None):
        """
        Save index to Redis.
        
        Args:
            path: Not used (for interface compatibility)
        """
        self._connect()
        
        # Clear existing data
        pattern = f"{self.key_prefix}:*"
        for key in self.redis_client.scan_iter(pattern):
            self.redis_client.delete(key)
        
        # Write index data
        for term, postings in self.index.items():
            key = f"{self.key_prefix}:term:{term}"
            value = pickle.dumps(postings)
            self.redis_client.set(key, value)
        
        # Write metadata
        metadata = {
            'version': self.version,
            'document_count': self.document_count,
            'documents': self.documents,
            'doc_lengths': self.doc_lengths,
            'avg_doc_length': self.avg_doc_length,
            'idf_values': getattr(self, 'idf_values', {})
        }
        
        meta_key = f"{self.key_prefix}:meta"
        self.redis_client.set(meta_key, pickle.dumps(metadata))
    
    def load(self, path: str = None):
        """
        Load index from Redis.
        
        Args:
            path: Not used (for interface compatibility)
        """
        self._connect()
        
        # Load metadata
        meta_key = f"{self.key_prefix}:meta"
        meta_data = self.redis_client.get(meta_key)
        
        if meta_data:
            metadata = pickle.loads(meta_data)
            self.version = metadata['version']
            self.document_count = metadata['document_count']
            self.documents = metadata['documents']
            self.doc_lengths = metadata['doc_lengths']
            self.avg_doc_length = metadata['avg_doc_length']
            
            if 'idf_values' in metadata:
                self.idf_values = metadata['idf_values']
        
        # Load index data
        self.index = {}
        pattern = f"{self.key_prefix}:term:*"
        
        for key in self.redis_client.scan_iter(pattern):
            key_str = key.decode('utf-8')
            term = key_str.split(':')[-1]
            value = self.redis_client.get(key)
            
            if value:
                postings = pickle.loads(value)
                self.index[term] = postings
    
    def get_postings(self, term: str) -> List[Any]:
        """Get postings for a term from Redis."""
        if term in self.index:
            return self.index[term]
        
        self._connect()
        key = f"{self.key_prefix}:term:{term}"
        value = self.redis_client.get(key)
        
        if value:
            return pickle.loads(value)
        
        return []
