import flet as ft
from os import environ
import shlex

from utils.utils import Platform
from ui.layouts.waterfall_layout import WaterfallView
from ui.components.widgets import FactoryHeader, PlatformsRow, IconsManager
from ui.components.form import FormState
from ui.components.toast import Toaster, ToastType, ToastPosition
from ui.views.sidebar import FactorySidebar
from config.settings_manager import SettingsManager

from ui.views.card_factory import CardFactory
from core.field_registry import FieldRegistry
from core.field_definitions import (
    get_building_fields, get_app_info_fields, get_versioning_fields,
    get_appearance_fields, get_package_options_fields, get_web_specific_fields,
    get_ios_specific_fields, get_android_specific_fields, get_macos_specific_fields,
    get_permissions_fields
)
from core.pyproject_service import PyProjectService
from config.pyproject_autosave import AutoSaveManager

environ["FLET_CLI_NO_RICH_OUTPUT"] = "1"

def main(page: ft.Page):
    page.title = "Flet Factory"
    page.on_error = lambda e: print(e.data)
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
    
    settings_manager = SettingsManager()
    settings_manager.set_page(page)
    
    form_state = FormState()
    field_registry = FieldRegistry(form_state)
    pyproject_service = PyProjectService()
    
    command_display_ref = ft.Ref[ft.Text]()
    
    def update_command_display():
        if command_display_ref.current:
            command_display_ref.current.value = shlex.join(form_state.get_build_command())
            page.update()
    
    form_state.on_change = update_command_display
    
    register_all_fields(field_registry)
    
    def populate_form_from_pyproject(e):
        python_app_path_ref = field_registry.get_ref("python_app_path")
        if not python_app_path_ref or not python_app_path_ref.current:
            return
            
        project_dir = python_app_path_ref.current.value
        if not project_dir:
            return
            
        get_pyproject = pyproject_service.load_from_path(project_dir)
        if get_pyproject:
            pyproject_service.populate_form_state(get_pyproject, form_state, field_registry)
            page.update()
            update_command_display()
    
    python_app_path_def = field_registry.field_definitions.get("python_app_path")
    if python_app_path_def:
        python_app_path_def.on_blur = populate_form_from_pyproject

    def get_project_path():
        python_app_path_ref = field_registry.get_ref("python_app_path")
        if python_app_path_ref and python_app_path_ref.current:
            return python_app_path_ref.current.value
        return None

    icons_manager = IconsManager(get_project_path)
    auto_save_manager = AutoSaveManager(form_state, get_project_path, settings_manager)
    toaster = Toaster(page, position=settings_manager.get("toast_position", "bottom-right"), theme="light")
    
    for field_name in ["icon", "icon_ios", "icon_android", "icon_web", "icon_macos", "icon_windows"]:
        ref = field_registry.get_ref(field_name)
        if ref and ref.current:
            icons_manager.register_icon_picker(field_name, ref.current)

    def update_toast_position(position_value):
        if toaster:
            toaster.position = position_value.lower()
            page.update()
    
    def update_verbose_build_ui(verbose_level):
        form_state.update("verbose_build", verbose_level > 0)
        form_state.update("verbose_build_level", verbose_level)
        update_command_display()
    
    def on_message_sent(message):
        if message.get("type") == "toast":
            toaster.show_toast(
                text=message.get("message", ""),
                toast_type=message.get("toast_type", "default"),
                duration=message.get("duration", 3),
                toast_id=message.get("toast_id", None)
            )

        elif message.get("type") == "remove_toast":
            toast_id = message.get("toast_id")
            if toast_id:
                toaster.remove_toast_by_id(toast_id)

        elif message.get("type") == "settings_changed":
            key = message.get("key")
            value = message.get("value")

            match key:
                case "toast_position":
                    update_toast_position(value)
                case "verbose_build":
                    update_verbose_build_ui(value)
                case "auto_save":
                    auto_save_manager.update_from_settings()
                
            page.update()
    
    page.pubsub.subscribe(on_message_sent)
    
    verbose_level = settings_manager.get("verbose_build", 1)
    form_state.update("verbose_build", verbose_level > 0)
    form_state.update("verbose_build_level", verbose_level)
    update_command_display()
    
    header = ft.Container(
        FactoryHeader(settings_manager=settings_manager),
        margin=ft.margin.only(left=5, right=10, top=10),
    )
    
    platforms_row = PlatformsRow(
        [Platform.WINDOWS, Platform.MACOS, Platform.LINUX, Platform.ANDROID_APK, Platform.ANDROID_AAP, Platform.IOS, Platform.WEB], 
        on_change=lambda platform: (form_state.update("selected_platform", platform), update_command_display()),
    )
    
    building_fields = [f.name for f in get_building_fields()]
    building_card = CardFactory.create_card("Building configuration", building_fields, field_registry)
    
    app_info_fields = [f.name for f in get_app_info_fields()]
    app_info_card = CardFactory.create_card("App informations", app_info_fields, field_registry)
    
    versioning_fields = [f.name for f in get_versioning_fields()]
    versioning_card = CardFactory.create_card("Versioning", versioning_fields, field_registry)
    
    appearance_fields = [f.name for f in get_appearance_fields()]
    appearance_card = CardFactory.create_card("Appearance", appearance_fields, field_registry)
    
    package_options_fields = [f.name for f in get_package_options_fields()]
    package_options_card = CardFactory.create_card("Package options", package_options_fields, field_registry)
    
    web_specific_fields = [f.name for f in get_web_specific_fields()]
    web_specific_card = CardFactory.create_card("Web specific options", web_specific_fields, field_registry)
    
    ios_specific_fields = [f.name for f in get_ios_specific_fields()]
    ios_specific_card = CardFactory.create_card("iOS specific options", ios_specific_fields, field_registry)
    
    android_specific_fields = [f.name for f in get_android_specific_fields()]
    android_specific_card = CardFactory.create_card("Android specific options", android_specific_fields, field_registry)
    
    macos_specific_fields = [f.name for f in get_macos_specific_fields()]
    macos_specific_card = CardFactory.create_card("macOS specific options", macos_specific_fields, field_registry)
    
    permissions_fields = [f.name for f in get_permissions_fields()]
    permissions_card = CardFactory.create_card("Permissions", permissions_fields, field_registry)
    
    main_content = ft.Container(
        content=ft.Column(
            controls=[
                header, 
                ft.Container(height=10),
                platforms_row,
                ft.Container(height=10),
                WaterfallView(
                    cross_axis_count=2,
                    main_axis_spacing=10,
                    cross_axis_spacing=10,
                    width=page.window.width - 290,
                    controls=[
                        building_card,
                        app_info_card,
                        versioning_card,
                        appearance_card,
                        package_options_card,
                        permissions_card,
                        macos_specific_card,
                        web_specific_card,
                        ios_specific_card,
                        android_specific_card,
                    ],
                )
            ],
            scroll=ft.ScrollMode.HIDDEN,
            spacing=0,
            height=page.window.height,
            width=page.window.width - 290,
        ),
        padding=20,
    )
    
    page.add(
        ft.Row(
            controls=[
                FactorySidebar(
                    command_ref=command_display_ref,
                    auto_save_manager=auto_save_manager,
                    icons_manager=icons_manager,  # Add this
                ),
                main_content,
            ],
            spacing=0,
            height=page.window.height,
            width=page.window.width,
        )
    )

def register_all_fields(registry: FieldRegistry):
    fields = []
    fields.extend(get_building_fields())
    fields.extend(get_app_info_fields())
    fields.extend(get_versioning_fields())
    fields.extend(get_appearance_fields())
    fields.extend(get_package_options_fields())
    fields.extend(get_web_specific_fields())
    fields.extend(get_ios_specific_fields())
    fields.extend(get_android_specific_fields())
    fields.extend(get_macos_specific_fields())
    fields.extend(get_permissions_fields())
    
    for field_def in fields:
        registry.register_field(field_def)

ft.app(main, assets_dir="assets")