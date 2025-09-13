import { api } from './api';

export const authService = {
  async login(username, password) {
    const response = await api.post('/auth/login', { username, password });
    return response.data;
  },

  async register(userData) {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  setToken(token) {
    localStorage.setItem('authToken', token);
  },

  getToken() {
    return localStorage.getItem('authToken');
  },

  removeToken() {
    localStorage.removeItem('authToken');
  },

  isAuthenticated() {
    return !!this.getToken();
  }
};
