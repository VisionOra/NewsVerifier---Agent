/**
 * This service handles API requests to the backend screening service
 * It follows the format shown in the screenshot with curl-like requests
 */

// Config for the real API
const API_CONFIG = {
  baseUrl: process.env.NEXT_PUBLIC_API_URL, // Replace with your actual API URL
  endpoints: {
    screen: '/screen',
  }
};

/**
 * Send a screening request to the backend API
 * @param {Object} clientData - Client data to screen
 * @param {string} clientData.name - Client name (required)
 * @param {string} [clientData.nationality] - Client nationality
 * @param {string} [clientData.industry] - Client industry
 * @param {string} [clientData.jobTitle] - Client job title
 * @returns {Promise<Object>} - API response data
 */
export async function screenClient(clientData) {
  try {
    // Prepare the request payload exactly as shown in the screenshot
    const requestPayload = {
      name: clientData.name || '',
      nationality: clientData.nationality || '',
      industry: clientData.industry || '',
      jobTitle: clientData.jobTitle || '',
    };
    
    console.log('Sending API request:', requestPayload);
    
    // Make the API call
    const response = await fetch(`${API_CONFIG.baseUrl}${API_CONFIG.endpoints.screen}`, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestPayload),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API error: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    console.log('API response received:', data);
    return data;
  } catch (error) {
    console.error('Error during API call:', error);
    // Re-throw the error so it can be handled by the caller
    throw error;
  }
} 