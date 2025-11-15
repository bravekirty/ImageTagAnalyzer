import axios from 'axios';

// Use absolute URL for Kubernetes environment
const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
});

export const uploadImage = (formData, confidenceThreshold = 30.0, language = 'en') => {
    return api.post('/analyze/', formData, {
        params: {
            confidence_threshold: confidenceThreshold,
            language: language
        },
        headers: {
            'Content-Type': 'multipart/form-data',
        }
    });
};

export const getAnalytics = (limit = 5, min_confidence = 30.0) => {
    return api.get('/analytics/top-tags/', {
        params: {
            limit: limit,
            min_confidence: min_confidence
        }
    });
};

export const getImageStats = () => {
    return api.get('/analytics/stats/');
};

export const analyzeSampleImage = (sampleId, confidenceThreshold = 30.0) => {
    return api.post(`/sample/${sampleId}/analyze`, null, {
        params: { confidence_threshold: confidenceThreshold }
    });
};

export const getSampleImages = () => {
    return api.get('/sample/'); // Fixed: changed from '/sample-images/' to '/sample/'
};

export const loadSampleImages = () => {
    return api.post('/sample/load');
};

// Add better error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error('API Error Details:', {
            message: error.message,
            status: error.response?.status,
            url: error.config?.url,
            data: error.response?.data
        });

        if (error.response?.status === 404) {
            console.error('Endpoint not found. Check if the service is running and routes are correct.');
        } else if (error.response?.status === 500) {
            console.error('Internal server error. Check backend service logs.');
        }

        throw error;
    }
);

// Add request logging for debugging
api.interceptors.request.use(
    (config) => {
        console.log(`Making ${config.method?.toUpperCase()} request to: ${config.baseURL}${config.url}`);
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export default api;