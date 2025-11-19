/**
 * API Client Module
 * Handles all HTTP requests to the backend API
 */

const API = {
    baseURL: CONFIG.API_BASE_URL,
    
    /**
     * Parse error response from API
     * @param {Response} response - Fetch response object
     * @param {string} defaultMessage - Default error message
     * @returns {Promise<Error>} Error object with message
     */
    async _parseError(response, defaultMessage) {
        const message = await response.text();
        try {
            const error = JSON.parse(message || '{}');
            throw new Error(error.error || defaultMessage);
        } catch (parseError) {
            throw new Error(message || defaultMessage);
        }
    },
    
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
            await this._parseError(response, 'Login failed');
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
            await this._parseError(response, 'Failed to create session');
        }

        return await response.json();
    },

    /**
     * Send a chat message with streaming response support
     * @param {number} sessionId - Session ID
     * @param {string} message - User's message
     * @param {Object} [options] - Stream handling options
     * @param {(delta: string) => void} [options.onToken] - Callback for streamed tokens
     * @param {AbortSignal} [options.signal] - Optional abort signal
     * @returns {Promise<Object>} { response, message_id, timestamp }
     */
    async sendMessage(sessionId, message, { onToken, signal } = {}) {
        const response = await fetch(CONFIG.API_ENDPOINTS.chat, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'text/event-stream',
            },
            body: JSON.stringify({
                session_id: sessionId,
                message: message,
            }),
            signal,
        });

        if (!response.ok) {
            await this._parseError(response, 'Failed to send message');
        }

        const contentType = response.headers.get('content-type') || '';

        // Fallback to non-streaming JSON response if backend does not stream
        if (!contentType.includes('text/event-stream')) {
            return await response.json();
        }

        if (!response.body) {
            throw new Error('No response body received from server');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let finalPayload = null;

        const processBuffer = (rawBuffer) => {
            const parts = rawBuffer.replace(/\r\n/g, '\n').split('\n\n');
            // The last element may be incomplete; keep it in the buffer.
            buffer = parts.pop() ?? '';

            for (const eventChunk of parts) {
                if (!eventChunk.trim()) {
                    continue;
                }

                const lines = eventChunk.split('\n');
                const dataLines = [];
                for (const line of lines) {
                    if (!line.startsWith('data:')) {
                        continue;
                    }
                    dataLines.push(line.slice(5).trimStart());
                }

                if (!dataLines.length) {
                    continue;
                }

                const payloadStr = dataLines.join('\n');
                let payload;

                try {
                    payload = JSON.parse(payloadStr);
                } catch (error) {
                    console.warn('Failed to parse stream payload', error);
                    continue;
                }

                if (payload.type === 'token') {
                    if (typeof onToken === 'function' && payload.delta) {
                        onToken(payload.delta);
                    }
                } else if (payload.type === 'end') {
                    finalPayload = payload;
                } else if (payload.type === 'error') {
                    throw new Error(payload.error || 'Streaming error');
                }
            }
        };

        try {
            while (true) {
                const { value, done } = await reader.read();
                if (done) {
                    buffer += decoder.decode();
                    break;
                }

                buffer += decoder.decode(value, { stream: true });
                processBuffer(buffer);
            }

            if (buffer) {
                processBuffer(buffer);
            }
        } finally {
            reader.releaseLock();
        }

        if (finalPayload) {
            return {
                response: finalPayload.content,
                message_id: finalPayload.message_id,
                timestamp: finalPayload.timestamp,
            };
        }

        throw new Error('Stream ended without a completion message');
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
            await this._parseError(response, 'Failed to reset session');
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
            await this._parseError(response, 'Failed to save prompt');
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
            await this._parseError(response, 'Failed to update prompt');
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
            await this._parseError(response, 'Failed to delete prompt');
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
            await this._parseError(response, 'Failed to end session');
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

    /**
     * Upload a moodboard image
     * @param {number} userId - User ID
     * @param {File} file - Image file to upload
     * @returns {Promise<Object>} { success, image }
     */
    async uploadMoodboardImage(userId, file) {
        const formData = new FormData();
        formData.append('user_id', userId);
        formData.append('file', file);

        const response = await fetch(`${CONFIG.API_BASE_URL}/api/moodboard/upload`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            await this._parseError(response, 'Failed to upload image');
        }

        return await response.json();
    },

    /**
     * Get all moodboard images for a user
     * @param {number} userId - User ID
     * @returns {Promise<Object>} { success, images: [...] }
     */
    async getMoodboard(userId) {
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/moodboard/${userId}`);

        if (!response.ok) {
            throw new Error('Failed to fetch moodboard images');
        }

        return await response.json();
    },

    /**
     * Delete a moodboard image
     * @param {number} imageId - Image ID
     * @returns {Promise<Object>} { success, message }
     */
    async deleteMoodboardImage(imageId) {
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/moodboard/image/${imageId}`, {
            method: 'DELETE',
        });

        if (!response.ok) {
            await this._parseError(response, 'Failed to delete image');
        }

        return await response.json();
    },

    /**
     * Clear all moodboard images for a user
     * @param {number} userId - User ID
     * @returns {Promise<Object>} { success, message, deleted_count }
     */
    async clearMoodboard(userId) {
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/moodboard/clear/${userId}`, {
            method: 'DELETE',
        });

        if (!response.ok) {
            await this._parseError(response, 'Failed to clear moodboard');
        }

        return await response.json();
    },

    /**
     * Submit a questionnaire response
     * @param {Object} payload - { user_id, session_id (optional), questionnaire_type, responses }
     * @returns {Promise<Object>} { success, response_id, message }
     */
    async submitQuestionnaire(payload) {
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/questionnaire/submit`, {
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
                throw new Error(error.error || 'Failed to submit questionnaire');
            } catch (parseError) {
                throw new Error(message || 'Failed to submit questionnaire');
            }
        }

        return await response.json();
    },

    /**
     * Get questionnaire responses for a user
     * @param {number} userId - User ID
     * @param {string} questionnaireType - Optional filter ('pre-activity' or 'post-activity')
     * @param {number} sessionId - Optional session ID filter
     * @returns {Promise<Object>} { success, responses }
     */
    async getQuestionnaireResponses(userId, questionnaireType = null, sessionId = null) {
        let url = `${CONFIG.API_BASE_URL}/api/questionnaire/user/${userId}`;
        const params = new URLSearchParams();
        
        if (questionnaireType) {
            params.append('questionnaire_type', questionnaireType);
        }
        if (sessionId) {
            params.append('session_id', sessionId);
        }
        
        if (params.toString()) {
            url += `?${params.toString()}`;
        }

        const response = await fetch(url);

        if (!response.ok) {
            throw new Error('Failed to fetch questionnaire responses');
        }

        return await response.json();
    },

    /**
     * Check if a questionnaire has been completed
     * @param {number} userId - User ID
     * @param {string} questionnaireType - 'pre-activity' or 'post-activity'
     * @param {number} sessionId - Optional session ID (required for post-activity)
     * @returns {Promise<Object>} { completed, response_id (if completed) }
     */
    async checkQuestionnaireCompletion(userId, questionnaireType, sessionId = null) {
        const payload = {
            user_id: userId,
            questionnaire_type: questionnaireType
        };
        
        if (sessionId) {
            payload.session_id = sessionId;
        }

        const response = await fetch(`${CONFIG.API_BASE_URL}/api/questionnaire/check`, {
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
                throw new Error(error.error || 'Failed to check questionnaire completion');
            } catch (parseError) {
                throw new Error(message || 'Failed to check questionnaire completion');
            }
        }

        return await response.json();
    },

    /**
     * Get completed models for a user
     * @param {number} userId - User ID
     * @returns {Promise<Object>} { completed_models: ['model1', 'model2'] }
     */
    async getCompletedModels(userId) {
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/completed-models/${userId}`);

        if (!response.ok) {
            throw new Error('Failed to fetch completed models');
        }

        return await response.json();
    },

    /**
     * Get study status for a user
     * @param {number} userId - User ID
     * @returns {Promise<Object>} Study status including completion info
     */
    async getStudyStatus(userId) {
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/study-status/${userId}`);

        if (!response.ok) {
            throw new Error('Failed to fetch study status');
        }

        return await response.json();
    },

    /**
     * Get the next assigned model for a user
     * @param {number} userId - User ID
     * @returns {Promise<Object>} { model_id, model_name, model_description, activity_number }
     */
    async getNextModel(userId) {
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/user/${userId}/next-model`);

        if (!response.ok) {
            await this._parseError(response, 'Failed to get next model');
        }

        return await response.json();
    },
};

// Export API object
window.API = API;
