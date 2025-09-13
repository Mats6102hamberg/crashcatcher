import { api } from './api';

export const incidentService = {
  async getIncidents(skip = 0, limit = 100) {
    const response = await api.get(`/incidents/?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  async getIncident(id) {
    const response = await api.get(`/incidents/${id}`);
    return response.data;
  },

  async createIncident(incident) {
    const response = await api.post('/incidents/', incident);
    return response.data;
  },

  async updateIncidentStatus(id, status) {
    const response = await api.put(`/incidents/${id}/status`, { status });
    return response.data;
  },

  async uploadLogFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/upload-log', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }
};
