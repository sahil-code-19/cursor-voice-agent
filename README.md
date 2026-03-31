# 🎙️ Cursor Voice-to-Text AI Agent

A voice-controlled AI developer agent that can write code, create files, and run commands — just by speaking.

---

## ⚡ Setup in 10 Minutes

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd cursor_voice-to-text
```

### 2. Install Dependencies

```bash
uv sync
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```dotenv
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=""
GOOGLE_API_KEY=""
LANGSMITH_WORKSPACE_ID=""
```

| Key | Description |
|---|---|
| `GOOGLE_API_KEY` | Gemini API key from [Google AI Studio](https://aistudio.google.com) |
| `LANGSMITH_API_KEY` | From [LangSmith](https://smith.langchain.com) for tracing |
| `LANGSMITH_WORKSPACE_ID` | Your LangSmith workspace ID |

### 4. Run the Agent

```bash
cd utils
uv run graph.py
```

### 5. Choose Interaction Mode

```
How do you want to interact with the AI?
  1. Voice
  2. Text
```

- **Voice** — speak your command, agent listens and responds
- **Text** — type your command in the terminal

---

## 🧠 What It Can Do

- ✅ Write full Python code files
- ✅ Find and fix bugs in existing code
- ✅ Run Python scripts
- ✅ Install packages via pip
- ✅ Commit and push code to GitHub

---

## 🗂️ Project Structure

```
cursor_voice-to-text/
├── utils/
│   ├── graph.py          # Main LangGraph agent
│   ├── speech_to_text.py # Voice input
│   └── text_to_speech.py # Voice output
├── .env                  # Your API keys (not committed)
├── .gitignore
└── README.md
```

---

## 🔐 Security

All file operations are restricted to the project directory. Shell commands run against a strict whitelist — no destructive commands allowed.
