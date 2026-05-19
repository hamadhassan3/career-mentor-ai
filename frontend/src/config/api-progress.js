import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const progressAPI = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

progressAPI.interceptors.request.use((config) => {
  const tokens = localStorage.getItem('tokens');
  if (tokens) {
    const { access } = JSON.parse(tokens);
    config.headers.Authorization = `Bearer ${access}`;
  }
  return config;
});

progressAPI.interceptors.response.use(
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
          return progressAPI(originalRequest);
        } catch {
          localStorage.removeItem('tokens');
          window.location.href = '/login';
        }
      }
    }

    return Promise.reject(error);
  }
);

export const progressService = {
  async getAchievements() {
    const response = await progressAPI.get('/progress/achievements/');
    return response.data;
  },

  async createAchievement(skill, imageFile) {
    const formData = new FormData();
    formData.append('skill', skill);
    formData.append('image', imageFile);
    
    const response = await progressAPI.post('/progress/achievements/create/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async deleteAchievement(achievementId) {
    const response = await progressAPI.delete(`/progress/achievements/${achievementId}/delete/`);
    return response.data;
  },

};

export default progressAPI;