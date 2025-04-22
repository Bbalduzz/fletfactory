from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
import flet as ft
from ui.components.form import FormState
from ui.components.widgets import (
    FactoryTextField, FactoryDropdown, FactoryCheckBox, FactoryBadgeInput,
    FactoryDropdownOption, FactoryField, IconPicker, MultipleFactoryTextField,
    FactoryAuthorRow
)

@dataclass
class FieldDefinition:
    name: str
    property_name: str
    title: str = ""
    hint_text: str = ""
    widget_type: str = "text"
    hint_widget: str = ""
    options: List[Dict[str, str]] = field(default_factory=list)
    on_blur: Optional[Callable] = None
    
    def __post_init__(self):
        if not self.title:
            self.title = self.name.replace('_', ' ').title()


class FieldRegistry:
    def __init__(self, form_state: FormState):
        self.form_state = form_state
        self.field_refs: Dict[str, ft.Ref] = {}
        self.field_definitions: Dict[str, FieldDefinition] = {}
    
    def register_field(self, field_def: FieldDefinition) -> ft.Ref:
        self.field_definitions[field_def.name] = field_def
        ref = ft.Ref()
        self.field_refs[field_def.name] = ref
        return ref
    
    def connect_field(self, field_name: str) -> Callable:
        ref = self.field_refs.get(field_name)
        prop_name = self.field_definitions[field_name].property_name
        
        def on_field_change(e):
            if ref and ref.current:
                self.form_state.update(prop_name, ref.current.value)
        
        return on_field_change
    
    def create_field_widget(self, field_name: str) -> ft.Control:
        field_def = self.field_definitions.get(field_name)
        if not field_def:
            raise ValueError(f"Field {field_name} not registered")
            
        ref = self.field_refs.get(field_name)

        if field_def.widget_type == "template_config":
            return MultipleFactoryTextField(
                titles=["path", "ref", "dir"],
                descriptions=[
                    "Repository or path to a directory with your own template",
                    "Relative path to template in repository",
                    "Branch, tag, or commit to checkout"
                ],
                hint_texts=[
                    "e.g. gh:my-org/my-repo",
                    "e.g. <user-directory>/.cookiecutters/flet-build-template",
                    "e.g. v1",
                ],
                ref=ref,
                on_change=lambda e: self._handle_template_config_change(e, field_def.property_name)
            )
        if field_def.widget_type == "author_info":
            return FactoryAuthorRow(
                ref=ref,
                on_change=self.connect_field(field_name)
            )
        if field_def.widget_type == "icon":
            return IconPicker(
                hint_text=field_def.hint_text,
                ref=ref,
                on_change=lambda e: self.form_state.update(field_def.property_name, e.control.value)
            )
        elif field_def.widget_type == "text":
            return FactoryTextField(
                hint_text=field_def.hint_widget or field_def.hint_text,
                ref=ref,
                on_change=self.connect_field(field_name),
                on_blur=field_def.on_blur
            )
        elif field_def.widget_type == "dropdown":
            options = [
                FactoryDropdownOption(key=opt["key"], text=opt["text"])
                for opt in field_def.options
            ]
            return FactoryDropdown(
                options=options,
                ref=ref,
                enable_filter=True,
                on_change=self.connect_field(field_name)
            )
        elif field_def.widget_type == "checkbox":
            return FactoryCheckBox(
                label=field_def.title,
                ref=ref,
                on_change=self.connect_field(field_name)
            )
        elif field_def.widget_type == "badges":
            return FactoryBadgeInput(
                hint_text=field_def.hint_widget or field_def.hint_text,
                ref=ref,
                on_change=self.connect_field(field_name)
            )
        
        return ft.Text("Unsupported widget type")
    
    def create_factory_field(self, field_name: str) -> FactoryField:
        field_def = self.field_definitions.get(field_name)
        if not field_def:
            raise ValueError(f"Field {field_name} not registered")
            
        widget = self.create_field_widget(field_name)
        
        return FactoryField(
            title=field_def.title,
            hint_text=field_def.hint_text,
            widget=widget
        )
    
    def get_ref(self, field_name: str) -> ft.Ref:
        return self.field_refs.get(field_name)

    def _handle_template_config_change(self, e, property_name):
        """Special handler for template configuration that maps to individual fields"""
        if hasattr(e, 'control') and hasattr(e.control, 'value'):
            template_values = e.control.value
            if 'path' in template_values:
                self.form_state.update('template_path', template_values['path'])
            if 'ref' in template_values:
                self.form_state.update('template_ref', template_values['ref'])
            if 'dir' in template_values:
                self.form_state.update('template_dir', template_values['dir'])