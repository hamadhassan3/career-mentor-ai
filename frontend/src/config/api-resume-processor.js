import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/resume-processor`,
  timeout: 60000,
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
    return apiClient.post('/resumes/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  getAllSkills: () => {
    return apiClient.get('/skills/all');
  },
  
  getITSkills: () => {
    return apiClient.get('/skills/it');
  },
  
  getSoftSkills: () => {
    return apiClient.get('/skills/soft');
  },
  
  getLanguages: () => {
    return apiClient.get('/skills/languages');
  },

  getDesignations: () => {
    return apiClient.get('/designations')
  },

  predictNextSkills: ({ itSkills = [], softSkills = [], designation = "" }) => {
    console.log(itSkills, softSkills, designation);
    return apiClient.post('/predict', {
      it_skill_categories: itSkills,
      soft_skills: softSkills,
      desired_designation: designation,
    });
  },

  predictNextSingleSkill: ({ itSkills = [], softSkills = [], designation = "" }) => {
    console.log(itSkills, softSkills, designation);
    return apiClient.post('/predict_next_skill', {
      it_skill_categories: itSkills,
      soft_skills: softSkills,
      desired_designation: designation,
    });
  },
};

export default apiClient;