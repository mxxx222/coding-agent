"""
A/B testing framework for prompt templates.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import random
import json
from services.prompts.template import PromptTemplate, TemplateStore


@dataclass
class Variant:
    """A test variant."""
    template_id: str
    traffic_percentage: float = 50.0
    impressions: int = 0
    conversions: int = 0
    conversion_rate: float = 0.0


@dataclass
class ABTest:
    """An A/B test configuration."""
    
    id: str
    name: str
    description: str
    variants: List[Variant]
    status: str = "draft"  # draft, running, completed
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    min_sample_size: int = 100
    max_duration_days: int = 7
    winner: Optional[str] = None
    confidence_level: float = 95.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "variants": [
                {
                    "template_id": v.template_id,
                    "traffic_percentage": v.traffic_percentage,
                    "impressions": v.impressions,
                    "conversions": v.conversions,
                    "conversion_rate": v.conversion_rate
                }
                for v in self.variants
            ],
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "min_sample_size": self.min_sample_size,
            "winner": self.winner,
            "confidence_level": self.confidence_level
        }
    
    def select_variant(self) -> str:
        """Select a random variant based on traffic allocation."""
        r = random.random() * 100
        
        cumulative = 0.0
        for variant in self.variants:
            cumulative += variant.traffic_percentage
            if r <= cumulative:
                return variant.template_id
        
        # Fallback to first variant
        return self.variants[0].template_id
    
    def record_impression(self, variant_id: str):
        """Record an impression for a variant."""
        for variant in self.variants:
            if variant.template_id == variant_id:
                variant.impressions += 1
                break
    
    def record_conversion(self, variant_id: str):
        """Record a conversion for a variant."""
        for variant in self.variants:
            if variant.template_id == variant_id:
                variant.conversions += 1
                if variant.impressions > 0:
                    variant.conversion_rate = variant.conversions / variant.impressions
                break
    
    def check_completion(self) -> bool:
        """Check if test should be completed."""
        if self.status != "running":
            return False
        
        # Check sample size
        total_impressions = sum(v.impressions for v in self.variants)
        if total_impressions >= self.min_sample_size:
            return True
        
        # Check duration
        if self.started_at:
            duration = (datetime.now() - self.started_at).days
            if duration >= self.max_duration_days:
                return True
        
        return False
    
    def determine_winner(self) -> Optional[str]:
        """Determine the winner based on conversion rates."""
        if len(self.variants) < 2:
            return None
        
        # Find variant with highest conversion rate
        winner = max(self.variants, key=lambda v: v.conversion_rate)
        
        # Check if statistically significant
        # Simple check: 10% improvement minimum
        if len(self.variants) > 1:
            baseline = min(v.conversion_rate for v in self.variants)
            winner_rate = winner.conversion_rate
            
            if winner_rate > baseline * 1.1:
                return winner.template_id
        
        return None


class ABTestManager:
    """Manage A/B tests."""
    
    def __init__(self, storage_path: str = "data/prompts/ab_tests.json"):
        self.storage_path = storage_path
        self.tests: Dict[str, ABTest] = {}
        self.template_store: TemplateStore = TemplateStore()
        self.load_tests()
    
    def load_tests(self):
        """Load tests from storage."""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                
                for test_data in data.get("tests", []):
                    # Reconstruct variants
                    variants = [
                        Variant(**v) for v in test_data.get("variants", [])
                    ]
                    
                    test = ABTest(
                        id=test_data["id"],
                        name=test_data["name"],
                        description=test_data["description"],
                        variants=variants,
                        status=test_data.get("status", "draft"),
                        created_at=datetime.fromisoformat(test_data.get("created_at", datetime.now().isoformat())),
                        started_at=datetime.fromisoformat(test_data["started_at"]) if test_data.get("started_at") else None,
                        completed_at=datetime.fromisoformat(test_data["completed_at"]) if test_data.get("completed_at") else None,
                        min_sample_size=test_data.get("min_sample_size", 100),
                        max_duration_days=test_data.get("max_duration_days", 7),
                        winner=test_data.get("winner"),
                        confidence_level=test_data.get("confidence_level", 95.0)
                    )
                    
                    self.tests[test.id] = test
                    
        except FileNotFoundError:
            import os
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            self.save_tests()
    
    def save_tests(self):
        """Save tests to storage."""
        import os
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        
        data = {
            "tests": [test.to_dict() for test in self.tests.values()]
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_test(
        self,
        name: str,
        description: str,
        template_ids: List[str],
        traffic_allocation: List[float] = None
    ) -> ABTest:
        """Create a new A/B test."""
        import hashlib
        test_id = hashlib.md5(f"{name}{description}".encode()).hexdigest()
        
        # Default to equal traffic allocation
        if traffic_allocation is None:
            traffic_allocation = [100.0 / len(template_ids)] * len(template_ids)
        
        # Create variants
        variants = [
            Variant(template_id=tid, traffic_percentage=traffic)
            for tid, traffic in zip(template_ids, traffic_allocation)
        ]
        
        test = ABTest(
            id=test_id,
            name=name,
            description=description,
            variants=variants
        )
        
        self.tests[test_id] = test
        self.save_tests()
        
        return test
    
    def start_test(self, test_id: str):
        """Start an A/B test."""
        test = self.tests.get(test_id)
        if test:
            test.status = "running"
            test.started_at = datetime.now()
            self.save_tests()
    
    def get_active_tests(self) -> List[ABTest]:
        """Get all active tests."""
        return [test for test in self.tests.values() if test.status == "running"]
    
    def select_template_for_test(self, test_id: str) -> str:
        """Select a template for testing."""
        test = self.tests.get(test_id)
        if test and test.status == "running":
            variant_id = test.select_variant()
            test.record_impression(variant_id)
            self.save_tests()
            return variant_id
        
        return None
    
    def record_test_result(self, test_id: str, variant_id: str, success: bool):
        """Record a test result."""
        test = self.tests.get(test_id)
        if test and test.status == "running":
            test.record_impression(variant_id)
            if success:
                test.record_conversion(variant_id)
            
            # Check if test should complete
            if test.check_completion():
                test.status = "completed"
                test.completed_at = datetime.now()
                test.winner = test.determine_winner()
                
                # Update winner template quality
                if test.winner:
                    self.template_store.update_metrics(test.winner, True)
            
            self.save_tests()

