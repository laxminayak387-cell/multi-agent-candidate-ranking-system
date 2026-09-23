from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import time

# Create FastAPI app
app = FastAPI()

# Enable CORS for all origins
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

# ========== Candidate Database ==========
CANDIDATES = [
    {
        "id": "1",
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "skills": ["Python", "FastAPI", "PostgreSQL", "React", "AWS", "Docker"],
        "experience_years": 6.5,
        "location": "San Francisco",
        "current_role": "Senior Software Engineer",
        "education": "MS Computer Science"
    },
    {
        "id": "2",
        "name": "Bob Smith",
        "email": "bob@example.com",
        "skills": ["JavaScript", "React", "Node.js", "MongoDB", "Express"],
        "experience_years": 4.0,
        "location": "New York",
        "current_role": "Full Stack Developer",
        "education": "BS Computer Science"
    },
    {
        "id": "3",
        "name": "Carol Davis",
        "email": "carol@example.com",
        "skills": ["Python", "Django", "PostgreSQL", "Docker", "Kubernetes", "AWS"],
        "experience_years": 8.0,
        "location": "Remote",
        "current_role": "Lead Backend Engineer",
        "education": "PhD Computer Science"
    },
    {
        "id": "4",
        "name": "David Wilson",
        "email": "david@example.com",
        "skills": ["Java", "Spring Boot", "MySQL", "Microservices", "Kafka"],
        "experience_years": 5.0,
        "location": "Austin",
        "current_role": "Software Engineer",
        "education": "BS Computer Engineering"
    },
    {
        "id": "5",
        "name": "Emma Brown",
        "email": "emma@example.com",
        "skills": ["Python", "Machine Learning", "TensorFlow", "SQL", "Pandas"],
        "experience_years": 3.5,
        "location": "Seattle",
        "current_role": "ML Engineer",
        "education": "MS Data Science"
    },
    {
        "id": "6",
        "name": "Frank Miller",
        "email": "frank@example.com",
        "skills": ["Python", "FastAPI", "React", "TypeScript", "PostgreSQL", "Redis"],
        "experience_years": 7.0,
        "location": "Remote",
        "current_role": "Senior Full Stack Engineer",
        "education": "BS Computer Science"
    }
]

