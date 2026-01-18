"""
Auto-Mapping Service
Maps character descriptions and data to canon layers
"""

import re
from typing import Dict, List, Optional, Tuple
from ..models.schemas import (
    CanonLayers,
    AutoMapResult,
    Sex, Skeleton, BodyComposition, Species
)


class AutoMapper:
    """Service for automatically mapping character data to canon layers"""
    
    # Height parsing patterns
    HEIGHT_PATTERNS = [
        r"(\d+)['\u2019](\d+)[\"″]?",  # 5'10" or 5'10
        r"(\d+)\s*feet?\s*(\d+)?\s*inch",  # 5 feet 10 inches
        r"(\d+\.\d+)\s*m",  # 1.78m
        r"(\d+)\s*cm",  # 178cm
    ]
    
    # Sex keywords
    SEX_KEYWORDS = {
        Sex.MALE: ["male", "man", "boy", "he", "him", "his", "masculine", "m"],
        Sex.FEMALE: ["female", "woman", "girl", "she", "her", "hers", "feminine", "f"],
    }
    
    # Skeleton keywords (beyond height)
    SKELETON_KEYWORDS = {
        Skeleton.H075: ["tiny", "very short", "diminutive", "small stature"],
        Skeleton.H085: ["short", "small", "compact", "petite"],
        Skeleton.H100: ["average", "medium", "normal height"],
        Skeleton.H110: ["tall", "above average", "lanky"],
        Skeleton.H120: ["very tall", "giant", "towering", "huge", "massive height"],
    }
    
    # Body composition keywords
    BODY_KEYWORDS = {
        BodyComposition.ECTO: ["gaunt", "wiry", "skeletal", "emaciated", "bony", "skin and bones"],
        BodyComposition.THIN: ["lean", "slender", "thin", "lithe", "slim", "svelte", "willowy"],
        BodyComposition.BASE: ["average", "normal build", "medium build"],
        BodyComposition.ATHL: ["muscular", "athletic", "toned", "fit", "strong", "powerful", "ripped", "buff"],
        BodyComposition.HEVY: ["stocky", "broad", "heavy", "thick", "sturdy", "burly", "solid"],
        BodyComposition.OVER: ["overweight", "portly", "chubby", "plump", "rotund", "pudgy"],
        BodyComposition.OBES: ["obese", "fat", "enormous", "very large", "extremely heavy"],
    }
    
    # Species keywords
    SPECIES_KEYWORDS = {
        Species.HUM: ["human", "normal", "ordinary"],
        Species.GHO: ["undead", "zombie", "ghoul", "corpse", "decayed", "rotting", "reborn"],
        Species.MUT: ["mutant", "mutated", "deformed", "aberrant", "twisted", "malformed"],
        Species.AND: ["android", "robot", "synthetic", "artificial", "mechanical", "warforged", "automaton"],
        Species.CYB: ["cyborg", "augmented", "cybernetic", "bionic", "half-machine", "tech implants"],
    }
    
    def parse_height(self, height_str: str) -> Optional[float]:
        """Parse height string to inches"""
        if not height_str:
            return None
        
        height_str = height_str.lower().strip()
        
        # Try feet and inches (5'10")
        match = re.search(r"(\d+)['\u2019](\d+)?", height_str)
        if match:
            feet = int(match.group(1))
            inches = int(match.group(2)) if match.group(2) else 0
            return feet * 12 + inches
        
        # Try meters
        match = re.search(r"(\d+\.?\d*)\s*m(?:eter)?", height_str)
        if match:
            meters = float(match.group(1))
            return meters * 39.37
        
        # Try cm
        match = re.search(r"(\d+)\s*cm", height_str)
        if match:
            cm = int(match.group(1))
            return cm / 2.54
        
        return None
    
    def height_to_skeleton(self, height_inches: float) -> Skeleton:
        """Convert height in inches to skeleton type"""
        if height_inches < 54:  # < 4'6"
            return Skeleton.H075
        elif height_inches < 62:  # < 5'2"
            return Skeleton.H085
        elif height_inches < 70:  # < 5'10"
            return Skeleton.H100
        elif height_inches < 76:  # < 6'4"
            return Skeleton.H110
        else:
            return Skeleton.H120
    
    def find_keywords(self, text: str, keyword_map: Dict) -> Tuple[Optional[any], float]:
        """Find matching keywords in text and return the match with confidence"""
        if not text:
            return None, 0.0
        
        text_lower = text.lower()
        
        for value, keywords in keyword_map.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return value, 0.9
        
        return None, 0.0
    
    def map_from_description(
        self,
        description: str,
        name: Optional[str] = None,
        sex: Optional[str] = None,
        height: Optional[str] = None,
        race: Optional[str] = None,
        additional_keywords: Optional[List[str]] = None
    ) -> AutoMapResult:
        """
        Map character description to canon layers
        
        Args:
            description: Free-text character description
            name: Character name
            sex: Explicit sex/gender if provided
            height: Height string if provided
            race: Race/species if provided
            additional_keywords: Extra keywords to consider
        """
        warnings = []
        confidence = {}
        
        # Combine all text for keyword searching
        all_text = " ".join(filter(None, [
            description,
            sex,
            height,
            race,
            " ".join(additional_keywords or [])
        ]))
        
        # === Map Sex ===
        if sex:
            found_sex, conf = self.find_keywords(sex, self.SEX_KEYWORDS)
            if found_sex:
                result_sex = found_sex
                confidence["sex"] = conf
            else:
                result_sex = Sex.MALE
                confidence["sex"] = 0.5
                warnings.append(f"Could not determine sex from '{sex}', defaulting to Male")
        else:
            found_sex, conf = self.find_keywords(all_text, self.SEX_KEYWORDS)
            if found_sex:
                result_sex = found_sex
                confidence["sex"] = conf * 0.8  # Lower confidence when inferred
            else:
                result_sex = Sex.MALE
                confidence["sex"] = 0.3
                warnings.append("No sex/gender specified, defaulting to Male")
        
        # === Map Skeleton ===
        result_skeleton = Skeleton.H100
        confidence["skeleton"] = 0.5
        
        # First try explicit height
        if height:
            height_inches = self.parse_height(height)
            if height_inches:
                result_skeleton = self.height_to_skeleton(height_inches)
                confidence["skeleton"] = 0.95
        
        # Then try keywords if height didn't give us high confidence
        if confidence["skeleton"] < 0.9:
            found_skeleton, conf = self.find_keywords(all_text, self.SKELETON_KEYWORDS)
            if found_skeleton and conf > confidence["skeleton"]:
                result_skeleton = found_skeleton
                confidence["skeleton"] = conf
        
        if confidence["skeleton"] < 0.6:
            warnings.append("No height information found, defaulting to Medium")
        
        # === Map Body Composition ===
        found_body, conf = self.find_keywords(all_text, self.BODY_KEYWORDS)
        if found_body:
            result_body = found_body
            confidence["body_composition"] = conf
        else:
            result_body = BodyComposition.BASE
            confidence["body_composition"] = 0.5
            warnings.append("No body type keywords found, defaulting to Base")
        
        # === Map Species ===
        found_species, conf = self.find_keywords(all_text, self.SPECIES_KEYWORDS)
        if found_species:
            result_species = found_species
            confidence["species"] = conf
        else:
            result_species = Species.HUM
            confidence["species"] = 0.8  # Human is a safe default
        
        return AutoMapResult(
            layers=CanonLayers(
                sex=result_sex,
                skeleton=result_skeleton,
                body_composition=result_body,
                species=result_species
            ),
            confidence=confidence,
            warnings=warnings
        )


# Singleton instance
auto_mapper = AutoMapper()
