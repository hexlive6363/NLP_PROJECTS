"""
Factory for creating indexes with different version specifications.
"""

from typing import Optional, Dict, Any
from ..datastore.local_storage import PickleDatastore, JSONDatastore
from ..datastore.db_storage import PostgreSQLDatastore, RocksDBDatastore, RedisDatastore


class IndexFactory:
    """Factory for creating inverted index instances based on version string."""
    
    @staticmethod
    def create_index(version: str = "1.1000", **kwargs) -> Any:
        """
        Create an index based on version specification.
        
        Version format: x.yziq
        - x: Index type (1=boolean, 2=count, 3=TF-IDF)
        - y: Datastore (1=pickle, 2=PostgreSQL, 3=RocksDB, 4=Redis)
        - z: Compression (0=none, 1=simple, 2=library)
        - i: Optimization (0=no skipping, 1=with skipping)
        - q: Query type (0=basic, 1=TAAT, 2=DAAT)
        
        Args:
            version: Version string
            **kwargs: Additional arguments for specific datastores
            
        Returns:
            InvertedIndex instance
        """
        # Parse version
        parts = version.split('.')
        index_type = int(parts[0]) if len(parts) > 0 else 1
        
        datastore_type = 1
        if len(parts) > 1 and len(parts[1]) >= 1:
            datastore_type = int(parts[1][0])
        
        # Create index based on datastore type
        if datastore_type == 1:
            # Pickle datastore
            return PickleDatastore(version)
        elif datastore_type == 2:
            # PostgreSQL datastore
            connection_params = kwargs.get('connection_params', None)
            return PostgreSQLDatastore(version, connection_params)
        elif datastore_type == 3:
            # RocksDB datastore
            db_path = kwargs.get('db_path', None)
            return RocksDBDatastore(version, db_path)
        elif datastore_type == 4:
            # Redis datastore
            redis_params = kwargs.get('redis_params', None)
            return RedisDatastore(version, redis_params)
        else:
            # Default to pickle
            return PickleDatastore(version)
    
    @staticmethod
    def parse_version(version: str) -> Dict[str, int]:
        """
        Parse version string into components.
        
        Args:
            version: Version string
            
        Returns:
            Dictionary with version components
        """
        parts = version.split('.')
        
        result = {
            'index_type': int(parts[0]) if len(parts) > 0 else 1,
            'datastore_type': 1,
            'compression_type': 0,
            'optimization_type': 0,
            'query_type': 0
        }
        
        if len(parts) > 1:
            version_code = parts[1]
            if len(version_code) >= 1:
                result['datastore_type'] = int(version_code[0])
            if len(version_code) >= 2:
                result['compression_type'] = int(version_code[1])
            if len(version_code) >= 3:
                result['optimization_type'] = int(version_code[2])
            if len(version_code) >= 4:
                result['query_type'] = int(version_code[3])
        
        return result
    
    @staticmethod
    def get_version_description(version: str) -> str:
        """
        Get human-readable description of version.
        
        Args:
            version: Version string
            
        Returns:
            Description string
        """
        parsed = IndexFactory.parse_version(version)
        
        index_types = {
            1: "Boolean index",
            2: "Word count index",
            3: "TF-IDF index"
        }
        
        datastore_types = {
            1: "Pickle/JSON",
            2: "PostgreSQL",
            3: "RocksDB",
            4: "Redis"
        }
        
        compression_types = {
            0: "No compression",
            1: "Simple compression",
            2: "Library compression"
        }
        
        optimization_types = {
            0: "No optimization",
            1: "With skipping pointers"
        }
        
        query_types = {
            0: "Basic query",
            1: "Term-at-a-time",
            2: "Document-at-a-time"
        }
        
        desc = f"Version {version}:\n"
        desc += f"  Index: {index_types.get(parsed['index_type'], 'Unknown')}\n"
        desc += f"  Datastore: {datastore_types.get(parsed['datastore_type'], 'Unknown')}\n"
        desc += f"  Compression: {compression_types.get(parsed['compression_type'], 'Unknown')}\n"
        desc += f"  Optimization: {optimization_types.get(parsed['optimization_type'], 'Unknown')}\n"
        desc += f"  Query: {query_types.get(parsed['query_type'], 'Unknown')}\n"
        
        return desc
