# FlipZen Negative News Agent

A LangGraph-based agent for screening entities against negative news, designed for AML and KYC workflows.

## Introduction

  FlipZen Negative News Agentis a powerful tool designed to automate the process of negative news screening for individuals and entities as part of Anti-Money Laundering (AML) and Know Your Customer (KYC) compliance workflows. Using advanced AI and natural language processing techniques, FlipZen can quickly analyze web content to identify potential risks associated with a person or organization.

The system leverages LangGraph's orchestration capabilities combined with large language models to intelligently search for, analyze, and synthesize information from public sources into a structured risk report. This helps compliance teams make faster, more informed decisions while reducing manual research efforts.

## Process

The FlipZen agent follows a sophisticated workflow to screen entities:

1. **Entity Resolution**: Processes and validates input information about the target entity
2. **Query Generation**: Creates optimized search queries based on entity attributes
3. **Web Search**: Executes searches to find relevant news and information about the entity
4. **Content Retrieval**: Scrapes and processes content from search results
5. **Content Analysis**: Analyzes retrieved content for negative sentiment and risk factors
6. **Risk Assessment**: Evaluates findings to determine an overall risk score
7. **Report Generation**: Compiles findings into a structured report with key concerns and summaries

This end-to-end process transforms raw entity data into actionable compliance insights with minimal human intervention.

## Setup with FastAPI

FlipZen can be used as a standalone Python package or deployed as a REST API service using FastAPI. Here's how to get started with the API:

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/flipzen.git
   cd flipzen
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with required API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   BING_SEARCH_API_KEY=your_bing_search_api_key
   MODEL=gpt-4
   # Add any other necessary API keys
   ```

4. Start the FastAPI server:
   ```bash
   python main.py
   ```

This will start the API server on `http://0.0.0.0:8002`.

5. Access the API documentation:
   - Swagger UI: `http://localhost:8002/docs`
   - ReDoc: `http://localhost:8002/redoc`

For production deployments, consider using Gunicorn with Uvicorn workers:

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

## Web Search Functionality

The agent uses the Bing Search API to find relevant information about the entity being screened. It performs searches using generated queries that combine the entity name with keywords related to potential risks, such as "scandal", "controversy", "legal issues", etc.

### Requirements
- A valid Bing Search API key is required for real web searches
- If no Bing Search API key is provided, the system will fall back to using mock data for testing purposes

### Configuration
In your `.env` file, set:
```
BING_SEARCH_API_KEY=your_bing_search_api_key
```

## Content Scraping

After finding relevant search results, the agent scrapes the content from the webpages to analyze them for negative news. The scraping functionality:

1. Uses BeautifulSoup to extract relevant content from HTML pages
2. Employs several strategies to identify main content (article tags, content divs, paragraphs)
3. Cleans and formats the content for analysis
4. Chunks larger content into manageable pieces

If scraping fails for any URL, the agent will fall back to using the search result description as minimal content to ensure the workflow continues.

## API Endpoints

### Root Endpoint

- **URL**: `/`
- **Method**: `GET`
- **Description**: Returns basic information about the API.

### Health Check

- **URL**: `/health`
- **Method**: `GET`
- **Description**: Basic health check endpoint.

### Screen Entity

- **URL**: `/screen`
- **Method**: `POST`
- **Description**: Screens an entity for negative news using default configuration.
- **Request Body**:
  ```json
  {
    "name": "John Doe",
    "dob": "1980-01-01",
    "nationality": "United States",
    "industry": "Finance",
    "jobTitle": "CEO"
  }
  ```

## Requirements Installation

The project requires the following key dependencies:

```bash
# Install from requirements.txt
pip install -r requirements.txt
```

Key dependencies include:

- **Core Components**:
  - langgraph (≥0.0.23): For workflow orchestration
  - langchain (≥0.1.0): For LLM interactions
  - openai (≥1.3.0): For accessing OpenAI models
  - python-dotenv (≥1.0.0): For environment variable management

- **Web Processing**:
  - requests (≥2.31.0): For HTTP requests
  - beautifulsoup4 (≥4.12.2): For HTML parsing
  - html2text (≥2022.1.0): For HTML to text conversion

- **API Components**:
  - fastapi (≥0.104.0): For API framework
  - uvicorn (≥0.24.0): For ASGI server
  - pydantic (≥2.4.2): For data validation

## Usage

### Running the Agent by using the FastAPI server

You can run the agent directly using the provided script:

```bash
python main.py
```

This will show you example usage and offer to run a demo with a sample entity.

### Using in Your Code

```python
from flipzen.src.agent.graph import graph

# Prepare input for the agent
input_data = {
    "name": "Elon Musk",
    "nationality": "United States",
    "industry": "Technology",
    "jobTitle": "CEO"
}

# Run the agent
result = graph.invoke(input_data)

# Process the results
report = result.get("report", {})
print(f"Entity: {report.get('entity', {}).get('name', 'Unknown')}")
print(f"Has negative news: {report.get('has_negative_news', False)}")
print(f"Risk score: {report.get('risk_score', 0)}/10")

if report.get("summary"):
    print("\nSummary:")
    print(report["summary"])

if report.get("key_concerns", []):
    print("\nKey concerns:")
    for concern in report["key_concerns"]:
        print(f"- {concern}")
```

### Using with LangGraph Server

To run a LangGraph server with this agent:

```bash
cd flipzen
langgraph dev
```

This makes the agent available through the LangGraph API at http://localhost:3001.

## Configuration

You can customize the agent behavior by providing configuration when invoking the graph:

```python
config = {
    "configurable": {
        "model": "gpt-4-turbo",  # Model to use (default: gpt-4)
        "search_top_k": 5,        # Number of search results to use
        "risk_threshold": "Low"   # Minimum risk level to report
    }
}

result = graph.invoke(input_data, config=config)
```

## Project Structure

- `src/agent/graph.py`: Main LangGraph workflow definition
- `src/agent/state.py`: State definitions for the workflow
- `src/agent/configuration.py`: Configuration settings
- `src/agent/nodes/`: Individual processing components
  - `entity_resolution.py`: Entity resolution logic
  - `query_generation.py`: Search query generation
  - `search.py`: Web search functionality using Bing Search API
  - `content_processing.py`: Web content scraping and chunking
  - `analysis.py`: Content analysis for negative news
  - `formatting.py`: Report formatting

## License

This project is licensed under the MIT License - see the LICENSE file for details.