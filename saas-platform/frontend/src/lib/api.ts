import axios from 'axios';

const getBaseUrl = () => {
    if (typeof window === 'undefined') return process.env.PUBLIC_API_URL || 'http://localhost:8000';
    
    const host = window.location.hostname;
    // For local development on localhost
    if (host === 'localhost') {
        return 'http://localhost:8001/api';
    }
    return `http://api.${host}/api`;
};

export const api = axios.create({
    baseURL: getBaseUrl(),
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    },
    withCredentials: true
});

api.interceptors.request.use(config => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export const apiGetDashboardData = async () => {
    const response = await api.get('/dashboard');
    return response.data;
};

export const getClusterDetail = async (id: string) => {
    const response = await api.get(`/dashboard/cluster/${id}`);
    return response.data;
};

export const getUsers = async () => {
    const response = await api.get('/users');
    return response.data;
};

export const createUser = async (userData: any) => {
    const response = await api.post('/users', userData);
    return response.data;
};

export const updateUser = async (id: string | number, userData: any) => {
    const response = await api.put(`/users/${id}`, userData);
    return response.data;
};

export const deleteUser = async (id: string | number) => {
    const response = await api.delete(`/users/${id}`);
    return response.data;
};

// Settings
export const apiGetSettings = () => api.get('/settings');
export const apiUpdateSettings = (settings: any) => api.post('/settings', settings);

// Observability
export const apiGetPve = () => api.get('/observability/pve');
export const apiGetSdn = () => api.get('/observability/sdn');
export const apiGetPbs = () => api.get('/observability/pbs');
export const apiGetPmg = () => api.get('/observability/pmg');

// SDN Management
export const apiCreateSdnZone = (data: any) => api.post('/sdn/zones', data);
export const apiDeleteSdnZone = (cluster_id: number, zone: string) => api.delete('/sdn/zones', { data: { cluster_id, zone } });
export const apiCreateSdnVnet = (data: any) => api.post('/sdn/vnets', data);
export const apiDeleteSdnVnet = (cluster_id: number, vnet: string) => api.delete('/sdn/vnets', { data: { cluster_id, vnet } });
export const apiCreateSdnSubnet = (data: any) => api.post('/sdn/subnets', data);
export const apiDeleteSdnSubnet = (cluster_id: number, vnet: string, subnet: string) => api.delete('/sdn/subnets', { data: { cluster_id, vnet, subnet } });
export const apiCreateSdnFirewallRule = (data: any) => api.post('/sdn/firewall', data);
export const apiDeleteSdnFirewallRule = (cluster_id: number, pos: number) => api.delete('/sdn/firewall', { data: { cluster_id, pos } });
export const apiApplySdn = (cluster_id: number) => api.post('/sdn/apply', { cluster_id });

export default api;
