import json
import re
from typing import List, Dict, Set
from pathlib import Path
from functools import lru_cache

class SkillsExtractor:
    def __init__(self):
        # Load skills database
        db_path = Path(__file__).parent.parent / "data" / "skills_database.json"
        with open(db_path, 'r') as f:
            self.skills_db = json.load(f)
        
        # Flatten all skills into optimized structures
        self.all_skills = set()
        self.skill_patterns = {}  # Pre-compiled regex patterns
        
        for category, skills in self.skills_db.items():
            if category != "skill_aliases":
                for skill in skills:
                    skill_lower = skill.lower()
                    self.all_skills.add(skill_lower)
                    # Create regex pattern for each skill
                    self.skill_patterns[skill_lower] = re.compile(
                        r'\b' + re.escape(skill_lower) + r'\b',
                        re.IGNORECASE
                    )
    
    @lru_cache(maxsize=128)
    def normalize_skill(self, skill: str) -> str:
        """Normalize skill names using aliases (cached for performance)"""
        skill = skill.strip()
        aliases = self.skills_db.get("skill_aliases", {})
        
        # Check if skill has an alias
        for alias, canonical in aliases.items():
            if skill.lower() == alias.lower():
                return canonical
        
        return skill
    
    def extract_by_keywords(self, text: str) -> Set[str]:
        """Extract skills using optimized keyword matching"""
        found_skills = set()
        text_lower = text.lower()
        
        # Use pre-compiled patterns for faster matching
        for skill_lower, pattern in self.skill_patterns.items():
            if pattern.search(text):
                # Find the original case from text
                match = pattern.search(text)
                if match:
                    # Get the properly cased version from our database
                    for category, skills in self.skills_db.items():
                        if category != "skill_aliases":
                            for s in skills:
                                if s.lower() == skill_lower:
                                    found_skills.add(s)
                                    break
        
        return found_skills
    
    def extract_by_context(self, text: str) -> Set[str]:
        """Extract skills by looking at common resume patterns (enhanced)"""
        found_skills = set()
        
        # Enhanced patterns with more variations
        patterns = [
            r'(?:Skills?|Technical Skills?|Technologies?|Tools?)[:\s]+([^\n]+)',
            r'(?:Proficient|Experienced|Expert) (?:in|with)[:\s]+([^\n]+)',
            r'(?:Knowledge|Experience) (?:of|in|with)[:\s]+([^\n]+)',
            r'(?:Programming Languages?|Languages?)[:\s]+([^\n]+)',
            r'(?:Frameworks?|Libraries?)[:\s]+([^\n]+)',
            r'(?:Databases?|Data)[:\s]+([^\n]+)',
            r'(?:Cloud|DevOps|Platform)[:\s]+([^\n]+)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                skills_line = match.group(1)
                # Split by common delimiters
                potential_skills = re.split(r'[,;|•·\n]', skills_line)
                
                for skill in potential_skills:
                    skill = skill.strip()
                    # Remove common non-skill words
                    skill = re.sub(r'^(and|or|with|using|including)\s+', '', skill, flags=re.IGNORECASE)
                    
                    if skill and len(skill) > 1:
                        skill_lower = skill.lower()
                        if skill_lower in self.all_skills:
                            # Find properly cased version
                            for category, skills_list in self.skills_db.items():
                                if category != "skill_aliases":
                                    for s in skills_list:
                                        if s.lower() == skill_lower:
                                            found_skills.add(s)
                                            break
        
        return found_skills
    
    def extract_by_phrases(self, text: str) -> Set[str]:
        """Extract multi-word skills and phrases"""
        found_skills = set()
        
        # Look for common skill phrases
        multi_word_skills = [
            "Machine Learning", "Deep Learning", "Data Science", 
            "Computer Vision", "Natural Language Processing",
            "REST API", "Web Development", "Mobile Development",
            "Cloud Computing", "Data Visualization", "Database Design",
            "Software Development", "Agile Methodology", "Problem Solving"
        ]
        
        for skill in multi_word_skills:
            pattern = re.compile(r'\b' + re.escape(skill) + r'\b', re.IGNORECASE)
            if pattern.search(text):
                found_skills.add(skill)
        
        return found_skills
    
    def extract_skills(self, resume_text: str) -> Dict[str, List[str]]:
        """Main extraction function combining multiple methods (optimized)"""
        # Extract using all methods in parallel
        keyword_skills = self.extract_by_keywords(resume_text)
        context_skills = self.extract_by_context(resume_text)
        phrase_skills = self.extract_by_phrases(resume_text)
        
        # Combine all results
        all_skills = keyword_skills.union(context_skills).union(phrase_skills)
        
        # Normalize and deduplicate
        normalized_skills = [self.normalize_skill(s) for s in all_skills]
        unique_skills = sorted(list(set(normalized_skills)))
        
        # Categorize skills
        categorized = self._categorize_skills(unique_skills)
        
        # Calculate confidence scores
        skill_scores = self._calculate_confidence(unique_skills, resume_text)
        
        return {
            "all_skills": unique_skills,
            "categorized": categorized,
            "count": len(unique_skills),
            "confidence_scores": skill_scores
        }
    
    def _calculate_confidence(self, skills: List[str], text: str) -> Dict[str, float]:
        """Calculate confidence score for each skill based on frequency and context"""
        scores = {}
        text_lower = text.lower()
        
        for skill in skills:
            skill_lower = skill.lower()
            # Count occurrences
            count = len(re.findall(r'\b' + re.escape(skill_lower) + r'\b', text_lower))
            
            # Check if mentioned in key sections
            in_skills_section = bool(re.search(
                r'(?:skills?|technologies?)[^\n]*' + re.escape(skill_lower),
                text_lower
            ))
            
            # Calculate score (0-1 scale)
            base_score = min(count * 0.2, 0.7)  # Max 0.7 from frequency
            section_bonus = 0.3 if in_skills_section else 0
            
            scores[skill] = min(base_score + section_bonus, 1.0)
        
        return scores
    
    def _categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """Organize skills by category (optimized)"""
        categorized = {}
        skills_lower = {s.lower(): s for s in skills}
        
        for category, skill_list in self.skills_db.items():
            if category == "skill_aliases":
                continue
            
            category_skills = []
            for db_skill in skill_list:
                if db_skill.lower() in skills_lower:
                    category_skills.append(skills_lower[db_skill.lower()])
            
            if category_skills:
                categorized[category] = sorted(category_skills)
        
        return categorized