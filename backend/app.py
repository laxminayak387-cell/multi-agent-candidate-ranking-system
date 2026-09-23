from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import time

# Create app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== Data ==========
class MatchRequest(BaseModel):
    job_description: str

CANDIDATES = [
    {"id": "1", "name": "Alice Johnson", "email": "alice@example.com",
     "skills": ["Python", "FastAPI", "React", "PostgreSQL", "AWS"],
     "experience_years": 6.5, "location": "Remote", "current_role": "Senior Engineer"},
    {"id": "2", "name": "Bob Smith", "email": "bob@example.com",
     "skills": ["JavaScript", "React", "Node.js", "MongoDB"],
     "experience_years": 4.0, "location": "New York", "current_role": "Full Stack Dev"},
    {"id": "3", "name": "Carol Davis", "email": "carol@example.com",
     "skills": ["Python", "Django", "PostgreSQL", "Docker", "AWS"],
     "experience_years": 8.0, "location": "Remote", "current_role": "Lead Engineer"},
    {"id": "4", "name": "Frank Miller", "email": "frank@example.com",
     "skills": ["Python", "FastAPI", "React", "TypeScript", "PostgreSQL"],
     "experience_years": 7.0, "location": "Remote", "current_role": "Senior Engineer"},
]

# ========== API ==========
@app.get("/")
async def root():
    return HTMLResponse(content=HTML_CONTENT)

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/Api/mike/match")
async def match(request: MatchRequest):
    start = time.time()
    
    # Simple extraction
    jd = request.job_description.lower()
    required_skills = []
    for skill in ["python", "fastapi", "react", "javascript", "postgresql", "aws"]:
        if skill in jd:
            required_skills.append(skill.title())
    if not required_skills:
        required_skills = ["Python", "JavaScript"]
    
    # Score candidates
    results = []
    for c in CANDIDATES:
        # Skill score
        matches = 0
        for rs in required_skills:
            if any(rs.lower() in cs.lower() or cs.lower() in rs.lower() for cs in c["skills"]):
                matches += 1
        skill_score = (matches / len(required_skills)) * 100
        
        # Experience
        min_exp = 5 if "senior" in jd else 3
        exp_match = c["experience_years"] >= min_exp
        exp_score = 100 if exp_match else (c["experience_years"] / min_exp) * 100
        
        # Total
        total = (skill_score * 0.6) + (exp_score * 0.4)
        
        results.append({
            "candidate": c,
            "match_score": round(total, 2),
            "match_rationale": f"{skill_score:.0f}% skills match | {c['experience_years']} years exp",
            "skill_match_percentage": round(skill_score, 2),
            "experience_match": exp_match,
            "location_match": True
        })
    
    results.sort(key=lambda x: x["match_score"], reverse=True)
    
    return {
        "job_requirements": {
            "role": "Senior Developer" if "senior" in jd else "Developer",
            "skills": required_skills,
            "experience_band": "senior" if "senior" in jd else "mid",
            "location": "Remote",
            "years_experience_min": min_exp,
            "raw_description": request.job_description
        },
        "top_candidates": results[:10],
        "total_candidates_considered": len(CANDIDATES),
        "query_time_ms": round((time.time() - start) * 1000, 2)
    }

# ========== HTML ==========
HTML_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Work360 Candidate Ranking</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }
        .card {
            background: white;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }
        .card h2 {
            margin-top: 0;
            color: #333;
        }
        textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-family: monospace;
            margin-bottom: 15px;
            box-sizing: border-box;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
        }
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 2px solid white;
            border-top-color: transparent;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 10px;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .candidate {
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 15px;
        }
        .candidate h3 {
            margin: 0 0 10px 0;
            display: flex;
            justify-content: space-between;
        }
        .score {
            background: #d4edda;
            color: #155724;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 14px;
        }
        .details {
            color: #666;
            font-size: 14px;
            margin-bottom: 10px;
        }
        .skills {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin: 10px 0;
        }
        .skill {
            background: #f0f0f0;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 12px;
        }
        .rationale {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 8px;
            font-size: 13px;
            margin-top: 10px;
        }
        .req-skills {
            background: #e8f4f8;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .skill-tag {
            background: #e0e7ff;
            color: #4338ca;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            display: inline-block;
            margin: 2px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 Work360 Candidate Ranking System</h1>
        <div class="grid">
            <div class="card">
                <h2>📋 Job Description</h2>
                <textarea id="jd" rows="8">Senior Python Developer needed with 5+ years experience.
Required skills: FastAPI, React, PostgreSQL.
Location: Remote</textarea>
                <button id="btn" onclick="findMatches()">🔍 Find Matches</button>
            </div>
            <div class="card">
                <h2>🏆 Top Candidates</h2>
                <div id="results">Click "Find Matches" to see results</div>
            </div>
        </div>
    </div>

    <script>
        async function findMatches() {
            const btn = document.getElementById('btn');
            const resultsDiv = document.getElementById('results');
            const jd = document.getElementById('jd').value;
            
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner"></span> Analyzing...';
            resultsDiv.innerHTML = 'Loading...';
            
            try {
                const response = await fetch('/Api/mike/match', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ job_description: jd })
                });
                
                const data = await response.json();
                
                let html = '<div class="req-skills"><strong>Required Skills:</strong><br>';
                html += data.job_requirements.skills.map(s => `<span class="skill-tag">${s}</span>`).join('');
                html += `<br><strong>Experience:</strong> ${data.job_requirements.years_experience_min}+ years</div>`;
                
                data.top_candidates.forEach((match, i) => {
                    const c = match.candidate;
                    html += `
                        <div class="candidate">
                            <h3>#${i+1} - ${c.name} <span class="score">${match.match_score}%</span></h3>
                            <div class="details">💼 ${c.current_role} | ⭐ ${c.experience_years} years | 📍 ${c.location}</div>
                            <div class="skills">
                                ${c.skills.map(s => `<span class="skill">${s}</span>`).join('')}
                            </div>
                            <div class="rationale">🔍 ${match.match_rationale}</div>
                        </div>
                    `;
                });
                
                resultsDiv.innerHTML = html;
            } catch (error) {
                resultsDiv.innerHTML = `<div style="color:red;padding:20px;">Error: ${error.message}</div>`;
            } finally {
                btn.disabled = false;
                btn.innerHTML = '🔍 Find Matches';
            }
        }
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*50)
    print("🚀 Work360 Candidate Ranking System")
    print("="*50)
    print("📍 Server: http://localhost:8000")
    print("📝 Open this URL in your browser")
    print("="*50 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)