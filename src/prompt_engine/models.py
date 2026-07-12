"""Dataclass models representing prompt structures, variables, testing setups, and history logs."""

import datetime
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


@dataclass
class TemplateVariable:
    """Represents a metadata declaration for a variable expected by a template."""

    name: str
    description: Optional[str] = None
    default_value: Optional[Any] = None
    is_required: bool = True
    type_hint: str = "str"  # "str", "int", "float", "list", "dict"
    fallback_env_var: Optional[str] = None  # OS environment variable fallback


@dataclass
class VersionInfo:
    """Versioning details for a specific template variation."""

    version: str  # Semantic version e.g. "1.0.0"
    author: str
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    description: str = "Initial release"
    stability: str = "Draft"  # "Draft", "Candidate", "Active", "Deprecated"
    change_log: Optional[str] = None


@dataclass
class PromptTemplate:
    """Enterprise-grade container storing a prompt template's body, variables, and parameters."""

    name: str
    category: str
    provider: str  # Target provider e.g. "Gemini", "OpenAI"
    version: str = "1.0.0"
    description: str = ""
    system_prompt: Optional[str] = None
    user_prompt: str = ""
    developer_prompt: Optional[str] = None  # For models supporting dev-specific instructions
    variables: List[TemplateVariable] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    json_schema: Optional[Dict[str, Any]] = None  # Target schema if JSON mode expected
    version_history: List[VersionInfo] = field(default_factory=list)
    is_locked: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RenderedPrompt:
    """Resolved and formatted prompts, fully loaded with variable data and ready to hit an LLM."""

    template_name: str
    version: str
    provider: str
    user_prompt: str
    system_prompt: Optional[str] = None
    developer_prompt: Optional[str] = None
    json_schema: Optional[Dict[str, Any]] = None
    resolved_variables: Dict[str, Any] = field(default_factory=dict)
    unresolved_variables: Set[str] = field(default_factory=set)
    meta_config: Dict[str, Any] = field(default_factory=dict)  # Model temperature, max tokens, etc.
    rendered_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


@dataclass
class OptimizationResult:
    """Compares prompt size and compression ratio before and after prompt optimization."""

    original_text: str
    optimized_text: str
    original_characters: int
    optimized_characters: int
    compression_ratio: float  # e.g., 0.72 (28% compression)
    tokens_saved_estimate: int
    optimizations_applied: List[str] = field(default_factory=list)


@dataclass
class ABTestConfig:
    """Configures and tracks performance metric ratios for multi-template A/B testing."""

    test_id: str
    name: str
    template_name: str
    version_a: str
    version_b: str
    allocation_ratio_a: float = 0.5  # 0.5 means 50% traffic goes to version_a, rest B
    impressions_a: int = 0
    impressions_b: int = 0
    conversions_a: int = 0
    conversions_b: int = 0
    is_active: bool = True
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


@dataclass
class PromptHistoryRecord:
    """Stores logs of prompt invocations and variable state values for diagnostics and auditing."""

    id: str
    template_name: str
    version: str
    provider: str
    user_prompt: str
    variables_used: Dict[str, Any]
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    system_prompt: Optional[str] = None
    developer_prompt: Optional[str] = None
    is_success: bool = True
    error_message: Optional[str] = None
    response_latency_ms: Optional[float] = None
    conversion_recorded: bool = False


@dataclass
class PromptDiffLine:
    """A single aligned line of text change between two prompt templates."""

    type: str  # "equal", "insert", "delete"
    line_number_a: Optional[int]
    line_number_b: Optional[int]
    content: str


@dataclass
class PromptCompareResult:
    """Deep visual difference breakdown comparing two prompts/templates."""

    template_name: str
    version_a: str
    version_b: str
    system_prompt_diff: List[PromptDiffLine] = field(default_factory=list)
    user_prompt_diff: List[PromptDiffLine] = field(default_factory=list)
    added_variables: List[str] = field(default_factory=list)
    removed_variables: List[str] = field(default_factory=list)
