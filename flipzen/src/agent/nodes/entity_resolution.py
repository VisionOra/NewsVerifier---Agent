"""Entity resolution node for the negative news agent."""

import json
from typing import Any, Dict

from agent.nodes.utils import get_openai_client, get_completion_params, safe_extract_json
from agent.configuration import Configuration

def resolve_entity(state: Dict[str, Any], api_key: str = None, model: str = None) -> Dict[str, Any]:
    """Resolves the entity from user input data.
    
    Takes user information and resolves it to a specific entity for news checking.
    
    Args:
        state (Dict[str, Any]): The current state containing user input
        api_key (str, optional): OpenAI API key to use. Defaults to None.
        model (str, optional): Model to use. Defaults to None.
        
    Returns:
        Dict[str, Any]: Updated state with entity information
    """
    # Get values from state, ensuring we have at least empty strings for optional fields
    name = state.get("name", "Unknown")
    dob = state.get("dob", "")
    nationality = state.get("nationality", "")
    industry = state.get("industry", "")
    job_title = state.get("jobTitle", "")
    
    # Debug print to verify input data
    print(f"Resolving entity: {name}, {nationality}, {industry}, {job_title}")
    print(f"DEBUG: Entity resolution input state keys: {list(state.keys())}")
    
    # Initialize OpenAI client with passed API key if provided
    client = get_openai_client(api_key)
    
    # Get the model from configuration if not provided
    config = Configuration()
    model_to_use = model or config.model
    
    try:
        # Use OpenAI to enhance entity information
        prompt = f"""
        Based on the following information, create a detailed entity profile for negative news screening:
        - Name: {name}
        - Date of Birth: {dob}
        - Nationality: {nationality}
        - Industry: {industry}
        - Job Title: {job_title}
        
        Provide a concise, fact-based entity profile that includes:
        1. Full name with any known variations or common spellings
        2. Age (if DOB provided)
        3. Country of citizenship/residence
        4. Professional sector and role
        5. Any other relevant identifiers for search purposes
        
        Format your response as JSON with these fields: full_name, variations, age, location, sector, role, description
        """
        
        messages = [
            {"role": "system", "content": "You are an entity resolution specialist for KYC and AML processes."},
            {"role": "user", "content": prompt}
        ]
        
        # Set appropriate parameters based on model
        completion_params = get_completion_params(
            model=model_to_use, 
            messages=messages,
            response_type="json",
            temperature=0.3
        )
        
        print(f"Sending entity resolution request using model {model_to_use}...")
        response = client.chat.completions.create(**completion_params)
        response_content = response.choices[0].message.content
        
        print(f"Entity resolution response received, length: {len(response_content)}")
        
        # Extract JSON data using the safe extraction function
        entity_data = safe_extract_json(response_content)
        
        if not entity_data:
            print("Failed to extract valid JSON, creating fallback entity data")
            # Fall back to creating structured data manually
            entity_data = {
                "full_name": name,
                "variations": [],
                "sector": industry,
                "role": job_title,
                "description": f"{name} is a {job_title} in the {industry} industry."
            }
        
        # Ensure all required fields are present
        required_fields = ["full_name", "variations", "sector", "role", "description"]
        for field in required_fields:
            if field not in entity_data:
                if field == "variations" and "variation" in entity_data:
                    # Fix common mistake in variations field
                    entity_data["variations"] = entity_data.pop("variation")
                elif field == "variations":
                    # Default empty list if variations not provided
                    entity_data[field] = []
                else:
                    # Use input data as fallback if available
                    if field == "full_name":
                        entity_data[field] = name
                    elif field == "sector":
                        entity_data[field] = industry
                    elif field == "role":
                        entity_data[field] = job_title
                    else:
                        entity_data[field] = f"No {field} provided"
        
        # Ensure variations is a list
        if not isinstance(entity_data["variations"], list):
            if isinstance(entity_data["variations"], str):
                # If it's a string, convert to list
                entity_data["variations"] = [entity_data["variations"]]
            else:
                # Default to empty list
                entity_data["variations"] = []
        
        # Add standard field names as well for consistency across the workflow
        if "name" not in entity_data:
            entity_data["name"] = entity_data["full_name"]
            
        if "job_title" not in entity_data:
            entity_data["job_title"] = entity_data["role"]
            
        if "nationality" not in entity_data and "location" in entity_data:
            entity_data["nationality"] = entity_data["location"]
            
        if "industry" not in entity_data:
            entity_data["industry"] = entity_data["sector"]
        
        print(f"Entity resolution complete: {entity_data['full_name']}, {entity_data.get('sector', 'Unknown')}")
                
    except Exception as e:
        print(f"Error in entity resolution: {str(e)}")
        # Fall back to basic entity data
        entity_data = {
            "full_name": name,
            "name": name,
            "variations": [],
            "age": None,
            "location": nationality,
            "nationality": nationality,
            "sector": industry,
            "industry": industry,
            "role": job_title,
            "job_title": job_title,
            "description": f"{name} is a {job_title} in the {industry} industry."
        }
    
    return {
        **state,
        "entity": entity_data
    } 