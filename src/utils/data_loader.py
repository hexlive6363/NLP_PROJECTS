"""
Data loading utilities for news and wiki datasets.
"""

import os
import json
import requests
from typing import List, Dict, Any, Iterator

try:
    from datasets import load_dataset
    DATASETS_AVAILABLE = True
except ImportError:
    DATASETS_AVAILABLE = False


class NewsDataLoader:
    """Loader for news data from webz.io."""
    
    def __init__(self, data_path: str = None):
        """
        Initialize news data loader.
        
        Args:
            data_path: Path to local news data file (JSON)
        """
        self.data_path = data_path
    
    def load_from_file(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        Load news data from local file.
        
        Args:
            limit: Maximum number of documents to load
            
        Returns:
            List of news documents
        """
        if not self.data_path or not os.path.exists(self.data_path):
            raise FileNotFoundError(f"News data file not found: {self.data_path}")
        
        documents = []
        
        with open(self.data_path, 'r', encoding='utf-8') as f:
            if self.data_path.endswith('.jsonl'):
                # JSONL format
                for i, line in enumerate(f):
                    if limit and i >= limit:
                        break
                    
                    try:
                        doc = json.loads(line)
                        documents.append(doc)
                    except json.JSONDecodeError:
                        continue
            else:
                # Regular JSON format
                data = json.load(f)
                
                if isinstance(data, list):
                    documents = data[:limit] if limit else data
                elif isinstance(data, dict):
                    # Extract articles if in specific format
                    if 'posts' in data:
                        documents = data['posts'][:limit] if limit else data['posts']
                    elif 'articles' in data:
                        documents = data['articles'][:limit] if limit else data['articles']
        
        return documents
    
    def extract_text(self, document: Dict[str, Any]) -> str:
        """
        Extract text from a news document.
        
        Args:
            document: News document dictionary
            
        Returns:
            Extracted text
        """
        # Try different field names
        text_fields = ['text', 'content', 'body', 'article', 'description', 'title']
        
        text_parts = []
        
        for field in text_fields:
            if field in document and document[field]:
                text_parts.append(str(document[field]))
        
        return ' '.join(text_parts)
    
    def load_sample_news(self, count: int = 100) -> List[str]:
        """
        Load sample news texts.
        
        Args:
            count: Number of sample documents
            
        Returns:
            List of text strings
        """
        # Sample news texts if no file is provided
        sample_texts = [
            "The global economy is showing signs of recovery as markets stabilize after recent turbulence.",
            "Tech giant announces breakthrough in artificial intelligence research with new language model.",
            "Scientists discover potential treatment for rare disease affecting thousands worldwide.",
            "International summit brings together leaders to discuss climate change mitigation strategies.",
            "Local community celebrates opening of new library and educational resource center.",
            "Sports team advances to championship finals after dramatic overtime victory.",
            "New study reveals surprising benefits of regular exercise for mental health.",
            "Government announces plans for infrastructure investment to boost economic growth.",
            "Researchers develop innovative method for clean energy production from renewable sources.",
            "Cultural festival attracts thousands of visitors showcasing diverse traditions and art."
        ]
        
        # Repeat to reach desired count
        texts = (sample_texts * ((count // len(sample_texts)) + 1))[:count]
        
        return texts


class WikiDataLoader:
    """Loader for Wikipedia data from HuggingFace."""
    
    def __init__(self, split: str = "20231101.en", cache_dir: str = None):
        """
        Initialize wiki data loader.
        
        Args:
            split: Dataset split to load
            cache_dir: Cache directory for downloaded data
        """
        self.split = split
        self.cache_dir = cache_dir
    
    def load(self, limit: int = None) -> List[str]:
        """
        Load Wikipedia data from HuggingFace.
        
        Args:
            limit: Maximum number of documents to load
            
        Returns:
            List of text strings
        """
        if not DATASETS_AVAILABLE:
            print("Warning: datasets library not available. Using sample data.")
            return self.load_sample_wiki(limit or 100)
        
        try:
            # Load dataset
            dataset = load_dataset(
                "wikimedia/wikipedia",
                self.split,
                cache_dir=self.cache_dir,
                split="train",
                streaming=limit is not None  # Use streaming for limited load
            )
            
            texts = []
            
            if limit:
                # Streaming mode
                for i, example in enumerate(dataset):
                    if i >= limit:
                        break
                    texts.append(example['text'])
            else:
                # Load all
                texts = [example['text'] for example in dataset]
            
            return texts
        
        except Exception as e:
            print(f"Error loading Wikipedia data: {e}")
            print("Falling back to sample data...")
            return self.load_sample_wiki(limit or 100)
    
    def load_sample_wiki(self, count: int = 100) -> List[str]:
        """
        Load sample Wikipedia-like texts.
        
        Args:
            count: Number of sample documents
            
        Returns:
            List of text strings
        """
        sample_texts = [
            "Python is a high-level, interpreted programming language known for its simplicity and readability.",
            "Machine learning is a subset of artificial intelligence that enables systems to learn from data.",
            "Natural language processing involves the interaction between computers and human language.",
            "Data structures are ways of organizing and storing data for efficient access and modification.",
            "Algorithms are step-by-step procedures for solving computational problems.",
            "Database systems provide efficient storage and retrieval of structured information.",
            "Web development encompasses frontend and backend technologies for building websites.",
            "Cloud computing delivers computing services over the internet on demand.",
            "Cybersecurity protects systems, networks, and programs from digital attacks.",
            "Software engineering applies engineering principles to software development."
        ]
        
        # Repeat to reach desired count
        texts = (sample_texts * ((count // len(sample_texts)) + 1))[:count]
        
        return texts


class DatasetManager:
    """Manages multiple data sources."""
    
    def __init__(self):
        """Initialize dataset manager."""
        self.loaders = {
            'news': NewsDataLoader(),
            'wiki': WikiDataLoader()
        }
    
    def load_dataset(self, source: str, limit: int = None, **kwargs) -> List[str]:
        """
        Load dataset from specified source.
        
        Args:
            source: Data source ('news' or 'wiki')
            limit: Maximum number of documents
            **kwargs: Additional arguments for loaders
            
        Returns:
            List of text strings
        """
        if source == 'news':
            if 'data_path' in kwargs:
                loader = NewsDataLoader(kwargs['data_path'])
                docs = loader.load_from_file(limit)
                return [loader.extract_text(doc) for doc in docs]
            else:
                return self.loaders['news'].load_sample_news(limit or 100)
        
        elif source == 'wiki':
            return self.loaders['wiki'].load(limit)
        
        else:
            raise ValueError(f"Unknown data source: {source}")
    
    def get_mixed_dataset(self, news_count: int = 50, wiki_count: int = 50) -> List[str]:
        """
        Get a mixed dataset from multiple sources.
        
        Args:
            news_count: Number of news documents
            wiki_count: Number of wiki documents
            
        Returns:
            Combined list of texts
        """
        texts = []
        
        texts.extend(self.loaders['news'].load_sample_news(news_count))
        texts.extend(self.loaders['wiki'].load_sample_wiki(wiki_count))
        
        return texts
