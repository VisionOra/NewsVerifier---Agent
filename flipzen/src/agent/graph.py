"""Negative News Agent Graph.

This module defines the negative news screening agent workflow graph with a redesigned structure
that focuses on modular components and clear analyzer/formatter outputs.
"""

from typing import Any, Dict, List, TypedDict, Optional, Annotated, Literal, Union
import sys
import traceback
import json

from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END

from agent.configuration import Configuration, OPENAI_API_KEY
from agent.state import UserInput
from agent.nodes import (
    resolve_entity,
    generate_queries,
    call_web_search,
    scrape_content,
    chunk_content,
    analyze_content,
    format_results,
)

# ----------------------
# State Type Definitions
# ----------------------

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

# Full state with all possible fields
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

# ----------------------
# Node Functions
# ----------------------

def initialize_state(user_input: Any) -> NegativeNewsState:
    """Initialize the workflow state from user input."""
    try:
        # Print the raw input type for debugging
        print(f"INITIALIZER: Received input type: {type(user_input)}")
        print(f"INITIALIZER DEBUG: Raw input: {user_input}")
        
        # WORKAROUND: Use the global _last_input_data if it exists and the input is empty
        global _last_input_data
        if (not user_input or user_input == {}) and _last_input_data:
            print(f"INITIALIZER: Using cached input data instead of empty input")
            user_input = _last_input_data
            print(f"INITIALIZER DEBUG: Using cached input: {user_input}")
        
        # Handle different input types
        if isinstance(user_input, dict):
            input_data = {
                "name": user_input.get("name", "Unknown"),
                "dob": user_input.get("dob"),
                "nationality": user_input.get("nationality"),
                "industry": user_input.get("industry"),
                "jobTitle": user_input.get("jobTitle"),
            }
            print(f"INITIALIZER DEBUG: Dict input, name='{user_input.get('name', 'Not found')}'")
        elif hasattr(user_input, "name"):
            # Handle object-like input
            input_data = {
                "name": getattr(user_input, "name", "Unknown"),
                "dob": getattr(user_input, "dob", None),
                "nationality": getattr(user_input, "nationality", None),
                "industry": getattr(user_input, "industry", None),
                "jobTitle": getattr(user_input, "jobTitle", None),
            }
            print(f"INITIALIZER DEBUG: Object input, name='{getattr(user_input, 'name', 'Not found')}'")
        elif hasattr(user_input, "model_dump"):
            # Handle Pydantic v2 model
            data = user_input.model_dump()
            input_data = {
                "name": data.get("name", "Unknown"),
                "dob": data.get("dob"),
                "nationality": data.get("nationality"),
                "industry": data.get("industry"),
                "jobTitle": data.get("jobTitle"),
            }
            print(f"INITIALIZER DEBUG: Pydantic v2 input, name='{data.get('name', 'Not found')}'")
        elif hasattr(user_input, "dict"):
            # Handle Pydantic v1 model
            data = user_input.dict()
            input_data = {
                "name": data.get("name", "Unknown"),
                "dob": data.get("dob"),
                "nationality": data.get("nationality"),
                "industry": data.get("industry"),
                "jobTitle": data.get("jobTitle"),
            }
            print(f"INITIALIZER DEBUG: Pydantic v1 input, name='{data.get('name', 'Not found')}'")
        else:
            # Fallback
            input_data = {
                "name": "Unknown Entity",
            }
            print("INITIALIZER DEBUG: Fallback case, using 'Unknown Entity'")
            
        # Create the initial state with clean structure
        print(f"INITIALIZER: Creating initial state for: {input_data['name']}")
        print(f"INITIALIZER DEBUG: Final input_data: {input_data}")
        
        return {
            "input": input_data,
            "entity": None,
            "debug": {"initialization": "success"},
            "output": {},
            "error": None,
            "queries": None,
            "search_results": None,
            "scraped_content": None,
            "content_chunks": None, 
            "analysis": None,
            "report": None
            }
    except Exception as e:
        print(f"ERROR in initialize_state: {type(e).__name__}: {str(e)}")
        traceback.print_exc(file=sys.stdout)
        # Return an error state
        return {
            "input": {"name": "Unknown"},
            "entity": None,
            "debug": {"initialization": "failed"},
            "output": {},
            "error": {"message": f"Initialization failed: {str(e)}"},
            "queries": None,
            "search_results": None,
            "scraped_content": None,
            "content_chunks": None,
            "analysis": None,
            "report": None
        }

