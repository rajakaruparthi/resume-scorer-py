# Resume Scorer API

A FastAPI-based application that scores resumes using Claude AI. Upload a PDF or Word document, and get an LLM-powered analysis with a score (1-100), feedback, strengths, and improvement suggestions.

## Features

- **Multi-format support**: PDF, DOCX, and DOC files
- **AI-powered scoring**: Uses Claude 3.5 Sonnet for intelligent resume analysis
- **Comprehensive feedback**: 
  - Overall score (1-100)
  - General feedback
  - Top 3 strengths
  - Top 3 improvement areas
- **RESTful API**: Easy to integrate
- **Interactive docs**: Built-in Swagger UI at `/docs`

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set API Key

You need to set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

Get your API key from [Anthropic Console](https://console.anthropic.com)

### 3. Run the Server

```bash
python resume_scorer.py
```

The API will start on `http://localhost:8000`

## Usage

### Via cURL

```bash
curl -X POST "http://localhost:8000/score" \
  -F "file=@resume.pdf"
```

### Via Python

```python
import requests

with open("resume.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/score",
        files={"file": f}
    )
    result = response.json()
    print(f"Score: {result['score']}")
    print(f"Feedback: {result['feedback']}")
    print(f"Strengths: {result['strengths']}")
    print(f"Improvements: {result['improvements']}")
```

### Via Swagger UI

1. Open `http://localhost:8000/docs` in your browser
2. Click "Try it out" on the `/score` endpoint
3. Select your resume file
4. Click "Execute"

## API Endpoints

### POST /score
Upload a resume and get scoring analysis.

**Request:**
- Form data with file field (PDF, DOCX, or DOC)

**Response:**
```json
{
  "filename": "resume.pdf",
  "score": 82,
  "feedback": "Well-structured resume with clear achievements...",
  "strengths": [
    "Strong quantifiable achievements",
    "Clear career progression",
    "Good use of action verbs"
  ],
  "improvements": [
    "Add more technical skills section",
    "Include certifications",
    "Improve formatting consistency"
  ]
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

### GET /
API information and available endpoints.

## Evaluation Criteria

The resume is evaluated based on:

1. **Clarity and formatting** - Is it easy to read?
2. **Relevant experience** - Does it show relevant background?
3. **Education and certifications** - Are qualifications clear?
4. **Specific achievements** - Are results quantifiable?
5. **Action verbs and language** - Is it written professionally?
6. **Skills presentation** - Are skills well-organized?
7. **Overall professionalism** - Does it make a good impression?

## Error Handling

- **400 Bad Request**: Invalid file format, empty file, or no filename
- **500 Internal Server Error**: Processing error

## Example Files

Test with these resume formats:
- `.pdf` - PDF documents
- `.docx` - Microsoft Word 2007+ documents
- `.doc` - Older Microsoft Word documents

## Limitations

- File size: Typically handles resumes up to a few MB
- Text extraction: Complex formatting may not extract perfectly
- Language: Works best with English resumes

## Future Enhancements

- Batch processing multiple resumes
- Customizable scoring criteria
- Resume improvement suggestions
- Comparison with job descriptions
- Historical scoring and tracking
