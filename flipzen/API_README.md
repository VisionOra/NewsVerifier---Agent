# FlipZen Negative News API

This API provides a FastAPI wrapper around the FlipZen negative news screening agent, allowing you to access the agent's functionality via RESTful API endpoints.

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   # Add any other necessary API keys
   ```

## Running the API Server

Start the API server using:

```bash
python main.py
```

This will start the FastAPI server on `http://0.0.0.0:8002`.

For production deployments, consider using Gunicorn with Uvicorn workers:

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

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
- **Response**:
  ```json
  {
    "report": {
      "risk_level": "Low",
      "findings": [...],
      "summary": "..."
    },
    "entity": {
      "full_name": "John Doe",
      "industry": "Finance",
      ...
    },
    "status": "success"
  }
  ```

## API Documentation

After starting the server, you can access the auto-generated Swagger documentation at:

- Swagger UI: `http://localhost:8002/docs`
- ReDoc: `http://localhost:8002/redoc`

## Error Handling

The API returns standard HTTP status codes:

- `200 OK`: The request was successful
- `400 Bad Request`: Invalid request parameters
- `500 Internal Server Error`: Server-side error

Error responses include a message explaining the error:

```json
{
  "status": "error",
  "message": "Error details"
}
``` 