def entity_resolution_node(state: NegativeNewsState) -> NegativeNewsState:
    """Resolve entity details."""
    if state.get("error"):
        print("ENTITY RESOLVER: Skipping due to previous error")
        return state
        
    try:
        print(f"ENTITY RESOLVER: Processing entity resolution for: {state['input']['name']}")
        
        # Debug print to identify the issue
        print(f"DEBUG: Input data before entity resolution: {state['input']}")
        
        # Pass the input data directly to resolve_entity
        result = resolve_entity(state["input"], api_key=OPENAI_API_KEY)
        
        # Update the state with entity data
        new_state = state.copy()
        new_state["entity"] = result["entity"]
        new_state["debug"] = {**new_state.get("debug", {}), "entity_resolution": "success"}
        
        # Add to the cumulative output
        new_state["output"]["entity"] = result["entity"]
        
        # Debug print after resolution
        print(f"DEBUG: Entity after resolution: {new_state['entity'].get('full_name', 'Unknown')}")
        
        return new_state
    except Exception as e:
        print(f"ERROR in entity_resolution_node: {type(e).__name__}: {str(e)}")
        traceback.print_exc(file=sys.stdout)
        
        # Create a minimal entity with available info
        fallback_entity = {
            "full_name": state["input"]["name"],
            "industry": state["input"].get("industry", "Unknown"),
        }
        
        # Update the state, indicating error but allowing workflow to continue
        new_state = state.copy()
        new_state["entity"] = fallback_entity
        new_state["debug"] = {**new_state.get("debug", {}), "entity_resolution": "failed"}
        new_state["output"]["entity"] = fallback_entity
        
        return new_state

def query_generation_node(state: NegativeNewsState, config: Optional[Dict[str, Any]] = None) -> NegativeNewsState:
    """Generate search queries for the entity."""
    if state.get("error"):
        print("QUERY GENERATOR: Skipping due to previous error")
        return state
        
    try:
        # Use entity from state, falling back to input if needed
        entity_info = state["entity"] if state.get("entity") else {"full_name": state["input"]["name"]}
        print(f"QUERY GENERATOR: Generating queries for entity: {entity_info.get('full_name', state['input']['name'])}")
        
        # Prepare input for query generation
        query_input = {
            "entity": entity_info,
            "name": state["input"]["name"]  # Fallback name
        }
        
        # Call query generation
        cfg = config or {}
        model = cfg.get("model", "gpt-4")
        result = generate_queries(query_input, model=model)
        
        # Update state with query results
        new_state = state.copy()
        new_state["queries"] = {
            "news_queries": result.get("news_queries", []),
            "web_queries": result.get("web_queries", [])
        }
        new_state["debug"] = {**new_state.get("debug", {}), "query_generation": "success"}
        
        # Add to cumulative output
        new_state["output"]["queries"] = new_state["queries"]
        
        return new_state
    except Exception as e:
        print(f"ERROR in query_generation_node: {type(e).__name__}: {str(e)}")
        traceback.print_exc(file=sys.stdout)
        
        # Generate fallback queries
        name = state["entity"].get("full_name", state["input"]["name"]) if state.get("entity") else state["input"]["name"]
        fallback_queries = [
            f"{name} scandal",
            f"{name} controversy",
            f"{name} negative news"
        ]
        
        # Update state with fallback queries
        new_state = state.copy()
        new_state["queries"] = {
            "news_queries": fallback_queries,
            "web_queries": fallback_queries
        }
        new_state["debug"] = {**new_state.get("debug", {}), "query_generation": "failed"}
        new_state["output"]["queries"] = new_state["queries"]

        return new_state

def search_node(state: NegativeNewsState, config: Optional[Dict[str, Any]] = None) -> NegativeNewsState:
    """Perform web search based on queries."""
    if state.get("error"):
        print("SEARCH: Skipping due to previous error")
        return state
        
    try:
        if not state.get("queries"):
            raise ValueError("No queries available for search")
            
        print(f"WEB SEARCH: Searching with {len(state['queries'].get('web_queries', []))} queries")
        
        # Prepare input for search
        search_input = {
            "web_queries": state["queries"]["web_queries"],
            "news_queries": state["queries"]["news_queries"],
            "entity": state.get("entity", {"full_name": state["input"]["name"]})
        }
        
        # Configure search
        cfg = config or {}
        engine = cfg.get("search_engine", "bing")
        top_k = cfg.get("top_k", 10)
        model = cfg.get("model", "gpt-4")
        
        # Call search
        result = call_web_search(search_input, engine, top_k, model=model)
        search_results = result.get("search_results", [])
        print(f"Web search found {len(search_results)} results")
        
        # Update state with search results
        new_state = state.copy()
        new_state["search_results"] = search_results
        new_state["debug"] = {**new_state.get("debug", {}), "search": "success"}
        
        # Add to cumulative output
        new_state["output"]["search_results"] = search_results
        
        return new_state
    except Exception as e:
        print(f"ERROR in search_node: {type(e).__name__}: {str(e)}")
        traceback.print_exc(file=sys.stdout)
        
        # Update state with empty search results, allowing workflow to continue
        new_state = state.copy()
        new_state["search_results"] = []
        new_state["debug"] = {**new_state.get("debug", {}), "search": "failed"}
        new_state["error"] = {"message": f"Search failed: {str(e)}"}
        
        return new_state

