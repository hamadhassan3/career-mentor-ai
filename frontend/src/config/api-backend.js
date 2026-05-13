import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

const backendClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

backendClient.interceptors.request.use((config) => {
  const tokens = localStorage.getItem('tokens');
  if (tokens) {
    const { access } = JSON.parse(tokens);
    config.headers.Authorization = `Bearer ${access}`;
  }
  return config;
});

backendClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const tokens = localStorage.getItem('tokens');
      if (tokens) {
        try {
          const { refresh } = JSON.parse(tokens);
          const res = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, { refresh });
          const newTokens = { access: res.data.access, refresh };
          localStorage.setItem('tokens', JSON.stringify(newTokens));
          originalRequest.headers.Authorization = `Bearer ${res.data.access}`;
          return backendClient(originalRequest);
        } catch {
          localStorage.removeItem('tokens');
          window.location.href = '/login';
        }
      }
    }

    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (data) => backendClient.post('/auth/register/', data),
  login: (data) => backendClient.post('/auth/login/', data),
  totpLoginVerify: (data) => backendClient.post('/auth/totp/login/', data),
  totpSetup: () => backendClient.get('/auth/totp/setup/'),
  totpConfirm: (data) => backendClient.post('/auth/totp/confirm/', data),
  me: () => backendClient.get('/auth/me/'),
  updateMe: (data) => backendClient.put('/auth/me/', data),
  changePassword: (data) => backendClient.post('/auth/change-password/', data),
  passwordResetRequest: (data) => backendClient.post('/auth/password-reset/', data),
  passwordResetConfirm: (data) => backendClient.post('/auth/password-reset/confirm/', data),
};

export const resumeAPI = {
  getResumes: () => backendClient.get('/resumes/'),
  getResume: (id) => backendClient.get(`/resumes/${id}/`),
  createResume: (data) => backendClient.post('/resumes/upload/', data),
  updateResume: (id, data) => backendClient.put(`/resumes/${id}/`, data),
  deleteResume: (id) => backendClient.delete(`/resumes/${id}/`),
  getLatestResume: () => backendClient.get('/resumes/latest/'),
  getActiveResume: () => backendClient.get('/resumes/active/'),
  activateResume: (id) => backendClient.post(`/resumes/${id}/activate/`),
  
  // Next Best Step API
  getNextBestStep: () => backendClient.get('/resumes/next-step/'),
  saveNextBestStep: (data) => backendClient.post('/resumes/next-step/save/', data),
  
  // Career Pathway API
  getCareerPathway: () => backendClient.get('/resumes/career-pathway/'),
  saveCareerPathway: (data) => backendClient.post('/resumes/career-pathway/save/', data),
  
  // Clear recommendations
  clearRecommendations: () => backendClient.delete('/resumes/recommendations/clear/'),
  
  // Course recommendations
  getCourseRecommendations: () => backendClient.get('/resumes/courses/'),
};

export const chatAPI = {
  sendMessage: (data) => backendClient.post('/chat/', data),
  getConversationHistory: (conversationId = null) => backendClient.get('/chat/', {
    params: conversationId ? { conversation_id: conversationId } : {}
  }),
};

export default backendClient;
