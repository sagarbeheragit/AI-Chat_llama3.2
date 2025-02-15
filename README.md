# Chatbot
Description: A chatbot that uses a large language model to generate responses to user messages. The llm models are locally hosted on the user's computer. This application is using ollama to host the models.

Features:
- Local hosting of LLM models
- Streamlined user experience with real-time chat history
- Real-time chat history stored in JSON file
- Real-time chat history saved to file after each message
- Support for web search and file system

# Tech Stack
- HTML, CSS, JS
- Node.js
- Ollama
- Python

## Setup

```bash
setup node js
npm install
```
install ollama from https://ollama.com/docs/installation

## Run

```bash
node server.js
```
Run the html and enter the message in the input field and click on the send button to see the response.

# UI
- HTML, CSS, JS

# LLM model Used
- deepseek-r1
- llama3.1

# Architecture
- server.js is the main file that is used to run the server.
- chat.py is the file that is used to chat with the model.
- UI is the folder that contains the HTML, CSS, and JS files for the chatbot.
- ollama is the model that is used to generate the response.
- ollama allows users to run large language models (LLMs) locally on their computers.


![Architecture Diagram](./assets/architecture.png)
