/**
 * API Client Module
 * Handles all HTTP requests to the backend API
 */

const API = {
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
     * Get concepts saved for a session
     * @param {number} sessionId - Session ID
     * @returns {Promise<Object>} { concepts: [...] }
     */
    async getConcepts(sessionId) {
        const response = await fetch(CONFIG.API_ENDPOINTS.sessionConcepts(sessionId));

        if (!response.ok) {
            throw new Error('Failed to fetch concepts');
        }

        return await response.json();
    },

    /**
     * Create a new concept for a session
     * @param {number} sessionId - Session ID
     * @param {Object} payload - { title, content, source_message_id }
     * @returns {Promise<Object>} Concept data
     */
    async createConcept(sessionId, payload) {
        const response = await fetch(CONFIG.API_ENDPOINTS.sessionConcepts(sessionId), {
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
                throw new Error(error.error || 'Failed to save concept');
            } catch (parseError) {
                throw new Error(message || 'Failed to save concept');
            }
        }

        return await response.json();
    },

    /**
     * Update an existing concept
     * @param {number} conceptId - Concept ID
     * @param {Object} payload - Updated concept data
     * @returns {Promise<Object>} Updated concept
     */
    async updateConcept(conceptId, payload) {
        const response = await fetch(`${CONFIG.API_ENDPOINTS.concepts}/${conceptId}`, {
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
                throw new Error(error.error || 'Failed to update concept');
            } catch (parseError) {
                throw new Error(message || 'Failed to update concept');
            }
        }

        return await response.json();
    },

    /**
     * Delete a concept
     * @param {number} conceptId - Concept ID
     * @returns {Promise<Object>} { success: true }
     */
    async deleteConcept(conceptId) {
        const response = await fetch(`${CONFIG.API_ENDPOINTS.concepts}/${conceptId}`, {
            method: 'DELETE',
        });

        if (!response.ok) {
            const message = await response.text();
            try {
                const error = JSON.parse(message || '{}');
                throw new Error(error.error || 'Failed to delete concept');
            } catch (parseError) {
                throw new Error(message || 'Failed to delete concept');
            }
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
