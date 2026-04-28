import json
from pathlib import Path
from typing import Dict, List, Set, Optional
from collections import defaultdict, deque
from functools import lru_cache

class RoadmapGenerator:
    """Generate personalized learning roadmaps based on skill gaps"""
    
    def __init__(self):
        # Load skill prerequisites
        prereq_path = Path(__file__).parent.parent / "data" / "skill_prerequisites.json"
        with open(prereq_path, 'r') as f:
            data = json.load(f)
            self.skill_graph = data["skill_graph"]
        
        # Load learning resources
        resources_path = Path(__file__).parent.parent / "data" / "learning_resources.json"
        with open(resources_path, 'r') as f:
            self.resources = json.load(f)
        
        # Cache for performance
        self._prereq_cache = {}
    
    @lru_cache(maxsize=128)
    def get_skill_info(self, skill: str) -> Optional[Dict]:
        """Get information about a specific skill (cached)"""
        # Try exact match
        if skill in self.skill_graph:
            return self.skill_graph[skill]
        
        # Try case-insensitive match
        for key, value in self.skill_graph.items():
            if key.lower() == skill.lower():
                return value
        
        # Return default for unknown skills
        return {
            "prerequisites": [],
            "difficulty": "intermediate",
            "estimated_hours": 30,
            "category": "general"
        }
    
    def resolve_prerequisites(self, target_skills: List[str], current_skills: List[str]) -> List[str]:
        """
        Enhanced prerequisite resolution with cycle detection
        Returns ordered list of skills to learn (dependencies first)
        """
        current_set = set([s.lower() for s in current_skills])
        target_set = set([s.lower() for s in target_skills])
        
        # Track visited skills to detect cycles
        visited = set()
        all_needed = []
        
        def add_skill_with_prereqs(skill: str, depth: int = 0):
            """Recursively add skills with cycle detection"""
            if depth > 10:  # Prevent infinite recursion
                return
            
            skill_lower = skill.lower()
            
            # Skip if already have or already processed
            if skill_lower in current_set or skill_lower in visited:
                return
            
            visited.add(skill_lower)
            
            skill_info = self.get_skill_info(skill)
            prerequisites = skill_info.get("prerequisites", [])
            
            # Add prerequisites first (recursively)
            for prereq in prerequisites:
                add_skill_with_prereqs(prereq, depth + 1)
            
            # Then add the skill itself
            if skill not in all_needed:
                all_needed.append(skill)
        
        # Process all target skills
        for skill in target_skills:
            add_skill_with_prereqs(skill)
        
        return all_needed
    
    def topological_sort(self, skills: List[str]) -> List[str]:
        """
        Enhanced topological sort with difficulty-based ordering
        Skills with same dependencies are ordered by difficulty
        """
        # Build adjacency list and in-degree map
        graph = defaultdict(list)
        in_degree = defaultdict(int)
        skill_difficulty = {}
        
        # Initialize all skills
        for skill in skills:
            if skill not in in_degree:
                in_degree[skill] = 0
            skill_info = self.get_skill_info(skill)
            skill_difficulty[skill] = {
                "beginner": 1,
                "intermediate": 2,
                "advanced": 3
            }.get(skill_info.get("difficulty", "intermediate"), 2)
        
        # Build dependency graph
        for skill in skills:
            skill_info = self.get_skill_info(skill)
            prerequisites = skill_info.get("prerequisites", [])
            
            for prereq in prerequisites:
                if prereq in skills:
                    graph[prereq].append(skill)
                    in_degree[skill] += 1
        
        # Modified Kahn's algorithm with difficulty sorting
        queue = []
        for skill in skills:
            if in_degree[skill] == 0:
                queue.append((skill, skill_difficulty[skill]))
        
        # Sort by difficulty
        queue.sort(key=lambda x: x[1])
        queue = deque([s[0] for s in queue])
        
        sorted_skills = []
        
        while queue:
            current = queue.popleft()
            sorted_skills.append(current)
            
            # Collect neighbors and their difficulties
            neighbors = []
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    neighbors.append((neighbor, skill_difficulty[neighbor]))
            
            # Sort neighbors by difficulty before adding to queue
            neighbors.sort(key=lambda x: x[1])
            queue.extend([n[0] for n in neighbors])
        
        return sorted_skills
    
    def create_weekly_plan(
        self, 
        skills_to_learn: List[str], 
        hours_per_week: int = 15,
        learning_style: str = "balanced"
    ) -> List[Dict]:
        """
        Create an adaptive weekly learning plan
        learning_style: 'intensive' (25h/week), 'balanced' (15h/week), 'relaxed' (10h/week)
        """
        weekly_plan = []
        current_week = {
            "week": 1,
            "skills": [],
            "total_hours": 0,
            "focus_area": "",
            "milestones": [],
            "projects": []
        }
        
        # Difficulty-based learning tips and strategies
        difficulty_strategies = {
            "beginner": {
                "tip": "Focus on fundamentals. Take your time with basics.",
                "practice_ratio": 0.6,  # 60% hands-on practice
                "study_ratio": 0.4      # 40% theory
            },
            "intermediate": {
                "tip": "Build projects while learning. Apply concepts immediately.",
                "practice_ratio": 0.7,
                "study_ratio": 0.3
            },
            "advanced": {
                "tip": "Deep dive into internals. Contribute to open source.",
                "practice_ratio": 0.8,
                "study_ratio": 0.2
            }
        }
        
        for i, skill in enumerate(skills_to_learn):
            skill_info = self.get_skill_info(skill)
            estimated_hours = skill_info.get("estimated_hours", 20)
            difficulty = skill_info.get("difficulty", "intermediate")
            category = skill_info.get("category", "general")
            
            strategy = difficulty_strategies.get(difficulty, difficulty_strategies["intermediate"])
            
            # If adding this skill exceeds weekly hours, start new week
            if current_week["total_hours"] + estimated_hours > hours_per_week and current_week["skills"]:
                # Finalize current week
                self._finalize_week(current_week)
                weekly_plan.append(current_week)
                
                # Start new week
                current_week = {
                    "week": len(weekly_plan) + 1,
                    "skills": [],
                    "total_hours": 0,
                    "focus_area": "",
                    "milestones": [],
                    "projects": []
                }
            
            # Add skill to current week
            practice_hours = int(estimated_hours * strategy["practice_ratio"])
            study_hours = estimated_hours - practice_hours
            
            current_week["skills"].append({
                "name": skill,
                "estimated_hours": estimated_hours,
                "study_hours": study_hours,
                "practice_hours": practice_hours,
                "difficulty": difficulty,
                "category": category,
                "learning_tip": strategy["tip"],
                "daily_goal": f"Study {study_hours // 5}h + Practice {practice_hours // 5}h per day"
            })
            current_week["total_hours"] += estimated_hours
            
            # Add milestone
            current_week["milestones"].append(
                f"✅ Complete {skill} fundamentals and build a mini-project"
            )
            
            # Add project suggestion
            project = self._suggest_project(skill, difficulty)
            if project:
                current_week["projects"].append(project)
        
        # Add the last week
        if current_week["skills"]:
            self._finalize_week(current_week)
            weekly_plan.append(current_week)
        
        return weekly_plan
    
    def _finalize_week(self, week: Dict):
        """Finalize week with focus area and summary"""
        categories = [s["category"] for s in week["skills"]]
        week["focus_area"] = max(set(categories), key=categories.count) if categories else "mixed"
        
        # Add weekly summary
        difficulties = [s["difficulty"] for s in week["skills"]]
        if "advanced" in difficulties:
            week["intensity"] = "High"
        elif "beginner" in difficulties and len(difficulties) == difficulties.count("beginner"):
            week["intensity"] = "Moderate"
        else:
            week["intensity"] = "Medium"
    
    def _suggest_project(self, skill: str, difficulty: str) -> Optional[str]:
        """Suggest a project based on skill and difficulty"""
        projects = {
            "Python": {
                "beginner": "Build a calculator or to-do list CLI app",
                "intermediate": "Create a web scraper or data analysis script",
                "advanced": "Build a REST API with authentication"
            },
            "React": {
                "beginner": "Create a personal portfolio website",
                "intermediate": "Build a weather app with API integration",
                "advanced": "Develop a full-featured dashboard with state management"
            },
            "Machine Learning": {
                "beginner": "Iris dataset classification",
                "intermediate": "Build a house price predictor",
                "advanced": "Create a recommendation system"
            },
            "Node.js": {
                "beginner": "Simple HTTP server",
                "intermediate": "RESTful API with database",
                "advanced": "Real-time chat application"
            },
            "Docker": {
                "beginner": "Containerize a simple app",
                "intermediate": "Multi-container app with Docker Compose",
                "advanced": "Deploy microservices architecture"
            }
        }
        
        skill_projects = projects.get(skill, {})
        return skill_projects.get(difficulty, f"Build a practical project using {skill}")
    
    def get_resources(self, skill: str) ->Dict:
        """Get learning resources for a skill with fallback"""
        skill_key = skill
        
        # Try exact match
        if skill_key in self.resources:
            return self.resources[skill_key]
        
        # Try case-insensitive match
        for key in self.resources.keys():
            if key.lower() == skill.lower():
                return self.resources[key]
        
        # Return default resources with skill-specific search links
        default = self.resources.get("default", {}).copy()
        
        # Add skill-specific search URLs
        default["search_links"] = {
            "udemy": f"https://www.udemy.com/courses/search/?q={skill.replace(' ', '+')}",
            "coursera": f"https://www.coursera.org/search?query={skill.replace(' ', '%20')}",
            "youtube": f"https://www.youtube.com/results?search_query={skill.replace(' ', '+')}+tutorial",
            "freecodecamp": f"https://www.freecodecamp.org/news/search/?query={skill.replace(' ', '%20')}"
        }
        
        return default
    
    def generate_roadmap(
        self,
        target_skills: List[str],
        current_skills: List[str],
        hours_per_week: int = 15,
        learning_style: str = "balanced"
    ) -> Dict:
        """
        Generate complete enhanced learning roadmap
        """
        # Resolve prerequisites
        skills_to_learn = self.resolve_prerequisites(target_skills, current_skills)
        
        # Sort in optimal learning order
        ordered_skills = self.topological_sort(skills_to_learn)
        
        # Create adaptive weekly plan
        weekly_plan = self.create_weekly_plan(ordered_skills, hours_per_week, learning_style)
        
        # Calculate comprehensive time estimates
        total_hours = sum([
            self.get_skill_info(skill).get("estimated_hours", 20)
            for skill in ordered_skills
        ])
        total_weeks = len(weekly_plan)
        total_months = round(total_weeks / 4.33, 1)
        
        # Get resources for all skills
        resources_map = {}
        for skill in ordered_skills:
            resources_map[skill] = self.get_resources(skill)
        
        # Group by difficulty and category
        skills_by_difficulty = {
            "beginner": [],
            "intermediate": [],
            "advanced": []
        }
        
        skills_by_category = defaultdict(list)
        
        for skill in ordered_skills:
            info = self.get_skill_info(skill)
            difficulty = info.get("difficulty", "intermediate")
            category = info.get("category", "general")
            
            skills_by_difficulty[difficulty].append(skill)
            skills_by_category[category].append(skill)
        
        # Generate learning milestones
        milestones = self._generate_milestones(ordered_skills, weekly_plan)
        
        # Calculate completion estimates for different paces
        pace_estimates = {
            "intensive": {
                "hours_per_week": 25,
                "weeks": max(1, round(total_hours / 25)),
                "months": max(0.5, round((total_hours / 25) / 4.33, 1))
            },
            "balanced": {
                "hours_per_week": 15,
                "weeks": total_weeks,
                "months": total_months
            },
            "relaxed": {
                "hours_per_week": 10,
                "weeks": max(1, round(total_hours / 10)),
                "months": max(0.5, round((total_hours / 10) / 4.33, 1))
            }
        }
        
        return {
            "total_weeks": total_weeks,
            "total_months": total_months,
            "total_hours": total_hours,
            "hours_per_week": hours_per_week,
            "skills_to_learn": ordered_skills,
            "skills_count": len(ordered_skills),
            "weekly_plan": weekly_plan,
            "milestones": milestones,
            "resources": resources_map,
            "skills_by_difficulty": skills_by_difficulty,
            "skills_by_category": dict(skills_by_category),
            "pace_estimates": pace_estimates,
            "learning_path_summary": {
                "beginner_skills": len(skills_by_difficulty["beginner"]),
                "intermediate_skills": len(skills_by_difficulty["intermediate"]),
                "advanced_skills": len(skills_by_difficulty["advanced"]),
                "categories_covered": list(skills_by_category.keys())
            },
            "recommendations": self._generate_recommendations(ordered_skills, current_skills, total_weeks),
            "success_tips": self._generate_success_tips(total_weeks, len(ordered_skills))
        }
    
    def _generate_milestones(self, skills: List[str], weekly_plan: List[Dict]) -> List[Dict]:
        """Generate achievement milestones throughout the learning journey"""
        milestones = []
        
        # Week 1 milestone
        if weekly_plan:
            first_skills = [s["name"] for s in weekly_plan[0]["skills"]]
            milestones.append({
                "week": 1,
                "title": "🚀 Journey Begins",
                "description": f"Complete your first skill: {first_skills[0] if first_skills else 'Foundation'}",
                "achievement": "Getting Started"
            })
        
        # Quarter milestones
        quarter_mark = len(weekly_plan) // 4
        if quarter_mark > 0:
            milestones.append({
                "week": quarter_mark,
                "title": "📈 25% Complete",
                "description": "You're making great progress! Keep the momentum.",
                "achievement": "Quarter Master"
            })
        
        # Half-way milestone
        half_mark = len(weekly_plan) // 2
        if half_mark > 0:
            milestones.append({
                "week": half_mark,
                "title": "🎯 Halfway There",
                "description": "You've covered half the journey. Time for a portfolio project!",
                "achievement": "Midway Champion"
            })
        
        # Three-quarter milestone
        three_quarter = (len(weekly_plan) * 3) // 4
        if three_quarter > 0:
            milestones.append({
                "week": three_quarter,
                "title": "🔥 75% Complete",
                "description": "Almost there! Start preparing for job applications.",
                "achievement": "Advanced Learner"
            })
        
        # Final milestone
        if weekly_plan:
            final_week = len(weekly_plan)
            last_skills = [s["name"] for s in weekly_plan[-1]["skills"]]
            milestones.append({
                "week": final_week,
                "title": "🎉 Journey Complete",
                "description": f"Congratulations! You've mastered all skills. You're job-ready!",
                "achievement": "Skill Master"
            })
        
        return milestones
    
    def _generate_recommendations(self, skills_to_learn: List[str], current_skills: List[str], total_weeks: int) -> List[str]:
        """Generate enhanced personalized learning recommendations"""
        recommendations = []
        
        # Time-based recommendations
        if total_weeks > 20:
            recommendations.append("⏰ This is a long journey (20+ weeks). Consider focusing on 3-5 high-priority skills first.")
        elif total_weeks > 10:
            recommendations.append("📅 Dedicate 3-6 months consistently. Create a study schedule and stick to it.")
        else:
            recommendations.append("🚀 Great! This roadmap is achievable in 2-3 months with consistent effort.")
        
        # Skill count recommendations
        if len(skills_to_learn) > 10:
            recommendations.append("🎯 Large skill set detected. Focus on 2-3 skills at a time for better retention.")
        elif len(skills_to_learn) > 5:
            recommendations.append("📚 Balance theory and practice. Build projects after every 2 skills.")
        else:
            recommendations.append("✨ Focused learning path! Deep dive into each skill before moving forward.")
        
        # Foundational skills
        foundational = ["Git", "HTML", "CSS", "Python", "JavaScript", "SQL"]
        missing_foundational = [s for s in foundational if s.lower() not in [c.lower() for c in current_skills] and s in skills_to_learn]
        
        if missing_foundational:
            recommendations.append(f"🔰 Master these foundational skills first: {', '.join(missing_foundational[:3])}")
        
        # Project-based learning
        recommendations.append("🛠️ Build a portfolio project after completing every 2-3 skills.")
        
        # Community engagement
        recommendations.append("👥 Join online communities (Discord, Reddit, Twitter) for support and networking.")
        
        # Practice recommendations
        recommendations.append("💻 Practice daily on platforms like LeetCode, HackerRank, or Kaggle (based on your focus).")
        
        # Career readiness
        if total_weeks < 12:
            recommendations.append("📝 Update your resume and LinkedIn profile after 50% completion.")
        else:
            recommendations.append("📝 Update your portfolio every month to track progress.")
        
        # Learning strategies
        recommendations.append("📖 Use the Feynman Technique: Teach what you learn to solidify understanding.")
        recommendations.append("🔄 Review previous skills weekly to prevent knowledge decay.")
        
        return recommendations
    
    def _generate_success_tips(self, total_weeks: int, skill_count: int) -> List[str]:
        """Generate tips for successful learning journey"""
        tips = [
            "🎯 Set SMART goals: Specific, Measurable, Achievable, Relevant, Time-bound",
            "⏰ Study at the same time daily to build a habit",
            "📝 Take notes and create a personal knowledge base",
            "🔄 Practice spaced repetition for better retention",
            "💪 Don't skip the fundamentals - they're crucial",
            "🚫 Avoid tutorial hell - build projects from scratch",
            "👨‍💻 Code every day, even if just for 30 minutes",
            "🤝 Pair program or join study groups for accountability",
            "📊 Track your progress weekly and celebrate small wins",
            "🧘 Take breaks to avoid burnout - learning is a marathon"
        ]
        
        # Add context-specific tips
        if total_weeks > 16:
            tips.insert(0, "⚡ Long journey ahead - stay consistent rather than intense")
        if skill_count > 8:
            tips.insert(0, "🎯 Create a visual skill tree to track dependencies and progress")
        
        return tips[:10]  # Return top 10 tips
    
    def generate_alternative_paths(self, target_role: str, current_skills: List[str]) -> List[Dict]:
        """Generate alternative learning paths for flexibility"""
        # This would be useful for showing different approaches to the same goal
        # For example: Frontend path vs Full-stack path vs Backend path
        # Implementation can be expanded based on requirements
        
        paths = []
        
        # Example structure
        paths.append({
            "name": "Fast Track",
            "description": "Focus on most critical skills first",
            "duration_weeks": "8-12",
            "skills": []  # Would contain prioritized subset
        })
        
        paths.append({
            "name": "Comprehensive",
            "description": "Cover all skills thoroughly",
            "duration_weeks": "12-16",
            "skills": []  # Would contain all skills
        })
        
        return paths