# 🧠 NeuroNest AI

**An AI-powered conversational chatbot built using Google Gemini API, FastAPI, and JavaScript.**

NeuroNest AI is a conversational AI application designed to provide intelligent, helpful, and interactive responses to user queries. It integrates Google's Gemini API with a FastAPI backend and a responsive frontend.

## ✨ Features

- 🤖 AI-powered conversations using Google Gemini.
- 💬 Natural-language question answering.
- ⚡ Streaming responses for a more interactive experience.
- 🧠 Conversation history management.
- 🌐 Interactive web-based chatbot interface.
- 🔐 Secure API key management using environment variables.
- 🚀 FastAPI backend integration.

## 🛠️ Technologies Used

- Python
- FastAPI
- Google Gemini API
- JavaScript
- HTML
- CSS
- Uvicorn
- Python-dotenv

## 📁 Project Structure

```text
NeuroNest-AI/
│
├── app.py
├── requirements.txt
├── .env
├── .gitignore
│
├── templates/
│   └── index.html
│
└── static/
    ├── style.css
    └── script.js
```

## ⚙️ Installation and Setup

**1. Clone the repository**

```bash
git clone https://github.com/batta-vaishnavi/NeuroNest-AI.git
cd NeuroNest-AI
```

**2. Create a virtual environment**

```bash
python -m venv venv
```

**3. Activate the environment**

Windows:

```bash
venv\Scripts\activate
```

**4. Install dependencies**

```bash
pip install -r requirements.txt
```

**5. Configure your API key**

Create a `.env` file in the root directory and add:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Replace the placeholder with your actual Gemini API key.

**6. Run the application**

```bash
uvicorn app:app --reload
```

**7. Open in your browser**

```text
http://127.0.0.1:8000
```

## 🔒 Security

- API keys are stored in environment variables.
- The `.env` file is excluded from Git using `.gitignore`.
- Never share your API key publicly.

## 🎯 Project Objective

The objective of NeuroNest AI is to develop a functional conversational AI application by integrating Large Language Models (LLMs) with a modern backend and frontend architecture.

## 👩‍💻 Author

**Vaishnavi Batta**

GitHub: [batta-vaishnavi](https://github.com/batta-vaishnavi)

Project Repository: [NeuroNest-AI](https://github.com/batta-vaishnavi/NeuroNest-AI)

---

*Built with curiosity and a passion for Artificial Intelligence.* ❤️