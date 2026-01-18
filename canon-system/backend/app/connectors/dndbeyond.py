"""
D&D Beyond Connector
Fetches character data from D&D Beyond and maps to standard schema
"""

import re
import httpx
from typing import Dict, Any, Optional, Tuple
from ..models.schemas import (
    StandardCharacterInput, 
    CharacterSource, 
    CanonLayers, 
    AutoMapResult,
    Sex, Skeleton, BodyComposition, Species
)


class DNDBeyondConnector:
    """Connector for importing characters from D&D Beyond"""
    
    # Race to skeleton mapping
    RACE_SKELETON_MAP = {
        "halfling": Skeleton.H075,
        "gnome": Skeleton.H075,
        "goblin": Skeleton.H075,
        "kobold": Skeleton.H075,
        "dwarf": Skeleton.H085,
        "human": Skeleton.H100,
        "half-elf": Skeleton.H100,
        "tiefling": Skeleton.H100,
        "elf": Skeleton.H110,
        "half-orc": Skeleton.H110,
        "dragonborn": Skeleton.H110,
        "orc": Skeleton.H110,
        "goliath": Skeleton.H120,
        "firbolg": Skeleton.H120,
        "bugbear": Skeleton.H120,
    }
    
    # Race to species mapping
    RACE_SPECIES_MAP = {
        "warforged": Species.AND,
        "autognome": Species.AND,
        "reborn": Species.GHO,
    }
    
    # Keywords for body composition
    BODY_KEYWORDS = {
        BodyComposition.ECTO: ["gaunt", "wiry", "skeletal", "emaciated", "bony"],
        BodyComposition.THIN: ["lean", "slender", "thin", "lithe", "slim"],
        BodyComposition.ATHL: ["muscular", "athletic", "toned", "fit", "strong", "powerful"],
        BodyComposition.HEVY: ["stocky", "broad", "heavy", "thick", "sturdy", "burly"],
        BodyComposition.OVER: ["overweight", "portly", "chubby", "plump", "rotund"],
        BodyComposition.OBES: ["obese", "massive", "enormous", "huge"],
    }
    
    @staticmethod
    def extract_character_id(url: str) -> Optional[str]:
        """Extract character ID from D&D Beyond URL"""
        # Patterns:
        # https://www.dndbeyond.com/characters/123456789
        # https://dndbeyond.com/characters/123456789
        # https://www.dndbeyond.com/characters/123456789/builder
        pattern = r'dndbeyond\.com/characters/(\d+)'
        match = re.search(pattern, url)
        return match.group(1) if match else None
    
    async def fetch_character(self, url: str) -> Dict[str, Any]:
        """
        Fetch character data from D&D Beyond
        
        Note: D&D Beyond doesn't have a public API, so this would need to either:
        1. Use browser automation
        2. Parse the page HTML
        3. Use their unofficial API endpoints
        
        For now, this returns a mock structure that the user would fill in
        or we'd implement actual scraping later.
        """
        char_id = self.extract_character_id(url)
        
        if not char_id:
            raise ValueError(f"Could not extract character ID from URL: {url}")
        
        # TODO: Implement actual D&D Beyond data fetching
        # For now, return a placeholder that indicates manual entry needed
        return {
            "id": char_id,
            "url": url,
            "name": None,  # To be filled
            "gender": None,
            "race": None,
            "height": None,
            "weight": None,
            "appearance": None,
            "_requires_manual_entry": True,
            "_message": "D&D Beyond API access not configured. Please enter character details manually."
        }
    
    def map_to_standard(self, dnd_data: Dict[str, Any], reference_image_path: Optional[str] = None) -> StandardCharacterInput:
        """Convert D&D Beyond data to standard character input format"""
        return StandardCharacterInput(
            source=CharacterSource(
                type="dndbeyond",
                id=dnd_data.get("id"),
                url=dnd_data.get("url"),
                data=dnd_data
            ),
            character={
                "name": dnd_data.get("name", "Unknown"),
                "description": dnd_data.get("appearance", ""),
                "sex": dnd_data.get("gender", "").lower(),
                "height": dnd_data.get("height", ""),
                "race": dnd_data.get("race", "").lower(),
                "build_keywords": self._extract_build_keywords(dnd_data.get("appearance", "")),
                "species_keywords": [dnd_data.get("race", "").lower()],
                "distinguishing_features": []
            },
            reference_image_path=reference_image_path
        )
    
    def _extract_build_keywords(self, appearance: str) -> list:
        """Extract body composition keywords from appearance text"""
        if not appearance:
            return []
        
        appearance_lower = appearance.lower()
        found_keywords = []
        
        for composition, keywords in self.BODY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in appearance_lower:
                    found_keywords.append(keyword)
        
        return found_keywords
    
    def auto_map_layers(self, standard_input: StandardCharacterInput) -> AutoMapResult:
        """Auto-map character data to canon layers"""
        char = standard_input.character
        warnings = []
        confidence = {}
        
        # Map sex
        sex_input = char.get("sex", "").lower()
        if sex_input in ["male", "man", "m", "he", "him"]:
            sex = Sex.MALE
            confidence["sex"] = 1.0
        elif sex_input in ["female", "woman", "f", "she", "her"]:
            sex = Sex.FEMALE
            confidence["sex"] = 1.0
        else:
            sex = Sex.MALE  # Default
            confidence["sex"] = 0.5
            warnings.append(f"Could not determine sex from '{sex_input}', defaulting to Male")
        
        # Map skeleton from race
        race = char.get("race", "").lower()
        skeleton = self.RACE_SKELETON_MAP.get(race, Skeleton.H100)
        confidence["skeleton"] = 1.0 if race in self.RACE_SKELETON_MAP else 0.7
        if race and race not in self.RACE_SKELETON_MAP:
            warnings.append(f"Unknown race '{race}', defaulting to medium height")
        
        # Map body composition from keywords
        build_keywords = char.get("build_keywords", [])
        body_comp = BodyComposition.BASE
        confidence["body_composition"] = 0.5
        
        for keyword in build_keywords:
            keyword_lower = keyword.lower()
            for comp, comp_keywords in self.BODY_KEYWORDS.items():
                if keyword_lower in comp_keywords:
                    body_comp = comp
                    confidence["body_composition"] = 0.9
                    break
        
        if not build_keywords:
            warnings.append("No body composition keywords found, defaulting to Base")
        
        # Map species
        species = Species.HUM
        confidence["species"] = 1.0
        
        if race in self.RACE_SPECIES_MAP:
            species = self.RACE_SPECIES_MAP[race]
        
        return AutoMapResult(
            layers=CanonLayers(
                sex=sex,
                skeleton=skeleton,
                body_composition=body_comp,
                species=species
            ),
            confidence=confidence,
            warnings=warnings
        )


# Singleton instance
dndbeyond_connector = DNDBeyondConnector()
