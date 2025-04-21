import toml
from pathlib import Path
from os import path
from typing import Any, Dict, Optional, List
from ui.components.form import FormState

class PyProjectWriter:
    """Service for updating pyproject.toml files based on form state following Flet documentation structure"""
    
    @staticmethod
    def save_to_path(directory_path: str, form_state: FormState) -> bool:
        """Save form state to pyproject.toml at the given path"""
        try:
            # Expand user directory if needed (e.g., ~/projects)
            expanded_path = path.expanduser(str(directory_path))
            pyproject_path = Path(expanded_path) / "pyproject.toml"
            
            # Load existing pyproject.toml or create a new one
            pyproject_data = {}
            if pyproject_path.exists():
                with open(pyproject_path, "r", encoding="utf-8") as f:
                    pyproject_data = toml.load(f)
            
            # Ensure basic structure exists
            if "project" not in pyproject_data:
                pyproject_data["project"] = {}
            
            if "tool" not in pyproject_data:
                pyproject_data["tool"] = {}
            
            if "flet" not in pyproject_data["tool"]:
                pyproject_data["tool"]["flet"] = {}
            
            # Update core project information
            PyProjectWriter._update_project_section(pyproject_data, form_state)
            
            # Update tool.flet section
            PyProjectWriter._update_flet_section(pyproject_data, form_state)
            
            # Write back to file
            with open(pyproject_path, "w", encoding="utf-8") as f:
                toml.dump(pyproject_data, f)
            
            return True
        except Exception as e:
            print(f"Error saving pyproject.toml: {e}")
            return False
    
    @staticmethod
    def _update_project_section(pyproject_data: Dict[str, Any], form_state: FormState) -> None:
        """Update the [project] section"""
        project = pyproject_data["project"]
        
        # Basic project info
        if form_state.project_name:
            project["name"] = str(form_state.project_name)
        
        if form_state.build_version:
            project["version"] = str(form_state.build_version)
        
        if form_state.description:
            project["description"] = str(form_state.description)
    
    @staticmethod
    def _update_flet_section(pyproject_data: Dict[str, Any], form_state: FormState) -> None:
        """Update the [tool.flet] section and subsections"""
        flet_data = pyproject_data["tool"]["flet"]
        
        # Core Flet settings - only add non-empty/non-zero values
        if form_state.product_name:
            flet_data["product"] = str(form_state.product_name)
        
        if form_state.organization:
            flet_data["org"] = str(form_state.organization)
        
        if form_state.build_number and form_state.build_number != "0":
            flet_data["build_number"] = str(form_state.build_number)
        
        if form_state.arch:
            flet_data["arch"] = str(form_state.arch)

        if form_state.include_optional_controls and len(form_state.include_optional_controls) > 0:
            PyProjectWriter._ensure_section(flet_data, "flutter")
            
            # https://flet.dev/docs/publish/#including-optional-controls
            # here we the simple list format if no version or path information
            # this converts ['flet_video', 'flet_audio'] to:
            # flutter.dependencies = ["flet_video", "flet_audio"]
            dependencies = [str(ctrl) for ctrl in form_state.include_optional_controls]
            flet_data["flutter"]["dependencies"] = dependencies
            
            # If I want to support the more complex format with versions,
            # I would need to parse the input strings to extract version info
            # and use a different structure (dunno)
        
        # App section - only create if needed
        if form_state.module_name or (form_state.exclude_additional_files and len(form_state.exclude_additional_files) > 0):
            PyProjectWriter._ensure_section(flet_data, "app")
            
            if form_state.app_path:
                flet_data["app"]["path"] = str(form_state.app_path)

            if form_state.module_name:
                flet_data["app"]["module"] = str(form_state.module_name)
            
            if form_state.exclude_additional_files and len(form_state.exclude_additional_files) > 0:
                flet_data["app"]["exclude"] = [str(item) for item in form_state.exclude_additional_files]
        
        # Compile section - only add true values
        if form_state.compile_app_py_files or form_state.compile_site_packages_py_files:
            PyProjectWriter._ensure_section(flet_data, "compile")
            
            if form_state.compile_app_py_files:
                flet_data["compile"]["app"] = True
            
            if form_state.compile_site_packages_py_files:
                flet_data["compile"]["packages"] = True
        
        # Cleanup section - only add true values
        if form_state.remove_unnecessary_app_files or form_state.remove_unnecessary_package_files:
            PyProjectWriter._ensure_section(flet_data, "cleanup")
            
            if form_state.remove_unnecessary_app_files:
                flet_data["cleanup"]["app_files"] = True
            
            if form_state.remove_unnecessary_package_files:
                flet_data["cleanup"]["package_files"] = True
        
        # Splash section - only create if needed
        splash_settings = [
            form_state.splash_screen_color,
            form_state.splash_screen_dark_color,
            form_state.disable_web_splash_screen,
            form_state.disable_ios_splash_screen,
            form_state.disable_android_splash_screen
        ]
        
        if any(splash_settings):
            PyProjectWriter._ensure_section(flet_data, "splash")
            
            if form_state.splash_screen_color:
                flet_data["splash"]["color"] = str(form_state.splash_screen_color)
            
            if form_state.splash_screen_dark_color:
                flet_data["splash"]["dark_color"] = str(form_state.splash_screen_dark_color)
            
            # Only add splash screen flags if they're disabled (inverted)
            if form_state.disable_web_splash_screen:
                flet_data["splash"]["web"] = False
            
            if form_state.disable_ios_splash_screen:
                flet_data["splash"]["ios"] = False
            
            if form_state.disable_android_splash_screen:
                flet_data["splash"]["android"] = False
        
        # Permissions section - only add if permissions are enabled
        permissions = []
        if form_state.permission_location:
            permissions.append("location")
        if form_state.permission_camera:
            permissions.append("camera")
        if form_state.permission_microphone:
            permissions.append("microphone")
        if form_state.permission_photo_library:
            permissions.append("photo_library")
        
        if permissions:
            flet_data["permissions"] = permissions
        
        # Platform-specific sections
        PyProjectWriter._update_web_section(flet_data, form_state)
        PyProjectWriter._update_ios_section(flet_data, form_state)
        PyProjectWriter._update_android_section(flet_data, form_state)
        PyProjectWriter._update_macos_section(flet_data, form_state)
        PyProjectWriter._update_deep_linking(flet_data, form_state)
        
        # Flutter build args - only add if not empty
        if form_state.flutter_args and len(form_state.flutter_args) > 0:
            PyProjectWriter._ensure_section(flet_data, "flutter")
            flet_data["flutter"]["build_args"] = [str(arg) for arg in form_state.flutter_args]
    
    @staticmethod
    def _update_web_section(flet_data: Dict[str, Any], form_state: FormState) -> None:
        """Update the web-specific configuration"""
        web_settings = [
            form_state.base_url,
            form_state.web_renderer,
            form_state.route_url_strategy,
            form_state.pwa_background_color,
            form_state.pwa_theme_color,
            form_state.enable_color_emojis
        ]
        
        if any(web_settings):
            PyProjectWriter._ensure_section(flet_data, "web")
            
            if form_state.base_url:
                flet_data["web"]["base_url"] = str(form_state.base_url)
            
            if form_state.web_renderer:
                flet_data["web"]["renderer"] = str(form_state.web_renderer)
            
            if form_state.route_url_strategy:
                flet_data["web"]["route_url_strategy"] = str(form_state.route_url_strategy)
            
            if form_state.pwa_background_color:
                flet_data["web"]["pwa_background_color"] = str(form_state.pwa_background_color)
            
            if form_state.pwa_theme_color:
                flet_data["web"]["pwa_theme_color"] = str(form_state.pwa_theme_color)
            
            # Only add color emoji setting if it's true
            if form_state.enable_color_emojis:
                flet_data["web"]["use_color_emoji"] = True
    
    @staticmethod
    def _update_ios_section(flet_data: Dict[str, Any], form_state: FormState) -> None:
        """Update the iOS-specific configuration"""
        ios_settings = [
            form_state.team_id,
            form_state.export_method,
            form_state.signing_certificate,
            form_state.provisioning_profile,
            form_state.ios_info_plist and len(form_state.ios_info_plist) > 0
        ]
        
        if any(ios_settings):
            PyProjectWriter._ensure_section(flet_data, "ios")
            
            if form_state.team_id:
                flet_data["ios"]["team_id"] = str(form_state.team_id)
            
            if form_state.export_method:
                flet_data["ios"]["export_method"] = str(form_state.export_method)
            
            if form_state.signing_certificate:
                flet_data["ios"]["signing_certificate"] = str(form_state.signing_certificate)
            
            if form_state.provisioning_profile:
                flet_data["ios"]["provisioning_profile"] = str(form_state.provisioning_profile)
            
            if form_state.ios_info_plist and len(form_state.ios_info_plist) > 0:
                flet_data["ios"]["info"] = [str(item) for item in form_state.ios_info_plist]
    
    @staticmethod
    def _update_android_section(flet_data: Dict[str, Any], form_state: FormState) -> None:
        """Update the Android-specific configuration"""
        android_settings = [
            form_state.android_metadata and len(form_state.android_metadata) > 0,
            form_state.android_features and len(form_state.android_features) > 0,
            form_state.android_permissions and len(form_state.android_permissions) > 0,
            form_state.android_key_store,
            form_state.android_key_alias,
            form_state.split_apk_per_abi
        ]
        
        if any(android_settings):
            PyProjectWriter._ensure_section(flet_data, "android")
            
            if form_state.android_metadata and len(form_state.android_metadata) > 0:
                flet_data["android"]["meta_data"] = [str(item) for item in form_state.android_metadata]
            
            if form_state.android_features and len(form_state.android_features) > 0:
                flet_data["android"]["feature"] = [str(item) for item in form_state.android_features]
            
            if form_state.android_permissions and len(form_state.android_permissions) > 0:
                flet_data["android"]["permission"] = [str(item) for item in form_state.android_permissions]
            
            # Only add split_per_abi if true
            if form_state.split_apk_per_abi:
                flet_data["android"]["split_per_abi"] = True
            
            # Android signing section - only create if needed
            if form_state.android_key_store or form_state.android_key_alias:
                PyProjectWriter._ensure_section(flet_data["android"], "signing")
                
                if form_state.android_key_store:
                    flet_data["android"]["signing"]["key_store"] = str(form_state.android_key_store)
                
                if form_state.android_key_alias:
                    flet_data["android"]["signing"]["key_alias"] = str(form_state.android_key_alias)
    
    @staticmethod
    def _update_macos_section(flet_data: Dict[str, Any], form_state: FormState) -> None:
        """Update the macOS-specific configuration"""
        macos_settings = [
            form_state.macos_entitlements and len(form_state.macos_entitlements) > 0,
            form_state.macos_info_plist and len(form_state.macos_info_plist) > 0
        ]
        
        if any(macos_settings):
            PyProjectWriter._ensure_section(flet_data, "macos")
            
            if form_state.macos_entitlements and len(form_state.macos_entitlements) > 0:
                flet_data["macos"]["entitlement"] = [str(item) for item in form_state.macos_entitlements]
            
            if form_state.macos_info_plist and len(form_state.macos_info_plist) > 0:
                flet_data["macos"]["info"] = [str(item) for item in form_state.macos_info_plist]
    
    @staticmethod
    def _update_deep_linking(flet_data: Dict[str, Any], form_state: FormState) -> None:
        """Update deep linking configuration"""
        # Check if we have common deep linking settings
        has_common_deep_linking = (form_state.ios_deep_linking_scheme and form_state.android_deep_linking_scheme and
                                  form_state.ios_deep_linking_scheme == form_state.android_deep_linking_scheme) or \
                                 (form_state.ios_deep_linking_host and form_state.android_deep_linking_host and
                                  form_state.ios_deep_linking_host == form_state.android_deep_linking_host)
        
        # Set common deep linking
        if has_common_deep_linking:
            PyProjectWriter._ensure_section(flet_data, "deep_linking")
            
            if form_state.ios_deep_linking_scheme and form_state.ios_deep_linking_scheme == form_state.android_deep_linking_scheme:
                flet_data["deep_linking"]["scheme"] = str(form_state.ios_deep_linking_scheme)
            
            if form_state.ios_deep_linking_host and form_state.ios_deep_linking_host == form_state.android_deep_linking_host:
                flet_data["deep_linking"]["host"] = str(form_state.ios_deep_linking_host)
        
        # iOS-specific deep linking
        if form_state.ios_deep_linking_scheme and (not form_state.android_deep_linking_scheme or 
                                                 form_state.ios_deep_linking_scheme != form_state.android_deep_linking_scheme):
            if "ios" not in flet_data:
                flet_data["ios"] = {}
            
            PyProjectWriter._ensure_section(flet_data["ios"], "deep_linking")
            flet_data["ios"]["deep_linking"]["scheme"] = str(form_state.ios_deep_linking_scheme)
        
        if form_state.ios_deep_linking_host and (not form_state.android_deep_linking_host or
                                               form_state.ios_deep_linking_host != form_state.android_deep_linking_host):
            if "ios" not in flet_data:
                flet_data["ios"] = {}
            
            PyProjectWriter._ensure_section(flet_data["ios"], "deep_linking")
            flet_data["ios"]["deep_linking"]["host"] = str(form_state.ios_deep_linking_host)
        
        # Android-specific deep linking
        if form_state.android_deep_linking_scheme and (not form_state.ios_deep_linking_scheme or
                                                    form_state.android_deep_linking_scheme != form_state.ios_deep_linking_scheme):
            if "android" not in flet_data:
                flet_data["android"] = {}
            
            PyProjectWriter._ensure_section(flet_data["android"], "deep_linking")
            flet_data["android"]["deep_linking"]["scheme"] = str(form_state.android_deep_linking_scheme)
        
        if form_state.android_deep_linking_host and (not form_state.ios_deep_linking_host or
                                                  form_state.android_deep_linking_host != form_state.ios_deep_linking_host):
            if "android" not in flet_data:
                flet_data["android"] = {}
            
            PyProjectWriter._ensure_section(flet_data["android"], "deep_linking")
            flet_data["android"]["deep_linking"]["host"] = str(form_state.android_deep_linking_host)
    
    @staticmethod
    def _ensure_section(data: Dict[str, Any], section: str) -> None:
        """Ensure a section exists in the data dictionary"""
        if section not in data:
            data[section] = {}