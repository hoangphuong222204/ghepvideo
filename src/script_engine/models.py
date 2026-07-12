"""Dataclass definitions representing inputs, outputs, analysis, and quality of the AI Script Engine."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ProductAnalysis:
    """Detailed structural decomposition of product attributes."""
    
    category: str
    selling_points: List[str] = field(default_factory=list)
    target_audience: List[str] = field(default_factory=list)
    buying_motivations: List[str] = field(default_factory=list)
    usage_scenarios: List[str] = field(default_factory=list)


@dataclass
class ScriptRequest:
    """Consolidated input request for generating customized video marketing scripts."""
    
    product_name: str
    product_description: str
    brand_name: Optional[str] = None
    target_audience: Optional[str] = None
    core_benefit: Optional[str] = None
    style: Optional[str] = None  # Problem Solution, Review, etc.
    duration_seconds: int = 45  # Target length
    platform: str = "TikTok"  # TikTok, Shopee, etc.
    quantity: int = 1  # How many variations to generate (1-50)
    campaign_id: Optional[int] = None
    min_quality_score: float = 70.0


@dataclass
class ScriptScene:
    """Represents a single segment/scene within a video script structure."""
    
    scene_number: int
    visual_description: str
    spoken_text: str
    duration_seconds: float


@dataclass
class VideoScript:
    """Enterprise-grade model storing generated video scripts along with performance analytics."""
    
    title: str
    style: str
    platform: str
    scenes: List[ScriptScene] = field(default_factory=list)
    estimated_duration: float = 0.0
    word_count: int = 0
    hook_score: float = 0.0
    selling_score: float = 0.0
    natural_speech_score: float = 0.0
    policy_score: float = 0.0
    originality_score: float = 0.0
    overall_score: float = 0.0
    content_text: str = ""  # Plain spoken text stitched together
    is_approved: bool = True
    rejection_reason: Optional[str] = None


@dataclass
class QualityScore:
    """Individual quality metric breakdowns."""
    
    hook_score: float
    selling_score: float
    natural_speech_score: float
    policy_score: float
    originality_score: float
    duration_score: float
    overall_score: float
    is_approved: bool
    rejection_reason: Optional[str] = None
