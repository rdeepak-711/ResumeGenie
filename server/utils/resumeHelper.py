from config import OPENAI_API
from openai import OpenAI
import json
import re

def clean_input_text(text: str) -> str:
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    return cleaned.strip()

MAX_FREE_CHARS=1500
def is_free_usage(resume: str, jd: str) -> bool:
    return len(resume) + len(jd) <= MAX_FREE_CHARS


client = OpenAI(api_key=OPENAI_API)

async def score_resume_with_openai(resume_text: str, job_description: str) -> dict:
    try:
        messages = [
            {
                "role": "user",
                "content": f"""
                    You will receive:
                    1. A job description (JD)
                    2. A LaTeX resume (Resume)

                    First validate the JD includes:
                    - Responsibilities or Job Description
                    - Qualifications or Required Skills
                    - Info about company or role context

                    If anything is missing, return:
                    {{"success": false, "message": "JD missing: [list]"}}.

                    Then validate the resume includes (in LaTeX):
                    - Education
                    - Work experience
                    - Skills
                    - Projects or accomplishments

                    If anything is missing, return:
                    {{"success": false, "message": "Resume missing: [list]"}}.

                    If both are complete:
                    1. Parse both
                    2. Assign a score (0–100) for job fit
                    3. Provide honest feedback
                    4. Return a tailored LaTeX resume

                    Respond ONLY in JSON:
                    {{
                        "success": true,
                        "score": <score>,
                        "feedback": "<feedback>",
                        "tailored_resume": "<LaTeX resume>"
                    }}

                    JD:
                    {job_description}

                    Resume:
                    {resume_text}
                """
            }
        ]

        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.4
        )
        content = response.choices[0].message.content.strip()

        try:
            result = json.loads(content)
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "message": f"JSON parse error: {e}. Raw response: {content}"
            }

        return result

    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }
