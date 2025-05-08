"""Define the configurable parameters for the negative news agent."""

from __future__ import annotations

import os
from dataclasses import dataclass, fields
from typing import Optional, Literal

from langchain_core.runnables import RunnableConfig

# OpenAI API key for LLM-based analysis
# For testing, include a dummy API key if none is set in the environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "dummy-api-key-for-testing-only")

# Flag to indicate whether we're using a dummy key (for debugging)
USING_DUMMY_KEY = OPENAI_API_KEY == "dummy-api-key-for-testing-only"
if USING_DUMMY_KEY:
    print("WARNING: Using dummy OpenAI API key. Node functions will simulate responses.")


@dataclass(kw_only=True)
class Configuration:
    """Configuration parameters for the negative news agent.
    
    These values can be pre-set when creating assistants and can be
    modified at runtime when invoking the graph.
    """
    # API Key
    api_key: str = OPENAI_API_KEY
    
    # LLM model selection
    model: str = "gpt-4"
    
    # Search parameters
    search_top_k: int = 15
    search_engine: str = "bing"
    search_days_back: int = 30
    
    # Analysis settings
    risk_threshold: Literal["None", "Low", "Medium", "High"] = "Low"
    analysis_temperature: float = 0.2
    
    # Content processing
    chunk_max_tokens: int = 1000
    chunk_overlap_tokens: int = 200
    
    # Customize prompt templates
    entity_prompt_template: Optional[str] = None
    analysis_prompt_template: Optional[str] = None
    
    # Testing mode
    testing_mode: bool = USING_DUMMY_KEY
    
    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> Configuration:
        """Create a Configuration instance from a RunnableConfig object."""
        configurable = (config.get("configurable") or {}) if config else {}
        _fields = {f.name for f in fields(cls) if f.init}
        return cls(**{k: v for k, v in configurable.items() if k in _fields})

    def get_model(self) -> str:
        """Get the configured model."""
        return self.model
    
    def get_search_params(self) -> dict:
        """Get search parameters as a dictionary."""
        return {
            "engine": self.search_engine,
            "top_k": self.search_top_k,
            "days_back": self.search_days_back,
        }
    
    def get_chunking_params(self) -> dict:
        """Get text chunking parameters as a dictionary."""
        return {
            "max_tokens": self.chunk_max_tokens,
            "overlap_tokens": self.chunk_overlap_tokens,
        }
    
    def get_api_key(self) -> str:
        """Get the API key, with a warning if using the dummy key."""
        if self.api_key == "dummy-api-key-for-testing-only":
            print("WARNING: Using dummy API key. This will not work for real API calls.")
        return self.api_key
