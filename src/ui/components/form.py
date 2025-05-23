from dataclasses import dataclass, field
from typing import Optional, List, Callable
from os.path import expanduser
from utils.utils import Platform
import shlex


@dataclass
class FormState:
    # Building configuration
    python_app_path: str = ""
    app_path: str = ""
    output_directory: str = ""
    module_name: str = ""
    arch: str = ""
    flutter_args: List[str] = field(default_factory=list)
    clear_build_cache: bool = False
    template_path: str = ""
    template_dir: str = ""
    template_ref: str = ""
    
    # App information
    project_name: str = ""
    product_name: str = ""
    description: str = ""
    organization: str = ""
    author: dict = field(default_factory=dict)
    
    # Versioning
    build_number: str = "0"
    build_version: str = "1.0.0"
    
    # Appearance
    splash_screen_color: str = ""
    splash_screen_dark_color: str = ""
    app_icon: str = ""
    disable_web_splash_screen: bool = False
    disable_ios_splash_screen: bool = False
    disable_android_splash_screen: bool = False
    
    # Package options
    include_optional_controls: List[str] = field(default_factory=list)
    exclude_additional_files: List[str] = field(default_factory=list)
    compile_app_py_files: bool = False
    compile_site_packages_py_files: bool = False
    remove_unnecessary_app_files: bool = False
    remove_unnecessary_package_files: bool = False
    
    # Web specific options
    base_url: str = ""
    web_renderer: str = ""
    route_url_strategy: str = ""
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
    android_key_store: str = ""
    android_key_store_password: str = ""
    android_key_password: str = ""
    android_key_alias: str = ""
    android_deep_linking_scheme: str = ""
    android_deep_linking_host: str = ""
    split_apk_per_abi: bool = False
    
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
    verbose_build: bool = False
    verbose_build_level: int = 1 # 0: none, 1: -v, 2: -vv
    
    # Callback on change
    on_change: Optional[Callable] = None

    def update(self, field_name, value):
        """Update a field and trigger the callback"""
        if hasattr(self, field_name):
            setattr(self, field_name, value)
            # only call on_change if it's not None
            if self.on_change is not None:
                self.on_change()

    def get_build_command(self):
        """Generate the flet build command based on current state"""
        cmd = ["flet", "build"]
        
        cli_args = self.cli_map()
        # convert the dictionary to command-line arguments
        for key, value in cli_args.items():
            if key == "platform":
                cmd.append(value)
            elif key == "python_app_path":
                cmd.append(expanduser(value))
            elif isinstance(value, bool) and value:
                cmd.append(f"{key}")
            elif isinstance(value, list) and value:
                for item in value:
                    cmd.append(f"{key}={shlex.quote(str(item))}")  # Convert item to string before quoting
            elif value:
                cmd.append(f"{key}={shlex.quote(str(value))}")  # Convert value to string before quoting
        
        if self.module_name:
            cmd.append(f"--module={self.module_name}")

        if hasattr(self, 'verbose_build_level'):
            if self.verbose_build_level == 1:
                cmd.append("-v")
            elif self.verbose_build_level == 2:
                cmd.append("-vv")
        elif self.verbose_build:  # backward compatibility
            cmd.append("-v")
        
        return cmd
    
    def cli_map(self) -> dict:
        """Convert FormState to a dictionary of CLI arguments."""
        if not self.selected_platform:
            return {}
            
        cli_map = {
            # Basic options
            "platform": self.selected_platform.cmd_value.lower(),
            "python_app_path": self.python_app_path,
            "--arch": self.arch,
            "--output": self.output_directory,
            "--clear-cache": self.clear_build_cache,
            "--template": self.template_path,
            "--template-dir": self.template_dir,
            "--template-ref": self.template_ref,

            "--build-version": self.build_version,
            "--build-number": self.build_number,
            
            # App information
            "--project": self.project_name,
            "--product": self.product_name,
            "--description": self.description,
            "--org": self.organization,
            
            # Appearance
            "--splash-color": self.splash_screen_color,
            "--splash-dark-color": self.splash_screen_dark_color,
            "--no-web-splash": self.disable_web_splash_screen,
            "--no-ios-splash": self.disable_ios_splash_screen,
            "--no-android-splash": self.disable_android_splash_screen,
            
            # Package options
            "--exclude": self.exclude_additional_files,
            "--compile-app": self.compile_app_py_files,
            "--compile-packages": self.compile_site_packages_py_files,
            "--cleanup-app": self.remove_unnecessary_app_files,
            "--cleanup-packages": self.remove_unnecessary_package_files,
            
            # Web specific options
            "--base-url": self.base_url,
            "--web-renderer": self.web_renderer,
            "--use-color-emoji": self.enable_color_emojis,
            "--route-url-strategy": self.route_url_strategy,
            "--pwa-background-color": self.pwa_background_color,
            "--pwa-theme-color": self.pwa_theme_color,
            
            # iOS specific options
            "--ios-team-id": self.team_id,
            "--ios-export-method": self.export_method,
            "--ios-signing-certificate": self.signing_certificate,
            "--ios-provisioning-profile": self.provisioning_profile,
            "--info-plist": self.ios_info_plist,
            
            # Android specific options
            "--android-meta-data": self.android_metadata,
            "--android-features": self.android_features,
            "--android-permissions": self.android_permissions,
            "--split-per-abi": self.split_apk_per_abi,
            
            # macOS specific options
            "--macos-entitlements": self.macos_entitlements,
            
            # Flutter build arguments
            "--flutter-build-args": self.flutter_args,

            # Optional flutter controls
            # this doesnt seems to be a valid command:
            # flet: error: unrecognized arguments: --include-packages=flet_video
            "--include-packages": self.include_optional_controls if hasattr(self, 'include_optional_controls') else None,
            
            # Permissions
            "--permissions": [p for p, enabled in {
                "location": self.permission_location,
                "camera": self.permission_camera,
                "microphone": self.permission_microphone,
                "photo_library": self.permission_photo_library
            }.items() if enabled]
        }
        
        # Filter out empty or False values
        return {k: v for k, v in cli_map.items() if v or isinstance(v, (int, float))}
    
    def to_dict(self):
        """Convert model to a dictionary for saving configuration"""
        return {k: v for k, v in self.__dict__.items() 
                if not k.startswith('_') and k != 'on_change' and k != 'selected_platform'}
    
    def from_dict(self, data):
        """Load model from a dictionary"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        if self.on_change is not None:
            self.on_change()