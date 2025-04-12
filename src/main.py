import flet as ft
from flet_cli.utils.pyproject_toml import load_pyproject_toml
from enum import Enum
from pathlib import Path
from os import path, environ
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
    PlatformButton, PlatformsRow,
    FactoryHeader
)
from components.toast import Toaster, ToastType, ToastPosition
from components.form import FormState
from views.sidebar import FactorySidebar

environ["FLET_CLI_NO_RICH_OUTPUT"] = "1"

def main(page: ft.Page):
    page.title = "Flet Factory"
    page.padding = 0
    page.window.width = 960
    page.window.height = 800
    page.window.resizable = False
    page.window.title_bar_hidden = True
    page.window.title_bar_buttons_hidden = True
    page.window.center()
    page.bgcolor = "#f9fafb"
    page.fonts = {
        "OpenRunde Regular": "/fonts/open_runde/OpenRunde-Regular.otf",
        "OpenRunde Medium": "/fonts/open_runde/OpenRunde-Medium.otf",
        "OpenRunde Bold": "/fonts/open_runde/OpenRunde-Bold.otf",
        "OpenRunde Semibold": "/fonts/open_runde/OpenRunde-Semibold.otf",
        "FiraCode Retina": "/fonts/fira_code/FiraCode-Retina.ttf",
        "FiraCode Light": "/fonts/fira_code/FiraCode-Light.ttf",
    }
    page.theme = ft.Theme(
        font_family="OpenRunde Regular"
    )

    toaster = Toaster(page, position=ToastPosition.TOP_RIGHT, theme="light")
    
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

    def populate_form_from_pyproject(e):
        """Populate form fields with data from pyproject.toml."""
        print("Populating form from pyproject.toml...")
        # Get the path from the text field
        project_dir = python_app_path_ref.current.value
        if not project_dir:
            return

        try:
            get_pyproject = load_pyproject_toml(Path(path.expanduser(str(project_dir))))
            # Check if pyproject.toml exists
            if not get_pyproject():
                print("No pyproject.toml found or file is empty")
                return

            # Helper function to update both UI and form state
            def update_field(ref, state_property, value):
                if ref.current:
                    ref.current.value = value
                    form_state.update(state_property, value)
            
            # Building configuration

            # if app_path := get_pyproject("tool.flet.app.path"): # is doesnt concern us
            #     update_field(python_app_path_ref, "python_app_path", app_path)
                
            if app_module := get_pyproject("tool.flet.app.module"):
                update_field(module_name_ref, "module_name", app_module)
            
            # App information - check both project and poetry sections
            if project_name := get_pyproject("project.name") or get_pyproject("tool.poetry.name"):
                update_field(project_name_ref, "project_name", project_name)
            
            if product_name := get_pyproject("tool.flet.product"):
                update_field(product_name_ref, "product_name", product_name)
            
            if description := get_pyproject("project.description") or get_pyproject("tool.poetry.description"):
                update_field(description_ref, "description", description)
            
            if organization := get_pyproject("tool.flet.org"):
                update_field(organization_ref, "organization", organization)
            
            # Versioning
            if build_number := get_pyproject("tool.flet.build_number"):
                update_field(build_number_ref, "build_number", str(build_number))
            
            if version := get_pyproject("project.version") or get_pyproject("tool.poetry.version"):
                update_field(build_version_ref, "build_version", version)
            
            # Appearance - updated paths
            if splash_color := get_pyproject("tool.flet.splash.color"):
                update_field(splash_screen_color_ref, "splash_screen_color", splash_color)
            
            if splash_dark_color := get_pyproject("tool.flet.splash.dark_color"):
                update_field(splash_screen_dark_color_ref, "splash_screen_dark_color", splash_dark_color)
            
            # Splash screen settings - note these are boolean values
            if splash_web := get_pyproject("tool.flet.splash.web") is not None:
                value = not get_pyproject("tool.flet.splash.web")  # Invert the logic
                update_field(disable_web_splash_ref, "disable_web_splash", value)
            
            if splash_ios := get_pyproject("tool.flet.splash.ios") is not None:
                value = not get_pyproject("tool.flet.splash.ios")  # Invert the logic
                update_field(disable_ios_splash_ref, "disable_ios_splash", value)
            
            if splash_android := get_pyproject("tool.flet.splash.android") is not None:
                value = not get_pyproject("tool.flet.splash.android")  # Invert the logic
                update_field(disable_android_splash_ref, "disable_android_splash", value)
            
            # Package options - updated paths
            if exclude_files := get_pyproject("tool.flet.app.exclude"):
                update_field(exclude_files_ref, "exclude_files", exclude_files)
            
            if compile_app_py := get_pyproject("tool.flet.compile.app") is not None:
                update_field(compile_app_py_ref, "compile_app_py", get_pyproject("tool.flet.compile.app"))
            
            if compile_site_packages := get_pyproject("tool.flet.compile.packages") is not None:
                update_field(compile_site_packages_ref, "compile_site_packages", get_pyproject("tool.flet.compile.packages"))
            
            if remove_app_files := get_pyproject("tool.flet.cleanup.app_files") is not None:
                update_field(remove_app_files_ref, "remove_app_files", get_pyproject("tool.flet.cleanup.app_files"))
            
            if remove_package_files := get_pyproject("tool.flet.cleanup.package_files") is not None:
                update_field(remove_package_files_ref, "remove_package_files", get_pyproject("tool.flet.cleanup.package_files"))
            
            # Continue with the rest of the fields using the update_field helper
            # Web specific options
            if base_url := get_pyproject("tool.flet.web.base_url"):
                update_field(base_url_ref, "base_url", base_url)
            
            if web_renderer := get_pyproject("tool.flet.web.renderer"):
                update_field(web_renderer_ref, "web_renderer", web_renderer)
            
            if url_strategy := get_pyproject("tool.flet.web.route_url_strategy"):
                update_field(url_strategy_ref, "url_strategy", url_strategy)
            
            if pwa_bg_color := get_pyproject("tool.flet.web.pwa_background_color"):
                update_field(pwa_bg_color_ref, "pwa_bg_color", pwa_bg_color)
            
            if pwa_theme_color := get_pyproject("tool.flet.web.pwa_theme_color"):
                update_field(pwa_theme_color_ref, "pwa_theme_color", pwa_theme_color)
            
            if enable_color_emojis := get_pyproject("tool.flet.web.use_color_emoji") is not None:
                update_field(enable_color_emojis_ref, "enable_color_emojis", get_pyproject("tool.flet.web.use_color_emoji"))
            
            # iOS specific options
            if team_id := get_pyproject("tool.flet.ios.team_id"):
                update_field(team_id_ref, "team_id", team_id)
            
            if export_method := get_pyproject("tool.flet.ios.export_method"):
                update_field(export_method_ref, "export_method", export_method)
            
            if signing_certificate := get_pyproject("tool.flet.ios.signing_certificate"):
                update_field(signing_certificate_ref, "signing_certificate", signing_certificate)
            
            if provisioning_profile := get_pyproject("tool.flet.ios.provisioning_profile"):
                update_field(provisioning_profile_ref, "provisioning_profile", provisioning_profile)
            
            if ios_info_plist := get_pyproject("tool.flet.ios.info"):
                update_field(ios_info_plist_ref, "ios_info_plist", ios_info_plist)
            
            # Deep linking configuration
            if deep_linking_scheme := get_pyproject("tool.flet.deep_linking.scheme"):
                update_field(ios_deep_linking_scheme_ref, "ios_deep_linking_scheme", deep_linking_scheme)
                update_field(android_deep_linking_scheme_ref, "android_deep_linking_scheme", deep_linking_scheme)
            
            if deep_linking_host := get_pyproject("tool.flet.deep_linking.host"):
                update_field(ios_deep_linking_host_ref, "ios_deep_linking_host", deep_linking_host)
                update_field(android_deep_linking_host_ref, "android_deep_linking_host", deep_linking_host)
            
            # Platform-specific deep linking
            if ios_deep_linking_scheme := get_pyproject("tool.flet.ios.deep_linking.scheme"):
                update_field(ios_deep_linking_scheme_ref, "ios_deep_linking_scheme", ios_deep_linking_scheme)
            
            if ios_deep_linking_host := get_pyproject("tool.flet.ios.deep_linking.host"):
                update_field(ios_deep_linking_host_ref, "ios_deep_linking_host", ios_deep_linking_host)
            
            if android_deep_linking_scheme := get_pyproject("tool.flet.android.deep_linking.scheme"):
                update_field(android_deep_linking_scheme_ref, "android_deep_linking_scheme", android_deep_linking_scheme)
            
            if android_deep_linking_host := get_pyproject("tool.flet.android.deep_linking.host"):
                update_field(android_deep_linking_host_ref, "android_deep_linking_host", android_deep_linking_host)
            
            # Android specific options
            if android_metadata := get_pyproject("tool.flet.android.meta_data"):
                update_field(android_metadata_ref, "android_metadata", android_metadata)
            
            if android_features := get_pyproject("tool.flet.android.feature"):
                update_field(android_features_ref, "android_features", android_features)
            
            if android_permissions := get_pyproject("tool.flet.android.permission"):
                update_field(android_permissions_ref, "android_permissions", android_permissions)
            
            if android_key_store := get_pyproject("tool.flet.android.signing.key_store"):
                update_field(android_key_store_ref, "android_key_store", android_key_store)
            
            if android_key_alias := get_pyproject("tool.flet.android.signing.key_alias"):
                update_field(android_key_alias_ref, "android_key_alias", android_key_alias)
            
            if split_apk_per_abi := get_pyproject("tool.flet.android.split_per_abi") is not None:
                update_field(split_apk_per_abi_ref, "split_apk_per_abi", get_pyproject("tool.flet.android.split_per_abi"))
            
            # macOS specific options
            if macos_entitlements := get_pyproject("tool.flet.macos.entitlement"):
                update_field(macos_entitlements_ref, "macos_entitlements", macos_entitlements)
            
            if macos_info_plist := get_pyproject("tool.flet.macos.info"):
                update_field(macos_info_plist_ref, "macos_info_plist", macos_info_plist)
            
            # Update the UI
            page.update()
            
            # Update the command display
            update_command_display()

        except Exception as e:
            print(f"Error reading pyproject.toml: {e}")

    def update_command_display():
        if command_display_ref.current:
            command_display_ref.current.value = form_state.get_build_command()
            page.update()

    def connect_field(field_ref, state_property):
        """Connect a field to FormState property"""
        def on_field_change(e):
            form_state.update(state_property, field_ref.current.value)
        
        return on_field_change

    def on_page_pubsub(message):
        if message.get("type") == "toast":
            toast_message = message.get("message", "")
            toast_type = message.get("toast_type", "default")
            duration = message.get("duration", 3)
            toast_id = message.get("toast_id", None)
            
            # Show the toast
            toaster.show_toast(
                text=toast_message,
                toast_type=toast_type,
                duration=duration,
                toast_id=toast_id
            )
        elif message.get("type") == "remove_toast":
            toast_id = message.get("toast_id")
            if toast_id:
                toaster.remove_toast_by_id(toast_id)
    
    page.pubsub.subscribe(on_page_pubsub)

    form_state.update("verbose_build", True)
    update_command_display()

    # MARK: ui #
    header = ft.Container(
        FactoryHeader(),
        margin=ft.margin.only(left=5, right=10, top=10),
    )
    platforms_row = PlatformsRow(
        [Platform.WINDOWS, Platform.MACOS, Platform.LINUX, Platform.ANDROID_APK, Platform.ANDROID_AAP, Platform.IOS, Platform.WEB], 
        on_change=lambda platform: (form_state.update("selected_platform", platform), update_command_display()),
    )
    
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
                hint_text="Identifier used as an internal version number (as int)",
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
                        FactoryCheckBox(label="Disable web splash screen", ref=disable_web_splash_ref, on_change=connect_field(disable_web_splash_ref, "disable_web_splash_screen")),
                        FactoryCheckBox(label="Disable iOS splash screen", ref=disable_ios_splash_ref, on_change=connect_field(disable_ios_splash_ref, "disable_ios_splash_screen")),
                        FactoryCheckBox(label="Disable Android splash screen", ref=disable_android_splash_ref, on_change=connect_field(disable_android_splash_ref, "disable_android_splash_screen")),
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
                    on_change=connect_field(exclude_files_ref, "exclude_additional_files"),
                )
            ),
            FactoryField(
                title="",
                hint_text="",
                widget=ft.Column(
                    controls=[
                        FactoryCheckBox(label="Compile app's .py files to .pyc", ref=compile_app_py_ref, on_change=connect_field(compile_app_py_ref, "compile_app_py_files")),
                        FactoryCheckBox(label="Compile site packages' .py files to .pyc", ref=compile_site_packages_ref, on_change=connect_field(compile_site_packages_ref, "compile_site_packages_py_files")),
                        FactoryCheckBox(label="Remove unnecessary app files", ref=remove_app_files_ref, on_change=connect_field(remove_app_files_ref, "remove_unnecessary_app_files")),
                        FactoryCheckBox(label="Remove unnecessary package files", ref=remove_package_files_ref, on_change=connect_field(remove_package_files_ref, "remove_unnecessary_package_files")),
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
                    enable_filter=True,
                    ref=url_strategy_ref,
                    on_change=connect_field(url_strategy_ref, "route_url_strategy"),
                )
            ),
            FactoryField(
                title="PWA Background color",
                hint_text="Initial background color for your web application",
                widget=FactoryTextField(
                    hint_text="e.g. #5b21b6",
                    ref=pwa_bg_color_ref,
                    on_change=connect_field(pwa_bg_color_ref, "pwa_background_color"),
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
                        FactoryCheckBox(label="Location", ref=location_permission_ref, on_change=connect_field(location_permission_ref, "permission_location")),
                        FactoryCheckBox(label="Camera", ref=camera_permission_ref, on_change=connect_field(camera_permission_ref, "permission_camera")),
                        FactoryCheckBox(label="Microphone", ref=microphone_permission_ref, on_change=connect_field(microphone_permission_ref, "permission_microphone")),
                        FactoryCheckBox(label="Photo Library", ref=photo_library_permission_ref, on_change=connect_field(photo_library_permission_ref, "permission_photo_library")),
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
