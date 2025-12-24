"""Pydantic schemas for Meshy AI tool inputs.

These schemas are used for AI framework integrations that require
Pydantic-based validation, such as the Vercel AI SDK.

Each schema corresponds to a function in vendor_connectors.meshy.tools.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class Text3DGenerateSchema(BaseModel):
    """Generate a 3D model from a text description."""

    prompt: str = Field(..., description="Detailed text description of the 3D model (max 600 chars)")
    art_style: str = Field(
        "realistic",
        description="One of: realistic, sculpture. For 'sculpture', set enable_pbr=False.",
    )
    negative_prompt: str = Field("", description="Things to avoid in the generation")
    target_polycount: int = Field(30000, description="Target polygon count")
    enable_pbr: bool = Field(
        True,
        description="Enable PBR materials. Set False for sculpture style.",
    )
    wait: bool = Field(True, description="Whether to wait for completion")


class Image3DGenerateSchema(BaseModel):
    """Generate a 3D model from an image."""

    image_url: str = Field(..., description="URL to the source image")
    topology: str = Field("", description="Mesh topology ('quad' or 'triangle'), empty for default")
    target_polycount: int = Field(15000, description="Target polygon count")
    enable_pbr: bool = Field(True, description="Enable PBR materials")
    wait: bool = Field(True, description="Whether to wait for completion")


class RigModelSchema(BaseModel):
    """Add a skeleton/rig to a static 3D model."""

    model_id: str = Field(..., description="Task ID of the static model to rig")
    wait: bool = Field(True, description="Whether to wait for completion")


class ApplyAnimationSchema(BaseModel):
    """Apply an animation to a rigged model."""

    model_id: str = Field(..., description="Task ID of the rigged model")
    animation_id: int = Field(..., description="Animation ID from the Meshy catalog")
    wait: bool = Field(True, description="Whether to wait for completion")


class RetextureModelSchema(BaseModel):
    """Apply new textures to an existing model."""

    model_id: str = Field(..., description="Task ID of the model to retexture")
    texture_prompt: str = Field(..., description="Description of the new texture/appearance")
    enable_pbr: bool = Field(True, description="Enable PBR materials")
    wait: bool = Field(True, description="Whether to wait for completion")


class ListAnimationsSchema(BaseModel):
    """List available animations from the Meshy catalog."""

    category: str = Field("", description="Optional category filter (Fighting, WalkAndRun, etc.)")
    limit: int = Field(50, description="Maximum number of results")


class CheckTaskStatusSchema(BaseModel):
    """Check the status of a Meshy task."""

    task_id: str = Field(..., description="The Meshy task ID")
    task_type: str = Field(
        "text-to-3d",
        description="Task type (text-to-3d, image-to-3d, rigging, animation, retexture)",
    )


class GetAnimationSchema(BaseModel):
    """Get details of a specific animation by ID."""

    animation_id: int = Field(..., description="The animation ID number")
