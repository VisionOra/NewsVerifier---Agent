"""Search-related nodes for the negative news agent."""

import json
import os
import requests
from typing import Any, Dict, List
from datetime import datetime

from agent.nodes.utils import get_openai_client, get_completion_params, safe_extract_json, mock_web_search
from agent.configuration import Configuration

def call_web_search(state: Dict[str, Any], engine: str = "bing", top_k: int = 10, model: str = "gpt-4") -> Dict[str, Any]:
    """Call web search API to find information about entity."""
    try:
        # Try to get user queries
        web_queries = state.get("web_queries", [])
        
        # Fallback to legacy field names
        if not web_queries:
            web_queries = state.get("queries", {}).get("web_queries", [])
            
        # If no web queries, try news queries
        if not web_queries:
            web_queries = state.get("news_queries", [])
            
        # Fallback to legacy field names
        if not web_queries:
            web_queries = state.get("queries", {}).get("news_queries", [])
            
        # If still no queries, generate some basic ones from entity name
        if not web_queries:
            entity = state.get("entity", {})
            name = entity.get("full_name", "Unknown")
            web_queries = [
                f"{name} controversy",
                f"{name} negative news",
                f"{name} scandal",
            ]
            
        print(f"Web search using queries: {web_queries}")
        
        # Check if we're in testing mode with a dummy API key
        api_key = os.getenv("OPENAI_API_KEY", "")
        bing_api_key = os.getenv("BING_SEARCH_API_KEY", "")
        
        if api_key == "dummy-api-key-for-testing-only" or not bing_api_key:
            print("Using mock web search for testing or no Bing API key provided")
            # Get entity info for mock results
            entity = state.get("entity", {})
            search_results = mock_web_search(web_queries, entity, engine, top_k)
        else:
            # Real web search implementation using Bing API
            search_results = []
            
            for query in web_queries:
                try:
                    # Call Bing Search API
                    bing_results = perform_bing_search(query, bing_api_key, top_k=top_k)
                    search_results.extend(bing_results)
                except Exception as e:
                    print(f"Error in Bing search for query '{query}': {str(e)}")
            
            # Deduplicate results by URL
            unique_results = {}
            for result in search_results:
                if result.get("url") not in unique_results:
                    unique_results[result.get("url")] = result
            
            search_results = list(unique_results.values())
            
            # Limit to top_k results
            search_results = search_results[:top_k]
            
        # Log the results
        result_count = len(search_results)
        print(f"Web search found {result_count} results")
        
        # Return the search results
        return {
            "search_results": search_results,
            "web_results": search_results,  # For backward compatibility
        }
        
    except Exception as e:
        print(f"ERROR in call_web_search: {str(e)}")
        # Return empty results on error
        return {
            "search_results": [],
            "web_results": [],
        }

def perform_bing_search(query: str, api_key: str, top_k: int = 10) -> List[Dict[str, Any]]:
    """
    Perform a real web search using the Bing Search API.
    
    Args:
        query: The search query
        api_key: Bing Search API key
        top_k: Maximum number of results to return
        
    Returns:
        List of search results
    """
    try:
        # Bing Search API endpoint
        endpoint = "https://api.bing.microsoft.com/v7.0/search"
        
        # Set up headers with API key
        headers = {
            "Ocp-Apim-Subscription-Key": api_key,
            "Accept": "application/json"
        }
        
        # Set up parameters
        params = {
            "q": query,
            "count": top_k,
            "offset": 0,
            "mkt": "en-US",
            "freshness": "Week"  # Focus on recent content
        }
        
        # Make the request
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()  # Raise for HTTP errors
        
        # Parse the response
        results = response.json()
        
        # Extract the relevant information from the response
        search_results = []
        
        if "webPages" in results and "value" in results["webPages"]:
            for item in results["webPages"]["value"]:
                search_results.append({
                    "url": item.get("url", ""),
                    "title": item.get("name", ""),
                    "description": item.get("snippet", ""),
                    "source": item.get("displayUrl", "").split("/")[0],
                    "published_at": datetime.now().strftime("%Y-%m-%d")  # Bing doesn't provide date
                })
                
        # Also check for news results if available
        if "news" in results and "value" in results["news"]:
            for item in results["news"]["value"]:
                # Format the date if available
                published_date = item.get("datePublished", "")
                if published_date:
                    try:
                        # Convert to YYYY-MM-DD format
                        date_obj = datetime.fromisoformat(published_date.replace("Z", "+00:00"))
                        formatted_date = date_obj.strftime("%Y-%m-%d")
                    except:
                        formatted_date = published_date
                else:
                    formatted_date = datetime.now().strftime("%Y-%m-%d")
                
                search_results.append({
                    "url": item.get("url", ""),
                    "title": item.get("name", ""),
                    "description": item.get("description", ""),
                    "source": item.get("provider", [{}])[0].get("name", "") if item.get("provider") else "",
                    "published_at": formatted_date
                })
        
        return search_results
        
    except Exception as e:
        print(f"Error in Bing search API call: {str(e)}")
        return []