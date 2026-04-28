from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import logging

from app.text_parser import ResumeParser
from app.skills_extractor import SkillsExtractor
from app.market_analyzer import MarketAnalyzer
from app.roadmap_generator import RoadmapGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="SkillCompass AI API",
    description="Resume skill extraction and analysis",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize extractors, analyzer, and roadmap generator
parser = ResumeParser()
extractor = SkillsExtractor()
analyzer = MarketAnalyzer()
roadmap_gen = RoadmapGenerator()

# ============================================
# RESPONSE MODELS
# ============================================

class SkillsResponse(BaseModel):
    all_skills: List[str]
    categorized: Dict[str, List[str]]
    count: int
    resume_text_preview: str

class HealthResponse(BaseModel):
    status: str
    message: str

class SkillsListRequest(BaseModel):
    skills: List[str]

class RoleComparisonRequest(BaseModel):
    skills: List[str]
    target_role: str

class RoleComparisonResponse(BaseModel):
    target_role: str
    experience_level: str
    avg_salary: int
    readiness_percentage: float
    matched_required_skills: List[str]
    missing_required_skills: List[str]
    matched_nice_to_have: List[str]
    missing_nice_to_have: List[str]
    total_required: int
    total_matched: int

class SkillRanking(BaseModel):
    skill: str
    priority_score: float
    demand_score: int
    growth_rate: int
    trend: str
    saturation: str
    job_postings: int
    avg_salary: int

class RankedSkillsResponse(BaseModel):
    ranked_skills: List[SkillRanking]
    count: int

class RoadmapRequest(BaseModel):
    target_skills: List[str]
    current_skills: List[str]
    hours_per_week: Optional[int] = 15

# ============================================
# ROUTES
# ============================================

