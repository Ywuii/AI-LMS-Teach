import axios, { type AxiosInstance } from "axios";

// Dify请求配置
axios.defaults.headers["Content-Type"] = "application/json;charset=utf-8";
const service: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_APP_BASE_API,
  timeout: 100000
});

service.interceptors.request.use(
  config => {
    config.headers.Authorization = `Bearer app-OodhYEvNsE0GBjv2vkxncF5F`;
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

service.interceptors.response.use(
  response => {
    return response.data;
  },
  error => {
    return Promise.reject(error);
  }
);

export default service;
