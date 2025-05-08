"""Define the state structures for the negative news agent."""

from __future__ import annotations

from typing import Optional, Dict, Any, List, TypedDict

from pydantic import BaseModel


class UserInput(BaseModel):
    """Defines the input state for the NegativeNewsCheckerAgent.
    
    Captures user information required for negative news screening.
    """
    name: str              # required full client name
    dob: Optional[str] = None     # optional date of birth
    nationality: Optional[str] = None
    industry: Optional[str] = None
    jobTitle: Optional[str] = None

    formatted_results: Optional[Dict[str, Any]] = None
    debug_info: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserInput':
        """Create a UserInput instance from a dictionary.
        
        This is a convenience method to support both object-oriented and 
        dictionary-based invocation patterns.
        
        Args:
            data (Dict[str, Any]): Dictionary containing user input data
            
        Returns:
            UserInput: A new UserInput instance
        """
        # Filter to only include valid fields
        valid_data = {k: v for k, v in data.items() if k in cls.__annotations__}
        return cls(**valid_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert this UserInput to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation
        """
        return {
            "name": self.name,
            "dob": self.dob,
            "nationality": self.nationality,
            "industry": self.industry,
            "jobTitle": self.jobTitle,
        }


# New state structure definitions to match the graph implementation

class BaseState(TypedDict):
    """Base state with common fields."""
    # Original input
    input: Dict[str, Any]
    # Entity information
    entity: Optional[Dict[str, Any]]
    # Debug information
    debug: Optional[Dict[str, Any]]
    # Cumulative state for output (will be built up through the pipeline)
    output: Dict[str, Any]
    # Flag to indicate error state
    error: Optional[Dict[str, str]]

class NegativeNewsState(BaseState):
    """Complete state for the negative news screening workflow."""
    # Generated search queries
    queries: Optional[Dict[str, List[str]]]
    # Results from search 
    search_results: Optional[List[Dict[str, Any]]]
    # Scraped content from URLs
    scraped_content: Optional[List[Dict[str, Any]]]
    # Content chunks for analysis
    content_chunks: Optional[List[Dict[str, Any]]]
    # Analysis results
    analysis: Optional[Dict[str, Any]]
    # Formatted report
    report: Optional[Dict[str, Any]]