def scraping_node(state: NegativeNewsState, config: Optional[Dict[str, Any]] = None) -> NegativeNewsState:
    """Scrape content from search results."""
    if state.get("error"):
        print("SCRAPING: Skipping due to previous error")
        return state
        
    try:
        if not state.get("search_results"):
            raise ValueError("No search results available for scraping")
            
        search_results = state["search_results"]
        print(f"CONTENT SCRAPER: Scraping {len(search_results)} URLs")
        
        # Prepare input for scraping
        scrape_input = {
            "search_results": search_results,
            "entity": state.get("entity", {"full_name": state["input"]["name"]})
        }
        
        # Call scraping
        result = scrape_content(scrape_input)
        scraped_content = result.get("scraped_content", [])
        print(f"Content scraping completed for {len(scraped_content)} URLs")
        
        # Update state with scraped content
        new_state = state.copy()
        new_state["scraped_content"] = scraped_content
        new_state["debug"] = {**new_state.get("debug", {}), "scraping": "success"}
        
        # Add to cumulative output
        new_state["output"]["scraped_content"] = scraped_content
        
        return new_state
    except Exception as e:
        print(f"ERROR in scraping_node: {type(e).__name__}: {str(e)}")
        traceback.print_exc(file=sys.stdout)
        
        # Update state with empty scraped content, allowing workflow to continue
        new_state = state.copy()
        new_state["scraped_content"] = []
        new_state["debug"] = {**new_state.get("debug", {}), "scraping": "failed"}
        
        return new_state

def chunking_node(state: NegativeNewsState, config: Optional[Dict[str, Any]] = None) -> NegativeNewsState:
    """Chunk scraped content for analysis."""
    if state.get("error"):
        print("CHUNKING: Skipping due to previous error")
        return state
        
    try:
        if not state.get("scraped_content"):
            raise ValueError("No scraped content available for chunking")
            
        scraped_content = state["scraped_content"]
        print(f"CONTENT CHUNKER: Chunking content from {len(scraped_content)} sources")
        
        # Prepare input for chunking
        chunk_input = {
            "scraped_content": scraped_content,
            "entity": state.get("entity", {"full_name": state["input"]["name"]})
        }
        
        # Call chunking
        result = chunk_content(chunk_input)
        content_chunks = result.get("content_chunks", [])
        print(f"Content chunking completed, created {len(content_chunks)} chunks")
        
        # Update state with content chunks
        new_state = state.copy()
        new_state["content_chunks"] = content_chunks
        new_state["debug"] = {**new_state.get("debug", {}), "chunking": "success"}
        
        # Add to cumulative output
        new_state["output"]["content_chunks"] = content_chunks
        
        return new_state
    except Exception as e:
        print(f"ERROR in chunking_node: {type(e).__name__}: {str(e)}")
        traceback.print_exc(file=sys.stdout)
        
        # Update state with empty content chunks, allowing workflow to continue
        new_state = state.copy()
        new_state["content_chunks"] = []
        new_state["debug"] = {**new_state.get("debug", {}), "chunking": "failed"}
        
        return new_state

