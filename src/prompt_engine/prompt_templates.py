"""Registry of default prebuilt prompt templates."""

from typing import Dict, List, Optional
from src.prompt_engine.constants import DEFAULT_TEMPLATES
from src.prompt_engine.models import PromptTemplate
from src.prompt_engine.template_loader import TemplateLoader


class PromptTemplates:
    """Preloaded registry for accessing and expanding standard system template configurations."""

    _registry: Dict[str, PromptTemplate] = {}

    @classmethod
    def initialize(cls) -> None:
        """Loads all default configurations declared in constants.py into the registry."""
        if cls._registry:
            return

        for raw_dict in DEFAULT_TEMPLATES:
            try:
                template = TemplateLoader.from_dict(raw_dict)
                cls._registry[template.name] = template
            except Exception:
                # Silently catch initialization errors during static binding
                pass

    @classmethod
    def get_default(cls, name: str) -> Optional[PromptTemplate]:
        """Fetches a default template by its name."""
        cls.initialize()
        return cls._registry.get(name)

    @classmethod
    def get_all_defaults(cls) -> List[PromptTemplate]:
        """Returns all pre-packaged system templates."""
        cls.initialize()
        return list(cls._registry.values())

    @classmethod
    def get_defaults_by_category(cls, category: str) -> List[PromptTemplate]:
        """Filters standard templates by their category classification."""
        cls.initialize()
        return [tpl for tpl in cls._registry.values() if tpl.category == category]

    @classmethod
    def register_default(cls, template: PromptTemplate) -> None:
        """Adds a custom PromptTemplate to the default preloaded memory registry."""
        cls._registry[template.name] = template


# Initialize immediately upon module load
PromptTemplates.initialize()
