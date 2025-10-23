"""
Compression utilities for postings lists.
Implements simple gap encoding and library-based compression.
"""

import zlib
import struct
from typing import List, Tuple


class SimpleCompression:
    """Simple gap encoding compression for postings lists."""
    
    @staticmethod
    def compress_postings(postings: List[Tuple]) -> bytes:
        """
        Compress postings list using gap encoding.
        
        Args:
            postings: List of postings tuples
            
        Returns:
            Compressed bytes
        """
        if not postings:
            return b''
        
        # Extract document IDs
        doc_ids = [p[0] for p in postings]
        
        # Sort by document ID
        sorted_postings = sorted(postings, key=lambda x: x[0])
        sorted_doc_ids = [p[0] for p in sorted_postings]
        
        # Gap encoding for document IDs
        gaps = [sorted_doc_ids[0]]
        for i in range(1, len(sorted_doc_ids)):
            gap = sorted_doc_ids[i] - sorted_doc_ids[i-1]
            gaps.append(gap)
        
        # Variable byte encoding
        compressed = []
        
        # Encode number of postings
        compressed.extend(SimpleCompression._vb_encode(len(postings)))
        
        # Encode gaps
        for gap in gaps:
            compressed.extend(SimpleCompression._vb_encode(gap))
        
        # Encode rest of the data (counts, positions, etc.)
        for posting in sorted_postings:
            # Skip doc_id (already encoded)
            for i in range(1, len(posting)):
                if isinstance(posting[i], (int, float)):
                    # For simple numbers, use variable byte encoding
                    if isinstance(posting[i], float):
                        # Convert float to int (multiply by 10000 to preserve precision)
                        val = int(posting[i] * 10000)
                        compressed.extend(SimpleCompression._vb_encode(val))
                        compressed.append(255)  # Float marker
                    else:
                        compressed.extend(SimpleCompression._vb_encode(posting[i]))
                elif isinstance(posting[i], list):
                    # For lists (positions), encode length and then values
                    compressed.extend(SimpleCompression._vb_encode(len(posting[i])))
                    for val in posting[i]:
                        compressed.extend(SimpleCompression._vb_encode(val))
        
        return bytes(compressed)
    
    @staticmethod
    def decompress_postings(compressed: bytes, posting_format: str = 'boolean') -> List[Tuple]:
        """
        Decompress postings list.
        
        Args:
            compressed: Compressed bytes
            posting_format: Format of postings ('boolean', 'count', 'tfidf')
            
        Returns:
            List of postings tuples
        """
        if not compressed:
            return []
        
        data = list(compressed)
        pos = 0
        
        # Decode number of postings
        num_postings, pos = SimpleCompression._vb_decode(data, pos)
        
        # Decode gaps and reconstruct doc IDs
        doc_ids = []
        current_id = 0
        
        for _ in range(num_postings):
            gap, pos = SimpleCompression._vb_decode(data, pos)
            current_id += gap
            doc_ids.append(current_id)
        
        # Decode rest of the data based on format
        postings = []
        
        if posting_format == 'boolean':
            # Format: (doc_id, positions)
            for doc_id in doc_ids:
                # Decode positions list
                list_len, pos = SimpleCompression._vb_decode(data, pos)
                positions = []
                for _ in range(list_len):
                    val, pos = SimpleCompression._vb_decode(data, pos)
                    positions.append(val)
                postings.append((doc_id, positions))
        
        elif posting_format == 'count':
            # Format: (doc_id, count, positions)
            for doc_id in doc_ids:
                count, pos = SimpleCompression._vb_decode(data, pos)
                list_len, pos = SimpleCompression._vb_decode(data, pos)
                positions = []
                for _ in range(list_len):
                    val, pos = SimpleCompression._vb_decode(data, pos)
                    positions.append(val)
                postings.append((doc_id, count, positions))
        
        elif posting_format == 'tfidf':
            # Format: (doc_id, tf, count, positions)
            for doc_id in doc_ids:
                tf_val, pos = SimpleCompression._vb_decode(data, pos)
                # Check for float marker
                if pos < len(data) and data[pos] == 255:
                    tf = tf_val / 10000.0
                    pos += 1
                else:
                    tf = float(tf_val)
                
                count, pos = SimpleCompression._vb_decode(data, pos)
                list_len, pos = SimpleCompression._vb_decode(data, pos)
                positions = []
                for _ in range(list_len):
                    val, pos = SimpleCompression._vb_decode(data, pos)
                    positions.append(val)
                postings.append((doc_id, tf, count, positions))
        
        return postings
    
    @staticmethod
    def _vb_encode(n: int) -> List[int]:
        """
        Variable byte encoding for integers.
        
        Args:
            n: Integer to encode
            
        Returns:
            List of bytes
        """
        if n == 0:
            return [128]
        
        bytes_list = []
        while n > 0:
            bytes_list.insert(0, n % 128)
            n //= 128
        
        # Set high bit on last byte
        bytes_list[-1] += 128
        
        return bytes_list
    
    @staticmethod
    def _vb_decode(data: List[int], pos: int) -> Tuple[int, int]:
        """
        Variable byte decoding.
        
        Args:
            data: Byte list
            pos: Starting position
            
        Returns:
            (decoded value, new position)
        """
        n = 0
        
        while pos < len(data):
            byte = data[pos]
            pos += 1
            
            if byte < 128:
                n = 128 * n + byte
            else:
                n = 128 * n + (byte - 128)
                break
        
        return n, pos


