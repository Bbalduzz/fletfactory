from pathlib import Path
from os import path
from typing import Any, Callable, Dict, Optional, Union
from flet_cli.utils.pyproject_toml import load_pyproject_toml
from ui.components.form import FormState
from core.field_registry import FieldRegistry

class PyProjectService:
    @staticmethod
    def load_from_path(directory_path: str) -> Optional[Callable]:
        try:
            get_pyproject = load_pyproject_toml(Path(path.expanduser(str(directory_path))))
            if not get_pyproject():
                print("No pyproject.toml found or file is empty")
                return None
            
            return get_pyproject
        except Exception as e:
            print(f"Error reading pyproject.toml: {e}")
            return None
    
    @staticmethod
    def populate_form_state(get_pyproject: Callable, form_state: FormState, field_registry: FieldRegistry) -> None:
        mapping = {
            "module_name": ["tool.flet.app.module"],
            "app_path": ["tool.flet.app.path"],
            "project_name": ["project.name", "tool.poetry.name"],
            "product_name": ["tool.flet.product"],
            "description": ["project.description", "tool.poetry.description"],
            "organization": ["tool.flet.org"],
            "arch": ["tool.flet.arch"],
            "build_number": ["tool.flet.build_number"],
            "build_version": ["project.version", "tool.poetry.version"],
            "splash_screen_color": ["tool.flet.splash.color"],
            "splash_screen_dark_color": ["tool.flet.splash.dark_color"],
            "base_url": ["tool.flet.web.base_url"],
            "web_renderer": ["tool.flet.web.renderer"],
            "route_url_strategy": ["tool.flet.web.route_url_strategy"],
            "pwa_background_color": ["tool.flet.web.pwa_background_color"],
            "pwa_theme_color": ["tool.flet.web.pwa_theme_color"],
            "team_id": ["tool.flet.ios.team_id"],
            "export_method": ["tool.flet.ios.export_method"],
            "signing_certificate": ["tool.flet.ios.signing_certificate"],
            "provisioning_profile": ["tool.flet.ios.provisioning_profile"],
            "ios_info_plist": ["tool.flet.ios.info"],
            "ios_deep_linking_scheme": ["tool.flet.ios.deep_linking.scheme", "tool.flet.deep_linking.scheme"],
            "ios_deep_linking_host": ["tool.flet.ios.deep_linking.host", "tool.flet.deep_linking.host"],
            "android_deep_linking_scheme": ["tool.flet.android.deep_linking.scheme", "tool.flet.deep_linking.scheme"],
            "android_deep_linking_host": ["tool.flet.android.deep_linking.host", "tool.flet.deep_linking.host"],
            "android_metadata": ["tool.flet.android.meta_data"],
            "android_features": ["tool.flet.android.feature"],
            "android_permissions": ["tool.flet.android.permission"],
            "android_key_store": ["tool.flet.android.signing.key_store"],
            "android_key_alias": ["tool.flet.android.signing.key_alias"],
            "macos_entitlements": ["tool.flet.macos.entitlement"],
            "macos_info_plist": ["tool.flet.macos.info"],
            "exclude_additional_files": ["tool.flet.app.exclude"]
        }
        
        invert_logic = {
            "disable_web_splash_screen": "tool.flet.splash.web",
            "disable_ios_splash_screen": "tool.flet.splash.ios",
            "disable_android_splash_screen": "tool.flet.splash.android"
        }
        
        boolean_fields = {
            "compile_app_py_files": "tool.flet.compile.app",
            "compile_site_packages_py_files": "tool.flet.compile.packages",
            "remove_unnecessary_app_files": "tool.flet.cleanup.app_files",
            "remove_unnecessary_package_files": "tool.flet.cleanup.package_files",
            "enable_color_emojis": "tool.flet.web.use_color_emoji",
            "split_apk_per_abi": "tool.flet.android.split_per_abi"
        }

        template_config_fields = {
            "path": "tool.flet.template.path",
            "dir": "tool.flet.template.dir",
            "ref": "tool.flet.template.ref"
        }

        authors = get_pyproject("project.authors")
        if authors and isinstance(authors, list) and len(authors) > 0:
            author_data = authors[0]
            if isinstance(author_data, dict) and "name" in author_data:
                for name, field_def in field_registry.field_definitions.items():
                    if field_def.property_name == "author":
                        form_state.update("author", author_data)
                        
                        ref = field_registry.get_ref(name)
                        if ref and ref.current:
                            ref.current.value = author_data
                        break
        
        for prop, paths in mapping.items():
            for path_str in paths:
                if value := get_pyproject(path_str):
                    PyProjectService._update_field_value(prop, value, form_state, field_registry)
                    break
        
        for prop, path_str in invert_logic.items():
            if get_pyproject(path_str) is not None:
                value = not get_pyproject(path_str)
                PyProjectService._update_field_value(prop, value, form_state, field_registry)
                
        for prop, path_str in boolean_fields.items():
            if get_pyproject(path_str) is not None:
                value = get_pyproject(path_str)
                PyProjectService._update_field_value(prop, value, form_state, field_registry)

        template_values = {}
        for field, path_str in template_config_fields.items():
            if value := get_pyproject(path_str):
                template_values[field] = value
        if template_values:
            for name, field_def in field_registry.field_definitions.items():
                if field_def.widget_type == "template_config":
                    ref = field_registry.get_ref(name)
                    if ref and ref.current:
                        ref.current.value = template_values
                    break
    
    @staticmethod
    def _update_field_value(property_name: str, value: Any, form_state: FormState, field_registry: FieldRegistry) -> None:
        field_name = None
        for name, field_def in field_registry.field_definitions.items():
            if field_def.property_name == property_name:
                field_name = name
                break
        
        if field_name:
            form_state.update(property_name, value)
            
            ref = field_registry.get_ref(field_name)
            if ref and ref.current:
                ref.current.value = value