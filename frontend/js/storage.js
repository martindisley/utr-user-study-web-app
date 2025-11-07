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
        localStorage.removeItem('preActivityCompleted');
        localStorage.removeItem('activityCount');
        localStorage.removeItem('studyCompleted');
        localStorage.removeItem('completedModels');
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
            preActivityCompleted: this.getPreActivityCompleted(),
            activityCount: this.getActivityCount(),
        };
    },

    /**
     * Set pre-activity questionnaire completion status
     * @param {boolean} completed - Whether pre-activity is completed
     */
    setPreActivityCompleted(completed) {
        localStorage.setItem('preActivityCompleted', completed ? 'true' : 'false');
    },

    /**
     * Get pre-activity questionnaire completion status
     * @returns {boolean} True if pre-activity questionnaire completed
     */
    getPreActivityCompleted() {
        return localStorage.getItem('preActivityCompleted') === 'true';
    },

    /**
     * Get current activity count (number of models tested)
     * @returns {number} Activity count
     */
    getActivityCount() {
        const count = localStorage.getItem('activityCount');
        return count ? parseInt(count) : 0;
    },

    /**
     * Increment activity count
     */
    incrementActivityCount() {
        const current = this.getActivityCount();
        localStorage.setItem('activityCount', (current + 1).toString());
    },

    /**
     * Reset activity tracking (for new study)
     */
    resetActivityTracking() {
        localStorage.removeItem('preActivityCompleted');
        localStorage.removeItem('activityCount');
    },

    /**
     * Set study completed status
     * @param {boolean} completed - Whether study is completed
     */
    setStudyCompleted(completed) {
        localStorage.setItem('studyCompleted', completed ? 'true' : 'false');
    },

    /**
     * Get study completed status
     * @returns {boolean} True if study is completed
     */
    getStudyCompleted() {
        return localStorage.getItem('studyCompleted') === 'true';
    },

    /**
     * Get completed model IDs
     * @returns {Array<string>} Array of completed model IDs
     */
    getCompletedModels() {
        const completed = localStorage.getItem('completedModels');
        return completed ? JSON.parse(completed) : [];
    },

    /**
     * Add a model to the completed list
     * @param {string} modelId - Model ID to mark as completed
     */
    addCompletedModel(modelId) {
        const completed = this.getCompletedModels();
        if (!completed.includes(modelId)) {
            completed.push(modelId);
            localStorage.setItem('completedModels', JSON.stringify(completed));
        }
    },

    /**
     * Check if a model has been completed
     * @param {string} modelId - Model ID to check
     * @returns {boolean} True if model has been completed
     */
    isModelCompleted(modelId) {
        return this.getCompletedModels().includes(modelId);
    },
};

// Export Storage object
window.Storage = Storage;
