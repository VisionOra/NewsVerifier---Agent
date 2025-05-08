"""Utility functions for agent nodes."""

import os
import re
import json
from typing import Dict, List, Any, Optional, Union

# Import the configuration
try:
    from agent.configuration import OPENAI_API_KEY
except ImportError:
    try:
        from flipzen.src.agent.configuration import OPENAI_API_KEY
    except ImportError:
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "dummy-api-key-for-testing-only")

def get_openai_client(api_key=None):
    """Get the OpenAI client, correctly configured with API key."""
    try:
        from openai import OpenAI
        # Try to get the API key from different sources
        final_api_key = api_key or os.getenv("OPENAI_API_KEY") or OPENAI_API_KEY
        
        # Check if this is the dummy key for testing
        if final_api_key == "dummy-api-key-for-testing-only":
            print("Using mock OpenAI client for testing")
            return MockOpenAIClient()
            
        if not final_api_key:
            raise ValueError("No OpenAI API key provided")
            
        return OpenAI(api_key=final_api_key)
    except ImportError:
        raise ImportError("OpenAI package not installed. Please install it with 'pip install openai'.")
        
# Mock implementation for testing without API keys
class MockOpenAIClient:
    """Mock implementation of OpenAI client for testing without API keys."""
    
    def __init__(self, *args, **kwargs):
        """Initialize the mock client."""
        self.chat = MockChatCompletions()
        
    def __str__(self):
        return "MockOpenAIClient (for testing only)"
        
class MockChatCompletions:
    """Mock implementation of chat completions for testing."""
    
    def create(self, model="gpt-4", messages=None, temperature=0, **kwargs):
        """Create a mock chat completion."""
        # Extract the last user message to generate a relevant response
        last_message = None
        for msg in messages:
            if msg.get("role") == "user":
                last_message = msg.get("content", "")
        
        # Generate a relevant mock response based on the content
        content = self._generate_mock_response(last_message)
        
        # Return a response object similar to OpenAI's
        return MockResponse(content)
    
    def _generate_mock_response(self, message):
        """Generate a mock response based on the message content."""
        if not message:
            return "I don't have enough information to provide a response."
            
        # Entity resolution mock responses
        if "full name" in message.lower() or "entity" in message.lower():
            return json.dumps({
                "entity": {
                    "full_name": "John Doe",
                    "industry": "Technology",
                    "position": "CEO",
                    "nationality": "American",
                    "aliases": ["J. Doe"],
                    "related_entities": []
                }
            })
            
        # Query generation mock responses
        if "generate" in message.lower() and "queries" in message.lower():
            return json.dumps({
                "news_queries": [
                    "John Doe scandal",
                    "John Doe controversy",
                    "John Doe legal issues"
                ],
                "web_queries": [
                    "John Doe CEO background",
                    "John Doe negative news",
                    "John Doe reputation issues"
                ]
            })
            
        # Analysis mock responses
        if "analyze" in message.lower() or "content" in message.lower():
            return json.dumps({
                "has_negative_news": True,
                "risk_score": 6.5,
                "summary": "The analysis found several negative news items about John Doe, including allegations of financial misconduct and workplace harassment. These issues suggest a moderate risk level.",
                "key_concerns": [
                    "Financial misconduct allegations",
                    "Workplace harassment claims",
                    "Legal disputes with former partners"
                ],
                "findings": [
                    {
                        "type": "Financial",
                        "description": "Alleged involvement in accounting irregularities at previous company",
                        "severity": "Medium",
                        "sources": ["Mock Financial Times", "Mock Wall Street Journal"]
                    },
                    {
                        "type": "Personal Conduct",
                        "description": "Workplace harassment allegations from 2018",
                        "severity": "High",
                        "sources": ["Mock News Daily"]
                    }
                ],
                "sources": [
                    {
                        "url": "https://www.mock-financial-times.com/john-doe-case",
                        "title": "John Doe Faces Questioning in Financial Case",
                        "publication": "Mock Financial Times",
                        "date": "2022-05-15"
                    },
                    {
                        "url": "https://www.mock-news-daily.com/workplace-case",
                        "title": "Former Employees Allege Harassment by Tech CEO",
                        "publication": "Mock News Daily",
                        "date": "2019-03-22"
                    }
                ]
            })
            
        # Formatting mock responses
        if "format" in message.lower() or "report" in message.lower():
            return json.dumps({
                "report": {
                    "has_negative_news": True,
                    "risk_score": 6.5,
                    "summary": "John Doe has been associated with several concerning issues, including allegations of financial misconduct and workplace harassment. These allegations suggest a moderate risk level that warrants further investigation.",
                    "key_concerns": [
                        "Financial misconduct allegations",
                        "Workplace harassment claims",
                        "Legal disputes with former partners"
                    ],
                    "findings": [
                        {
                            "type": "Financial",
                            "description": "Alleged involvement in accounting irregularities at previous company",
                            "severity": "Medium",
                            "sources": ["Mock Financial Times", "Mock Wall Street Journal"]
                        },
                        {
                            "type": "Personal Conduct",
                            "description": "Workplace harassment allegations from 2018",
                            "severity": "High",
                            "sources": ["Mock News Daily"]
                        }
                    ],
                    "sources": [
                        {
                            "url": "https://www.mock-financial-times.com/john-doe-case",
                            "title": "John Doe Faces Questioning in Financial Case",
                            "publication": "Mock Financial Times",
                            "date": "2022-05-15"
                        },
                        {
                            "url": "https://www.mock-news-daily.com/workplace-case",
                            "title": "Former Employees Allege Harassment by Tech CEO",
                            "publication": "Mock News Daily",
                            "date": "2019-03-22"
                        }
                    ]
                }
            })
            
        # Default fallback response
        return json.dumps({
            "response": "This is a mock response for testing purposes only. In production, this would be generated by OpenAI's API."
        })