# ========== API Endpoints ==========
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.post("/Api/mike/match")
async def match_candidates(request: MatchRequest):
    start_time = time.time()
    
    # Extract requirements from job description
    jd_lower = request.job_description.lower()
    
    # Extract required skills
    skill_keywords = ["python", "fastapi", "react", "javascript", "postgresql", 
                      "mongodb", "aws", "docker", "kubernetes", "django", "java", "spring"]
    required_skills = []
    for skill in skill_keywords:
        if skill in jd_lower:
            required_skills.append(skill.title())
    
    if not required_skills:
        required_skills = ["Python", "JavaScript", "SQL"]
    
    # Determine experience requirement
    min_years = 3
    experience_band = "mid"
    if "senior" in jd_lower or "lead" in jd_lower:
        min_years = 5
        experience_band = "senior"
    elif "junior" in jd_lower or "entry" in jd_lower:
        min_years = 1
        experience_band = "junior"
    
    # Determine role
    role = "Software Engineer"
    if "python" in jd_lower:
        role = "Python Developer"
    elif "react" in jd_lower or "frontend" in jd_lower:
        role = "Frontend Developer"
    elif "devops" in jd_lower:
        role = "DevOps Engineer"
    
    if min_years >= 5:
        role = "Senior " + role
    
    # Score each candidate
    scored_candidates = []
    for candidate in CANDIDATES:
        # Calculate skill match
        candidate_skills_lower = [s.lower() for s in candidate["skills"]]
        required_lower = [s.lower() for s in required_skills]
        
        matched = 0
        for req in required_lower:
            for cand_skill in candidate_skills_lower:
                if req in cand_skill or cand_skill in req:
                    matched += 1
                    break
        
        skill_score = (matched / len(required_lower)) * 100 if required_lower else 50
        
        # Calculate experience match
        candidate_exp = candidate["experience_years"]
        if candidate_exp >= min_years:
            exp_score = 100
            exp_match = True
        else:
            exp_score = (candidate_exp / min_years) * 100
            exp_match = False
        
        # Calculate location match
        req_location = "remote" if "remote" in jd_lower else "any"
        cand_location = candidate["location"].lower()
        loc_match = req_location == "remote" or req_location == cand_location
        loc_score = 100 if loc_match else 50
        
        # Calculate total score
        total_score = (skill_score * 0.5) + (exp_score * 0.3) + (loc_score * 0.2)
        
        # Generate rationale
        rationale_parts = []
        if skill_score >= 80:
            rationale_parts.append(f"✅ Excellent skill match ({skill_score:.0f}%)")
        elif skill_score >= 60:
            rationale_parts.append(f"📚 Good skill match ({skill_score:.0f}%)")
        elif skill_score >= 40:
            rationale_parts.append(f"📖 Partial skill match ({skill_score:.0f}%)")
        else:
            rationale_parts.append(f"⚠️ Limited skill match ({skill_score:.0f}%)")
        
        if exp_match:
            rationale_parts.append(f"💼 {candidate_exp} years experience")
        else:
            rationale_parts.append(f"⚠️ Needs {min_years}+ years (has {candidate_exp})")
        
        if loc_match:
            rationale_parts.append(f"📍 Location compatible")
        else:
            rationale_parts.append(f"🌍 Location mismatch")
        
        scored_candidates.append({
            "candidate": candidate,
            "match_score": round(total_score, 2),
            "match_rationale": " | ".join(rationale_parts),
            "skill_match_percentage": round(skill_score, 2),
            "experience_match": exp_match,
            "location_match": loc_match
        })
    
    # Sort by score (highest first)
    scored_candidates.sort(key=lambda x: x["match_score"], reverse=True)
    
    # Return top 10
    return {
        "job_requirements": {
            "role": role,
            "skills": required_skills,
            "experience_band": experience_band,
            "location": "Remote" if "remote" in jd_lower else "On-site",
            "years_experience_min": min_years,
            "raw_description": request.job_description
        },
        "top_candidates": scored_candidates[:10],
        "total_candidates_considered": len(CANDIDATES),
        "query_time_ms": round((time.time() - start_time) * 1000, 2)
    }

