from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import time
import re

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== Data Models ==========
class MatchRequest(BaseModel):
    job_description: str
    job_id: Optional[str] = None

class Candidate(BaseModel):
    id: str
    name: str
    email: str
    skills: List[str]
    experience_years: float
    location: str
    current_role: Optional[str] = None
    education: Optional[str] = None

# ========== Mock Data ==========
CANDIDATES = [
    {
        "id": "1", "name": "Alice Johnson", "email": "alice@example.com",
        "skills": ["Python", "FastAPI", "PostgreSQL", "React", "AWS"],
        "experience_years": 6.5, "location": "San Francisco",
        "current_role": "Senior Software Engineer", "education": "MS Computer Science"
    },
    {
        "id": "2", "name": "Bob Smith", "email": "bob@example.com",
        "skills": ["JavaScript", "React", "Node.js", "MongoDB"],
        "experience_years": 4.0, "location": "New York",
        "current_role": "Full Stack Developer", "education": "BS Computer Science"
    },
    {
        "id": "3", "name": "Carol Davis", "email": "carol@example.com",
        "skills": ["Python", "Django", "PostgreSQL", "Docker", "AWS"],
        "experience_years": 8.0, "location": "Remote",
        "current_role": "Lead Backend Engineer", "education": "PhD Computer Science"
    },
    {
        "id": "4", "name": "Frank Miller", "email": "frank@example.com",
        "skills": ["Python", "FastAPI", "React", "TypeScript", "PostgreSQL"],
        "experience_years": 7.0, "location": "Remote",
        "current_role": "Senior Full Stack Engineer", "education": "BS Computer Science"
    }
]

# ========== API Endpoint ==========
@app.post("/Api/mike/match")
async def match_candidates(request: MatchRequest):
    start_time = time.time()
    
    # Extract requirements from job description
    jd_lower = request.job_description.lower()
    
    # Extract skills
    required_skills = []
    skill_keywords = ["python", "fastapi", "react", "javascript", "postgresql", "aws", "docker"]
    for skill in skill_keywords:
        if skill in jd_lower:
            required_skills.append(skill.title())
    
    if not required_skills:
        required_skills = ["Python", "JavaScript", "SQL"]
    
    # Determine experience level
    min_years = 3
    if "senior" in jd_lower:
        min_years = 5
    elif "junior" in jd_lower:
        min_years = 1
    
    # Score each candidate
    results = []
    for cand in CANDIDATES:
        # Calculate skill match
        cand_skills_lower = [s.lower() for s in cand["skills"]]
        matched = sum(1 for rs in [s.lower() for s in required_skills] 
                     if any(rs in cs or cs in rs for cs in cand_skills_lower))
        skill_score = (matched / len(required_skills)) * 100 if required_skills else 50
        
        # Calculate experience match
        exp_match = cand["experience_years"] >= min_years
        exp_score = min(100, (cand["experience_years"] / min_years) * 100) if not exp_match else 100
        
        # Calculate total score
        total_score = (skill_score * 0.6) + (exp_score * 0.4)
        
        # Generate rationale
        rationale_parts = []
        if skill_score >= 70:
            rationale_parts.append(f"✅ Strong skill match ({skill_score:.0f}%)")
        elif skill_score >= 40:
            rationale_parts.append(f"📚 Partial skill match ({skill_score:.0f}%)")
        else:
            rationale_parts.append(f"⚠️ Limited skill match ({skill_score:.0f}%)")
        
        if exp_match:
            rationale_parts.append(f"💼 {cand['experience_years']} years experience")
        else:
            rationale_parts.append(f"⚠️ Needs {min_years}+ years (has {cand['experience_years']})")
        
        results.append({
            "candidate": cand,
            "match_score": round(total_score, 2),
            "match_rationale": " | ".join(rationale_parts),
            "skill_match_percentage": round(skill_score, 2),
            "experience_match": exp_match,
            "location_match": True  # Simplified
        })
    
    # Sort by score
    results.sort(key=lambda x: x["match_score"], reverse=True)
    
    return {
        "job_requirements": {
            "role": "Senior Software Engineer" if min_years >= 5 else "Software Engineer",
            "skills": required_skills,
            "experience_band": "senior" if min_years >= 5 else "mid",
            "location": "remote",
            "years_experience_min": min_years,
            "raw_description": request.job_description
        },
        "top_candidates": results[:10],
        "total_candidates_considered": len(CANDIDATES),
        "query_time_ms": round((time.time() - start_time) * 1000, 2)
    }

