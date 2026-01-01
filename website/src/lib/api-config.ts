const isDevelopment = process.env.NODE_ENV === 'development';

export const API_BASE_URL = isDevelopment ? 'http://127.0.0.1:5000/' : '/';
