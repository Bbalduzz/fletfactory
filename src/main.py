import flet as ft
# from flet_cli.utils.pyproject_toml import load_pyproject_toml
from enum import Enum
from pathlib import Path
from os.path import expanduser
from typing import List
import toml

from components.utils import colors_map, Platform, buildable_platforms
from components.waterfall_layout import WaterfallView
from components.widgets import (
    FactoryCard,
    FactoryCheckBox,
    FactoryDropdown,
    FactoryDropdownOption,
    FactoryField,
    FactoryTextField,
    FactoryBadge,
    FactoryBadgeInput,
    colors_map,
    PlatformButton, PlatformsRow
)
from components.form import FormState, connect_field
from views.sidebar import FactorySidebar

def load_pyproject_toml(project_dir: Path):
    project_str = Path(expanduser(str(project_dir)))
    pyproject_toml = {}
    pyproject_toml_file = project_str.joinpath("pyproject.toml")

    if pyproject_toml_file.exists():
        print("Loading pyproject.toml...")
        with open(pyproject_toml_file, "r") as f:
            pyproject_toml = toml.loads(f.read())  # Use toml.load instead of loads
    
    def get_pyproject(setting: str = None):
        if not setting:
            return pyproject_toml
        
        d = pyproject_toml
        for k in setting.split("."):
            if not isinstance(d, dict):
                return None
            d = d.get(k)
            if d is None:
                return None
        return d
    
    return get_pyproject

## title section
class FactoryHeader(ft.Row):
    def __init__(self):
        super().__init__(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=10
        )
        self.controls = [
            ft.Row(
                alignment=ft.CrossAxisAlignment.BASELINE,
                spacing=10,
                controls=[
                    ft.Text("Flet Factory", style=ft.TextStyle(
                        font_family="OpenRunde Bold",
                        size=30,
                        color=colors_map["text_secondary"],
                    )),
                ]
            ),
        ]