@app.get("/", response_model=HealthResponse)
async def root():
    return {
        "status": "online",
        "message": "SkillCompass AI API is running"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return {
        "status": "healthy",
        "message": "All systems operational"
    }

@app.post("/api/extract-skills", response_model=SkillsResponse)
async def extract_skills(file: UploadFile = File(...)):
    """
    Extract skills from uploaded resume (PDF or DOCX)
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.docx')):
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Only PDF and DOCX allowed."
            )
        
        # Read file content
        file_content = await file.read()
        
        # Extract text from resume
        logger.info(f"Parsing resume: {file.filename}")
        resume_text = parser.extract_text(file_content, file.filename)
        
        if not resume_text or len(resume_text) < 50:
            raise HTTPException(
                status_code=400,
                detail="Could not extract sufficient text from resume"
            )
        
        # Extract skills
        logger.info("Extracting skills...")
        skills_data = extractor.extract_skills(resume_text)
        
        # Return response
        return {
            **skills_data,
            "resume_text_preview": resume_text[:200] + "..."
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing resume: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/api/test-skills")
async def test_skills_extraction(text: str):
    """
    Test endpoint: Extract skills from plain text
    """
    try:
        skills_data = extractor.extract_skills(text)
        return skills_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/roles", response_model=List[str])
async def get_available_roles():
    """
    Get list of all available job roles
    """
    return analyzer.get_all_roles()

@app.post("/api/rank-skills", response_model=RankedSkillsResponse)
async def rank_skills(request: SkillsListRequest):
    """
    Rank skills by market priority
    """
    try:
        ranked = analyzer.rank_skills(request.skills)
        return {
            "ranked_skills": ranked,
            "count": len(ranked)
        }
    except Exception as e:
        logger.error(f"Error ranking skills: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/compare-role")
async def compare_with_role(request: RoleComparisonRequest):
    """
    Compare user skills with target job role
    """
    try:
        comparison = analyzer.compare_with_role(
            request.skills,
            request.target_role
        )
        
        if "error" in comparison:
            raise HTTPException(status_code=404, detail=comparison["error"])
        
        return comparison
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing with role: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze-resume-full")
async def analyze_resume_full(
    file: UploadFile = File(...),
    target_role: Optional[str] = None
):
    """
    Complete resume analysis with skill extraction, ranking, and role comparison
    """
    try:
        # Extract skills from resume
        file_content = await file.read()
        resume_text = parser.extract_text(file_content, file.filename)
        skills_data = extractor.extract_skills(resume_text)
        
        user_skills = skills_data["all_skills"]
        
        # Rank skills by market priority
        ranked_skills = analyzer.rank_skills(user_skills)
        
        # Role comparison (if provided)
        role_comparison = None
        if target_role:
            role_comparison = analyzer.compare_with_role(user_skills, target_role)
        
        return {
            "extracted_skills": skills_data,
            "market_analysis": {
                "ranked_skills": ranked_skills,
                "top_skills": ranked_skills[:5]  # Top 5 highest priority
            },
            "role_comparison": role_comparison,
            "available_roles": analyzer.get_all_roles()
        }
    
    except Exception as e:
        logger.error(f"Error in full analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-roadmap")
async def generate_roadmap(request: RoadmapRequest):
    """
    Generate personalized learning roadmap
    """
    try:
        roadmap = roadmap_gen.generate_roadmap(
            target_skills=request.target_skills,
            current_skills=request.current_skills,
            hours_per_week=request.hours_per_week
        )
        return roadmap
    except Exception as e:
        logger.error(f"Error generating roadmap: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze-resume-with-roadmap")
async def analyze_resume_with_roadmap(
    file: UploadFile = File(...),
    target_role: str = "Data Scientist",
    hours_per_week: int = 15
):
    """
    Complete analysis: Extract skills + Compare with role + Generate roadmap
    This is the main endpoint that combines everything!
    """
    try:
        # Extract skills from resume
        file_content = await file.read()
        resume_text = parser.extract_text(file_content, file.filename)
        skills_data = extractor.extract_skills(resume_text)
        
        user_skills = skills_data["all_skills"]
        
        # Rank skills by market priority
        ranked_skills = analyzer.rank_skills(user_skills)
        
        # Role comparison
        role_comparison = analyzer.compare_with_role(user_skills, target_role)
        
        # Generate roadmap for missing skills
        missing_skills = role_comparison.get("missing_required_skills", [])
        
        roadmap = None
        if missing_skills:
            roadmap = roadmap_gen.generate_roadmap(
                target_skills=missing_skills,
                current_skills=user_skills,
                hours_per_week=hours_per_week
            )
        
        return {
            "extracted_skills": skills_data,
            "market_analysis": {
                "ranked_skills": ranked_skills,
                "top_skills": ranked_skills[:5]
            },
            "role_comparison": role_comparison,
            "learning_roadmap": roadmap,
            "summary": {
                "current_skill_count": len(user_skills),
                "required_skill_count": role_comparison.get("total_required", 0),
                "readiness_percentage": role_comparison.get("readiness_percentage", 0),
                "skills_to_learn": len(missing_skills),
                "estimated_weeks": roadmap.get("total_weeks", 0) if roadmap else 0,
                "estimated_hours": roadmap.get("total_hours", 0) if roadmap else 0
            }
        }
    
    except Exception as e:
        logger.error(f"Error in complete analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
from time import time

# Add performance tracking middleware
@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time()
    response = await call_next(request)
    process_time = time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time, 3))
    logger.info(f"Request to {request.url.path} took {process_time:.3f}s")
    return response

# Add a new endpoint for performance insights
@app.get("/api/stats")
async def get_api_stats():
    """Get API statistics and capabilities"""
    return {
        "total_endpoints": 10,
        "skills_tracked": len(analyzer.market_data),
        "job_roles_available": len(analyzer.job_roles),
        "skill_graph_nodes": len(roadmap_gen.skill_graph),
        "learning_resources": len(roadmap_gen.resources),
        "market_insights": analyzer.get_market_insights(),
        "api_version": "1.0.0",
        "features": [
            "Resume skill extraction",
            "Market demand analysis",
            "Role comparison",
            "Learning roadmap generation",
            "Prerequisite resolution",
            "Resource recommendations",
            "Career advice",
            "Progress tracking"
        ]
    }