# ========== Health Check ==========
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "Work360"}

# ========== Frontend ==========
HTML_FRONTEND = '''
<!DOCTYPE html>
<html>
<head>
    <title>Work360 Candidate Ranking</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .header h1 { font-size: 2rem; margin-bottom: 10px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }
        @media (max-width: 768px) { .grid { grid-template-columns: 1fr; } }
        .card {
            background: white;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }
        .card h2 { margin-bottom: 20px; color: #333; }
        textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-family: monospace;
            font-size: 14px;
            margin-bottom: 15px;
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
        button:disabled { opacity: 0.6; cursor: not-allowed; }
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
        @keyframes spin { to { transform: rotate(360deg); } }
        .candidate {
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 15px;
        }
        .candidate:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .candidate-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            flex-wrap: wrap;
        }
        .candidate-name { font-size: 18px; font-weight: bold; color: #333; }
        .score {
            padding: 4px 12px;
            border-radius: 20px;
            font-weight: bold;
        }
        .score-high { background: #d4edda; color: #155724; }
        .score-medium { background: #fff3cd; color: #856404; }
        .score-low { background: #f8d7da; color: #721c24; }
        .details {
            display: flex;
            gap: 15px;
            margin: 10px 0;
            font-size: 14px;
            color: #666;
            flex-wrap: wrap;
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
        .requirements {
            background: #e8f4f8;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Work360 Candidate Ranking System</h1>
            <p>AI-powered candidate matching</p>
        </div>
        
        <div class="grid">
            <div class="card">
                <h2>📋 Job Description</h2>
                <textarea id="jd" rows="8">Senior Python Developer needed with 5+ years experience.
Required skills: FastAPI, React, PostgreSQL, Docker.
Location: Remote</textarea>
                <button id="findBtn" onclick="findMatches()">🔍 Find Matches</button>
            </div>
            
            <div class="card">
                <h2>🏆 Top Candidates</h2>
                <div id="results">Click "Find Matches" to see results</div>
            </div>
        </div>
    </div>

    <script>
        async function findMatches() {
            const btn = document.getElementById('findBtn');
            const resultsDiv = document.getElementById('results');
            const jd = document.getElementById('jd').value;
            
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner"></span> Analyzing...';
            resultsDiv.innerHTML = '<div style="text-align:center"><span class="spinner"></span> Loading...</div>';
            
            try {
                const response = await fetch('/Api/mike/match', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ job_description: jd })
                });
                
                const data = await response.json();
                
                let html = '<div class="requirements">';
                html += `<strong>📋 Requirements:</strong><br>`;
                html += `Role: ${data.job_requirements.role}<br>`;
                html += `Experience: ${data.job_requirements.experience_band} (${data.job_requirements.years_experience_min}+ years)<br>`;
                html += `Skills: ${data.job_requirements.skills.join(', ')}`;
                html += `</div>`;
                
                data.top_candidates.forEach((match, idx) => {
                    const c = match.candidate;
                    let scoreClass = 'score-low';
                    if (match.match_score >= 70) scoreClass = 'score-high';
                    else if (match.match_score >= 50) scoreClass = 'score-medium';
                    
                    html += `
                        <div class="candidate">
                            <div class="candidate-header">
                                <div class="candidate-name">#${idx+1} - ${c.name}</div>
                                <div class="score ${scoreClass}">${match.match_score}%</div>
                            </div>
                            <div class="details">
                                <span>💼 ${c.current_role || 'N/A'}</span>
                                <span>⭐ ${c.experience_years} years</span>
                                <span>📍 ${c.location}</span>
                            </div>
                            <div class="skills">
                                ${c.skills.map(s => `<span class="skill">${s}</span>`).join('')}
                            </div>
                            <div class="rationale">
                                <strong>Analysis:</strong> ${match.match_rationale}
                            </div>
                        </div>
                    `;
                });
                
                resultsDiv.innerHTML = html;
            } catch (error) {
                resultsDiv.innerHTML = `<div class="error">❌ Error: ${error.message}<br><br>Make sure backend is running on port 8000</div>`;
            } finally {
                btn.disabled = false;
                btn.innerHTML = '🔍 Find Matches';
            }
        }
    </script>
</body>
</html>
'''

@app.get("/")
@app.get("/ui")
async def frontend():
    return HTMLResponse(content=HTML_FRONTEND)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)