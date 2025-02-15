const express = require('express');
const cors = require('cors');
const { spawn } = require('child_process');
const app = express();

// Enable CORS and JSON parsing
app.use(cors());
app.use(express.json());

// Serve static files from the UI directory
app.use(express.static('UI'));

// Store chat history (in memory - will be lost on server restart)
let chatHistory = [];

// Handle chat requests
app.post('/chat', (req, res) => {
    const userMessage = req.body.message;
    if (!userMessage || userMessage.trim() === '') {
        return res.status(400).json({ error: 'Empty message' });
    }
    
    // Set headers for streaming
    res.setHeader('Content-Type', 'text/plain');
    res.setHeader('Transfer-Encoding', 'chunked');
    
    // Spawn Python process
    const pythonProcess = spawn('python', ['chat.py']);
    let botResponse = '';

    // Handle Python process output
    pythonProcess.stdout.on('data', (data) => {
        const chunk = data.toString();
        botResponse += chunk;
        res.write(chunk);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Error: ${data}`);
    });

    pythonProcess.on('close', (code) => {
        // Update chat history only if there's a response
        if (botResponse.trim()) {
            chatHistory.push(
                { role: 'User', content: userMessage },
                { role: 'Assistant', content: botResponse }
            );
        }
        res.end();
    });

    // Send user message to Python process and immediately end the input stream
    pythonProcess.stdin.write(userMessage);
    pythonProcess.stdin.end();
});

// Add endpoint to get chat history
app.get('/history', (req, res) => {
    res.json(chatHistory);
});

// Add endpoint to clear chat history
app.post('/clear-history', (req, res) => {
    chatHistory = [];
    res.json({ message: 'Chat history cleared' });
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
}); 