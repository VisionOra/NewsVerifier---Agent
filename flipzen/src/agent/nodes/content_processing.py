"""Content processing nodes for the negative news agent."""

import os
import json
import requests
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import time
import re

from agent.nodes.utils import (
    get_openai_client, 
    get_completion_params, 
    safe_extract_json, 
    combine_content,
    mock_scrape_url
)
from agent.configuration import Configuration

def scrape_content(state: Dict[str, Any], model: str = None) -> Dict[str, Any]:
    """Scrape content from URLs in search results.
    
    Args:
        state (Dict[str, Any]): State containing search results
        model (str, optional): Model to use for processing. Defaults to None.
        
    Returns:
        Dict[str, Any]: Updated state with scraped content
    """
    try:
        # Get search results, checking both possible field names
        search_results = state.get("search_results", [])
        if not search_results:
            search_results = state.get("web_results", [])
        
        print(f"Scraping content from {len(search_results)} search results")
        
        # Check if we're in testing mode with a dummy API key
        api_key = os.getenv("OPENAI_API_KEY", "")
        if api_key == "dummy-api-key-for-testing-only":
            print("Using mock content scraping for testing")
            # Use the mock scraper for each URL
            scraped_content = []
            for result in search_results[:5]:  # Limit to 5 for testing
                url = result.get("url", "")
                if url:
                    try:
                        content = mock_scrape_url(url)
                        # Add any additional fields from the original result
                        content["title"] = content.get("title") or result.get("title", "")
                        content["published_date"] = content.get("published_date") or result.get("published_at", "")
                        scraped_content.append(content)
                    except Exception as e:
                        print(f"Error in mock scraping URL {url}: {str(e)}")
        else:
            # Real content scraping implementation
            scraped_content = []
            
            # Add request headers to mimic a browser
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
            
            # Process each search result
            for i, result in enumerate(search_results):
                url = result.get("url", "")
                if not url:
                    continue
                
                try:
                    print(f"Scraping content from URL: {url}")
                    
                    # Make the request
                    response = requests.get(url, headers=headers, timeout=10)
                    response.raise_for_status()
                    
                    # Parse the HTML content with BeautifulSoup
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract the title
                    title = result.get("title", "")
                    if not title:
                        title_tag = soup.find('title')
                        title = title_tag.text.strip() if title_tag else "Unknown Title"
                    
                    # Extract the main content
                    # Strategy 1: Look for article or main tags
                    content_tag = soup.find('article') or soup.find('main')
                    
                    # Strategy 2: Look for common content divs if no article/main tag found
                    if not content_tag:
                        for div in soup.find_all('div', class_=re.compile('(content|article|post|story)')):
                            if len(div.get_text(strip=True)) > 200:  # Check it has substantial content
                                content_tag = div
                                break
                    
                    # Strategy 3: Fall back to extracting paragraphs
                    if not content_tag:
                        paragraphs = soup.find_all('p')
                        content_text = "\n".join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
                    else:
                        # Clean the content tag by removing script and style elements
                        for script in content_tag(['script', 'style', 'nav', 'footer', 'header']):
                            script.decompose()
                        content_text = content_tag.get_text(separator="\n", strip=True)
                    
                    # Get source from result or extract from domain
                    source = result.get("source", "")
                    if not source:
                        domain = urlparse(url).netloc
                        source = domain.replace('www.', '').split('.')[0].capitalize()
                    
                    # Get published date from result
                    published_date = result.get("published_at", "")
                    
                    # Store the scraped content
                    content = {
                        "url": url,
                        "title": title,
                        "content": content_text,
                        "source": source,
                        "published_date": published_date
                    }
                    
                    scraped_content.append(content)
                    
                    # Add a small delay to avoid overwhelming servers
                    if i < len(search_results) - 1:
                        time.sleep(0.5)
                    
                except Exception as e:
                    print(f"Error scraping URL {url}: {str(e)}")
                    # If scraping fails, create a minimal entry with available info
                    minimal_content = {
                        "url": url,
                        "title": result.get("title", "Unknown Title"),
                        "content": result.get("description", "Content scraping failed."),
                        "source": result.get("source", "Unknown Source"),
                        "published_date": result.get("published_at", "")
                    }
                    scraped_content.append(minimal_content)
            
        print(f"Successfully scraped content from {len(scraped_content)} URLs")
        
        # Return an updated state with the scraped content
        return {
            "scraped_content": scraped_content
        }
        
    except Exception as e:
        print(f"Error in scrape_content: {str(e)}")
        return {
            "scraped_content": []
        }

