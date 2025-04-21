from typing import List, Dict
from ui.components.widgets import FactoryCard
from core.field_registry import FieldRegistry

class CardFactory:
    @staticmethod
    def create_card(title: str, field_names: List[str], registry: FieldRegistry) -> FactoryCard:
        content = []
        
        for field_name in field_names:
            try:
                field = registry.create_factory_field(field_name)
                content.append(field)
            except ValueError as e:
                print(f"Error creating field: {e}")
        
        return FactoryCard(title=title, content=content)