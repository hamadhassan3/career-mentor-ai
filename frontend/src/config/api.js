import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const resumeAPI = {
  uploadResume: (formData) => {
    return apiClient.post('/resumes/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  getAllSkills: () => {
    return apiClient.get('/resumes/skills/all/');
  },
  
  getITSkills: () => {
    return apiClient.get('/resumes/skills/it/');
  },
  
  getSoftSkills: () => {
    return apiClient.get('/resumes/skills/soft/');
  },
  
  getLanguages: () => {
    return apiClient.get('/resumes/skills/languages/');
  },
};

export default apiClient;