def chunk_content(state: Dict[str, Any]) -> Dict[str, Any]:
    """Chunk scraped content into smaller pieces.
    
    Args:
        state (Dict[str, Any]): Current state with scraped content
        
    Returns:
        Dict[str, Any]: Updated state with content chunks
    """
    # Get scraped content from state
    scraped_content = state.get("scraped_content", [])
    
    # Check if we have any content to chunk
    print(f"Chunking {len(scraped_content)} scraped content items")
    if not scraped_content:
        print("Warning: No scraped content to chunk")
        return {**state, "content_chunks": []}
    
    # Counter for documents chunked and chunks created
    documents_chunked = 0
    chunks_created = 0
    
    chunks = []
    
    # Process each document
    for doc in scraped_content:
        try:
            # Extract document information
            url = doc.get("url", "")
            title = doc.get("title", "")
            source = doc.get("source", "")
            published_date = doc.get("published_date", "")
            
            # Check both "content" and "text" fields for compatibility
            content = doc.get("content", doc.get("text", ""))
            
            if not content:
                print(f"Warning: Empty content in document from {url}")
                continue
            
            documents_chunked += 1
            
            # Create a metadata header for each chunk
            metadata_header = f"SOURCE: {source}\nTITLE: {title}\nURL: {url}\nDATE: {published_date}\n\n"
            
            # Split content into paragraphs
            paragraphs = [p for p in content.split("\n") if p.strip()]
            
            # For short content, use a single chunk
            if len(content) < 2000:
                chunk_text = metadata_header + content
                chunks.append({
                    "url": url,
                    "title": title,
                    "source": source,
                    "published_date": published_date,
                    "content": chunk_text,
                    "text": chunk_text  # Add text field for compatibility
                })
                chunks_created += 1
                print(f"Created 1 chunk for {title} (short content)")
                continue
            
            # For longer content, create overlapping chunks
            chunk_size = 2000
            overlap = 200
            
            # Join paragraphs until reaching chunk size
            current_chunk = []
            current_length = 0
            
            for paragraph in paragraphs:
                current_chunk.append(paragraph)
                current_length += len(paragraph)
                
                # If we've reached the chunk size, create a chunk
                if current_length >= chunk_size:
                    chunk_text = metadata_header + "\n".join(current_chunk)
                    chunks.append({
                        "url": url,
                        "title": title,
                        "source": source,
                        "published_date": published_date,
                        "content": chunk_text,
                        "text": chunk_text  # Add text field for compatibility
                    })
                    chunks_created += 1
                    
                    # Keep some paragraphs for overlap
                    overlap_length = 0
                    overlap_paragraphs = []
                    
                    # Start from the end and work backward to create overlap
                    for para in reversed(current_chunk):
                        overlap_paragraphs.insert(0, para)
                        overlap_length += len(para)
                        if overlap_length >= overlap:
                            break
                    
                    # Reset with overlap paragraphs
                    current_chunk = overlap_paragraphs
                    current_length = overlap_length
            
            # Don't forget the last chunk if there's content left
            if current_chunk and current_length > 0:
                chunk_text = metadata_header + "\n".join(current_chunk)
                chunks.append({
                    "url": url,
                    "title": title,
                    "source": source,
                    "published_date": published_date,
                    "content": chunk_text,
                    "text": chunk_text  # Add text field for compatibility
                })
                chunks_created += 1
            
            print(f"Created {chunks_created - len(chunks)} chunks for {title}")
            
        except Exception as e:
            print(f"Error chunking content from {doc.get('url')}: {str(e)}")
    
    print(f"Chunking complete: {documents_chunked} documents processed, {chunks_created} chunks created")
    
    # Return an updated state with the content chunks
    return {
        **state,
        "content_chunks": chunks
    } 