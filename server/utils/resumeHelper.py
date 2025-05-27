from config import CLAUDE_API

from anthropic import Anthropic
import json
import re
from fastapi import HTTPException

# Character limits
FREE_TIER_LIMITS = {
    "resume_chars": 1000,      
    "jd_chars": 1500,         
    "total_chars": 2500        
}

PAID_TIER_LIMITS = {
    "resume_chars": 3000,
    "jd_chars": 5000,   
    "total_chars": 8000  
}

def clean_input_text(text: str) -> str:
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    return cleaned.strip()

def validate_text_limits(resume_text: str, job_description: str, is_paid: bool = False):
    resume_chars = len(resume_text)
    jd_chars = len(job_description)
    total_chars = resume_chars + jd_chars
    limits = PAID_TIER_LIMITS if is_paid else FREE_TIER_LIMITS
    
    errors = []
    
    if resume_chars > limits["resume_chars"]:
        errors.append(f"Resume too long: {resume_chars}/{limits['resume_chars']} characters")
    
    if jd_chars > limits["jd_chars"]:
        errors.append(f"Job description too long: {jd_chars}/{limits['jd_chars']} characters")
        
    if total_chars > limits["total_chars"]:
        errors.append(f"Total content too long: {total_chars}/{limits['total_chars']} characters")
    
    if errors:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Text limits exceeded",
                "errors": errors,
                "limits": limits,
                "current": {
                    "resume_chars": resume_chars,
                    "jd_chars": jd_chars,
                    "total_chars": total_chars
                }
            }
        )

def is_free_usage(resume_text: str, job_description: str) -> bool:
    resume_chars = len(resume_text)
    jd_chars = len(job_description)
    total_chars = resume_chars + jd_chars
    return (resume_chars <= FREE_TIER_LIMITS["resume_chars"] and 
            jd_chars <= FREE_TIER_LIMITS["jd_chars"] and 
            total_chars <= FREE_TIER_LIMITS["total_chars"])

# client = OpenAI(api_key=OPENAI_API)
claude_client = Anthropic(api_key=CLAUDE_API)

async def score_resume_with_claude(resume_text: str, job_description: str, is_paid_user: bool = False) -> dict:
    try:
        if is_paid_user:
            validation_section = """
                **VALIDATION REQUIREMENTS:**
                Job Description must include:
                - Job responsibilities or description
                - Required qualifications/skills
                - Company or role context information

                Resume must include (in LaTeX format):
                - Education section
                - Work experience
                - Skills section
                - Projects or accomplishments"""
            
            validation_instruction = "- If validation fails, return success=false with specific message listing what's missing"
        else: 
            validation_section = """
                **VALIDATION REQUIREMENTS:**

                For free tier analysis, we'll work with whatever content is provided. Basic validation only:
                - Job description should contain some job-related information
                - Resume should contain some professional information"""
            
            validation_instruction = "- Work with the provided content even if some sections are missing"

        prompt = f"""
            You are a professional resume analysis AI. You will receive a job description and a LaTeX resume, then provide analysis and optimization.

            {validation_section}
            {validation_instruction}

            **ANALYSIS TASK:**
            1. {"Validate both inputs meet requirements" if is_paid_user else "Review provided content"}
            2. Score the resume's fit for the job (0-100)
            3. Provide specific, actionable feedback
            4. Generate an optimized LaTeX resume tailored to the job

            **RESPONSE FORMAT:**
            Respond ONLY with valid JSON in this exact format:

            ```json
                {{
                    "success": true/false,
                    "score": <0-100 integer>,
                    "message": "<error message if success=false>",
                    "feedback": "<detailed feedback string>",
                    "tailored_resume": "<complete LaTeX resume code>"
                }}
            ``` """
        response = claude_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            temperature=0.3,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        content = response.content[0].text.strip()
        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            content = content[start:end].strip()
        elif "```" in content:
            start = content.find("```") + 3
            end = content.find("```", start)
            content = content[start:end].strip()
        
        try:
            result = json.loads(content)
            
            if not isinstance(result.get("success"), bool):
                raise ValueError("Missing or invalid 'success' field")
            
            if result["success"]:
                required_fields = ["score", "feedback", "tailored_resume"]
                for field in required_fields:
                    if field not in result:
                        raise ValueError(f"Missing required field: {field}")
                if not isinstance(result["score"], int) or not 0 <= result["score"] <= 100:
                    result["score"] = max(0, min(100, int(result.get("score", 0))))
            
            return result
            
        except (json.JSONDecodeError, ValueError) as e:
            return {
                "success": False,
                "message": f"Failed to parse Claude response: {str(e)}. Raw response: {content[:200]}..."
            }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Claude API error: {str(e)}"
        }
