from dataclasses import dataclass, field
from typing import Optional, List
from .utils import Platform

@dataclass
class FormState:
    # Building configuration
    python_app_path: str = ""
    output_directory: str = ""
    module_name: str = ""
    flutter_args: List[str] = field(default_factory=list)
    clear_build_cache: bool = False
    
    # App information
    project_name: str = ""
    product_name: str = ""
    description: str = ""
    organization: str = ""
    
    # Versioning
    build_number: str = "0"
    build_version: str = "1.0.0"
    
    # Appearance
    splash_screen_color: str = ""
    splash_screen_dark_color: str = ""
    disable_web_splash_screen: bool = False
    disable_ios_splash_screen: bool = False
    disable_android_splash_screen: bool = False
    
    # Package options
    exclude_additional_files: List[str] = field(default_factory=list)
    compile_app_py_files: bool = False
    compile_site_packages_py_files: bool = False
    remove_unnecessary_app_files: bool = False
    remove_unnecessary_package_files: bool = False
    
    # Web specific options
    base_url: str = ""
    web_renderer: str = "canvaskit"
    route_url_strategy: str = "path"
    pwa_background_color: str = ""
    pwa_theme_color: str = ""
    enable_color_emojis: bool = False
    
    # iOS specific options
    team_id: str = ""
    export_method: str = ""
    signing_certificate: str = ""
    provisioning_profile: str = ""
    ios_info_plist: List[str] = field(default_factory=list)
    ios_deep_linking_scheme: str = ""
    ios_deep_linking_host: str = ""
    
    # Android specific options
    android_metadata: List[str] = field(default_factory=list)
    android_features: List[str] = field(default_factory=list)
    android_permissions: List[str] = field(default_factory=list)
    android_signing_key_store: str = ""
    android_signing_key_store_password: str = ""
    android_signing_key_password: str = ""
    android_signing_key_alias: str = "upload"
    android_deep_linking_scheme: str = ""
    android_deep_linking_host: str = ""
    split_apk_per_abis: bool = False
    
    # macOS specific options
    macos_entitlements: List[str] = field(default_factory=list)
    macos_info_plist: List[str] = field(default_factory=list)
    
    # Permissions
    permission_location: bool = False
    permission_camera: bool = False
    permission_microphone: bool = False
    permission_photo_library: bool = False
    
    # Selected platform
    selected_platform: Optional[Platform] = None

    def update(self, field_name, value):
        """Update a field and trigger the callback"""
        if hasattr(self, field_name):
            setattr(self, field_name, value)
            if self.on_change:
                self.on_change()
                
    @property
    def cli_map(form) -> dict:
        """Convert FormState to a dictionary of CLI arguments."""
        cli_map = {
            # Basic options
            "python_app_path": form.python_app_path,
            "--output": form.output_directory,
            "--clear-cache": form.clear_build_cache,
            
            # App information
            "--project": form.project_name,
            "--product": form.product_name,
            "--description": form.description,
            "--org": form.organization,
            
            # Appearance
            "--splash-color": form.splash_screen_color,
            "--splash-dark-color": form.splash_screen_dark_color,
            "--no-web-splash": form.disable_web_splash_screen,
            "--no-ios-splash": form.disable_ios_splash_screen,
            "--no-android-splash": form.disable_android_splash_screen,
            
            # Package options
            "--exclude": form.exclude_additional_files,
            "--compile-app": form.compile_app_py_files,
            "--compile-packages": form.compile_site_packages_py_files,
            "--cleanup-app": form.remove_unnecessary_app_files,
            "--cleanup-packages": form.remove_unnecessary_package_files,
            
            # Web specific options
            "--base-url": form.base_url,
            "--web-renderer": form.web_renderer,
            "--use-color-emoji": form.enable_color_emojis,
            "--route-url-strategy": form.route_url_strategy,
            "--pwa-background-color": form.pwa_background_color,
            "--pwa-theme-color": form.pwa_theme_color,
            
            # iOS specific options
            "--ios-team-id": form.team_id,
            "--ios-export-method": form.export_method,
            "--ios-signing-certificate": form.signing_certificate,
            "--ios-provisioning-profile": form.provisioning_profile,
            "--info-plist": form.ios_info_plist,
            
            # Android specific options
            "--android-meta-data": form.android_metadata,
            "--android-features": form.android_features,
            "--android-permissions": form.android_permissions,
            "--split-per-abi": form.split_apk_per_abis,
            
            # macOS specific options
            "--macos-entitlements": form.macos_entitlements,
            
            # Flutter build arguments
            "--flutter-build-args": form.flutter_args,
            
            # Permissions
            "--permissions": [p for p, enabled in {
                "location": form.permission_location,
                "camera": form.permission_camera,
                "microphone": form.permission_microphone,
                "photo_library": form.permission_photo_library
            }.items() if enabled]
        }
        
        # Add platform if selected
        if form.selected_platform:
            cli_map["platform"] = form.selected_platform.value
        
        # Filter out empty or False values
        return {k: v for k, v in cli_map.items() if v or isinstance(v, (int, float))}


def connect_field(field_ref, state_property):
    """Connect a field to FormState property"""
    def on_field_change(e):
        form_state.update(state_property, field_ref.current.value)
    
    return on_field_change
    