# ========== HTML Frontend (This is the important part!) ==========
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Work360 - Candidate Ranking System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        .header h1 { font-size: 2.5rem; margin-bottom: 10px; }
        .header p { font-size: 1.1rem; opacity: 0.9; }
        .status {
            background: #28a745;
            color: white;
            padding: 10px;
            border-radius: 8px;
            text-align: center;
            margin-bottom: 20px;
            font-weight: bold;
        }
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }
        @media (max-width: 768px) {
            .grid { grid-template-columns: 1fr; }
        }
        .card {
            background: white;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }
        .card h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.5rem;
        }
        .template-buttons {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        .template-btn {
            background: #f0f0f0;
            border: none;
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.3s;
        }
        .template-btn:hover {
            background: #667eea;
            color: white;
            transform: translateY(-2px);
        }
        textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-family: monospace;
            font-size: 14px;
            resize: vertical;
            margin-bottom: 15px;
        }
        textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: transform 0.2s;
        }
        button:hover { transform: translateY(-2px); }
        button:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 2px solid white;
            border-top-color: transparent;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 10px;
            vertical-align: middle;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .results {
            margin-top: 20px;
            max-height: 600px;
            overflow-y: auto;
        }
        .stats {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            font-size: 14px;
        }
        .requirements {
            background: #e8f4f8;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            font-size: 14px;
        }
        .candidate-card {
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            transition: all 0.3s;
            background: white;
        }
        .candidate-card:hover {
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            flex-wrap: wrap;
            gap: 10px;
        }
        .candidate-name {
            font-size: 18px;
            font-weight: 700;
            color: #333;
        }
        .match-score {
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: 700;
            font-size: 14px;
        }
        .score-high { background: #d4edda; color: #155724; }
        .score-medium { background: #fff3cd; color: #856404; }
        .score-low { background: #f8d7da; color: #721c24; }
        .candidate-details {
            display: flex;
            gap: 20px;
            margin-bottom: 15px;
            font-size: 14px;
            color: #666;
            flex-wrap: wrap;
        }
        .skills {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 15px;
        }
        .skill {
            background: #f0f0f0;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 12px;
            color: #555;
        }
        .skill.highlight {
            background: #667eea;
            color: white;
        }
        .rationale {
            background: #f8f9fa;
            padding: 12px;
            border-radius: 8px;
            font-size: 13px;
            border-left: 3px solid #667eea;
        }
        .badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            margin-left: 10px;
        }
        .badge-yes { background: #d4edda; color: #155724; }
        .badge-no { background: #f8d7da; color: #721c24; }
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 10px;
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
        <div class="header">
            <h1>🎯 Work360 Candidate Ranking System</h1>
            <p>AI-powered candidate matching with intelligent ranking</p>
        </div>
        
        <div class="status" id="status">✅ Backend Connected - Ready</div>
        
        <div class="grid">
            <div class="card">
                <h2>📋 Job Description</h2>
                <div class="template-buttons">
                    <button class="template-btn" onclick="loadTemplate('python')">🐍 Python Developer</button>
                    <button class="template-btn" onclick="loadTemplate('react')">⚛️ React Developer</button>
                    <button class="template-btn" onclick="loadTemplate('devops')">☁️ DevOps Engineer</button>
                    <button class="template-btn" onclick="loadTemplate('fullstack')">🔄 Full Stack</button>
                </div>
                <textarea id="jobDescription" rows="8">Senior Python Developer needed with 5+ years experience.
Required skills: FastAPI, React, PostgreSQL, Docker.
Location: Remote</textarea>
                <button id="findBtn" onclick="findMatches()">🔍 Find Matching Candidates</button>
            </div>
            
            <div class="card">
                <h2>🏆 Candidate Rankings</h2>
                <div id="results">
                    <div style="text-align: center; padding: 40px; color: #999;">
                        Click "Find Matches" to see ranked candidates
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const templates = {
            python: `Senior Python Developer - Remote\\nRequired Skills:\\n- Python\\n- FastAPI\\n- PostgreSQL\\n- React\\n- Docker\\n\\nLocation: Remote`,
            react: `Senior React Developer - Remote\\nRequired Skills:\\n- React.js\\n- TypeScript\\n- Redux\\n- Node.js\\n- MongoDB\\n\\nLocation: Remote`,
            devops: `DevOps Engineer - Remote\\nRequired Skills:\\n- Kubernetes\\n- Docker\\n- AWS\\n- Terraform\\n- CI/CD\\n\\nLocation: Remote`,
            fullstack: `Full Stack Developer - Remote\\nRequired Skills:\\n- Python/JavaScript\\n- React\\n- Node.js\\n- PostgreSQL\\n- Docker\\n\\nLocation: Remote`
        };

        function loadTemplate(type) {
            document.getElementById('jobDescription').value = templates[type];
        }

        async function findMatches() {
            const btn = document.getElementById('findBtn');
            const resultsDiv = document.getElementById('results');
            const jobDescription = document.getElementById('jobDescription').value;
            
            if (!jobDescription.trim()) {
                resultsDiv.innerHTML = '<div class="error">❌ Please enter a job description</div>';
                return;
            }
            
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner"></span> Analyzing Candidates...';
            resultsDiv.innerHTML = '<div style="text-align: center; padding: 40px;"><span class="spinner"></span> Loading matches...</div>';
            
            try {
                const response = await fetch('/Api/mike/match', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        job_description: jobDescription
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                displayResults(data);
            } catch (error) {
                console.error('Error:', error);
                resultsDiv.innerHTML = `
                    <div class="error">
                        <strong>❌ Error: ${error.message}</strong><br><br>
                        Make sure the backend is running at http://localhost:8000
                    </div>
                `;
            } finally {
                btn.disabled = false;
                btn.innerHTML = '🔍 Find Matching Candidates';
            }
        }
        
        function displayResults(data) {
            const resultsDiv = document.getElementById('results');
            
            if (!data.top_candidates || data.top_candidates.length === 0) {
                resultsDiv.innerHTML = '<div class="error">No candidates found matching your criteria</div>';
                return;
            }
            
            const requiredSkills = data.job_requirements.skills.map(s => s.toLowerCase());
            
            let html = `
                <div class="stats">
                    <span>📊 ${data.total_candidates_considered} candidates analyzed</span>
                    <span>⚡ ${data.query_time_ms} ms</span>
                </div>
                <div class="requirements">
                    <strong>📋 Job Requirements</strong><br>
                    <strong>Role:</strong> ${data.job_requirements.role}<br>
                    <strong>Experience:</strong> ${data.job_requirements.experience_band} (${data.job_requirements.years_experience_min}+ years)<br>
                    <strong>Location:</strong> ${data.job_requirements.location}<br>
                    <strong>Required Skills:</strong><br>
                    ${data.job_requirements.skills.map(s => `<span class="skill-tag">${s}</span>`).join('')}
                </div>
            `;
            
            data.top_candidates.forEach((match, index) => {
                const c = match.candidate;
                let scoreClass = 'score-low';
                if (match.match_score >= 70) scoreClass = 'score-high';
                else if (match.match_score >= 50) scoreClass = 'score-medium';
                
                html += `
                    <div class="candidate-card">
                        <div class="card-header">
                            <div class="candidate-name">
                                #${index + 1} - ${c.name}
                                <span class="badge ${match.experience_match ? 'badge-yes' : 'badge-no'}">
                                    ${match.experience_match ? '✓ Experience' : '! Experience Gap'}
                                </span>
                                <span class="badge ${match.location_match ? 'badge-yes' : 'badge-no'}">
                                    ${match.location_match ? '✓ Location' : '! Location'}
                                </span>
                            </div>
                            <div class="match-score ${scoreClass}">
                                ${match.match_score}% Match
                            </div>
                        </div>
                        
                        <div class="candidate-details">
                            <span>💼 ${c.current_role || 'N/A'}</span>
                            <span>⭐ ${c.experience_years} years</span>
                            <span>📍 ${c.location}</span>
                            <span>🎓 ${c.education || 'N/A'}</span>
                        </div>
                        
                        <div class="skills">
                            ${c.skills.map(skill => {
                                const isHighlight = requiredSkills.includes(skill.toLowerCase());
                                return `<span class="skill ${isHighlight ? 'highlight' : ''}">${skill}</span>`;
                            }).join('')}
                        </div>
                        
                        <div class="rationale">
                            <strong>🔍 Match Analysis:</strong> ${match.match_rationale}
                        </div>
                    </div>
                `;
            });
            
            resultsDiv.innerHTML = html;
        }
    </script>
</body>
</html>
"""

# THIS IS THE IMPORTANT PART - Root endpoint serves the HTML
@app.get("/")
async def root():
    return HTMLResponse(content=HTML_PAGE)

# Also serve at /ui for convenience
@app.get("/ui")
async def ui():
    return HTMLResponse(content=HTML_PAGE)

if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("Work360 Candidate Ranking System")
    print("=" * 50)
    print("Server running at: http://localhost:8000")
    print("Open your browser and go to: http://localhost:8000")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)