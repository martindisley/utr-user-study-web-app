/**
 * API Client Module
 * Handles all HTTP requests to the backend API
 */

const API = {
    baseURL: CONFIG.API_BASE_URL,
    
    /**
     * Login with email
     * @param {string} email - User's email address
     * @returns {Promise<Object>} User data { user_id, email, is_new_user }
     */
    async login(email) {
        const response = await fetch(CONFIG.API_ENDPOINTS.login, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email }),
        });

        if (!response.ok) {
            const message = await response.text();
            try {
                const error = JSON.parse(message || '{}');
                throw new Error(error.error || 'Login failed');
            } catch (parseError) {
                throw new Error(message || 'Login failed');
            }
        }

        return await response.json();
    },

    /**
     * Get available models
     * @returns {Promise<Object>} { models: [...] }
     */
    async getModels() {
        const response = await fetch(CONFIG.API_ENDPOINTS.models);

        if (!response.ok) {
            throw new Error('Failed to fetch models');
        }

        return await response.json();
    },

    /**
     * Create a new chat session
     * @param {number} userId - User ID
     * @param {string} modelName - Model identifier
     * @returns {Promise<Object>} Session data { id, user_id, model_name, created_at }
     */
    async createSession(userId, modelName) {
        const response = await fetch(CONFIG.API_ENDPOINTS.session, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: userId,
                model_name: modelName,
            }),
        });

        if (!response.ok) {
            const message = await response.text();
            try {
                const error = JSON.parse(message || '{}');
                throw new Error(error.error || 'Failed to create session');
            } catch (parseError) {
                throw new Error(message || 'Failed to create session');
            }
        }

        return await response.json();
    },

    /**
     * Send a chat message
     * @param {number} sessionId - Session ID
     * @param {string} message - User's message
     * @returns {Promise<Object>} { response, message_id, timestamp }
     */
    async sendMessage(sessionId, message) {
        const response = await fetch(CONFIG.API_ENDPOINTS.chat, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
                message: message,
            }),
        });

        if (!response.ok) {
            const message = await response.text();
            try {
                const error = JSON.parse(message || '{}');
                throw new Error(error.error || 'Failed to send message');
            } catch (parseError) {
                throw new Error(message || 'Failed to send message');
            }
        }

        return await response.json();
    },

    /**
     * Reset the current session by clearing model context in place.
     * @param {number} sessionId - Current session ID
     * @returns {Promise<Object>} { success, session_id, cleared_messages, ollama_cleared }
     */
    async resetSession(sessionId) {
        const response = await fetch(CONFIG.API_ENDPOINTS.reset, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
            }),
        });

        if (!response.ok) {
            const message = await response.text();
            try {
                const error = JSON.parse(message || '{}');
                throw new Error(error.error || 'Failed to reset session');
            } catch (parseError) {
                throw new Error(message || 'Failed to reset session');
            }
        }

        return await response.json();
    },

    /**
     * Get prompts saved for a session
     * @param {number} sessionId - Session ID
     * @returns {Promise<Object>} { prompts: [...] }
     */
    async getPrompts(sessionId) {
        const response = await fetch(CONFIG.API_ENDPOINTS.sessionPrompts(sessionId));

        if (!response.ok) {
            throw new Error('Failed to fetch prompts');
        }

        return await response.json();
    },

    /**
     * Create a new prompt for a session
     * @param {number} sessionId - Session ID
     * @param {Object} payload - { title, content, source_message_id }
     * @returns {Promise<Object>} Prompt data
     */
    async createPrompt(sessionId, payload) {
        const response = await fetch(CONFIG.API_ENDPOINTS.sessionPrompts(sessionId), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const message = await response.text();
            try {
                const error = JSON.parse(message || '{}');
                throw new Error(error.error || 'Failed to save prompt');
            } catch (parseError) {
                throw new Error(message || 'Failed to save prompt');
            }
        }

        return await response.json();
    },

    /**
     * Update an existing prompt
     * @param {number} promptId - Prompt ID
     * @param {Object} payload - Updated prompt data
     * @returns {Promise<Object>} Updated prompt
     */
    async updatePrompt(promptId, payload) {
        const response = await fetch(`${CONFIG.API_ENDPOINTS.prompts}/${promptId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const message = await response.text();
            try {
                const error = JSON.parse(message || '{}');
                throw new Error(error.error || 'Failed to update prompt');
            } catch (parseError) {
                throw new Error(message || 'Failed to update prompt');
            }
        }

        return await response.json();
    },

    /**
     * Delete a prompt
     * @param {number} promptId - Prompt ID
     * @returns {Promise<Object>} { success: true }
     */
    async deletePrompt(promptId) {
        const response = await fetch(`${CONFIG.API_ENDPOINTS.prompts}/${promptId}`, {
            method: 'DELETE',
        });

        if (!response.ok) {
            const message = await response.text();
            try {
                const error = JSON.parse(message || '{}');
                throw new Error(error.error || 'Failed to delete prompt');
            } catch (parseError) {
                throw new Error(message || 'Failed to delete prompt');
            }
        }

        return await response.json();
    },

    /**
     * End a chat session and trigger image generation
     * @param {number} sessionId - Session ID
     * @returns {Promise<Object>} { success, session_id, prompt_count, images_generated }
     */
    async endSession(sessionId) {
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/end-session`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
            }),
        });

        if (!response.ok) {
            const message = await response.text();
            try {
                const error = JSON.parse(message || '{}');
                throw new Error(error.error || 'Failed to end session');
            } catch (parseError) {
                throw new Error(message || 'Failed to end session');
            }
        }

        return await response.json();
    },

    /**
     * Get images for a session
     * @param {number} sessionId - Session ID
     * @returns {Promise<Object>} { success, images: [...] }
     */
    async getImages(sessionId) {
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/images/${sessionId}`);

        if (!response.ok) {
            throw new Error('Failed to fetch images');
        }

        return await response.json();
    },

    /**
     * Check server health
     * @returns {Promise<Object>} { status, service }
     */
    async checkHealth() {
        const response = await fetch(CONFIG.API_ENDPOINTS.health);

        if (!response.ok) {
            throw new Error('Server health check failed');
        }

        return await response.json();
    },
};

// Export API object
window.API = API;
