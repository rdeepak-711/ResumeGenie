# 🎯 ResumeGenie: Score & Tailor Your Resume with AI

An AI-powered resume analysis tool that helps you:
- ✅ Upload your resume (paste as plain text).
- ✅ Provide a job description (paste manually).
- 🤖 AI engine:
  - Scores your resume based on similarity with the JD (cosine similarity + keyword match).
  - Gives feedback and suggestions (via OpenAI).
  - Optionally tailors your resume to fit the JD better.
- 💾 Saves your sessions (resume, JD, score, feedback, tailored resume) to MongoDB.

---

## 🧩 Tech Stack

### 🖥️ Frontend
- ReactJS (Vite)
- Tailwind CSS (optional, clean UI)
- Axios for API calls

### 🚀 Backend
- FastAPI (Python)
- MongoDB (async with Motor)
- OpenAI API (for scoring & tailoring resumes)

---

## 🗂️ Monorepo Structure

ResumeGenie/
├── client/ # Vite + React frontend
├── server/ # FastAPI backend
├── .gitignore
├── README.md


---

## 📦 Setup

### Backend (FastAPI)
```bash
cd server
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
uvicorn main:app --reload

```

---


### Frontend(React + Vite)
```bash
cd client
npm install
npm run dev
```