def main(page: ft.Page):
    page.title = "Flet Factory"
    page.padding = 0
    page.window.width = 960
    page.window.height = 800
    page.window.resizable = False
    page.window.title_bar_hidden = True
    page.bgcolor = "#f9fafb"
    page.fonts = {
        "OpenRunde Regular": "/fonts/open_runde/OpenRunde-Regular.otf",
        "OpenRunde Medium": "/fonts/open_runde/OpenRunde-Medium.otf",
        "OpenRunde Bold": "/fonts/open_runde/OpenRunde-Bold.otf",
        "OpenRunde Semibold": "/fonts/open_runde/OpenRunde-Semibold.otf",
    }
    page.theme = ft.Theme(
        font_family="OpenRunde Regular"
    )
    
    # MARK: state #
    form_state = FormState()
    form_state.on_change = lambda: update_command_display()

    python_app_path_ref = ft.Ref[FactoryTextField]()
    output_directory_ref = ft.Ref[FactoryTextField]()
    module_name_ref = ft.Ref[FactoryTextField]()
    flutter_args_ref = ft.Ref[FactoryBadgeInput]()
    clear_build_cache_ref = ft.Ref[FactoryCheckBox]()
    
    # App information refs
    project_name_ref = ft.Ref[FactoryTextField]()
    product_name_ref = ft.Ref[FactoryTextField]()
    description_ref = ft.Ref[FactoryTextField]()
    organization_ref = ft.Ref[FactoryTextField]()
    
    # Versioning refs
    build_number_ref = ft.Ref[FactoryTextField]()
    build_version_ref = ft.Ref[FactoryTextField]()
    
    # Appearance refs
    splash_screen_color_ref = ft.Ref[FactoryTextField]()
    splash_screen_dark_color_ref = ft.Ref[FactoryTextField]()
    disable_web_splash_ref = ft.Ref[FactoryCheckBox]()
    disable_ios_splash_ref = ft.Ref[FactoryCheckBox]()
    disable_android_splash_ref = ft.Ref[FactoryCheckBox]()
    
    # Package options refs
    exclude_files_ref = ft.Ref[FactoryBadgeInput]()
    compile_app_py_ref = ft.Ref[FactoryCheckBox]()
    compile_site_packages_ref = ft.Ref[FactoryCheckBox]()
    remove_app_files_ref = ft.Ref[FactoryCheckBox]()
    remove_package_files_ref = ft.Ref[FactoryCheckBox]()
    
    # Web specific refs
    base_url_ref = ft.Ref[FactoryTextField]()
    web_renderer_ref = ft.Ref[FactoryDropdown]()
    url_strategy_ref = ft.Ref[FactoryDropdown]()
    pwa_bg_color_ref = ft.Ref[FactoryTextField]()
    pwa_theme_color_ref = ft.Ref[FactoryTextField]()
    enable_color_emojis_ref = ft.Ref[FactoryCheckBox]()
    
    # iOS specific refs
    team_id_ref = ft.Ref[FactoryTextField]()
    export_method_ref = ft.Ref[FactoryDropdown]()
    signing_certificate_ref = ft.Ref[FactoryTextField]()
    provisioning_profile_ref = ft.Ref[FactoryTextField]()
    ios_info_plist_ref = ft.Ref[FactoryBadgeInput]()
    ios_deep_linking_scheme_ref = ft.Ref[FactoryTextField]()
    ios_deep_linking_host_ref = ft.Ref[FactoryTextField]()
    
    # Android specific refs
    android_metadata_ref = ft.Ref[FactoryBadgeInput]()
    android_features_ref = ft.Ref[FactoryBadgeInput]()
    android_permissions_ref = ft.Ref[FactoryBadgeInput]()
    android_key_store_ref = ft.Ref[FactoryTextField]()
    android_key_store_password_ref = ft.Ref[FactoryTextField]()
    android_key_password_ref = ft.Ref[FactoryTextField]()
    android_key_alias_ref = ft.Ref[FactoryTextField]()
    android_deep_linking_scheme_ref = ft.Ref[FactoryTextField]()
    android_deep_linking_host_ref = ft.Ref[FactoryTextField]()
    split_apk_per_abi_ref = ft.Ref[FactoryCheckBox]()
    
    # macOS specific refs
    macos_entitlements_ref = ft.Ref[FactoryBadgeInput]()
    macos_info_plist_ref = ft.Ref[FactoryBadgeInput]()
    
    # Permissions refs
    location_permission_ref = ft.Ref[FactoryCheckBox]()
    camera_permission_ref = ft.Ref[FactoryCheckBox]()
    microphone_permission_ref = ft.Ref[FactoryCheckBox]()
    photo_library_permission_ref = ft.Ref[FactoryCheckBox]()

    command_display_ref = ft.Ref[ft.Text]()

    # Add this function after defining all the refs and before creating the UI components
    def populate_form_from_pyproject(e):
        """Populate form fields with data from pyproject.toml."""
        print("Populating form from pyproject.toml...")
        # Get the path from the text field
        project_dir = python_app_path_ref.current.value
        if not project_dir:
            return

        try:
            get_pyproject = load_pyproject_toml(Path(project_dir))
            # Check if pyproject.toml exists
            if not get_pyproject():
                print("No pyproject.toml found or file is empty")
                return

            # Remove assertion to make the function more robust
            # assert get_pyproject("tool.flet.app.path")
            
            # Building configuration
            if app_path := get_pyproject("tool.flet.app.path"):
                # This is the app path
                python_app_path_ref.current.value = app_path
                form_state.python_app_path = app_path
                
            if app_module := get_pyproject("tool.flet.app.module"):
                module_name_ref.current.value = app_module
                form_state.module_name = app_module
            
            # App information - check both project and poetry sections
            if project_name := get_pyproject("project.name") or get_pyproject("tool.poetry.name"):
                project_name_ref.current.value = project_name
                form_state.project_name = project_name
            
            if product_name := get_pyproject("tool.flet.product"):
                product_name_ref.current.value = product_name
                form_state.product_name = product_name
            
            if description := get_pyproject("project.description") or get_pyproject("tool.poetry.description"):
                description_ref.current.value = description
                form_state.description = description
            
            if organization := get_pyproject("tool.flet.org"):
                organization_ref.current.value = organization
                form_state.organization = organization
            
            # Versioning
            if build_number := get_pyproject("tool.flet.build_number"):
                build_number_ref.current.value = str(build_number)
                form_state.build_number = str(build_number)
            
            if version := get_pyproject("project.version") or get_pyproject("tool.poetry.version"):
                build_version_ref.current.value = version
                form_state.build_version = version
            
            # Appearance - updated paths
            if splash_color := get_pyproject("tool.flet.splash.color"):
                splash_screen_color_ref.current.value = splash_color
                form_state.splash_screen_color = splash_color
            
            if splash_dark_color := get_pyproject("tool.flet.splash.dark_color"):
                splash_screen_dark_color_ref.current.value = splash_dark_color
                form_state.splash_screen_dark_color = splash_dark_color
            
            # Splash screen settings - note these are boolean values
            if splash_web := get_pyproject("tool.flet.splash.web"):
                disable_web_splash_ref.current.value = not splash_web  # Invert the logic
                form_state.disable_web_splash = not splash_web
            
            if splash_ios := get_pyproject("tool.flet.splash.ios"):
                disable_ios_splash_ref.current.value = not splash_ios  # Invert the logic
                form_state.disable_ios_splash = not splash_ios
            
            if splash_android := get_pyproject("tool.flet.splash.android"):
                disable_android_splash_ref.current.value = not splash_android  # Invert the logic
                form_state.disable_android_splash = not splash_android
            
            # Package options - updated paths
            if exclude_files := get_pyproject("tool.flet.app.exclude"):
                exclude_files_ref.current.value = exclude_files
                form_state.exclude_files = exclude_files
            
            if compile_app_py := get_pyproject("tool.flet.compile.app"):
                compile_app_py_ref.current.value = compile_app_py
                form_state.compile_app_py = compile_app_py
            
            if compile_site_packages := get_pyproject("tool.flet.compile.packages"):
                compile_site_packages_ref.current.value = compile_site_packages
                form_state.compile_site_packages = compile_site_packages
            
            if remove_app_files := get_pyproject("tool.flet.cleanup.app_files"):
                remove_app_files_ref.current.value = remove_app_files
                form_state.remove_app_files = remove_app_files
            
            if remove_package_files := get_pyproject("tool.flet.cleanup.package_files"):
                remove_package_files_ref.current.value = remove_package_files
                form_state.remove_package_files = remove_package_files
            
            # Web specific options - correct paths
            if base_url := get_pyproject("tool.flet.web.base_url"):
                base_url_ref.current.value = base_url
                form_state.base_url = base_url
            
            if web_renderer := get_pyproject("tool.flet.web.renderer"):
                web_renderer_ref.current.value = web_renderer
                form_state.web_renderer = web_renderer
            
            if url_strategy := get_pyproject("tool.flet.web.route_url_strategy"):
                url_strategy_ref.current.value = url_strategy
                form_state.url_strategy = url_strategy
            
            if pwa_bg_color := get_pyproject("tool.flet.web.pwa_background_color"):
                pwa_bg_color_ref.current.value = pwa_bg_color
                form_state.pwa_bg_color = pwa_bg_color
            
            if pwa_theme_color := get_pyproject("tool.flet.web.pwa_theme_color"):
                pwa_theme_color_ref.current.value = pwa_theme_color
                form_state.pwa_theme_color = pwa_theme_color
            
            if enable_color_emojis := get_pyproject("tool.flet.web.use_color_emoji"):
                enable_color_emojis_ref.current.value = enable_color_emojis
                form_state.enable_color_emojis = enable_color_emojis
            
            # iOS specific options - updated paths
            if team_id := get_pyproject("tool.flet.ios.team_id"):
                team_id_ref.current.value = team_id
                form_state.team_id = team_id
            
            if export_method := get_pyproject("tool.flet.ios.export_method"):
                export_method_ref.current.value = export_method
                form_state.export_method = export_method
            
            if signing_certificate := get_pyproject("tool.flet.ios.signing_certificate"):
                signing_certificate_ref.current.value = signing_certificate
                form_state.signing_certificate = signing_certificate
            
            if provisioning_profile := get_pyproject("tool.flet.ios.provisioning_profile"):
                provisioning_profile_ref.current.value = provisioning_profile
                form_state.provisioning_profile = provisioning_profile
            
            if ios_info_plist := get_pyproject("tool.flet.ios.info"):
                ios_info_plist_ref.current.value = ios_info_plist
                form_state.ios_info_plist = ios_info_plist
            
            # Deep linking configuration
            if deep_linking_scheme := get_pyproject("tool.flet.deep_linking.scheme"):
                ios_deep_linking_scheme_ref.current.value = deep_linking_scheme
                android_deep_linking_scheme_ref.current.value = deep_linking_scheme
                form_state.ios_deep_linking_scheme = deep_linking_scheme
                form_state.android_deep_linking_scheme = deep_linking_scheme
            
            if deep_linking_host := get_pyproject("tool.flet.deep_linking.host"):
                ios_deep_linking_host_ref.current.value = deep_linking_host
                android_deep_linking_host_ref.current.value = deep_linking_host
                form_state.ios_deep_linking_host = deep_linking_host
                form_state.android_deep_linking_host = deep_linking_host
            
            # Platform-specific deep linking
            if ios_deep_linking_scheme := get_pyproject("tool.flet.ios.deep_linking.scheme"):
                ios_deep_linking_scheme_ref.current.value = ios_deep_linking_scheme
                form_state.ios_deep_linking_scheme = ios_deep_linking_scheme
            
            if ios_deep_linking_host := get_pyproject("tool.flet.ios.deep_linking.host"):
                ios_deep_linking_host_ref.current.value = ios_deep_linking_host
                form_state.ios_deep_linking_host = ios_deep_linking_host
            
            if android_deep_linking_scheme := get_pyproject("tool.flet.android.deep_linking.scheme"):
                android_deep_linking_scheme_ref.current.value = android_deep_linking_scheme
                form_state.android_deep_linking_scheme = android_deep_linking_scheme
            
            if android_deep_linking_host := get_pyproject("tool.flet.android.deep_linking.host"):
                android_deep_linking_host_ref.current.value = android_deep_linking_host
                form_state.android_deep_linking_host = android_deep_linking_host
            
            # Android specific options - updated paths
            if android_metadata := get_pyproject("tool.flet.android.meta_data"):
                android_metadata_ref.current.value = android_metadata
                form_state.android_metadata = android_metadata
            
            if android_features := get_pyproject("tool.flet.android.feature"):
                android_features_ref.current.value = android_features
                form_state.android_features = android_features
            
            if android_permissions := get_pyproject("tool.flet.android.permission"):
                android_permissions_ref.current.value = android_permissions
                form_state.android_permissions = android_permissions
            
            if android_key_store := get_pyproject("tool.flet.android.signing.key_store"):
                android_key_store_ref.current.value = android_key_store
                form_state.android_key_store = android_key_store
            
            if android_key_alias := get_pyproject("tool.flet.android.signing.key_alias"):
                android_key_alias_ref.current.value = android_key_alias
                form_state.android_key_alias = android_key_alias
            
            if split_apk_per_abi := get_pyproject("tool.flet.android.split_per_abi"):
                split_apk_per_abi_ref.current.value = split_apk_per_abi
                form_state.split_apk_per_abi = split_apk_per_abi
            
            # macOS specific options - updated paths
            if macos_entitlements := get_pyproject("tool.flet.macos.entitlement"):
                macos_entitlements_ref.current.value = macos_entitlements
                form_state.macos_entitlements = macos_entitlements
            
            if macos_info_plist := get_pyproject("tool.flet.macos.info"):
                macos_info_plist_ref.current.value = macos_info_plist
                form_state.macos_info_plist = macos_info_plist
            
            # Update the UI
            page.update()
            # TODO: self.update_command()
        except Exception as e:
            print(f"Error reading pyproject.toml: {e}")

    def update_command_display():
        if command_display_ref.current:
            command_display_ref.current.value = form_state.get_build_command()
            page.update()

    # MARK: ui #
    header = ft.Container(
        FactoryHeader(),
        margin=ft.margin.only(left=5, right=10, top=10),
    )
    platforms_row = PlatformsRow([Platform.WINDOWS, Platform.MACOS, Platform.LINUX, Platform.ANDROID_APK, Platform.ANDROID_AAP, Platform.IOS, Platform.WEB])
    
    building_configuration_card = FactoryCard(
        title="Building configuration",
        content=[
            FactoryField(
                title="Python App Path",
                hint_text="Path to a directory with the flet project",
                widget=FactoryTextField(
                    hint_text="My project",
                    ref=python_app_path_ref,
                    on_change=connect_field(python_app_path_ref, "python_app_path"),
                    on_blur=populate_form_from_pyproject
                )
            ),
            FactoryField(
                title="Output directory",
                hint_text="Where to put resulting executable or bundle",
                widget=FactoryTextField(
                    hint_text="Default: <python_app_directory>/build/<target_platform>",
                    ref=output_directory_ref,
                    on_change=connect_field(output_directory_ref, "output_directory"),
                )
            ),
            FactoryField(
                title="Module name",
                hint_text="Python module name with an app entry point",
                widget=FactoryTextField(
                    hint_text="e.g main",
                    ref=module_name_ref,
                    on_change=connect_field(module_name_ref, "module_name"),
                )
            ),
            FactoryField(
                title="Flutter args",
                hint_text="Additional arguments for flutter build command",
                widget=FactoryBadgeInput(
                    "e.g --no-tree-shake-icons",
                    ref=flutter_args_ref,
                    on_change=connect_field(flutter_args_ref, "flutter_args"),
                )
            ),
            FactoryField(
                title="",
                hint_text="",
                widget=ft.Column(
                    controls=[
                        FactoryCheckBox(
                            label="Clear build cache",
                            ref=clear_build_cache_ref,
                            on_change=connect_field(clear_build_cache_ref, "clear_build_cache"),
                        ),
                    ]
                )
            )
        ]
    )

    app_informations_card = FactoryCard(
        title="App informations",
        content=[
            FactoryField(
                title="Project name",
                hint_text="Project name for executable or bundle",
                widget=FactoryTextField(
                    hint_text="e.g my_flet_app",
                    ref=project_name_ref,
                    on_change=connect_field(project_name_ref, "project_name"),
                )
            ),
            FactoryField(
                title="Product name",
                hint_text="Display name shown in window titles and about dialogs",
                widget=FactoryTextField(
                    hint_text="e.g My Flet App",
                    ref=product_name_ref,
                    on_change=connect_field(product_name_ref, "product_name"),
                )
            ),
            FactoryField(
                title="Description",
                hint_text="The description to use for executable or bundle",
                widget=FactoryTextField(
                    hint_text="A short description of your app",
                    ref=description_ref,
                    on_change=connect_field(description_ref, "description"),
                )
            ),
            FactoryField(
                title="Organization",
                hint_text="Org name in reverse domain name notation",
                widget=FactoryTextField(
                    hint_text="e.g com.mycompany",
                    ref=organization_ref,
                    on_change=connect_field(organization_ref, "organization"),
                )
            ),
        ]
    )

    versioning_card = FactoryCard(
        title="Versioning",
        content=[
            FactoryField(
                title="Build number",
                hint_text="Identifier used as an internal version number",
                widget=FactoryTextField(
                    hint_text="0",
                    ref=build_number_ref,
                    on_change=connect_field(build_number_ref, "build_number"),
                )
            ),
            FactoryField(
                title="Build version",
                hint_text='A "x.y.z" string shown to users',
                widget=FactoryTextField(
                    hint_text="1.0.0",
                    ref=build_version_ref,
                    on_change=connect_field(build_version_ref, "build_version"),
                )
            )
        ]
    )

    appearance_card = FactoryCard(
        title="Appearance",
        content=[
            FactoryField(
                title="Splash Screen Color",
                hint_text="Background color of splash screen",
                widget=FactoryTextField(
                    hint_text="e.g. #5b21b6",
                    ref=splash_screen_color_ref,
                    on_change=connect_field(splash_screen_color_ref, "splash_screen_color"),
                )
            ),
            FactoryField(
                title="Splash Screen Dark Color",
                hint_text="Background color in dark mode",
                widget=FactoryTextField(
                    hint_text="e.g. #1e1b4b",
                    ref=splash_screen_dark_color_ref,
                    on_change=connect_field(splash_screen_dark_color_ref, "splash_screen_dark_color"),
                )
            ),
            FactoryField(
                title="",
                hint_text="",
                widget=ft.Column(
                    controls=[
                        FactoryCheckBox(label="Disable web splash screen", ref=disable_web_splash_ref, on_change=connect_field(disable_web_splash_ref, "disable_web_splash")),
                        FactoryCheckBox(label="Disable iOS splash screen", ref=disable_ios_splash_ref, on_change=connect_field(disable_ios_splash_ref, "disable_ios_splash")),
                        FactoryCheckBox(label="Disable Android splash screen", ref=disable_android_splash_ref, on_change=connect_field(disable_android_splash_ref, "disable_android_splash")),
                    ]
                )
            )
        ]
    )

    package_options_card = FactoryCard(
        title="Package options",
        content=[
            FactoryField(
                title="Exclude Additional Files",
                hint_text="Exclude files and directories from Python app package",
                widget=FactoryBadgeInput(
                    hint_text="e.g. __pycache__/",
                    ref=exclude_files_ref,
                    on_change=connect_field(exclude_files_ref, "exclude_files"),
                )
            ),
            FactoryField(
                title="",
                hint_text="",
                widget=ft.Column(
                    controls=[
                        FactoryCheckBox(label="Compile app's .py files to .pyc", ref=compile_app_py_ref, on_change=connect_field(compile_app_py_ref, "compile_app_py")),
                        FactoryCheckBox(label="Compile site packages' .py files to .pyc", ref=compile_site_packages_ref, on_change=connect_field(compile_site_packages_ref, "compile_site_packages")),
                        FactoryCheckBox(label="Remove unnecessary app files", ref=remove_app_files_ref, on_change=connect_field(remove_app_files_ref, "remove_app_files")),
                        FactoryCheckBox(label="Remove unnecessary package files", ref=remove_package_files_ref, on_change=connect_field(remove_package_files_ref, "remove_package_files")),
                    ]
                )
            )
        ]
    )

    web_specific_options_card = FactoryCard(
        title="Web specific options",
        content=[
            FactoryField(
                title="Base URL",
                hint_text="Base URL for the app",
                widget=FactoryTextField(
                    hint_text="e.g. /myapp",
                    ref=base_url_ref,
                    on_change=connect_field(base_url_ref, "base_url"),
                )
            ),
            FactoryField(
                title="Web Renderer",
                hint_text="Renderer to use",
                widget=FactoryDropdown(
                    options=[
                        FactoryDropdownOption(key="canvaskit", text="CanvasKit"),
                        FactoryDropdownOption(key="html", text="HTML"),
                    ],
                    value="canvaskit",
                    ref=web_renderer_ref,
                    enable_filter=True,
                    on_change=connect_field(web_renderer_ref, "web_renderer"),
                )
            ),
            FactoryField(
                title="Route URL Strategy",
                hint_text="URL routing strategy",
                widget=FactoryDropdown(
                    options=[
                        FactoryDropdownOption(key="path", text="Path"),
                        FactoryDropdownOption(key="hash", text="Hash"),
                    ],
                    value="path",
                    enable_filter=True,
                    ref=url_strategy_ref,
                    on_change=connect_field(url_strategy_ref, "url_strategy"),
                )
            ),
            FactoryField(
                title="PWA Background color",
                hint_text="Initial background color for your web application",
                widget=FactoryTextField(
                    hint_text="e.g. #5b21b6",
                    ref=pwa_bg_color_ref,
                    on_change=connect_field(pwa_bg_color_ref, "pwa_bg_color"),
                )
            ),
            FactoryField(
                title="PWA Theme color",
                hint_text="Default color for your web application's user interface",
                widget=FactoryTextField(
                    hint_text="e.g. #000000",
                    ref=pwa_theme_color_ref,
                    on_change=connect_field(pwa_theme_color_ref, "pwa_theme_color"),
                )
            ),
            FactoryField(
                title="",
                hint_text="",
                widget=ft.Column(
                    controls=[
                        FactoryCheckBox(
                            label="Enable color emojis with CanvasKit",
                            ref=enable_color_emojis_ref,
                            on_change=connect_field(enable_color_emojis_ref, "enable_color_emojis"),
                        ),
                    ]
                )
            )
        ]
    )

    ios_specific_options_card = FactoryCard(
        title="iOS specific options",
        content=[
            FactoryField(
                title="Team ID",
                hint_text="Team ID to sign iOS bundle (10 characters)",
                widget=FactoryTextField(
                    hint_text="e.g. e.g. A1B2C3D4E5",
                    ref=team_id_ref,
                    on_change=connect_field(team_id_ref, "team_id"),
                )
            ),
            FactoryField(
                title="Export Method",
                hint_text="Export method for iOS app",
                widget=FactoryDropdown(
                    options=[
                        FactoryDropdownOption(key="debugging", text="Debugging", ),
                        FactoryDropdownOption(key="release-testing", text="Release-Testing"),
                        FactoryDropdownOption(key="app-store-connect", text="App Store"),
                        FactoryDropdownOption(key="enterprise", text="Enterprise"),
                    ],
                    ref = export_method_ref,
                    enable_filter=True,
                    on_change=connect_field(export_method_ref, "export_method"),
                )
            ),
            FactoryField(
                title="Signing Certificate",
                hint_text="Certificate name, SHA-1 hash, or automatic selector to use for signing iOS app bundle",
                widget=FactoryTextField(
                    hint_text="e.g. Apple Distribution",
                    ref=signing_certificate_ref,
                    on_change=connect_field(signing_certificate_ref, "signing_certificate"),
                )
            ),
            FactoryField(
                title="Provisioning Profile",
                hint_text="Provisioning profile name or UUID that used to sign and export iOS app",
                widget=FactoryTextField(
                    hint_text="e.g. <export-method> com.mycompamy.myapp",
                    ref=provisioning_profile_ref,
                    on_change=connect_field(provisioning_profile_ref, "provisioning_profile"),
                )
            ),
            FactoryField(
                title="Info plist",
                hint_text='the list of "<key>=<value>|True|False" pairs to add to Info.plist',
                widget=FactoryBadgeInput(
                    hint_text="e.g. <key>=<value>",
                    ref=ios_info_plist_ref,
                    on_change=connect_field(ios_info_plist_ref, "ios_info_plist"),
                )
            ),
            FactoryField(
                title="Deep Linking Scheme",
                hint_text="Deep linking URL scheme to configure for iOS and Android builds",
                widget=FactoryTextField(
                    hint_text='e.g. "https" or "myapp"',
                    ref=ios_deep_linking_scheme_ref,
                    on_change=connect_field(ios_deep_linking_scheme_ref, "ios_deep_linking_scheme"),
                )
            ),
            FactoryField(
                title="Deep Linking Host",
                hint_text="Deep linking URL host for iOS and Android builds",
                widget=FactoryTextField(
                    hint_text='',
                    ref=ios_deep_linking_host_ref,
                    on_change=connect_field(ios_deep_linking_host_ref, "ios_deep_linking_host"),
                )
            ),
        ]
    )

    android_specific_options_card = FactoryCard(
        title="Android specific options",
        content=[
            FactoryField(
                title="Android metadata",
                hint_text='the list of "<name>=<value>" app meta-data entries to add to AndroidManifest.xml',
                widget=FactoryBadgeInput(
                    hint_text="e.g. <name>=<value>",
                    ref=android_metadata_ref,   
                    on_change=connect_field(android_metadata_ref, "android_metadata"),
                )
            ),
            FactoryField(
                title="Android fatures",
                hint_text='the list of "<feature_name>=True|False" features to add to AndroidManifest.xml',
                widget=FactoryBadgeInput(
                    hint_text="e.g. <name>=<value>",
                    ref=android_features_ref,
                    on_change=connect_field(android_features_ref, "android_features"),
                )
            ),
            FactoryField(
                title="Android Permissions",
                hint_text='the list of "<uses-permission android:name=\'...\'/>" permissions to add to AndroidManifest.xml',
                widget=FactoryBadgeInput(
                    hint_text="e.g. <uses-permission android:name='...'/>",
                    ref=android_permissions_ref,
                    on_change=connect_field(android_permissions_ref, "android_permissions"),
                )
            ),
            FactoryField(
                title="Android Signing Key Store",
                hint_text="Path to an upload keystore .jks file",
                widget=FactoryTextField(
                    hint_text="e.g. /path/to/keystore.jks",
                    ref=android_key_store_ref,
                    on_change=connect_field(android_key_store_ref, "android_key_store"),
                )
            ),
            FactoryField(
                title="Android Signing Key Store Password",
                hint_text="Android signing key store password",
                widget=FactoryTextField(
                    hint_text="e.g. mypassword",
                    ref=android_key_store_password_ref,
                    on_change=connect_field(android_key_store_password_ref, "android_key_store_password"),
                )
            ),
            FactoryField(
                title="Android Signing Key Password",
                hint_text="Android signing key password",
                widget=FactoryTextField(
                    hint_text="e.g. myalias",
                    ref=android_key_password_ref,
                    on_change=connect_field(android_key_password_ref, "android_key_password"),
                )
            ),
            FactoryField(
                title="Android Signing Key Alias",
                hint_text='Android signing key alias. Default is "upload"',
                widget=FactoryTextField(
                    hint_text="e.g. upload",
                    ref=android_key_alias_ref,
                    on_change=connect_field(android_key_alias_ref, "android_key_alias"),
                )
            ),
            FactoryField(
                title="Deep Linking Scheme",
                hint_text="Deep linking URL scheme to configure for iOS and Android builds",
                widget=FactoryTextField(
                    hint_text='e.g. "https" or "myapp"',
                    ref=android_deep_linking_scheme_ref,
                    on_change=connect_field(android_deep_linking_scheme_ref, "android_deep_linking_scheme"),
                )
            ),
            FactoryField(
                title="Deep Linking Host",
                hint_text="Deep linking URL host for iOS and Android builds",
                widget=FactoryTextField(
                    hint_text='',
                    ref=android_deep_linking_host_ref,
                    on_change=connect_field(android_deep_linking_host_ref, "android_deep_linking_host"),
                )
            ),
            FactoryField(
                title="",
                hint_text="",
                widget=ft.Column(
                    controls=[
                        FactoryCheckBox(label="Split APK per ABIs", ref=split_apk_per_abi_ref, on_change=connect_field(split_apk_per_abi_ref, "split_apk_per_abi")),
                    ]
                )
            )
        ]
    )

    macos_specific_options_card = FactoryCard(
        title="macOS specific options",
        content=[
            FactoryField(
                title="Entitlements",
                hint_text='the list of "<key>=<value>|True|False" entitlements for macOS builds',
                widget=FactoryBadgeInput(
                    hint_text="e.g. <key>=<value>",
                    ref=macos_entitlements_ref,
                    on_change=connect_field(macos_entitlements_ref, "macos_entitlements"),
                )
            ),
            FactoryField(
                title="Info plist",
                hint_text='the list of "<key>=<value>|True|False" pairs to add to Info.plist',
                widget=FactoryBadgeInput(
                    hint_text="e.g. <key>=<value>",
                    ref=macos_info_plist_ref,
                    on_change=connect_field(macos_info_plist_ref, "macos_info_plist"),
                )
            )
        ]
    )

    permissions_card = FactoryCard(
        title="Permissions",
        content=[
            FactoryField(
                title="",
                hint_text="",
                widget=ft.Column( # location,camera,microphone,photo_library
                    controls=[
                        FactoryCheckBox(label="Location", ref=location_permission_ref, on_change=connect_field(location_permission_ref, "location_permission")),
                        FactoryCheckBox(label="Camera", ref=camera_permission_ref, on_change=connect_field(camera_permission_ref, "camera_permission")),
                        FactoryCheckBox(label="Microphone", ref=microphone_permission_ref, on_change=connect_field(microphone_permission_ref, "microphone_permission")),
                        FactoryCheckBox(label="Photo Library", ref=photo_library_permission_ref, on_change=connect_field(photo_library_permission_ref, "photo_library_permission")),
                    ]
                )
            )
        ]
    )
    
    # Create a scrollable right content area
    right_content = ft.Container(
        content=ft.Column(
            controls=[
                header, 
                ft.Container(height=10),  # Spacing
                platforms_row,
                ft.Container(height=10),  # Spacing
                WaterfallView(
                    cross_axis_count=2,
                    main_axis_spacing=10,
                    cross_axis_spacing=10,
                    width=page.window.width - 290,  # Adjust width to account for sidebar
                    controls=[
                        building_configuration_card,
                        app_informations_card,
                        versioning_card,
                        appearance_card,
                        package_options_card,
                        permissions_card,
                        macos_specific_options_card,
                        web_specific_options_card,
                        ios_specific_options_card,
                        android_specific_options_card,
                    ],
                )
            ],
            scroll=ft.ScrollMode.HIDDEN,  # Enable scrolling for this column
            spacing=0,
            height=page.window.height,  # Full height
            width=page.window.width - 290,  # Width minus sidebar
        ),
        padding=20,
    )
    
    # Create a row with the sidebar and content
    page.add(
        ft.Row(
            controls=[
                FactorySidebar(command_ref=command_display_ref),
                right_content,
            ],
            spacing=0,  # No spacing between sidebar and content
            height=page.window.height,
            width=page.window.width,
        )
    )

ft.app(main, assets_dir="assets")
