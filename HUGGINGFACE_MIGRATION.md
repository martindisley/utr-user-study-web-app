# Hugging Face Migration Summary

This document summarizes the migration from Ollama local LLMs to Hugging Face hosted instances.

## Branch: `hugging-face-integration`

## Changes Made

### 1. Configuration (`backend/config.py`)
- **Removed**: `OLLAMA_HOST` configuration
- **Added**: `HUGGINGFACE_API_TOKEN` configuration
- **Updated**: `AVAILABLE_MODELS` to use Hugging Face model endpoints:
  - `meta-llama/Llama-3.2-3B-Instruct` (Standard Llama 3.2 model)
  - `martindisley/unlearning-to-rest` (Ablated test model)
- Each model now includes an `endpoint` field for the Hugging Face model path

### 2. Dependencies (`backend/requirements.txt`)
- **Removed**: `ollama==0.3.3`, `huggingface-hub==0.20.0`
- **Using**: `requests==2.31.0` (already in requirements) for direct HTTP calls to Inference Endpoints

### 3. Chat Routes (`backend/routes/chat.py`)
- **Removed**: 
  - `import ollama` and `from huggingface_hub import InferenceClient`
  - `clear_ollama_context()` function (no longer needed - HF API is stateless)
  - References to `config.OLLAMA_HOST`
- **Added**:
  - `import requests` for direct HTTP API calls
  - `call_huggingface_endpoint()` function to make POST requests to your Inference Endpoint
  - Proper message formatting to convert chat history into a prompt string
  - Response parsing to handle different JSON formats from the endpoint
- **Updated**:
  - `send_message()` endpoint now uses direct HTTP requests to your HF Inference Endpoint
  - Messages are formatted as "User: ... Assistant: ..." prompts
  - Model endpoint is retrieved dynamically based on model configuration
  - Better error handling for HTTP request exceptions
  - `reset_session()` simplified (no need to clear server-side context)

### 4. Application Startup (`backend/app.py`)
- **Updated**: Startup banner to show Hugging Face API status instead of Ollama host
- Now displays: `"Hugging Face API: Configured"` or `"Not configured"`

### 5. Environment Configuration (`.env`)
- **Removed**: 
  - `OLLAMA_HOST=http://localhost:11434`
- **Added**:
  - `HUGGINGFACE_ENDPOINT` - Your deployed Inference Endpoint URL
  - `HUGGINGFACE_ENDPOINT_UNLEARNING` - Optional separate endpoint for the unlearning model (defaults to HUGGINGFACE_ENDPOINT)
- **Reorganized**: Moved `HUGGINGFACE_API_TOKEN` to top with proper comments
- Maintained existing token: `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`

Example `.env`:
```bash
HUGGINGFACE_API_TOKEN=hf_your_token_here
HUGGINGFACE_ENDPOINT=https://f25f96grq046tq3b.eu-west-1.aws.endpoints.huggingface.cloud
# Optional: separate endpoint for second model
# HUGGINGFACE_ENDPOINT_UNLEARNING=https://another-endpoint.huggingface.cloud
```

### 6. Model Routes (`backend/routes/models.py`)
- **Updated**: Documentation and comments to reference Hugging Face instead of Ollama
- Model response now includes `endpoint` field in the JSON response

## Key Architectural Changes

### From Ollama (Local/Self-hosted)
- Stateful conversation management
- Required explicit context clearing
- Local model execution
- Model IDs with tags (e.g., `llama3.2:3b`, `model:latest`)

### To Hugging Face (Cloud-hosted)
- Stateless API calls
- Context managed by message history sent with each request
- Remote model execution via Inference API
- Model IDs as Hugging Face Hub paths (e.g., `meta-llama/Llama-3.2-3B-Instruct`)

## Benefits of Migration

1. **No Local Infrastructure**: Eliminates need to run Ollama server locally
2. **Scalability**: Hugging Face's hosted infrastructure handles scaling
3. **Model Management**: Easier to deploy and update models via Hugging Face Hub
4. **Reliability**: Enterprise-grade API with better uptime guarantees
5. **Flexibility**: Easy to add more models from Hugging Face's vast model catalog

## API Changes

### Chat Completion
```python
# OLD (Ollama)
response = ollama.chat(
    model=session.model_name,
    messages=ollama_messages,
    options={'host': config.OLLAMA_HOST}
)
assistant_message = response['message']['content']

# NEW (Hugging Face Inference Endpoint)
def call_huggingface_endpoint(endpoint_url, messages, token):
    # Format messages into prompt
    prompt = ""
    for msg in messages:
        if msg['role'] == 'user':
            prompt += f"User: {msg['content']}\n"
        elif msg['role'] == 'assistant':
            prompt += f"Assistant: {msg['content']}\n"
    prompt += "Assistant:"
    
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 500,
            "temperature": 0.7,
            "top_p": 0.9,
            "return_full_text": False
        }
    }
    
    response = requests.post(endpoint_url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    result = response.json()
    
    # Extract text from response
    if isinstance(result, list) and len(result) > 0:
        return result[0].get('generated_text', '').strip()
    elif isinstance(result, dict):
        return result.get('generated_text', '').strip()
    else:
        return str(result).strip()

# Usage
assistant_message = call_huggingface_endpoint(
    endpoint_url=config.HUGGINGFACE_ENDPOINT,
    messages=hf_messages,
    token=config.HUGGINGFACE_API_TOKEN
)
```

### Session Reset
- **Before**: Required clearing context on Ollama server
- **After**: Simply updates `context_reset_at` timestamp; context managed by filtering messages

## Testing Checklist

Before merging this branch, ensure:

- [ ] Dependencies installed: `pip install -r backend/requirements.txt`
- [ ] `HUGGINGFACE_API_TOKEN` is set in `.env`
- [ ] Both models are accessible via Hugging Face API
- [ ] Chat sessions create successfully
- [ ] Messages send and receive properly
- [ ] Session reset functionality works
- [ ] Image generation still works (uses Replicate, unchanged)
- [ ] Frontend displays models correctly
- [ ] No references to Ollama remain in codebase

## Installation Instructions

1. **Update dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Verify environment**:
   - Ensure `.env` has `HUGGINGFACE_API_TOKEN` set
   - Remove any Ollama-related environment variables

3. **Test Hugging Face connection**:
   ```python
   from huggingface_hub import InferenceClient
   client = InferenceClient(token="your_token_here")
   # Test with a simple prompt
   ```

4. **Start the server**:
   ```bash
   python backend/app.py
   # or
   ./start_optimized.sh
   ```

## Rollback Plan

If issues arise, revert to the previous branch:
```bash
git checkout main  # or previous branch
pip install -r backend/requirements.txt  # reinstall ollama
```

## Future Considerations

- Consider using Hugging Face Inference Endpoints for dedicated instances
- Implement rate limiting for API calls
- Add retry logic for transient API failures
- Cache model metadata to reduce config lookups
- Monitor API usage and costs
