import os
import io
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import PyPDF2
from docx import Document
import anthropic

app = FastAPI(title="Resume Scorer API", version="1.0.0")

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


class ResumeScore(BaseModel):
    filename: str
    score: int
    feedback: str
    strengths: list[str]
    improvements: list[str]


def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file."""
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from Word document."""
    doc = Document(io.BytesIO(file_content))
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text


def extract_text_from_file(file_content: bytes, filename: str) -> str:
    """Extract text based on file type."""
    if filename.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_content)
    elif filename.lower().endswith((".docx", ".doc")):
        return extract_text_from_docx(file_content)
    else:
        raise ValueError("Unsupported file format. Please use PDF or Word documents.")


def score_resume_with_llm(resume_text: str) -> ResumeScore:
    """Use Claude to score and analyze the resume."""
    
    prompt = f"""Analyze the following resume and provide a structured evaluation:

RESUME:
{resume_text}

Please provide your analysis in the following format:

SCORE: [1-100]
FEEDBACK: [2-3 sentences overall assessment]

STRENGTHS:
- [strength 1]
- [strength 2]
- [strength 3]

IMPROVEMENTS:
- [improvement 1]
- [improvement 2]
- [improvement 3]

Evaluate based on:
1. Clarity and formatting
2. Relevant experience
3. Education and certifications
4. Specific achievements and quantifiable results
5. Action verbs and strong language
6. Skills presentation
7. Overall professionalism"""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    response_text = message.content[0].text
    
    # Parse the response
    lines = response_text.split("\n")
    score = 75
    feedback = ""
    strengths = []
    improvements = []
    
    current_section = None
    
    for line in lines:
        line = line.strip()
        if line.startswith("SCORE:"):
            try:
                score = int(line.replace("SCORE:", "").strip())
            except ValueError:
                score = 75
        elif line.startswith("FEEDBACK:"):
            feedback = line.replace("FEEDBACK:", "").strip()
        elif line == "STRENGTHS:":
            current_section = "strengths"
        elif line == "IMPROVEMENTS:":
            current_section = "improvements"
        elif line.startswith("- ") and current_section:
            item = line.replace("- ", "").strip()
            if current_section == "strengths":
                strengths.append(item)
            elif current_section == "improvements":
                improvements.append(item)
    
    return {
        "score": score,
        "feedback": feedback,
        "strengths": strengths[:3],
        "improvements": improvements[:3]
    }


@app.post("/score", response_model=ResumeScore)
async def score_resume(file: UploadFile = File(...)):
    """
    Upload a resume (PDF or Word document) and get an LLM-based score.
    
    - **file**: Upload a PDF or Word document (.pdf, .docx, .doc)
    
    Returns a ResumeScore object with score (1-100), feedback, strengths, and improvements.
    """
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        if not file.filename.lower().endswith((".pdf", ".docx", ".doc")):
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format. Please upload a PDF or Word document."
            )
        
        # Read file content
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty file provided")
        
        # Extract text
        resume_text = extract_text_from_file(content, file.filename)
        if not resume_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from file")
        
        # Score with LLM
        score_result = score_resume_with_llm(resume_text)
        score_result["filename"] = file.filename
        
        return score_result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/")
async def root():
    """Root endpoint with API documentation."""
    return {
        "name": "Resume Scorer API",
        "version": "1.0.0",
        "endpoints": {
            "POST /score": "Upload a resume file and get an LLM-based score",
            "GET /health": "Health check",
            "GET /docs": "Interactive API documentation (Swagger UI)"
        },
        "supported_formats": ["PDF", "DOCX", "DOC"]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)