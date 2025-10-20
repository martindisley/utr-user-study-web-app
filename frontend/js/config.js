/**
 * Configuration file for the Unlearning to Rest User Study
 * Contains API endpoints, constants, and application settings
 */

// API Configuration
const API_BASE_URL = window.ENV?.API_BASE_URL || window.location.origin;

const API_ENDPOINTS = {
    login: `${API_BASE_URL}/api/login`,
    models: `${API_BASE_URL}/api/models`,
    session: `${API_BASE_URL}/api/session`,
    chat: `${API_BASE_URL}/api/chat`,
    reset: `${API_BASE_URL}/api/reset`,
    health: `${API_BASE_URL}/health`,
};

// Application Constants
const APP_CONFIG = {
    appName: 'Unlearning to Rest User Study',
    storageKeys: {
        userId: 'utr_user_id',
        userEmail: 'utr_user_email',
        currentSessionId: 'utr_session_id',
        currentModel: 'utr_current_model',
    },
    emailRegex: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
};

// Study Instructions (displayed in chat interface)
const STUDY_INSTRUCTIONS = `
<h3 class="font-semibold text-lg mb-2">Welcome to the User Study</h3>
<p class="mb-3">Thank you for participating in this design ideation study. You will be using this chat interface to explore ideas with an AI assistant.</p>
<h4 class="font-semibold mb-1">Instructions:</h4>
<ul class="list-disc list-inside space-y-1 text-sm">
    <li>Engage naturally with the AI to explore design concepts</li>
    <li>Feel free to ask questions and build on ideas</li>
    <li>Use "Reset Chat" to clear the conversation and start fresh with the same model</li>
    <li>Use "New Session" to return to model selection and try a different model</li>
</ul>
<p class="mt-3 text-sm text-gray-600">All conversations are automatically saved for research purposes.</p>
`;

// Export configuration
window.CONFIG = {
    API_BASE_URL,
    API_ENDPOINTS,
    APP_CONFIG,
    STUDY_INSTRUCTIONS,
};
