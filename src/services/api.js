import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || '/api'

export const api = axios.create({
    baseURL: API_URL,
    withCredentials: true
})

api.interceptors.response.use(
    (response) => response,
    (error) => {
        // A 401 from /auth/me simply means the user isn't logged in.
        // Do not redirect/reload because the login page needs to remain accessible.
        return Promise.reject(error)
    }
)

export const authAPI = {
    loginGoogle: () => api.get('/auth/google'),
    getMe: () => api.get('/auth/me'),
    logout: () => api.post('/auth/logout')
}

export const profileAPI = {
    get: () => api.get('/profile'),
    update: (data) => api.put('/profile', data),
    uploadResume: (file) => {
        const formData = new FormData()
        formData.append('file', file)
        return api.post('/profile/resume', formData)
    }
}

export const jobsAPI = {
    search: (query, location) =>
        api.post('/jobs/search', { query, location }),

    list: () =>
        api.get('/jobs'),

    get: (id) =>
        api.get(`/jobs/${id}`),

    analyze: (id) =>
        api.post(`/jobs/${id}/analyze`),

    company: (id) =>
        api.post(`/jobs/${id}/company`),

    contact: (id) =>
        api.post(`/jobs/${id}/contact`),

    generateEmail: (id) =>
        api.post(`/jobs/${id}/generate-email`),

    toggleSave: (id) =>
        api.post(`/jobs/${id}/save`)
}

export const gmailAPI = {
    connect: () =>
        api.get('/gmail/connect'),

    status: () =>
        api.get('/gmail/status'),

    disconnect: () =>
        api.post('/gmail/disconnect'),

    send: (data) =>
        api.post('/email/send', data)
}

export const applicationsAPI = {
    list: () =>
        api.get('/applications'),

    create: (data) =>
        api.post('/applications', data),

    update: (id, status) =>
        api.patch(`/applications/${id}`, { status })
}

export const notificationsAPI = {
    list: () =>
        api.get('/notifications'),

    read: (id) =>
        api.patch(`/notifications/${id}/read`)
}