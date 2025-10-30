"""
Prompt template system with versioning and quality metrics.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
import json
import hashlib


@dataclass
class PromptTemplate:
    """A versioned prompt template."""
    
    id: str
    name: str
    description: str
    version: str
    category: str
    template: str
    input_schema: Dict[str, Any]
    examples: List[Dict[str, Any]] = field(default_factory=list)
    quality_score: float = 0.0
    usage_count: int = 0
    success_rate: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    author: str = "system"
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "category": self.category,
            "template": self.template,
            "input_schema": self.input_schema,
            "examples": self.examples,
            "quality_score": self.quality_score,
            "usage_count": self.usage_count,
            "success_rate": self.success_rate,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "author": self.author,
            "tags": self.tags
        }
    
    def render(self, **kwargs) -> str:
        """Render template with variables."""
        rendered = self.template
        
        # Validate inputs
        for key, value in kwargs.items():
            if key not in self.input_schema:
                raise ValueError(f"Unknown variable: {key}")
            rendered = rendered.replace(f"{{{key}}}", str(value))
        
        return rendered
    
    def calculate_quality_score(self) -> float:
        """Calculate quality score based on metrics."""
        # Factors: success_rate (60%), usage_count (20%), recent updates (20%)
        recency_factor = 1.0 if (datetime.now() - self.updated_at).days < 30 else 0.8
        
        score = (
            self.success_rate * 0.6 +
            min(self.usage_count / 100, 1.0) * 0.2 +
            recency_factor * 0.2
        )
        
        return round(score, 2)
    
    def update_metrics(self, success: bool):
        """Update usage and success metrics."""
        self.usage_count += 1
        
        if self.usage_count == 1:
            self.success_rate = 1.0 if success else 0.0
        else:
            # Running average
            self.success_rate = (
                (self.success_rate * (self.usage_count - 1) + (1.0 if success else 0.0))
                / self.usage_count
            )
        
        self.quality_score = self.calculate_quality_score()
        self.updated_at = datetime.now()


class TemplateStore:
    """Store and manage prompt templates."""
    
    def __init__(self, storage_path: str = "data/prompts/templates.json"):
        self.storage_path = storage_path
        self.templates: Dict[str, PromptTemplate] = {}
        self.load_templates()
    
    def load_templates(self):
        """Load templates from storage."""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                
                for template_data in data.get("templates", []):
                    template = PromptTemplate(**template_data)
                    self.templates[template.id] = template
                    
        except FileNotFoundError:
            # Create directory if it doesn't exist
            import os
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            self.save_templates()
    
    def save_templates(self):
        """Save templates to storage."""
        import os
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        
        data = {
            "templates": [template.to_dict() for template in self.templates.values()]
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_template(
        self,
        name: str,
        description: str,
        category: str,
        template: str,
        input_schema: Dict[str, Any],
        examples: List[Dict[str, Any]] = None,
        author: str = "system"
    ) -> PromptTemplate:
        """Create a new template."""
        template_id = hashlib.md5(f"{name}{description}".encode()).hexdigest()
        
        prompt_template = PromptTemplate(
            id=template_id,
            name=name,
            description=description,
            version="1.0.0",
            category=category,
            template=template,
            input_schema=input_schema,
            examples=examples or [],
            author=author
        )
        
        self.templates[template_id] = prompt_template
        self.save_templates()
        
        return prompt_template
    
    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """Get a template by ID."""
        return self.templates.get(template_id)
    
    def search_templates(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        min_quality: float = 0.0
    ) -> List[PromptTemplate]:
        """Search templates by criteria."""
        results = []
        
        for template in self.templates.values():
            if category and template.category != category:
                continue
            
            if tags and not any(tag in template.tags for tag in tags):
                continue
            
            if template.quality_score < min_quality:
                continue
            
            results.append(template)
        
        # Sort by quality score
        results.sort(key=lambda t: t.quality_score, reverse=True)
        
        return results
    
    def get_top_templates(self, limit: int = 10) -> List[PromptTemplate]:
        """Get top templates by quality."""
        templates = list(self.templates.values())
        templates.sort(key=lambda t: t.quality_score, reverse=True)
        return templates[:limit]
    
    def update_metrics(self, template_id: str, success: bool):
        """Update template metrics."""
        template = self.templates.get(template_id)
        if template:
            template.update_metrics(success)
            self.save_templates()

