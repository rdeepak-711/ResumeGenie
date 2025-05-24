### ResumeGenie: Score & Tailor Your Resume with AI

- Upload your resume (text or paste).
- Select a job description (paste JD or fetch from LinkedIn URL).
- AI model:
    - Scores the resume against the JD (math: cosine similarity, keyword match %).
    - Suggests improvements (LLM).
    - Optionally tailors your resume to match the JD better.
- Stores sessions in MongoDB (resume + JD + scores + suggestions).
- Frontend in ReactJS with a clean UI to display score, suggestions, and before/after resume text.