class LibraryCompression:
    """Library-based compression using zlib."""
    
    @staticmethod
    def compress_postings(postings: List[Tuple]) -> bytes:
        """
        Compress postings list using zlib.
        
        Args:
            postings: List of postings tuples
            
        Returns:
            Compressed bytes
        """
        if not postings:
            return b''
        
        # Convert to bytes
        data = str(postings).encode('utf-8')
        
        # Compress with zlib
        compressed = zlib.compress(data, level=9)
        
        return compressed
    
    @staticmethod
    def decompress_postings(compressed: bytes) -> List[Tuple]:
        """
        Decompress postings list using zlib.
        
        Args:
            compressed: Compressed bytes
            
        Returns:
            List of postings tuples
        """
        if not compressed:
            return []
        
        # Decompress with zlib
        data = zlib.decompress(compressed)
        
        # Convert back to list
        postings = eval(data.decode('utf-8'))
        
        return postings


class CompressionWrapper:
    """Wrapper to add compression to an inverted index."""
    
    def __init__(self, index, compression_type: int = 0):
        """
        Initialize compression wrapper.
        
        Args:
            index: InvertedIndex instance
            compression_type: 0=none, 1=simple, 2=library
        """
        self.index = index
        self.compression_type = compression_type
        self.compressed_index = {}
    
    def compress(self):
        """Compress all postings lists."""
        if self.compression_type == 0:
            # No compression
            return
        
        for term, postings in self.index.index.items():
            if self.compression_type == 1:
                # Simple compression
                if self.index.index_type == 1:
                    compressed = SimpleCompression.compress_postings(postings)
                elif self.index.index_type == 2:
                    compressed = SimpleCompression.compress_postings(postings)
                else:
                    compressed = SimpleCompression.compress_postings(postings)
            else:
                # Library compression
                compressed = LibraryCompression.compress_postings(postings)
            
            self.compressed_index[term] = compressed
    
    def get_postings(self, term: str) -> List[Tuple]:
        """
        Get decompressed postings for a term.
        
        Args:
            term: Search term
            
        Returns:
            List of postings
        """
        if self.compression_type == 0:
            return self.index.get_postings(term)
        
        if term not in self.compressed_index:
            return []
        
        compressed = self.compressed_index[term]
        
        if self.compression_type == 1:
            # Simple decompression
            if self.index.index_type == 1:
                return SimpleCompression.decompress_postings(compressed, 'boolean')
            elif self.index.index_type == 2:
                return SimpleCompression.decompress_postings(compressed, 'count')
            else:
                return SimpleCompression.decompress_postings(compressed, 'tfidf')
        else:
            # Library decompression
            return LibraryCompression.decompress_postings(compressed)
    
    def get_compression_ratio(self) -> float:
        """
        Calculate compression ratio.
        
        Returns:
            Compression ratio (original size / compressed size)
        """
        if self.compression_type == 0:
            return 1.0
        
        original_size = sum(len(str(postings)) for postings in self.index.index.values())
        compressed_size = sum(len(compressed) for compressed in self.compressed_index.values())
        
        if compressed_size == 0:
            return 0.0
        
        return original_size / compressed_size