class MockResponse:
    """Mock response object similar to what OpenAI returns."""
    
    def __init__(self, content):
        """Initialize the mock response."""
        self.choices = [
            MockChoice(content)
        ]
        
class MockChoice:
    """Mock choice object similar to what OpenAI returns."""
    
    def __init__(self, content):
        """Initialize the mock choice."""
        self.message = MockMessage(content)
        
class MockMessage:
    """Mock message object similar to what OpenAI returns."""
    
    def __init__(self, content):
        """Initialize the mock message."""
        self.content = content

# Mock implementation for web search during testing
def mock_web_search(queries, entity, engine="bing", top_k=10):
    """Mock web search implementation for testing."""
    results = []
    
    # Generate mock results for each query
    for i, query in enumerate(queries[:3]): # Limit to 3 queries for testing
        for j in range(min(3, top_k)):  # Generate up to 3 results per query
            results.append({
                "url": f"https://www.mock-news-{i+1}.com/article-{j+1}",
                "title": f"Mock Result {j+1} for '{query}'",
                "description": f"This is a mock search result about {entity.get('full_name', 'the entity')} related to '{query}'.",
                "source": f"Mock News Source {i+1}",
                "published_at": "2023-01-01" if j % 2 == 0 else "2022-06-15"
            })
    
    return results

# Mock implementation for content scraping during testing
def mock_scrape_url(url):
    """Mock URL scraping implementation for testing."""
    # Extract info from the mock URL to generate relevant content
    url_parts = url.replace("https://", "").split("/")
    source = url_parts[0] if url_parts else "unknown"
    topic = url_parts[1] if len(url_parts) > 1 else "general"
    
    # Generate mock content based on URL pattern
    if "scandal" in url or "controversy" in url or "negative" in url:
        content = f"""
        This is a mock article about negative news from {source}.
        
        The article discusses allegations of misconduct, including financial irregularities
        and workplace issues. According to sources, these allegations are significant and
        could pose reputation risks.
        
        Multiple stakeholders have expressed concerns about these developments, and
        regulatory bodies are reportedly looking into the matter.
        """
    else:
        content = f"""
        This is a standard mock article from {source} about {topic}.
        
        The article contains general information about business activities and industry
        developments. It mentions various entities and their roles in the market.
        
        There are no significant negative mentions or concerning elements in this
        article's content.
        """
    
    # Return the mock scraped content
    return {
        "url": url,
        "title": f"Mock Article from {source} about {topic}",
        "content": content.strip(),
        "source": source.replace("www.mock-", "").replace(".com", "").title(),
        "published_date": "2023-01-01"
    }

def supports_json_response(model: str) -> bool:
    """Check if a model supports JSON response format.
    
    Args:
        model (str): Model name
        
    Returns:
        bool: True if model supports JSON response, False otherwise
    """
    # Models known to support JSON response format as of May 2024
    json_compatible_models = [
        "gpt-4-turbo",
        "gpt-4-turbo-preview",
        "gpt-4-0125-preview",
        "gpt-4-1106-preview",
        "gpt-4-vision-preview",
        "gpt-3.5-turbo-1106",
        "gpt-3.5-turbo-0125"
    ]
    
    # For specific model versions
    model_lower = model.lower()
    
    # Check for exact matches first
    if model in json_compatible_models:
        return True
        
    # Check for model prefixes/patterns
    for compatible_model in json_compatible_models:
        if model_lower.startswith(compatible_model.lower()):
            return True
            
    # Check for specific versions
    if "gpt-4-" in model_lower and any(suffix in model_lower for suffix in ["0125", "1106", "turbo"]):
        return True
    
    return False

