"""
Text preprocessing utilities for indexing.
Includes tokenization, stemming, stopword removal, and text normalization.
"""

import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from typing import List, Set


class TextPreprocessor:
    """Handles text preprocessing for indexing."""
    
    def __init__(self, use_stemming=True, remove_stopwords=True, lowercase=True):
        """
        Initialize text preprocessor.
        
        Args:
            use_stemming: Whether to apply stemming
            remove_stopwords: Whether to remove stopwords
            lowercase: Whether to convert to lowercase
        """
        self.use_stemming = use_stemming
        self.remove_stopwords = remove_stopwords
        self.lowercase = lowercase
        
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
            nltk.download('punkt_tab', quiet=True)
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)
        
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet', quiet=True)
        
        # Initialize stemmer and stopwords
        if use_stemming:
            self.stemmer = PorterStemmer()
        
        if remove_stopwords:
            self.stop_words: Set[str] = set(stopwords.words('english'))
        else:
            self.stop_words = set()
    
    def preprocess(self, text: str) -> List[str]:
        """
        Preprocess text into a list of terms.
        
        Args:
            text: Input text
            
        Returns:
            List of preprocessed terms
        """
        # Lowercase
        if self.lowercase:
            text = text.lower()
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove punctuation and non-alphanumeric tokens
        tokens = [token for token in tokens if token.isalnum()]
        
        # Remove stopwords
        if self.remove_stopwords:
            tokens = [token for token in tokens if token not in self.stop_words]
        
        # Apply stemming
        if self.use_stemming:
            tokens = [self.stemmer.stem(token) for token in tokens]
        
        return tokens
    
    def preprocess_with_positions(self, text: str) -> List[tuple]:
        """
        Preprocess text and keep position information.
        
        Args:
            text: Input text
            
        Returns:
            List of (term, position) tuples
        """
        # Lowercase
        if self.lowercase:
            text = text.lower()
        
        # Tokenize
        tokens = word_tokenize(text)
        
        result = []
        position = 0
        
        for token in tokens:
            # Remove punctuation and non-alphanumeric tokens
            if not token.isalnum():
                continue
            
            # Remove stopwords
            if self.remove_stopwords and token in self.stop_words:
                position += 1
                continue
            
            # Apply stemming
            if self.use_stemming:
                term = self.stemmer.stem(token)
            else:
                term = token
            
            result.append((term, position))
            position += 1
        
        return result
    
    def extract_phrases(self, text: str, phrase_length: int = 2) -> List[str]:
        """
        Extract n-gram phrases from text.
        
        Args:
            text: Input text
            phrase_length: Length of phrases (n-grams)
            
        Returns:
            List of phrases
        """
        tokens = self.preprocess(text)
        
        if len(tokens) < phrase_length:
            return []
        
        phrases = []
        for i in range(len(tokens) - phrase_length + 1):
            phrase = ' '.join(tokens[i:i + phrase_length])
            phrases.append(phrase)
        
        return phrases
