"""
Prompt Generation Service
Generates AI image/video prompts from character canon data
"""

from typing import Dict, List, Optional
from ..models.schemas import (
    CanonLayers, 
    Sex, Skeleton, BodyComposition, Species,
    FaceExpression, BodyAngle
)


class PromptGenerator:
    """Service for generating AI prompts from canon data"""
    
    # Human-readable descriptions for each layer value
    SEX_DESC = {
        Sex.MALE: "male",
        Sex.FEMALE: "female",
    }
    
    SKELETON_DESC = {
        Skeleton.H075: "very short, diminutive stature",
        Skeleton.H085: "short, compact build",
        Skeleton.H100: "average height",
        Skeleton.H110: "tall, above average height",
        Skeleton.H120: "very tall, towering stature",
    }
    
    BODY_DESC = {
        BodyComposition.ECTO: "very lean, ectomorphic build with minimal muscle mass",
        BodyComposition.THIN: "thin, slender build",
        BodyComposition.BASE: "average build",
        BodyComposition.ATHL: "athletic, muscular build with defined muscles",
        BodyComposition.HEVY: "heavy, stocky build with broad frame",
        BodyComposition.OVER: "overweight build with extra body fat",
        BodyComposition.OBES: "obese, very heavy build",
    }
    
    SPECIES_DESC = {
        Species.HUM: "human",
        Species.GHO: "ghoulish, with pallid decaying skin and sunken features",
        Species.MUT: "mutated, with visible physical mutations",
        Species.AND: "android, with synthetic skin and visible seams",
        Species.CYB: "cyborg, with visible cybernetic implants and tech",
    }
    
    EXPRESSION_DESC = {
        FaceExpression.NEUT: "neutral expression, calm and composed",
        FaceExpression.HPPY: "happy expression, genuine warm smile",
        FaceExpression.SAD: "sad expression, downcast eyes, melancholy",
        FaceExpression.ANGR: "angry expression, furrowed brow, intense glare",
        FaceExpression.EYEC: "eyes closed, peaceful, resting",
    }
    
    ANGLE_DESC = {
        BodyAngle.FRNT: "front view, facing camera directly",
        BodyAngle.Q34F: "three-quarter front view, 45 degree angle",
        BodyAngle.SIDE: "side profile view, 90 degrees",
        BodyAngle.Q34B: "three-quarter back view, 135 degrees",
        BodyAngle.BACK: "back view, facing away from camera",
    }
    
    def build_character_description(
        self,
        name: str,
        layers: CanonLayers,
        distinguishing_features: Optional[List[str]] = None
    ) -> str:
        """Build a consistent character description from canon layers"""
        parts = [
            f"A {self.SKELETON_DESC[layers.skeleton]}",
            f"{self.SEX_DESC[layers.sex]}",
            f"{self.SPECIES_DESC[layers.species]}",
            f"named {name}.",
            f"Body type: {self.BODY_DESC[layers.body_composition]}.",
        ]
        
        if distinguishing_features:
            parts.append(f"Distinguishing features: {', '.join(distinguishing_features)}.")
        
        return " ".join(parts)
    
    def generate_face_prompt(
        self,
        name: str,
        layers: CanonLayers,
        expression: FaceExpression,
        reference_image_note: bool = True
    ) -> str:
        """Generate prompt for face canon image"""
        
        base_desc = self.build_character_description(name, layers)
        
        prompt_parts = [
            "Character reference sheet, single character portrait.",
            "",
            base_desc,
            "",
            f"Expression: {self.EXPRESSION_DESC[expression]}.",
            "",
            "Requirements:",
            "- Head and shoulders portrait",
            "- Plain neutral background",
            "- Consistent lighting from front",
            "- High detail on facial features",
            "- Bald or very short hair (for costume flexibility)",
        ]
        
        if reference_image_note:
            prompt_parts.extend([
                "",
                "CRITICAL: Match the face from the reference image exactly.",
                "Maintain identical facial structure, features, and proportions.",
            ])
        
        return "\n".join(prompt_parts)
    
    def generate_body_prompt(
        self,
        name: str,
        layers: CanonLayers,
        angle: BodyAngle,
        reference_image_note: bool = True
    ) -> str:
        """Generate prompt for body canon image"""
        
        base_desc = self.build_character_description(name, layers)
        
        prompt_parts = [
            "Character reference sheet, full body view.",
            "",
            base_desc,
            "",
            f"Pose: Standing T-pose or neutral pose, {self.ANGLE_DESC[angle]}.",
            "",
            "Requirements:",
            "- Full body visible head to toe",
            "- Plain neutral background",
            "- Wearing plain underwear/base clothing only",
            "- Neutral expression",
            "- Anatomically accurate proportions",
            "- Consistent lighting",
        ]
        
        if reference_image_note:
            prompt_parts.extend([
                "",
                "CRITICAL: Match the body proportions and face from the reference image.",
                "Do not alter skeleton or body composition.",
            ])
        
        return "\n".join(prompt_parts)
    
    def generate_all_face_prompts(
        self,
        name: str,
        layers: CanonLayers
    ) -> Dict[str, str]:
        """Generate prompts for all face expressions"""
        return {
            expr.value: self.generate_face_prompt(name, layers, expr)
            for expr in FaceExpression
        }
    
    def generate_all_body_prompts(
        self,
        name: str,
        layers: CanonLayers
    ) -> Dict[str, str]:
        """Generate prompts for all body angles"""
        return {
            angle.value: self.generate_body_prompt(name, layers, angle)
            for angle in BodyAngle
        }
    
    def generate_video_prompt(
        self,
        name: str,
        layers: CanonLayers,
        action: str,
        environment: Optional[str] = None,
        expression: FaceExpression = FaceExpression.NEUT,
        costume: Optional[str] = None
    ) -> str:
        """Generate prompt for video generation"""
        
        base_desc = self.build_character_description(name, layers)
        
        prompt_parts = [
            "Consistent character, same person throughout the video.",
            "",
            base_desc,
            "",
            f"Expression: {self.EXPRESSION_DESC[expression]}.",
        ]
        
        if costume:
            prompt_parts.append(f"Wearing: {costume}.")
        
        prompt_parts.extend([
            "",
            f"Action: {action}",
        ])
        
        if environment:
            prompt_parts.append(f"Setting: {environment}")
        
        prompt_parts.extend([
            "",
            "CRITICAL: Reference images attached for face and body consistency.",
            "Maintain exact facial features from reference.",
            "Do not alter body proportions.",
        ])
        
        return "\n".join(prompt_parts)


# Singleton instance
prompt_generator = PromptGenerator()
