"""Formatting node for the negative news agent."""

import json
from typing import Any, Dict, List
from datetime import datetime

from agent.nodes.utils import get_openai_client, get_completion_params, safe_extract_json
from agent.configuration import Configuration

def format_results(state: Dict[str, Any], api_key: str = None, model: str = None) -> Dict[str, Any]:
    """Formats the analysis results into a structured JSON response.
    
    Returns the final formatted output with risk assessment.
    
    Args:
        state (Dict[str, Any]): Current state with analysis results
        api_key (str, optional): OpenAI API key. Defaults to None.
        model (str, optional): Model to use. Defaults to None.
        
    Returns:
        Dict[str, Any]: Updated state with formatted results
    """
    analysis_results = state.get("analysis_results", [])
    entity = state.get("entity", {})
    name = entity.get("full_name", entity.get("name", ""))
    
    # Initialize OpenAI client with passed API key if provided
    client = get_openai_client(api_key)
    
    # Get the model from configuration if not provided
    config = Configuration()
    model_to_use = model or config.model
    
    print(f"Formatting results for entity: {name}")
    print(f"Found {len(analysis_results)} analysis results to format")
    
    # Count risk levels
    risk_counts = {"None": 0, "Low": 0, "Medium": 0, "High": 0, "unknown": 0}
    
    for result in analysis_results:
        risk_level = result.get("analysis", {}).get("risk_level", "unknown")
        risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
    
    # Determine overall risk level
    overall_risk = "Low"  # Default
    if risk_counts.get("High", 0) >= 1:
        overall_risk = "High"
    elif risk_counts.get("Medium", 0) >= 2:
        overall_risk = "Medium"
    elif risk_counts.get("Low", 0) >= 3:
        overall_risk = "Low"
    
    # Extract key risk factors across all sources
    all_risk_factors = []
    for result in analysis_results:
        factors = result.get("analysis", {}).get("risk_factors", [])
        if isinstance(factors, list):
            all_risk_factors.extend(factors)
        elif isinstance(factors, str):
            all_risk_factors.append(factors)
    
    # Deduplicate risk factors
    unique_risk_factors = list(set(filter(None, all_risk_factors)))
    
    print(f"Overall risk level: {overall_risk}")
    print(f"Found {len(unique_risk_factors)} unique risk factors")
    
    # Generate summary of findings using OpenAI
    summary_prompt = f"""
    Create a concise summary of the negative news screening results for {name}.
    
    Overall Risk Level: {overall_risk}
    
    Risk Breakdown:
    - High Risk Items: {risk_counts.get("High", 0)}
    - Medium Risk Items: {risk_counts.get("Medium", 0)}
    - Low Risk Items: {risk_counts.get("Low", 0)}
    - No Risk Items: {risk_counts.get("None", 0)}
    
    Key Risk Factors:
    {", ".join(unique_risk_factors[:10]) if unique_risk_factors else "None identified"}
    
    Create a professional 2-3 paragraph summary explaining the findings and recommendations.
    """
    
    messages = [
        {"role": "system", "content": "You are a compliance officer preparing a negative news screening report."},
        {"role": "user", "content": summary_prompt}
    ]
    
    # Get appropriate completion parameters
    completion_params = get_completion_params(
        model=model_to_use,
        messages=messages,
        temperature=0.4
    )
    
    try:
        print(f"Generating executive summary using model {model_to_use}...")
        response = client.chat.completions.create(**completion_params)
        executive_summary = response.choices[0].message.content
        print(f"Executive summary generated ({len(executive_summary)} chars)")
    except Exception as e:
        print(f"Error generating executive summary: {str(e)}")
        executive_summary = f"Error generating summary: {str(e)}. Overall risk level: {overall_risk}."
    
    # Format the final results
    formatted_results = {
        "entity": name,
        "timestamp": datetime.now().isoformat(),
        "overall_risk_level": overall_risk,
        "risk_breakdown": risk_counts,
        "key_risk_factors": unique_risk_factors[:15] if unique_risk_factors else [],  # Limit to top 15
        "executive_summary": executive_summary,
        "detailed_findings": [
            {
                "source": result.get("source"),
                "url": result.get("url"),
                "title": result.get("title"),
                "risk_level": result.get("analysis", {}).get("risk_level"),
                "sentiment": result.get("analysis", {}).get("sentiment"),
                "details": result.get("analysis", {}).get("details"),
                "summary": result.get("analysis", {}).get("summary")
            }
            for result in analysis_results
        ]
    }
    
    print("Results formatting complete")
    
    return {
        **state,
        "formatted_results": formatted_results
    } 