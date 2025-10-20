/**
 * Local Storage Utility Module
 * Manages user session data in browser localStorage
 */

const Storage = {
    /**
     * Save user data after login
     * @param {number} userId - User ID
     * @param {string} email - User email
     */
    saveUser(userId, email) {
        localStorage.setItem(CONFIG.APP_CONFIG.storageKeys.userId, userId);
        localStorage.setItem(CONFIG.APP_CONFIG.storageKeys.userEmail, email);
    },

    /**
     * Get saved user ID
     * @returns {number|null} User ID or null if not found
     */
    getUserId() {
        const userId = localStorage.getItem(CONFIG.APP_CONFIG.storageKeys.userId);
        return userId ? parseInt(userId) : null;
    },

    /**
     * Get saved user email
     * @returns {string|null} User email or null if not found
     */
    getUserEmail() {
        return localStorage.getItem(CONFIG.APP_CONFIG.storageKeys.userEmail);
    },

    /**
     * Check if user is logged in
     * @returns {boolean} True if user data exists
     */
    isLoggedIn() {
        return this.getUserId() !== null;
    },

    /**
     * Save current session data
     * @param {number} sessionId - Session ID
     * @param {string} modelName - Model name
     */
    saveSession(sessionId, modelName) {
        localStorage.setItem(CONFIG.APP_CONFIG.storageKeys.currentSessionId, sessionId);
        localStorage.setItem(CONFIG.APP_CONFIG.storageKeys.currentModel, modelName);
    },

    /**
     * Get current session ID
     * @returns {number|null} Session ID or null if not found
     */
    getSessionId() {
        const sessionId = localStorage.getItem(CONFIG.APP_CONFIG.storageKeys.currentSessionId);
        return sessionId ? parseInt(sessionId) : null;
    },

    /**
     * Get current model name
     * @returns {string|null} Model name or null if not found
     */
    getCurrentModel() {
        return localStorage.getItem(CONFIG.APP_CONFIG.storageKeys.currentModel);
    },

    /**
     * Clear session data (but keep user data)
     */
    clearSession() {
        localStorage.removeItem(CONFIG.APP_CONFIG.storageKeys.currentSessionId);
        localStorage.removeItem(CONFIG.APP_CONFIG.storageKeys.currentModel);
    },

    /**
     * Clear all data (logout)
     */
    clearAll() {
        localStorage.removeItem(CONFIG.APP_CONFIG.storageKeys.userId);
        localStorage.removeItem(CONFIG.APP_CONFIG.storageKeys.userEmail);
        localStorage.removeItem(CONFIG.APP_CONFIG.storageKeys.currentSessionId);
        localStorage.removeItem(CONFIG.APP_CONFIG.storageKeys.currentModel);
    },

    /**
     * Get complete user state
     * @returns {Object} User state object
     */
    getState() {
        return {
            userId: this.getUserId(),
            email: this.getUserEmail(),
            sessionId: this.getSessionId(),
            modelName: this.getCurrentModel(),
            isLoggedIn: this.isLoggedIn(),
        };
    },
};

// Export Storage object
window.Storage = Storage;
