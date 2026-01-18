"""
Image Generation Service
Handles AI image generation via various providers
"""

import os
import httpx
import base64
import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path


class ImageGeneratorBase(ABC):
    """Abstract base class for image generators"""
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        reference_image_path: Optional[str] = None,
        output_path: str = None,
        **kwargs
    ) -> str:
        """
        Generate an image from a prompt
        
        Args:
            prompt: Text prompt for generation
            reference_image_path: Path to reference image for consistency
            output_path: Where to save the result
            
        Returns:
            Path to generated image
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Return the generator name"""
        pass


class StabilityAIGenerator(ImageGeneratorBase):
    """Stability AI image generator"""
    
    def __init__(self):
        self.api_key = os.environ.get("STABILITY_API_KEY")
        self.base_url = "https://api.stability.ai"
    
    def get_name(self) -> str:
        return "stability"
    
    async def generate(
        self,
        prompt: str,
        reference_image_path: Optional[str] = None,
        output_path: str = None,
        **kwargs
    ) -> str:
        if not self.api_key:
            raise ValueError("STABILITY_API_KEY environment variable not set")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "image/*"
        }
        
        # Build request based on whether we have a reference image
        if reference_image_path and os.path.exists(reference_image_path):
            # Use image-to-image endpoint
            endpoint = f"{self.base_url}/v2beta/stable-image/generate/sd3"
            
            with open(reference_image_path, "rb") as f:
                image_data = f.read()
            
            files = {
                "image": ("reference.png", image_data, "image/png"),
            }
            data = {
                "prompt": prompt,
                "mode": "image-to-image",
                "strength": 0.5,  # How much to change from reference
                "output_format": "png",
            }
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    endpoint,
                    headers=headers,
                    files=files,
                    data=data
                )
        else:
            # Text-to-image
            endpoint = f"{self.base_url}/v2beta/stable-image/generate/sd3"
            
            data = {
                "prompt": prompt,
                "output_format": "png",
            }
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    endpoint,
                    headers={**headers, "Content-Type": "application/json"},
                    json=data
                )
        
        if response.status_code != 200:
            raise Exception(f"Stability AI error: {response.status_code} - {response.text}")
        
        # Save the image
        if not output_path:
            output_path = f"./data/generated/{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        return output_path


class ReplicateGenerator(ImageGeneratorBase):
    """Replicate.com image generator"""
    
    def __init__(self):
        self.api_key = os.environ.get("REPLICATE_API_KEY")
        self.base_url = "https://api.replicate.com/v1"
    
    def get_name(self) -> str:
        return "replicate"
    
    async def generate(
        self,
        prompt: str,
        reference_image_path: Optional[str] = None,
        output_path: str = None,
        model: str = "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
        **kwargs
    ) -> str:
        if not self.api_key:
            raise ValueError("REPLICATE_API_KEY environment variable not set")
        
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        }
        
        input_data = {
            "prompt": prompt,
        }
        
        # Add reference image if provided
        if reference_image_path and os.path.exists(reference_image_path):
            with open(reference_image_path, "rb") as f:
                image_base64 = base64.b64encode(f.read()).decode()
            input_data["image"] = f"data:image/png;base64,{image_base64}"
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Start prediction
            response = await client.post(
                f"{self.base_url}/predictions",
                headers=headers,
                json={
                    "version": model.split(":")[-1],
                    "input": input_data
                }
            )
            
            if response.status_code != 201:
                raise Exception(f"Replicate error: {response.status_code} - {response.text}")
            
            prediction = response.json()
            prediction_id = prediction["id"]
            
            # Poll for completion
            while True:
                response = await client.get(
                    f"{self.base_url}/predictions/{prediction_id}",
                    headers=headers
                )
                prediction = response.json()
                
                if prediction["status"] == "succeeded":
                    break
                elif prediction["status"] == "failed":
                    raise Exception(f"Replicate prediction failed: {prediction.get('error')}")
                
                await asyncio.sleep(2)
            
            # Download the result
            output_url = prediction["output"][0] if isinstance(prediction["output"], list) else prediction["output"]
            
            image_response = await client.get(output_url)
            
            if not output_path:
                output_path = f"./data/generated/{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, "wb") as f:
                f.write(image_response.content)
            
            return output_path


class MockGenerator(ImageGeneratorBase):
    """Mock generator for testing without API keys"""
    
    def get_name(self) -> str:
        return "mock"
    
    async def generate(
        self,
        prompt: str,
        reference_image_path: Optional[str] = None,
        output_path: str = None,
        **kwargs
    ) -> str:
        """Generate a placeholder image for testing"""
        
        if not output_path:
            output_path = f"./data/generated/{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Create a simple placeholder PNG
        # This is a minimal valid PNG (1x1 gray pixel)
        placeholder_png = bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
            0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
            0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
            0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,  # IDAT chunk
            0x54, 0x08, 0xD7, 0x63, 0x78, 0x78, 0x78, 0x00,
            0x00, 0x00, 0x07, 0x00, 0x03, 0x5A, 0x6B, 0xB3,
            0x2C, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,  # IEND chunk
            0x44, 0xAE, 0x42, 0x60, 0x82
        ])
        
        with open(output_path, "wb") as f:
            f.write(placeholder_png)
        
        return output_path


class ImageGenerationService:
    """Main service for image generation"""
    
    def __init__(self):
        self.generators: Dict[str, ImageGeneratorBase] = {}
        self._register_generators()
    
    def _register_generators(self):
        """Register available generators"""
        # Always register mock for testing
        self.generators["mock"] = MockGenerator()
        
        # Register real generators if API keys are available
        if os.environ.get("STABILITY_API_KEY"):
            self.generators["stability"] = StabilityAIGenerator()
        
        if os.environ.get("REPLICATE_API_KEY"):
            self.generators["replicate"] = ReplicateGenerator()
    
    def get_available_generators(self) -> List[str]:
        """Return list of available generator names"""
        return list(self.generators.keys())
    
    def get_generator(self, name: str) -> ImageGeneratorBase:
        """Get a specific generator by name"""
        if name not in self.generators:
            raise ValueError(f"Generator '{name}' not available. Available: {self.get_available_generators()}")
        return self.generators[name]
    
    async def generate(
        self,
        prompt: str,
        generator: str = "mock",
        reference_image_path: Optional[str] = None,
        output_path: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate an image using the specified generator"""
        gen = self.get_generator(generator)
        return await gen.generate(
            prompt=prompt,
            reference_image_path=reference_image_path,
            output_path=output_path,
            **kwargs
        )


# Singleton instance
image_generation_service = ImageGenerationService()