def analysis_node(state: NegativeNewsState, config: Optional[Dict[str, Any]] = None) -> NegativeNewsState:
    """Analyze content chunks for negative news."""
    if state.get("error") and state.get("content_chunks", []) == []:
        print("ANALYSIS: Skipping due to previous error and no content")
        return state
        
    try:
        content_chunks = state.get("content_chunks", [])
        if not content_chunks:
            print("WARNING: No content chunks available, creating empty analysis")
            analysis_result = {
                "has_negative_news": False,
                "risk_score": 0,
                "summary": "No content was available for analysis",
                "key_concerns": [],
                "findings": [],
                "sources": []
            }
        else:
            print(f"ANALYZER: Analyzing {len(content_chunks)} content chunks")
            
            # Prepare input for analysis
            analysis_input = {
                "content_chunks": content_chunks,
                "entity": state.get("entity", {"full_name": state["input"]["name"]})
            }
            
            # Call analysis
            cfg = config or {}
            model = cfg.get("model", "gpt-4")
            result = analyze_content(analysis_input, model=model)
            analysis_result = result.get("analysis", {})
            print(f"Analysis completed with risk score: {analysis_result.get('risk_score', 0)}")
        
        # Update state with analysis results
        new_state = state.copy()
        new_state["analysis"] = analysis_result
        new_state["debug"] = {**new_state.get("debug", {}), "analysis": "success"}
        
        # Add to cumulative output
        new_state["output"]["analysis"] = analysis_result
        new_state["output"]["has_negative_news"] = analysis_result.get("has_negative_news", False)
        new_state["output"]["risk_score"] = analysis_result.get("risk_score", 0)
        new_state["output"]["summary"] = analysis_result.get("summary", "No summary available")
        
        return new_state
    except Exception as e:
        print(f"ERROR in analysis_node: {type(e).__name__}: {str(e)}")
        traceback.print_exc(file=sys.stdout)
        
        # Create a default analysis result
        default_analysis = {
            "has_negative_news": False,
            "risk_score": 0,
            "summary": f"Analysis failed: {str(e)}",
            "key_concerns": [],
                "findings": [],
            "sources": []
        }
        
        # Update state with default analysis, allowing workflow to continue
        new_state = state.copy()
        new_state["analysis"] = default_analysis
        new_state["debug"] = {**new_state.get("debug", {}), "analysis": "failed"}
        
        # Add to cumulative output
        new_state["output"]["analysis"] = default_analysis
        new_state["output"]["has_negative_news"] = False
        new_state["output"]["risk_score"] = 0
        new_state["output"]["summary"] = default_analysis["summary"]
        
        return new_state

def formatting_node(state: NegativeNewsState, config: Optional[Dict[str, Any]] = None) -> NegativeNewsState:
    """Format final results."""
    try:
        analysis = state.get("analysis", {})
        entity = state.get("entity", {"full_name": state["input"]["name"]})
        
        print(f"FORMATTER: Formatting final results for {entity.get('full_name', state['input']['name'])}")
        
        if not analysis:
            print("WARNING: No analysis available, creating default report")
            report = {
                "has_negative_news": False,
                "risk_score": 0,
                "summary": "No analysis was available to format",
                "key_concerns": [],
                "findings": [],
                "sources": []
            }
        else:
            # Prepare input for formatting
            format_input = {
                "analysis": analysis,
                "entity": entity
            }
            
            # Call formatting
            result = format_results(format_input)
            report = result.get("report", {})
            print(f"Formatting completed with risk score: {report.get('risk_score', 0)}")
        
        # Update state with formatted report
        new_state = state.copy()
        new_state["report"] = report
        new_state["debug"] = {**new_state.get("debug", {}), "formatting": "success"}
        
        # Add to cumulative output
        new_state["output"]["report"] = report
        
        # Ensure critical fields are available in output
        if "has_negative_news" not in new_state["output"]:
            new_state["output"]["has_negative_news"] = report.get("has_negative_news", False)
        if "risk_score" not in new_state["output"]:
            new_state["output"]["risk_score"] = report.get("risk_score", 0)
        if "summary" not in new_state["output"]:
            new_state["output"]["summary"] = report.get("summary", "No summary available")
        
        return new_state
    except Exception as e:
        print(f"ERROR in formatting_node: {type(e).__name__}: {str(e)}")
        traceback.print_exc(file=sys.stdout)
        
        # Create a default report
        default_report = {
            "has_negative_news": False,
            "risk_score": 0,
            "summary": f"Formatting failed: {str(e)}",
            "key_concerns": [],
            "findings": [],
                "sources": []
        }
        
        # Update state with default report
        new_state = state.copy()
        new_state["report"] = default_report
        new_state["debug"] = {**new_state.get("debug", {}), "formatting": "failed"}
        
        # Add to cumulative output
        new_state["output"]["report"] = default_report
        
        # Ensure critical fields are available in output
        if "has_negative_news" not in new_state["output"]:
            new_state["output"]["has_negative_news"] = False
        if "risk_score" not in new_state["output"]:
            new_state["output"]["risk_score"] = 0
        if "summary" not in new_state["output"]:
            new_state["output"]["summary"] = default_report["summary"]
        
        return new_state

