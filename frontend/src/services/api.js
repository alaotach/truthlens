import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export const analyzeProduct = async (productInput) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/analyze`, productInput);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Analysis failed');
  }
};

export const extractClaims = async (productInput) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/extract-claims`, productInput);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Claim extraction failed');
  }
};

export const checkHealth = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/health`);
    return response.data;
  } catch (error) {
    throw new Error('Backend not reachable');
  }
};
