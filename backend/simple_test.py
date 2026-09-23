from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MatchRequest(BaseModel):
    job_description: str

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/Api/mike/match")
async def match(request: MatchRequest):
    # Simple mock response
    return {
        "job_requirements": {
            "role": "Python Developer",
            "skills": ["Python", "FastAPI", "React"],
            "experience_band": "senior",
            "location": "remote",
            "years_experience_min": 5,
            "raw_description": request.job_description
        },
        "top_candidates": [
            {
                "candidate": {
                    "id": "1",
                    "name": "Alice Johnson",
                    "email": "alice@example.com",
                    "skills": ["Python", "FastAPI", "React", "PostgreSQL"],
                    "experience_years": 6.5,
                    "location": "Remote",
                    "current_role": "Senior Engineer",
                    "education": "MS CS"
                },
                "match_score": 95.0,
                "match_rationale": "✅ Strong skill match | 💼 6.5 years experience | 📍 Remote ready",
                "skill_match_percentage": 100.0,
                "experience_match": True,
                "location_match": True
            }
        ],
        "total_candidates_considered": 6,
        "query_time_ms": 45.2
    }

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Work360 Test</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
        pre { background: #f4f4f4; padding: 10px; overflow-x: auto; }
    </style>
</head>
<body>
    <h1>Work360 Candidate Ranking</h1>
    <textarea id="jd" rows="5" style="width:100%">Senior Python Developer</textarea>
    <button onclick="test()">Find Matches</button>
    <pre id="result">Click button to test...</pre>

    <script>
        async function test() {
            const jd = document.getElementById('jd').value;
            const resultDiv = document.getElementById('result');
            resultDiv.textContent = 'Loading...';
            
            try {
                const response = await fetch('/Api/mike/match', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ job_description: jd })
                });
                const data = await response.json();
                resultDiv.textContent = JSON.stringify(data, null, 2);
            } catch (error) {
                resultDiv.textContent = 'Error: ' + error.message;
            }
        }
    </script>
</body>
</html>
"""

@app.get("/")
async def root():
    return HTMLResponse(content=HTML)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)