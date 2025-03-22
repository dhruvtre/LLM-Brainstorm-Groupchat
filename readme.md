# Six Thinking Hats Chat

A collaborative group discussion application based on Edward de Bono's Six Thinking Hats approach, featuring AI agents that participate in conversations with different perspectives.

## Overview

This application implements a chat interface with three AI agents representing different thinking hats:

- **White Hat**: Focuses on facts and information
- **Black Hat**: Focuses on risks, difficulties, and problems
- **Green Hat**: Focuses on creativity, possibilities, and new ideas

Each agent has an "inner voice" that decides whether their message should be sent to the group chat.

## Tech Stack

### Backend
- Flask (Python)
- OpenAI and Anthropic APIs
- Asynchronous processing with `asyncio`

### Frontend
- React
- CSS for styling
- Vite for build and development

## Setup

1. Clone the repository
2. Install dependencies:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install JavaScript dependencies
cd frontend
npm install
```

3. Set up environment variables:
   Create a `.env` file in the backend directory with your OpenAI API key:

```
OpenAI_key=your_openai_api_key
```

4. Start the backend:

```bash
cd backend
python flask_app.py
```

5. Start the frontend:

```bash
cd frontend
npm run dev
```

6. Open the application in your browser (typically at http://localhost:5173)

## Features

- Real-time AI agent responses
- Inner voice reflection for each agent
- Toggle to show/hide filtered messages
- Reset chat functionality
- Visual distinction between different agent messages