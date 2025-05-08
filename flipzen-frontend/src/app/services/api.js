// API service for news search
import { screenClient } from './curl-api-client';

/**
 * Search for negative news about a client
 * @param {Object} clientData - Client data for searching
 * @param {string} clientData.name - Client name (required)
 * @param {string} [clientData.nationality] - Client nationality (optional, for enhanced search)
 * @param {string} [clientData.industry] - Client industry (optional, for enhanced search)
 * @param {string} [clientData.jobTitle] - Client job title (optional, for enhanced search)
 * @returns {Promise<Object>} - Rich response object with report and entity data
 */
export async function searchNews(clientData) {
  try {
    // Call the actual API client
    const response = await screenClient({
      name: clientData.name,
      nationality: clientData.nationality || '',
      industry: clientData.industry || '',
      jobTitle: clientData.jobTitle || '',
    });
    
    return response;
  } catch (error) {
    console.error('Error searching news:', error);
    return { 
      status: "error", 
      message: "Failed to fetch data",
      error: error.message 
    };
  }
}

// Mock data for Elon Musk example
const elonMuskExample = {
  "report": {
    "has_negative_news": true,
    "risk_score": 4.2,
    "summary": "The negative news screening report for Elon Musk, currently serving as Chief Executive Officer in the Information Technology industry, reveals the presence of negative news. The primary concern revolves around some controversial business decisions linked to Example Article 1. This information, sourced from Example News, has been published on 2023-01-01. The severity of the issue is rated at 6, with a confidence level of 7, indicating a moderately high level of certainty regarding the information.",
    "key_concerns": [
      "Controversial business decisions linked to Example Article 1"
    ],
    "findings": [
      {
        "type": "Controversial Business Decisions",
        "description": "Controversial business decisions related to Example Article 1",
        "severity": 6,
        "confidence": 7,
        "source": "Example News",
        "url": "https://example.com/article1",
        "published_at": "2023-01-01"
      }
    ],
    "sources": [
      {
        "url": "https://example.com/article1",
        "title": "",
        "publication": "Example News",
        "date": "2023-01-01"
      }
    ],
    "entity": {
      "full_name": "Elon Musk",
      "variations": [
        "E. Musk",
        "Musk, Elon"
      ],
      "age": "Not Provided",
      "location": "United States",
      "sector": "Information Technology",
      "role": "Chief Executive Officer",
      "description": "Elon Musk is a Chief Executive Officer in the Information Technology industry",
      "name": "Elon Musk",
      "job_title": "Chief Executive Officer",
      "nationality": "United States",
      "industry": "Information Technology"
    },
    "recommendations": [
      "Given the severity and confidence levels associated with the controversial business decisions, it is recommended to further investigate these concerns. It is also advisable to monitor future news related to Elon Musk for any potential negative implications."
    ]
  },
  "entity": {
    "full_name": "Elon Musk",
    "variations": [
      "E. Musk",
      "Musk, Elon"
    ],
    "age": "Not Provided",
    "location": "United States",
    "sector": "Information Technology",
    "role": "Chief Executive Officer",
    "description": "Elon Musk is a Chief Executive Officer in the Information Technology industry",
    "name": "Elon Musk",
    "job_title": "Chief Executive Officer",
    "nationality": "United States",
    "industry": "Information Technology"
  },
  "status": "success"
};

// Generate mock data based on search criteria
function generateMockResponse(clientData) {
  const hasNegativeNews = Math.random() > 0.3; // 70% chance of negative news
  const riskScore = hasNegativeNews ? (Math.random() * 7 + 1).toFixed(1) : (Math.random() * 2).toFixed(1);
  const riskLevel = riskScore > 5 ? "High" : riskScore > 3 ? "Medium" : "Low";
  
  // Default values for missing fields
  const industry = clientData.industry || "Banking";
  const jobTitle = clientData.jobTitle || "Client";
  const nationality = clientData.nationality || "Uruguay";

  // Generate mock findings based on risk level
  const findings = [];
  if (hasNegativeNews) {
    findings.push({
      type: riskLevel === "High" ? "Fraud Allegations" : 
            riskLevel === "Medium" ? "Controversial Business Practices" : 
            "Minor Regulatory Issues",
      description: `Potential issues related to ${clientData.name} in the ${industry} sector`,
      severity: riskLevel === "High" ? 8 : riskLevel === "Medium" ? 5 : 2,
      confidence: Math.floor(Math.random() * 4) + 5, // 5-9
      source: "El Observador",
      url: "https://example.com/article1",
      published_at: "2023-05-15"
    });
  }

  return {
    "report": {
      "has_negative_news": hasNegativeNews,
      "risk_score": Number.parseFloat(riskScore),
      "summary": hasNegativeNews ? 
        `The negative news screening for ${clientData.name}, a ${jobTitle} in the ${industry} industry, reveals ${riskLevel.toLowerCase()} risk concerns.` : 
        `No significant negative news has been found for ${clientData.name}, a ${jobTitle} in the ${industry} industry.`,
      "key_concerns": hasNegativeNews ? 
        [`${riskLevel} risk indicators related to ${industry} sector activities`] : [],
      "findings": findings,
      "sources": hasNegativeNews ? [
        {
          "url": "https://example.com/article1",
          "title": `News about ${clientData.name}`,
          "publication": "El Observador",
          "date": "2023-05-15"
        }
      ] : [],
      "entity": {
        "full_name": clientData.name,
        "variations": clientData.name.includes(' ') ? [`${clientData.name.split(' ')[1]}, ${clientData.name.split(' ')[0]}`] : [],
        "age": "Not Provided",
        "location": nationality,
        "sector": industry,
        "role": jobTitle,
        "description": `${clientData.name} is a ${jobTitle} in the ${industry} industry`,
        "name": clientData.name,
        "job_title": jobTitle,
        "nationality": nationality,
        "industry": industry
      },
      "recommendations": hasNegativeNews ? [
        `Based on the ${riskLevel.toLowerCase()} risk level, further review is recommended before proceeding with this client.`
      ] : [
        "No special measures needed based on news screening results."
      ]
    },
    "entity": {
      "full_name": clientData.name,
      "variations": clientData.name.includes(' ') ? [`${clientData.name.split(' ')[1]}, ${clientData.name.split(' ')[0]}`] : [],
      "age": "Not Provided",
      "location": nationality,
      "sector": industry,
      "role": jobTitle,
      "description": `${clientData.name} is a ${jobTitle} in the ${industry} industry`,
      "name": clientData.name,
      "job_title": jobTitle,
      "nationality": nationality,
      "industry": industry
    },
    "status": "success"
  };
} 