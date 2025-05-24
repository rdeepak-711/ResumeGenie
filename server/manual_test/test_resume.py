import requests
import fitz
from pathlib import Path
import subprocess
import os
import uuid

API_URL = "http://localhost:8000/analyze"

def save_latex_to_pdf(latex_code: str, output_dir: str = "pdf_output") -> str:
    os.makedirs(output_dir, exist_ok=True)
    file_id = str(uuid.uuid4())
    tex_path = os.path.join(output_dir, f"{file_id}.tex")
    pdf_path = os.path.join(output_dir, f"{file_id}.pdf")

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(latex_code)
    try:
        subprocess.run(["pdflatex", "-output-directory", output_dir, tex_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return pdf_path
    except subprocess.CalledProcessError as e:
        raise Exception(f"LaTeX PDF generation failed: {e}")


def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()

def load_text_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
    
def save_output(filename, content):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    try:
        pdf_path = Path("resume.pdf")
        if not pdf_path.exists():
            raise FileNotFoundError(f"Resume PDF not found at: {pdf_path.resolve()}")

        resume_text = extract_text_from_pdf(str(pdf_path))
        job_description = load_text_file("job_description.txt")

        payload = {
            "resume_text": resume_text,
            "job_description": job_description
        }

        response = requests.post(API_URL, json=payload)
        data = response.json()

        if data.get("success"):
            print("\n✅ SCORE:", data["data"]["score"])
            print("\n🧠 FEEDBACK:\n", data["data"]["feedback"])
            print("\n📄 Tailored Resume saved to 'tailored_resume.txt'")
            latex_code = data["data"]["tailored_resume"]
            pdf_path = save_latex_to_pdf(latex_code)
        else:
            print("\n❌ ERROR:", data.get("message"))
    except Exception as e:
        print("Request failed:", e)

if __name__ == "__main__":
    main()