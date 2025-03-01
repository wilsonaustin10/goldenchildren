# BrowserUse Testing Guide

This guide explains how to test the BrowserUse function call generation functionality using the provided test scripts.

## Prerequisites

1. Make sure you have installed all the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Ensure you have set up your environment variables in a `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key
   GROQ_API_KEY=your_groq_api_key
   ```

## Test Scripts

There are three test scripts available:

### 1. Direct Test (direct_test_browser_use.py)

This script directly tests the BrowserUse function call generation without any intent detection or conversation history.

**Usage:**
```bash
./direct_test_browser_use.py
```

**Example Input:**
```
Describe the browser actions to perform: > Go to Google, search for "latest AI news", and extract the headlines
```

### 2. Full Conversation Test (test_browser_use.py)

This script simulates the full conversation flow, including intent detection and conversation history.

**Usage:**
```bash
./test_browser_use.py
```

**Example Conversation:**
```
What would you like your agent to do? > I want to find the latest news about artificial intelligence
```

### 3. API Test (api_test_browser_use.py)

This script tests the API endpoints directly, allowing you to test both the direct and chat endpoints.

**Usage:**
```bash
# First, make sure the FastAPI server is running
uvicorn main:app --reload

# Then, in another terminal
./api_test_browser_use.py
```

**Example Usage:**
```
Select test mode (direct/chat) or exit: > direct
Describe the browser actions to perform: > Go to Google, search for "latest AI news", and extract the headlines

Select test mode (direct/chat) or exit: > chat
What would you like your agent to do? > I want to find the latest news about artificial intelligence
```

## Example Browser Actions to Test

Here are some example browser actions you can test:

1. "Go to Google, search for 'latest AI news', and extract the headlines"
2. "Navigate to Amazon, search for 'wireless headphones', and extract the prices of the top 5 results"
3. "Go to Twitter, log in with my credentials, and post a tweet saying 'Testing my AI agent!'"
4. "Visit YouTube, search for 'machine learning tutorials', and extract the titles of the first 3 videos"
5. "Go to Wikipedia, search for 'artificial intelligence', and extract the first paragraph of the article"

## Troubleshooting

If you encounter any issues:

1. Check that your API keys are correctly set in the `.env` file
2. Ensure all dependencies are installed
3. Check the server logs for any errors
4. Make sure the FastAPI server is running when using the API test script 