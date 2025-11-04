import express from 'express';
import fetch from 'node-fetch';
import dotenv from 'dotenv';
import cors from 'cors';
import path, { dirname } from 'path';
import { fileURLToPath } from 'url';

dotenv.config();
const __dirname = dirname(fileURLToPath(import.meta.url));
const app = express();
app.use(cors());
app.use(express.json());

const OPENAI_API_KEY = process.env.OPENAI_API_KEY;

// ======================= HELPER FUNCTION FOR DYNAMIC TIME =======================
async function getDynamicTime(userInput, apiKey) {
    const timeKeywordsRegex = /\b(time|date|clock)\b/i;
    if (!timeKeywordsRegex.test(userInput)) {
        return null;
    }

    try {
        const timeResponsePrompt = `The user asked: "${userInput}". Give a friendly, concise response with the current time and date in the user's location. The current time is ${new Date().toLocaleString()}.`;
        const openaiResponse = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model: "gpt-3.5-turbo",
                messages: [{ role: "user", content: timeResponsePrompt }],
                temperature: 0.7
            })
        });
        const openaiData = await openaiResponse.json();
        return openaiData.choices?.[0]?.message?.content || null;
    } catch (error) {
        console.error("❌ Error in getDynamicTime function:", error);
        return "I'm sorry, I had trouble fetching the time. Please try again.";
    }
}

// ======================= MAIN CHAT ENDPOINT =======================
app.post('/api/chat', async (req, res) => {
    try {
        const { messages } = req.body;
        const userInput = messages[messages.length - 1]?.content;

        // Check for time queries first
        const timeResponse = await getDynamicTime(userInput, OPENAI_API_KEY);
        if (timeResponse) {
            return res.json({ choices: [{ message: { content: timeResponse } }] });
        }

        // Otherwise, forward the request to the Python LangChain backend
        const pythonResponse = await fetch("http://localhost:5005/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userInput })
        });

        if (!pythonResponse.ok) {
            throw new Error(`Python server error: ${pythonResponse.statusText}`);
        }
        
        const pythonData = await pythonResponse.json();
        return res.json({ choices: [{ message: { content: pythonData.response } }] });

    } catch (err) {
        console.error("❌ Backend error:", err);
        res.status(500).json({ error: err.message || 'API call failed' });
    }
});
app.listen(3001, () => console.log('✅ Node.js proxy server running on http://localhost:3001'));