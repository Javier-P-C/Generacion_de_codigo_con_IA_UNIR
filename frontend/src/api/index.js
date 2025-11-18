import apiClient from './client';

export const authAPI = {
  login: async (username, password) => {
    const { data } = await apiClient.post('/auth/login/', { username, password });
    return data;
  },
  refresh: async (refreshToken) => {
    const { data } = await apiClient.post('/auth/refresh/', { refresh: refreshToken });
    return data;
  },
};

export const employeeAPI = {
  list: async () => {
    const { data } = await apiClient.get('/employees/');
    return data;
  },
  get: async (id) => {
    const { data } = await apiClient.get(`/employees/${id}/`);
    return data;
  },
  create: async (employee) => {
    const { data } = await apiClient.post('/employees/', employee);
    return data;
  },
  update: async (id, employee) => {
    const { data } = await apiClient.put(`/employees/${id}/`, employee);
    return data;
  },
  delete: async (id) => {
    await apiClient.delete(`/employees/${id}/`);
  },
};

export const productAPI = {
  list: async () => {
    const { data } = await apiClient.get('/products/');
    return data;
  },
  get: async (id) => {
    const { data } = await apiClient.get(`/products/${id}/`);
    return data;
  },
  create: async (product) => {
    const { data } = await apiClient.post('/products/', product);
    return data;
  },
  update: async (id, product) => {
    const { data } = await apiClient.put(`/products/${id}/`, product);
    return data;
  },
  delete: async (id) => {
    await apiClient.delete(`/products/${id}/`);
  },
};

export const inventoryAPI = {
  list: async () => {
    const { data } = await apiClient.get('/inventory/');
    return data;
  },
  increase: async (id, amount) => {
    const { data } = await apiClient.post(`/inventory/${id}/increase/`, { amount });
    return data;
  },
};

export const salesAPI = {
  list: async () => {
    const { data } = await apiClient.get('/sales/');
    return data;
  },
  get: async (id) => {
    const { data } = await apiClient.get(`/sales/${id}/`);
    return data;
  },
  create: async (sale) => {
    const { data } = await apiClient.post('/sales/', sale);
    return data;
  },
  getDetails: async (id) => {
    const { data } = await apiClient.get(`/sales/${id}/details/`);
    return data;
  },
};
