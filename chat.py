import ollama
import sys
import json
from duckduckgo_search import DDGS
from datetime import datetime
import re

def needs_web_search(query):
    # Keywords that suggest need for current information
    current_info_keywords = [
        'current', 'latest', 'recent', 'news', 'today', 'now',
        'weather', 'price', 'stock', 'update', '2024', '2023',
        'happening', 'trending', 'live', 'when'
    ]
    
    # Check if query contains time-sensitive keywords
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in current_info_keywords)

def search_internet(query, num_results=3):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=num_results))
            search_summary = "\nRelevant information from the web:\n"
            for i, result in enumerate(results, 1):
                search_summary += f"{i}. {result['title']}: {result['body']}\n"
            return search_summary
    except Exception as e:
        print(f"Search error: {str(e)}", flush=True)
        return ""

def load_chat_history(filename='chat_history.json'):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_chat_history(chat_history, filename='chat_history.json'):
    with open(filename, 'w') as f:
        json.dump(chat_history, f, indent=2)

def process_single_message(user_input, chat_history=None):
    if chat_history is None:
        chat_history = load_chat_history()
        
    client = ollama.Client(host='http://localhost:11434')
    model = "llama3.1"
    max_tokens = 0
    max_tokens_limit = 1500
    
    try:
        # Add current date/time context
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        context = f"Current date and time: {current_time}\n"
        
        # Only search web if query suggests need for current information
        if needs_web_search(user_input):
            search_results = search_internet(user_input)
            if search_results:
                context += search_results
        
        # Construct prompt with chat history and context
        prompt = context + "\n"
        for message in chat_history:
            prompt += f"{message['role']}: {message['content']}\n"
        
        # Add current user input
        prompt += f"User: {user_input}\nAssistant: "
        
        response = client.chat(
            model=model,
            messages=[{
                "role": "user",
                "content": prompt
            }],
            stream=True,
            options={
                "temperature": 0.7,
                "top_k": 40,
                "top_p": 0.9,
                "num_predict": 1500,
                "stop": ["User:", "\nUser:", "\n\nUser:"],
                "repeat_penalty": 1.1,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
            }
        )
        
        assistant_response = ""
        sentence_buffer = ""
        
        for part in response:
            if 'message' in part:
                chunk = part['message']['content']
                chunk = chunk.replace('<think>', '').replace('</think>', '')
                
                max_tokens += 1
                if max_tokens >= max_tokens_limit:
                    print("\n[Response truncated]", flush=True)
                    break
                
                sentence_buffer += chunk
                
                if any(sentence_buffer.endswith(end) for end in ['.', '!', '?', '\n']):
                    print(sentence_buffer, end='', flush=True)
                    assistant_response += sentence_buffer
                    sentence_buffer = ""
                
                if len(assistant_response) > 4000:
                    print("\n[Response truncated due to length]", flush=True)
                    break
        
        if sentence_buffer:
            print(sentence_buffer, end='', flush=True)
            assistant_response += sentence_buffer
        
        # Update chat history
        chat_history.append({"role": "User", "content": user_input})
        chat_history.append({"role": "Assistant", "content": assistant_response.strip()})
        save_chat_history(chat_history)
        
    except Exception as e:
        print(f"Error: {str(e)}", flush=True)

    return chat_history

if __name__ == "__main__":
    chat_history = load_chat_history()
    
    try:
        # Check if running interactively
        if sys.stdin.isatty():
            print("Chat started. Type 'exit' or 'quit' to end the conversation.")
            while True:
                try:
                    user_input = input("\nYou: ").strip()
                    if user_input.lower() in ['exit', 'quit']:
                        break
                    print("\nAssistant: ", end='', flush=True)
                    chat_history = process_single_message(user_input, chat_history)
                except KeyboardInterrupt:
                    break
        else:
            # Running non-interactively (e.g., from Node.js)
            user_input = sys.stdin.read().strip()
            chat_history = process_single_message(user_input, chat_history)
            
    except Exception as e:
        print(f"Error: {str(e)}", flush=True)