const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const matchCandidates = async (jobDescription, jobId = null) => {
  const response = await fetch(`${API_BASE_URL}/Api/mike/match`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      job_description: jobDescription,
      job_id: jobId,
    }),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to match candidates');
  }
  
  return response.json();
};

export const healthCheck = async () => {
  const response = await fetch(`${API_BASE_URL}/health`);
  return response.json();
};