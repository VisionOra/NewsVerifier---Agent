"""FlipZen Negative News Agent.

This module provides a graph-based workflow for screening entities against negative news.
"""

# Export the main components by importing locally
from .graph import build_negative_news_graph, graph
from .state import UserInput, BaseState, NegativeNewsState

# Add the invoke_negative_news_check function directly if it's missing from the original import
from .graph import invoke_negative_news_check

# Export the main components
__all__ = [
    "build_negative_news_graph",
    "graph",
    "invoke_negative_news_check",
    "UserInput",
    "BaseState",
    "NegativeNewsState",
]