def get_completion_params(
    model: str,
    messages: List[Dict[str, str]],
    response_type: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    top_p: Optional[float] = None,
    frequency_penalty: Optional[float] = None,
    presence_penalty: Optional[float] = None,
) -> Dict[str, Any]:
    """Get parameters for OpenAI chat completion based on model capabilities.
    
    Args:
        model (str): Model to use
        messages (List[Dict[str, str]]): Messages for the chat completion
        response_type (Optional[str], optional): Desired response type (json or text). Defaults to None.
        temperature (float, optional): Temperature parameter. Defaults to 0.7.
        max_tokens (Optional[int], optional): Maximum tokens. Defaults to None.
        top_p (Optional[float], optional): Top p parameter. Defaults to None.
        frequency_penalty (Optional[float], optional): Frequency penalty. Defaults to None.
        presence_penalty (Optional[float], optional): Presence penalty. Defaults to None.
        
    Returns:
        Dict[str, Any]: Parameters for OpenAI chat completion
    """
    params = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    
    # Add optional parameters if provided
    if max_tokens is not None:
        params["max_tokens"] = max_tokens
    
    if top_p is not None:
        params["top_p"] = top_p
        
    if frequency_penalty is not None:
        params["frequency_penalty"] = frequency_penalty
        
    if presence_penalty is not None:
        params["presence_penalty"] = presence_penalty
    
    # Add response format if model supports it and JSON is requested
    json_support = supports_json_response(model)
    
    # When JSON format is requested
    if response_type == "json":
        if json_support:
            # Add response_format parameter for supported models
            params["response_format"] = {"type": "json_object"}
            
            # Don't change the messages for supported models
        else:
            # For non-supported models, modify the system message to request JSON
            system_message_found = False
            
            for i, message in enumerate(params["messages"]):
                if message["role"] == "system":
                    # Add JSON formatting instruction to system message
                    original_content = message["content"]
                    if "JSON" not in original_content.upper():
                        message["content"] = original_content + "\n\nImportant: Respond with valid JSON only."
                    system_message_found = True
                    break
            
            # If no system message found, insert one at the beginning
            if not system_message_found:
                params["messages"].insert(0, {
                    "role": "system", 
                    "content": "You must respond with valid JSON only."
                })
                
            # Add JSON instruction to the user message as well
            if len(params["messages"]) > 0 and params["messages"][-1]["role"] == "user":
                last_index = len(params["messages"]) - 1
                original_content = params["messages"][last_index]["content"]
                
                if not original_content.strip().endswith("JSON"):
                    params["messages"][last_index]["content"] = original_content + "\n\nRespond with valid JSON only."
                    
            # IMPORTANT: For models that don't support the response_format parameter,
            # make sure we don't include it to avoid API errors
            # The parameter is already not included by default
    
    return params

def safe_extract_json(text: str) -> Dict[str, Any]:
    """Safely extract JSON from a text response.
    
    Args:
        text (str): Text potentially containing JSON
        
    Returns:
        Dict[str, Any]: Extracted JSON or empty dict if not found
    """
    import json
    import re
    
    # Try to parse as JSON directly
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Try to extract JSON from text
    json_pattern = r'```(?:json)?\s*([\s\S]*?)```'
    match = re.search(json_pattern, text)
    if match:
        json_str = match.group(1).strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    
    # Try to find JSON enclosed in braces
    brace_pattern = r'({[\s\S]*?})'
    match = re.search(brace_pattern, text)
    if match:
        json_str = match.group(1)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    
    # Return empty dict if no JSON found
    return {} 

def combine_content(content_items: List[Dict[str, Any]]) -> str:
    """Combine multiple content items into a single text.
    
    Args:
        content_items (List[Dict[str, Any]]): List of content items
        
    Returns:
        str: Combined text of all content items
    """
    combined_text = []
    
    for i, item in enumerate(content_items):
        # Extract content from either "content" or "text" field
        content = item.get("content", item.get("text", ""))
        title = item.get("title", f"Document {i+1}")
        url = item.get("url", "")
        source = item.get("source", "Unknown Source")
        
        # Add a separator between documents
        if i > 0:
            combined_text.append("\n" + "-"*50 + "\n")
            
        # Add document header
        header = f"DOCUMENT {i+1}: {title}\nSOURCE: {source}\nURL: {url}\n"
        combined_text.append(header)
        
        # Add the content
        combined_text.append(content)
    
    return "\n".join(combined_text) 