# ----------------------
# Graph Construction
# ----------------------

def build_negative_news_graph(config: Optional[Dict[str, Any]] = None) -> StateGraph:
    """Build the negative news screening workflow graph."""
    # Create a workflow with the NegativeNewsState
    workflow = StateGraph(NegativeNewsState)
    
    # Add nodes
    workflow.add_node("initialize", initialize_state)
    workflow.add_node("entity_resolution", entity_resolution_node)
    workflow.add_node("query_generation", query_generation_node)
    workflow.add_node("search", search_node)
    workflow.add_node("scraping", scraping_node)
    workflow.add_node("chunking", chunking_node)
    workflow.add_node("analyzer", analysis_node)
    workflow.add_node("formatting", formatting_node)
    
    # Define the edges
    workflow.set_entry_point("initialize")
    workflow.add_edge("initialize", "entity_resolution")
    workflow.add_edge("entity_resolution", "query_generation")
    workflow.add_edge("query_generation", "search")
    workflow.add_edge("search", "scraping")
    workflow.add_edge("scraping", "chunking")
    workflow.add_edge("chunking", "analyzer")
    workflow.add_edge("analyzer", "formatting")
    workflow.add_edge("formatting", END)
    
    # Compile the workflow
    return workflow.compile()

# ----------------------
# User-Facing Functions
# ----------------------

# Create the graph
graph = build_negative_news_graph()

# Global variable to store the most recent input for debugging and workarounds
_last_input_data = None

def invoke_negative_news_check(input_data: Any) -> Dict[str, Any]:
    """Invoke the negative news check workflow with the provided input.
    
    This is a user-friendly wrapper that provides proper error handling and
    ensures consistent output format.
    
    Args:
        input_data: Dictionary or UserInput model containing entity information to check
        
    Returns:
        Dict[str, Any]: Results of the negative news check including:
            - report: The formatted report with findings
            - analysis: The full analysis data
            - entity: Entity information
            - has_negative_news: Whether negative news was found
            - risk_score: Risk score from 0-10
            - summary: Summary of findings
    """
    try:
        # Store the input data for initializer to access
        global _last_input_data
        _last_input_data = input_data
        
        # Handle different input types
        if hasattr(input_data, 'name'):
            # This is a UserInput or similar object
            entity_name = input_data.name
        elif isinstance(input_data, dict):
            # This is a dictionary
            entity_name = input_data.get('name', 'Unknown entity')
        else:
            entity_name = 'Unknown entity'
            
        print(f"INVOKING NEGATIVE NEWS CHECK FOR: {entity_name}")
        print(f"INVOKE DEBUG: Input data type: {type(input_data)}")
        print(f"INVOKE DEBUG: Input data: {input_data}")
        
        # Run the graph - DIRECTLY pass the input_data, don't transform it
        # The initialize_state function will handle the different input types
        result = graph.invoke(input_data)
        
        # Extract output from the final state
        output = result.get("output", {})
        
        # Ensure critical fields exist
        if not output.get("entity") and result.get("entity"):
            output["entity"] = result["entity"]
            
        if not output.get("report") and result.get("report"):
            output["report"] = result["report"]
            
        if not output.get("analysis") and result.get("analysis"):
            output["analysis"] = result["analysis"]
            
        # Add important fields at the top level for easy access
        output["has_negative_news"] = output.get("has_negative_news", False)
        output["risk_score"] = output.get("risk_score", 0)
        output["summary"] = output.get("summary", "No summary available")
        
        print(f"NEGATIVE NEWS CHECK COMPLETE WITH RISK SCORE: {output.get('risk_score', 0)}")
        
        return output
    except Exception as e:
        print(f"ERROR in invoke_negative_news_check: {type(e).__name__}: {str(e)}")
        traceback.print_exc(file=sys.stdout)
        
        # Return a minimal viable output
        # Handle different input types for entity name
        if hasattr(input_data, 'name'):
            entity_name = input_data.name
        elif isinstance(input_data, dict) and 'name' in input_data:
            entity_name = input_data["name"]
        else:
            entity_name = "Unknown entity"
            
        return {
            "entity": {"full_name": entity_name},
            "has_negative_news": False,
            "risk_score": 0,
            "summary": f"Error during negative news check: {str(e)}",
            "report": {
                "has_negative_news": False,
                "risk_score": 0,
                "summary": f"Error during negative news check: {str(e)}",
                "key_concerns": [],
                "findings": [],
                "sources": []
            },
            "analysis": {},
            "error": str(e)
        }
