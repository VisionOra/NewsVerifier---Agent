"""Query generation nodes for the negative news agent."""

import json
from typing import Any, Dict, List

from agent.nodes.utils import get_openai_client, get_completion_params, safe_extract_json
from agent.configuration import Configuration

def generate_queries(state: Dict[str, Any], api_key: str = None, model: str = None) -> Dict[str, Any]:
    """Generate search queries based on entity data.
    
    Args:
        state (Dict[str, Any]): Current state with entity information
        api_key (str, optional): OpenAI API key. Defaults to None.
        model (str, optional): Model to use. Defaults to None.
        
    Returns:
        Dict[str, Any]: Updated state with generated search queries
    """
    entity = state.get("entity", {})
    
    if not entity:
        return {**state, "web_queries": [], "news_queries": []}
    
    # Initialize OpenAI client with passed API key if provided
    client = get_openai_client(api_key)
    
    # Get the model from configuration if not provided
    config = Configuration()
    model_to_use = model or config.model
    
    # Extract entity information - check both standard field names and those from entity resolution
    name = entity.get("full_name", entity.get("name", ""))
    dob = entity.get("dob", "")
    nationality = entity.get("location", entity.get("nationality", ""))
    industry = entity.get("sector", entity.get("industry", ""))
    job_title = entity.get("role", entity.get("jobTitle", entity.get("job_title", "")))
    
    # Add debugging output
    print(f"Generating queries for entity: {name} in {industry}")
    
    # Calculate approximate age from DOB if available
    age_info = ""
    if dob:
        try:
            from datetime import datetime
            birth_year = int(dob.split("-")[0])
            current_year = datetime.now().year
            age = current_year - birth_year
            age_info = f", age {age}"
        except (ValueError, IndexError):
            pass
    
    # Format basic profile for prompt
    profile = f"{name}{age_info}"
    if nationality:
        profile += f", {nationality}"
    if industry or job_title:
        profile += f", {job_title + ' in ' if job_title else ''}{industry if industry else ''}"
    
    # Add debugging output
    print(f"Generated profile for queries: {profile}")
    
    prompt = f"""
    Generate search queries to detect any potential negative news, scandals, or controversies for this individual:
    
    Individual: {profile}
    
    Create 2-3 specific search queries that would help find relevant negative information.
    Focus on different types of potential issues:
    1. General scandal or controversy
    2. Fraud, embezzlement, or financial misconduct
    3. Legal troubles or lawsuits
    4. Regulatory investigations
    5. Sanctions or penalties
    6. Criminal allegations
    7. Controversial statements, actions, or associations
    
    Ensure queries are specific enough to return relevant results but general enough to catch various issues.
    Return the queries ONLY as a JSON object with two arrays - "web_queries" for general web searches and "news_queries" for news-specific searches.
    """
    
    messages = [
        {"role": "system", "content": "You are a search query generation assistant for negative news screening."},
        {"role": "user", "content": prompt}
    ]
    
    # Set appropriate parameters based on model
    completion_params = get_completion_params(
        model=model_to_use,
        messages=messages,
        response_type="json",
        temperature=0.7
    )
    
    try:
        print(f"Sending query generation request using model {model_to_use}...")
        response = client.chat.completions.create(**completion_params)
        response_content = response.choices[0].message.content
        
        # Add debugging output
        print(f"Query generation response received, length: {len(response_content)}")
        
        # Try to parse the response using safe extraction
        parsed_content = safe_extract_json(response_content)
        
        web_queries = []
        news_queries = []
        
        if parsed_content:
            web_queries = parsed_content.get("web_queries", [])
            news_queries = parsed_content.get("news_queries", [])
            
            # Ensure we have some queries even if parsing didn't give us the expected structure
            if not web_queries and not news_queries:
                # Look for any arrays in the response
                for key, value in parsed_content.items():
                    if isinstance(value, list) and value:
                        if "web" in key.lower():
                            web_queries = value
                        elif "news" in key.lower():
                            news_queries = value
                        elif not web_queries:  # Use any array if we haven't found web_queries yet
                            web_queries = value
        
        # If JSON extraction failed or didn't give us queries, try to extract from text
        if not web_queries and not news_queries:
            print("Extracting queries from text response")
            # Fallback: Extract queries from text using a simple heuristic
            lines = response_content.strip().split('\n')
            
            current_section = "web"  # Default section
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Check if this line indicates a section
                if "web" in line.lower() and ":" in line:
                    current_section = "web"
                    continue
                elif "news" in line.lower() and ":" in line:
                    current_section = "news"
                    continue
                
                # Clean up the line to extract just the query
                for prefix in ["-", "*", "•", "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10."]:
                    if line.startswith(prefix):
                        line = line[len(prefix):].strip()
                        break
                
                # Remove quotes if present
                if (line.startswith('"') and line.endswith('"')) or (line.startswith("'") and line.endswith("'")):
                    line = line[1:-1]
                
                if line:
                    if current_section == "web":
                        web_queries.append(line)
                    else:
                        news_queries.append(line)
        
        # Default queries if we still don't have any
        if not web_queries:
            print("Using default web queries")
            web_queries = [
                f"{name} scandal",
                f"{name} fraud",
                f"{name} investigation",
                f"{name} lawsuit",
                f"{name} controversy",
                f"{name} criminal"
            ]
        
        if not news_queries:
            print("Using web queries for news queries")
            news_queries = web_queries.copy()
        
        # Add debugging output
        print(f"Generated {len(web_queries)} web queries and {len(news_queries)} news queries")
        
        # Return updated state with generated queries
        return {
            **state,
            "web_queries": web_queries,
            "news_queries": news_queries
        }
        
    except Exception as e:
        print(f"Error generating queries: {str(e)}")
        # Fallback queries based on the entity name
        fallback_queries = [
            f"{name} scandal",
            f"{name} fraud",
            f"{name} investigation",
            f"{name} lawsuit",
            f"{name} controversy"
        ]
        return {
            **state,
            "web_queries": fallback_queries,
            "news_queries": fallback_queries
        } 