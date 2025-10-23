"""SelfIndex Package - Custom Inverted Index Implementation"""

__version__ = "1.0.0"

from .index.self_index import SelfIndex
from .index.factory import IndexFactory
from .preprocessing import TextPreprocessor
from .metrics import MetricsCollector, FunctionalMetrics

__all__ = [
    'SelfIndex',
    'IndexFactory',
    'TextPreprocessor',
    'MetricsCollector',
    'FunctionalMetrics'
]
