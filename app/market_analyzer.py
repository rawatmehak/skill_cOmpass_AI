import json
from pathlib import Path
from typing import Dict, List, Optional
from functools import lru_cache

class MarketAnalyzer:
    """Analyze market demand and trends for skills"""
    
    def __init__(self):
        # Load market demand data
        demand_path = Path(__file__).parent.parent / "data" / "market_demand.json"
        with open(demand_path, 'r') as f:
            self.market_data = json.load(f)
        
        # Load job roles data
        roles_path = Path(__file__).parent.parent / "data" / "job_roles.json"
        with open(roles_path, 'r') as f:
            self.job_roles = json.load(f)
        
        # Precompute market insights
        self._precompute_insights()
    
    def _precompute_insights(self):
        """Precompute common market insights for better performance"""
        self.top_demand_skills = sorted(
            self.market_data.keys(),
            key=lambda x: self.market_data[x]["demand_score"],
            reverse=True
        )[:10]
        
        self.fastest_growing = sorted(
            self.market_data.keys(),
            key=lambda x: self.market_data[x]["growth_rate"],
            reverse=True
        )[:10]
        
        self.highest_salary_skills = sorted(
            self.market_data.keys(),
            key=lambda x: self.market_data[x].get("avg_salary", 0),
            reverse=True
        )[:10]
    
    @lru_cache(maxsize=256)
    def get_skill_demand(self, skill: str) -> Optional[Dict]:
        """Get market demand data for a specific skill (cached)"""
        # Try exact match first
        if skill in self.market_data:
            return self.market_data[skill]
        
        # Try case-insensitive match
        for key in self.market_data.keys():
            if key.lower() == skill.lower():
                return self.market_data[key]
        
        # Return default data for unknown skills
        return {
            "demand_score": 50,
            "growth_rate": 0,
            "job_postings": 1000,
            "trend": "unknown",
            "saturation": "unknown",
            "avg_salary": 75000
        }
    
    def calculate_priority_score(self, skill: str, user_context: Dict = None) -> float:
        """
        Enhanced priority score calculation
        Formula: Considers demand, growth, saturation, salary, and user context
        """
        demand_data = self.get_skill_demand(skill)
        
        # Base components
        demand_component = demand_data["demand_score"] * 0.5
        growth_component = demand_data["growth_rate"] * 2.5
        
        # Salary impact
        salary = demand_data.get("avg_salary", 75000)
        salary_component = (salary / 150000) * 10  # Normalize to 0-10 scale
        
        # Saturation penalty (enhanced)
        saturation_penalties = {
            "very_high": -20,
            "high": -10,
            "medium": 0,
            "low": 10,
            "unknown": 0
        }
        saturation_penalty = saturation_penalties.get(demand_data["saturation"], 0)
        
        # Trend bonus
        trend_bonuses = {
            "rapidly_rising": 15,
            "rising": 8,
            "stable": 0,
            "declining": -10,
            "unknown": 0
        }
        trend_bonus = trend_bonuses.get(demand_data["trend"], 0)
        
        # Context-based adjustments
        context_bonus = 0
        if user_context:
            # Bonus for skills in user's target role
            target_role = user_context.get("target_role")
            if target_role and target_role in self.job_roles:
                role_skills = self.job_roles[target_role]["required_skills"]
                if skill in role_skills:
                    context_bonus += 15
        
        priority = (
            demand_component + 
            growth_component + 
            salary_component +
            saturation_penalty + 
            trend_bonus +
            context_bonus
        )
        
        return round(priority, 2)
    
    def rank_skills(self, skills: List[str], user_context: Dict = None) -> List[Dict]:
        """Rank skills by enhanced priority score"""
        ranked = []
        
        for skill in skills:
            demand_data = self.get_skill_demand(skill)
            priority = self.calculate_priority_score(skill, user_context)
            
            # Calculate market position
            market_position = self._calculate_market_position(skill)
            
            ranked.append({
                "skill": skill,
                "priority_score": priority,
                "demand_score": demand_data["demand_score"],
                "growth_rate": demand_data["growth_rate"],
                "trend": demand_data["trend"],
                "saturation": demand_data["saturation"],
                "job_postings": demand_data["job_postings"],
                "avg_salary": demand_data["avg_salary"],
                "market_position": market_position,
                "recommendation": self._get_skill_recommendation(demand_data)
            })
        
        # Sort by priority score (descending)
        ranked.sort(key=lambda x: x["priority_score"], reverse=True)
        
        return ranked
    
    def _calculate_market_position(self, skill: str) -> str:
        """Determine market position of a skill"""
        demand_data = self.get_skill_demand(skill)
        demand = demand_data["demand_score"]
        growth = demand_data["growth_rate"]
        
        if demand >= 90 and growth >= 20:
            return "🔥 Hot & Growing"
        elif demand >= 85:
            return "⭐ High Demand"
        elif growth >= 20:
            return "📈 Rapidly Growing"
        elif demand >= 70:
            return "✅ Steady Demand"
        elif growth < 0:
            return "⚠️ Declining"
        else:
            return "📊 Moderate"
    
    def _get_skill_recommendation(self, demand_data: Dict) -> str:
        """Get personalized recommendation for a skill"""
        demand = demand_data["demand_score"]
        growth = demand_data["growth_rate"]
        saturation = demand_data["saturation"]
        
        if demand >= 90 and growth >= 20 and saturation in ["low", "medium"]:
            return "Excellent career opportunity! High demand with strong growth."
        elif demand >= 85:
            return "Strong market demand. Great skill to have."
        elif growth >= 20:
            return "Emerging skill with high growth potential."
        elif saturation == "very_high":
            return "Highly competitive. Consider specializing."
        elif growth < 0:
            return "Declining demand. Consider alternatives."
        else:
            return "Valuable skill with steady opportunities."
    
    def compare_with_role(self, user_skills: List[str], target_role: str) -> Dict:
        """Enhanced role comparison with detailed insights"""
        if target_role not in self.job_roles:
            return {
                "error": f"Role '{target_role}' not found",
                "available_roles": list(self.job_roles.keys())
            }
        
        role_data = self.job_roles[target_role]
        required_skills = set(role_data["required_skills"])
        nice_to_have_skills = set(role_data.get("nice_to_have", []))
        user_skills_set = set(user_skills)
        
        # Calculate matches
        matched_required = user_skills_set.intersection(required_skills)
        missing_required = required_skills - user_skills_set
        matched_nice = user_skills_set.intersection(nice_to_have_skills)
        missing_nice = nice_to_have_skills - user_skills_set
        
        # Calculate readiness percentage
        required_match_percent = (
            len(matched_required) / len(required_skills) * 100
            if required_skills else 0
        )
        
        # Overall readiness (including nice-to-have)
        total_desired = len(required_skills) + len(nice_to_have_skills)
        total_matched = len(matched_required) + len(matched_nice)
        overall_readiness = (total_matched / total_desired * 100) if total_desired > 0 else 0
        
        # Prioritize missing skills
        prioritized_missing = self.rank_skills(
            list(missing_required),
            user_context={"target_role": target_role}
        )
        
        # Career advice based on readiness
        career_advice = self._generate_career_advice(
            required_match_percent,
            len(missing_required),
            target_role
        )
        
        return {
            "target_role": target_role,
            "experience_level": role_data["experience_level"],
            "avg_salary": role_data["avg_salary_usd"],
            "readiness_percentage": round(required_match_percent, 1),
            "overall_readiness": round(overall_readiness, 1),
            "matched_required_skills": list(matched_required),
            "missing_required_skills": list(missing_required),
            "prioritized_missing_skills": prioritized_missing[:5],  # Top 5
            "matched_nice_to_have": list(matched_nice),
            "missing_nice_to_have": list(missing_nice),
            "total_required": len(required_skills),
            "total_matched": len(matched_required),
            "career_advice": career_advice,
            "next_steps": self._generate_next_steps(prioritized_missing[:3])
        }
    
    def _generate_career_advice(self, readiness: float, missing_count: int, role: str) -> str:
        """Generate personalized career advice"""
        if readiness >= 90:
            return f"🎉 Excellent! You're well-prepared for {role} roles. Start applying!"
        elif readiness >= 75:
            return f"👍 Strong foundation! Focus on the {missing_count} remaining skills to become job-ready."
        elif readiness >= 50:
            return f"📚 Good progress! Dedicate time to learn {missing_count} key skills over the next few months."
        elif readiness >= 25:
            return f"🎯 You're on the right path. Consistent learning over 3-6 months will get you there."
        else:
            return f"🚀 Starting fresh? No problem! Follow the roadmap and you'll build these skills step by step."
    
    def _generate_next_steps(self, top_missing_skills: List[Dict]) -> List[str]:
        """Generate actionable next steps"""
        steps = []
        
        if not top_missing_skills:
            steps.append("✅ You have all required skills! Consider nice-to-have skills to stand out.")
            return steps
        
        for i, skill_data in enumerate(top_missing_skills, 1):
            skill = skill_data["skill"]
            steps.append(f"{i}. Start learning {skill} - {skill_data.get('recommendation', 'Important skill for this role')}")
        
        steps.append(f"{len(top_missing_skills) + 1}. Build projects to demonstrate these skills")
        steps.append(f"{len(top_missing_skills) + 2}. Update your resume and LinkedIn once you've learned 2-3 skills")
        
        return steps
    
    def get_all_roles(self) -> List[str]:
        """Get list of all available job roles"""
        return list(self.job_roles.keys())
    
    def get_market_insights(self) -> Dict:
        """Get overall market insights"""
        return {
            "top_demand_skills": self.top_demand_skills[:5],
            "fastest_growing_skills": self.fastest_growing[:5],
            "highest_salary_skills": self.highest_salary_skills[:5],
            "total_skills_tracked": len(self.market_data),
            "total_roles_available": len(self.job_roles)
        }