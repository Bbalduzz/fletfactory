import flet as ft
from config.settings_manager import SettingsManager
from typing import List, Union, Callable, Optional
from time import time, sleep
from utils.utils import colors_map, Platform, buildable_platforms, current_os
import asyncio, re, json, shutil, os
from .toast import ToastPosition

class FactoryButton(ft.TextButton):
    def __init__(self, content, on_click=None, **kwargs):
        super().__init__(
            content=content,
            on_click=on_click,
            **kwargs
        )
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=6),
            bgcolor={
                ft.ControlState.DEFAULT: colors_map["primary"],
                ft.ControlState.DISABLED: colors_map["secondary"],
            },
            color={
                ft.ControlState.DEFAULT: colors_map["text_accent"],
                ft.ControlState.DISABLED: colors_map["text_secondary"],
            },
            side=ft.BorderSide(
                color=colors_map["primary"],
                stroke_align=1,
                width=1,
            )
        )

class FactorySecondaryButton(ft.TextButton):
    def __init__(self, content, on_click=None, **kwargs):
        super().__init__(
            content=content,
            on_click=on_click,
            **kwargs
        )
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=6),
            bgcolor="#ffffff",
            color=colors_map["text_secondary"],
            overlay_color="#ffffff",
            side=ft.BorderSide(
                color=colors_map["border_normal"],
                stroke_align=1,
                width=1,
            )
        )

class FactoryTextField(ft.TextField):
    def __init__(self, hint_text="", value="", height=40, **kwargs):
        height_param = {} if kwargs.get("multiline", False) else {"height": height}
        default_text_style = ft.TextStyle(
            size=14,
            color=colors_map["text_secondary"],
        )
        
        # If text_style is provided in kwargs, merge it with default
        if "text_style" in kwargs:
            custom_text_style = kwargs.pop("text_style")
            # Create a dictionary from default text style
            merged_style_dict = {k: v for k, v in default_text_style.__dict__.items() if v is not None}
            # Update with custom style attributes
            merged_style_dict.update({k: v for k, v in custom_text_style.__dict__.items() if v is not None})
            # Create new TextStyle with merged attributes
            text_style = ft.TextStyle(**merged_style_dict)
        else:
            text_style = default_text_style

        content_padding = kwargs.pop("content_padding", ft.padding.symmetric(horizontal=10, vertical=5))

        super().__init__(
            cursor_color=colors_map["text_secondary"],
            border_color=colors_map["border_normal"],
            border_width=1,
            content_padding=content_padding,
            focused_border_color=colors_map["primary"],
            text_style=text_style,
            hint_text=hint_text,
            value=value,
            border_radius=6,
            **height_param,  # Apply height only if not multiline
            **kwargs
        )

    @property
    def result(self):
        return self.content.value

class FactoryCheckBox(ft.Checkbox):
    def __init__(self, label="", value=False, on_change=None, **kwargs):
        self._user_on_change = on_change
        super().__init__(
            label=label,
            value=value,
            label_style=ft.TextStyle(
                size=12,
                color=colors_map["text_secondary"],
            ),
            shape=ft.ContinuousRectangleBorder(radius=8),
            splash_radius=5.0,
            fill_color={
                ft.ControlState.HOVERED: colors_map["secondary"],
                ft.ControlState.FOCUSED: colors_map["secondary"],
                ft.ControlState.DEFAULT: "#ffffff",
            },
            border_side={
                ft.ControlState.HOVERED: ft.BorderSide(
                    color=colors_map["primary"],
                    stroke_align=1,
                    width=1,
                ),
                ft.ControlState.FOCUSED: ft.BorderSide(
                    color=colors_map["primary"],
                    stroke_align=1,
                    width=1,
                ),
                ft.ControlState.DEFAULT: ft.BorderSide(
                    color=colors_map["border_normal"],
                    stroke_align=1,
                    width=1,
                ),
            },
            check_color=colors_map["primary"],
            on_change=self._handle_change,
            **kwargs
        )

    # TODO: add on_change listener
    def _handle_change(self, e):
        """Internal handler that ensures the form state is updated"""
        if self._user_on_change:
            self._user_on_change(e)

    @property
    def result(self):
        return self.value

class FactoryRadio(ft.Radio):
    def __init__(
        self, 
        value="", 
        label="", 
        on_change=None, 
        label_position=ft.LabelPosition.RIGHT,
        adaptive=False,
        autofocus=False,
        toggleable=False,
        **kwargs
    ):
        self._user_on_change = on_change
        super().__init__(
            value=value,
            label=label,
            label_position=label_position,
            adaptive=adaptive,
            autofocus=autofocus,
            toggleable=toggleable,
            label_style=ft.TextStyle(
                size=12,
                font_family="OpenRunde Regular",
                color=colors_map["text_secondary"],
            ),
            fill_color={
                ft.ControlState.DEFAULT: colors_map["primary"],
                ft.ControlState.DISABLED: colors_map["border_normal"],
            },
            hover_color=colors_map["secondary"],
            focus_color=colors_map["secondary"],
            overlay_color={
                ft.ControlState.HOVERED: colors_map["secondary"],
                ft.ControlState.FOCUSED: colors_map["secondary"],
            },
            splash_radius=10.0,
            visual_density=ft.VisualDensity.STANDARD,
            **kwargs
        )

    @property
    def result(self):
        return self.value

class FactoryDropdownOption(ft.DropdownOption):
    def __init__(self, key, text, **kwargs):
        super().__init__(
            key=key,
            content=ft.Text(
                value=text,
                size=14,
                color=colors_map["text_secondary"],
            ),
            **kwargs
        )
class FactoryDropdown(ft.Dropdown):
    def __init__(self, options=None, value=None, hint_text="", enable_filter=False, **kwargs):
        super().__init__(
            options=options or [],
            value=value,
            hint_text=hint_text,
            border_color=colors_map["border_normal"],
            bgcolor="#f9fafb",
            text_style=ft.TextStyle(
                size=14,
                color=colors_map["text_secondary"],
            ),
            border_radius=6,
            enable_filter=enable_filter,
            **kwargs
        )

    @property
    def result(self):
        return self.value

class FactoryField(ft.Container):
    def __init__(self, title, hint_text, widget, **kwargs):
        super().__init__(**kwargs)
        self.bgcolor = "#ffffff"
        self.content_padding = ft.padding.symmetric(horizontal=10, vertical=5)
        self._title = title
        self._hint_text = hint_text
        self._widget = widget
        self.content = ft.Column(
            spacing=10,
            controls=[
                *([] if not self._title else [
                    ft.Text(
                        self._title,
                        style = ft.TextStyle(
                            font_family="OpenRunde Medium",
                            size=14,
                            color=colors_map["text_secondary"],
                        )
                    ),
                ]),
                self._widget,
                *([] if not self._hint_text else [
                    ft.Text(
                        self._hint_text,
                        style = ft.TextStyle(
                            size=10,
                            color=ft.Colors.GREY_500,
                        )
                    )
                ]),
            ]
        )

class FactoryBadge(ft.TextButton):
    def __init__(self, text, on_click=None, **kwargs):
        super().__init__(
            on_click=on_click,
            **kwargs
        )
        self.text = text
        self.style = ft.ButtonStyle(
            color=colors_map["primary"],
            bgcolor=colors_map["secondary"],
            shape=ft.RoundedRectangleBorder(radius=6),
        )
        self.content=ft.Row(
            [
                ft.Text(self.text),
                ft.Icon(ft.Icons.CLOSE, size=12, color=colors_map["primary"])
            ]
        )

class FactoryBadgeInput(ft.Container):
    def __init__(self, hint_text="", value="", badges=[], on_change=None, **kwargs):
        super().__init__(**kwargs)
        self.bgcolor = "#ffffff"
        self.border = ft.border.all(1, colors_map["border_normal"])
        self.border_radius = 6
        self.padding = 5
        self.on_change = on_change
        # Create a new list to avoid shared list issues
        self._badges = badges.copy() if badges else []
        self._text_field = FactoryTextField(
            hint_text=hint_text,
            value=value,
            on_submit=self.on_submit,
        )
        self._badges_row = ft.Row(
            spacing=5,
            controls=self._badges,
            scroll=ft.ScrollMode.HIDDEN
        )
        self.content = ft.Column(
            controls=[
                self._badges_row,
                self._text_field
            ]
        )

    def _trigger_on_change(self):
        """Trigger the on_change event with the current badge values"""
        if self.on_change:
            # Create a synthetic event with the current badge values
            e = type('obj', (object,), {
                'control': self,
                'data': self.value
            })
            self.on_change(e)

    @property
    def value(self):
        """Return the list of badge texts"""
        return [badge.text for badge in self._badges]

    @value.setter
    def value(self, new_values):
        """Set badges from a list of values"""
        # Clear existing badges
        self._badges.clear()
        
        # Add new badges
        if isinstance(new_values, list):
            for val in new_values:
                badge = FactoryBadge(text=str(val), on_click=self.remove_badge)
                self._badges.append(badge)
        
        # Update the row's controls
        self._badges_row.controls = self._badges
        self._badges_row.update()
        self.update()

    @property
    def result(self):
        return self.value

    def remove_badge(self, e):
        # Find the badge in the list and remove it
        for badge in self._badges[:]:  # Create a copy to safely iterate
            if badge == e.control:
                self._badges.remove(badge)
                # Update the row's controls directly
                self._badges_row.controls = self._badges
                print("removed badge", badge.text)
                self._badges_row.update()
                self.update()
                # Trigger on_change event
                self._trigger_on_change()
                break

    def on_submit(self, e):
        if e.data:
            # Create badge with removal function
            badge = FactoryBadge(text=e.data, on_click=self.remove_badge)
            self._badges.append(badge)
            # Update the row's controls directly
            self._badges_row.controls = self._badges
            print("added badge", e.data)
            # Clear the text field
            self._text_field.value = ""
            self._text_field.update()
            self._badges_row.update()
            self.update()
            # Trigger on_change event
            self._trigger_on_change()

class FactoryCard(ft.Container):
    def __init__(self, title: ft.Text = "Title", content: List[FactoryField] = []):
        super().__init__(
            width=400,
        )
        # self.expand=True
        self.bgcolor = "#ffffff"
        self.border = ft.border.all(1, colors_map["border_normal"])
        self.border_radius = 6
        self.padding = 20
        self._title = title
        self._content = content

        self.content = ft.Column(
            controls=[
                ft.Text(
                    self._title, 
                    style = ft.TextStyle(
                        font_family="OpenRunde Semibold",
                        size=18,
                        color=colors_map["text_secondary"],
                    )
                ),
                ft.Column(
                    spacing=20,
                    controls=self._content
                )
            ]
        )

    def did_mount(self):
        self.size = (self.width, self.height)
        

## platform section
class PlatformButton(ft.ElevatedButton):
    def __init__(self, platform: Platform, on_select=None):
        super().__init__(
            text=platform.value,
            on_click=lambda e: self._handle_click(e, on_select),
            on_hover=self._on_hover
        )
        self.platform = platform
        self.state = 0  # 0 = unselected, 1 = selected, 2 = disabled, 3 = hover
        self.width = 120
        self.height = 40

    def did_mount(self):
        self._update_style()

    def _update_style(self):
        if self.state == 0:  # unselected
            self.style = ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=6),
                bgcolor="#ffffff",
                color=colors_map["text_secondary"],
                side=ft.BorderSide(
                    color=colors_map["border_normal"],
                    stroke_align=1,
                    width=1,
                )
            )
        elif self.state == 1:  # selected
            self.style = ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=6),
                bgcolor=colors_map["primary"],
                color=colors_map["text_accent"],
                side=ft.BorderSide(
                    color=colors_map["primary"],
                    stroke_align=1,
                    width=1,
                )
            )
        elif self.state == 2:  # disabled
            self.style = ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=6),
                bgcolor="#e0e0e0",
                color="#a0a0a0",
                elevation=0
            )
        elif self.state == 3:  # hover
            self.style = ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=6),
                bgcolor=colors_map["secondary"],
                color=colors_map["text_secondary"],
                side=ft.BorderSide(
                    color=colors_map["primary"],
                    stroke_align=1,
                    width=2,
                ),
            )
        self.update()

    def _handle_click(self, e, on_select):
        print("Clicked", self.platform.value)
        if self.state != 2:  # if not disabled
            self.state = 1 if self.state == 0 else 0  # toggle between unselected and selected
            self._update_style()
            if on_select:
                on_select(self)

    def _on_hover(self, e):
        prev_state = self.state
        if e.data == "true" and self.state != 2 and self.state != 1:  # if hovering and not disabled or selected
            self.state = 3
        elif e.data == "false" and self.state == 3:  # if not hovering and was in hover state
            self.state = 0
        
        if prev_state != self.state:
            self._update_style()

    def select(self):
        self.state = 1
        self._update_style()
        
    def deselect(self):
        self.state = 0
        self._update_style()
        
    def disable(self):
        self.state = 2
        
    def enable(self):
        self.state = 0

class PlatformsRow(ft.Row):
    def __init__(self, platforms: list[Platform], on_change=None):
        super().__init__(
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
            height=60, 
            width=730,
            scroll=ft.ScrollMode.AUTO,
        )
        self._on_change_callback = on_change
        self.buttons = []
        self.selected_button = None
        
        # adding the scrollmode make the fisrt button overflow the row
        # this is a workaround
        self.controls.append(ft.Container(width=0))

        # Create a button for each platform
        for platform in platforms:
            button = PlatformButton(platform, on_select=self._handle_button_select)
            self.buttons.append(button)
            self.controls.append(button)

            if platform not in buildable_platforms:
                button.disable()
                button.tooltip = ft.Tooltip(
                    message=f"Cannot build {platform.value} app on {current_os.capitalize()}",
                    prefer_below=False,
                    
                )
        
        # same as before
        self.controls.append(ft.Container(width=0))
    
    def _handle_button_select(self, button):
        if button == self.selected_button:
            return
            
        # deselect the previously selected button
        if self.selected_button:
            self.selected_button.deselect()
            
        # select the clicked button
        self.selected_button = button
        self.selected_button.select() 

        if self._on_change_callback:
            self._on_change_callback(self.get_selected_platform())

    def get_selected_platform(self):
        """Returns the currently selected platform or None if none selected"""
        return self.selected_button.platform if self.selected_button else None

# MARK: Icon selector
class IconPicker(ft.Container):
    def __init__(
        self,
        hint_text: str = "Select icon file...",
        on_change: Optional[Callable] = None,
        ref: Optional[ft.Ref] = None
    ):
        super().__init__()
        self.hint_text = hint_text
        self.on_change = on_change
        self._value = ""
        self.ref = ref
        self.content = self._build_content()
        self.padding = 0
        self.margin = 0
        
    def _build_content(self):
        self.text_field = FactoryTextField(
            hint_text=self.hint_text,
            read_only=False,
            expand=True,
        )
        
        self.browse_button = FactoryButton(
            content=ft.Icon(ft.Icons.FOLDER_OPEN, size=12, color=ft.Colors.WHITE),
            height=40,
            width=40,
            on_click=self._pick_file
        )
        
        self.preview = ft.Container(
            content=ft.Image(
                src="/api/placeholder/48/48",
                width=33,
                height=33,
                fit=ft.ImageFit.CONTAIN,
                border_radius=6,
            ),
            visible=False,
            padding=2,
            border=ft.border.all(1, "#e2e8f0"),
            border_radius=6,
        )
        
        return ft.Row(
            controls=[
                self.preview,
                self.text_field,
                self.browse_button,
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
    
    def _pick_file(self, e):
        def on_dialog_result(e: ft.FilePickerResultEvent):
            if e.files and len(e.files) > 0:
                selected_file = e.files[0].path
                self.value = selected_file
                if self.on_change:
                    self.on_change(e)
                
        file_picker = ft.FilePicker(on_result=on_dialog_result)
        self.page.overlay.append(file_picker)
        self.page.update()
        # Only allow image files
        file_picker.pick_files(
            dialog_title=f"Select app icon file",
            allowed_extensions=["png", "jpg", "jpeg", "webp", "bmp", "gif"],
            allow_multiple=False,
        )
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        if value != self._value:
            self._value = value
            self.text_field.value = value
            
            if value:
                # Update preview
                self.preview.visible = True
                self.preview.content.src = value
            else:
                self.preview.visible = False
            
            self.update()
    
    def copy_to_assets(self, project_path, create_assets=True):
        """
        Copy the selected icon to the assets directory with all the required filenames
        
        Args:
            project_path: Path to the project directory
            create_assets: Whether to create the assets directory if it doesn't exist
            
        Returns:
            List of paths to the copied files or None if no file was copied
        """
        if not self.value:
            return None
            
        assets_dir = Path(project_path) / "assets"
        if not assets_dir.exists():
            if create_assets:
                assets_dir.mkdir(parents=True, exist_ok=True)
            else:
                return None
        
        # Get file extension
        source_path = Path(self.value)
        if not source_path.exists():
            return None
            
        ext = source_path.suffix.lower()
        
        # All icon types to create
        icon_types = ["icon", "icon_ios", "icon_android", "icon_web", "icon_macos", "icon_windows"]
        
        copied_files = []
        
        # Copy the file with each icon type name
        for icon_type in icon_types:
            dest_filename = f"{icon_type}{ext}"
            dest_path = assets_dir / dest_filename
            
            # Copy the file
            shutil.copy2(source_path, dest_path)
            copied_files.append(str(dest_path))
        
        return copied_files


class IconsManager:
    """
    Manages icon selection and copying to the assets directory
    """
    def __init__(self, project_path_getter):
        self.project_path_getter = project_path_getter
        self.icon_picker = None
    
    def set_icon_picker(self, picker):
        """Set the icon picker component"""
        self.icon_picker = picker
    
    def copy_icons_to_assets(self):
        """Copy icon to the assets directory with all needed filenames"""
        project_path = self.project_path_getter()
        if not project_path or not self.icon_picker:
            return False
            
        copied_files = self.icon_picker.copy_to_assets(project_path, create_assets=True)
        return copied_files

# MARK: Template
class MultipleFactoryTextField(ft.Container):
    def __init__(self, titles: list[str], descriptions: list[str], hint_texts: list[str], on_change: Optional[Callable] = None, ref: Optional[ft.Ref] = None):
        super().__init__()
        self.bgcolor = "#ffffff"
        self.border = ft.border.all(1, colors_map["border_normal"])
        self.border_radius = 6
        self.padding = 10
        self.margin = 0
        self.on_change = on_change
        self.hint_texts = hint_texts
        self.titles = titles
        self.descriptions = descriptions
        self.ref = ref
        self._values = [""] * len(hint_texts)
        self.content = self._build_content()

    def _build_content(self):
        self.text_fields = []
        fields_column = ft.Column(spacing=8, scroll = ft.ScrollMode.AUTO)
        
        for i, title in enumerate(self.titles):
            text_field = FactoryTextField(
                hint_text=self.hint_texts[i],
                read_only=False,
                expand=True,
                on_change=lambda e, idx=i: self._handle_text_change(e, idx)
            )
            self.text_fields.append(text_field)
            
            field_col = ft.Column(
                controls=[
                    ft.Text(title, size=12, color=colors_map["text_secondary"]),
                    text_field,
                    ft.Text(self.descriptions[i], size=10, color=ft.Colors.GREY_500)
                ],
                spacing=2,
            )
            
            fields_column.controls.append(field_col)
        
        return fields_column
    
    def _handle_text_change(self, e, index):
        self._values[index] = e.control.value
        if self.on_change:
            # Create a synthetic event with all values
            event = type('obj', (object,), {
                'control': self,
                'data': self.value
            })
            self.on_change(event)
    
    @property
    def value(self):
        """Return a dictionary with the values from all fields"""
        result = {}
        for i, title in enumerate(self.titles):
            key = title.lower().replace(' ', '_')
            result[key] = self._values[i]
        return result
    
    @value.setter
    def value(self, val):
        """Set values from a dictionary or list"""
        if isinstance(val, dict):
            for i, title in enumerate(self.titles):
                key = title.lower().replace(' ', '_')
                if key in val:
                    self._values[i] = val[key]
                    if i < len(self.text_fields):
                        self.text_fields[i].value = val[key]
        elif isinstance(val, list) and len(val) <= len(self.text_fields):
            for i, v in enumerate(val):
                self._values[i] = v
                self.text_fields[i].value = v
        self.update()
    
    @property
    def result(self):
        return self.value

# MARK: Author
class FactoryAuthorRow(ft.Row):
    def __init__(self, author: str = "", email: str = "", on_change: Optional[Callable] = None, ref: Optional[ft.Ref] = None):
        super().__init__(spacing=10)
        self.author = author
        self.email = email
        self.on_change = on_change
        self.ref = ref
        self.controls = self._build_content()

    def _build_content(self):
        self.author_field = FactoryTextField(
            hint_text="Author name",
            value=self.author,
            read_only=False,
            expand=True,
            on_change=self._handle_author_change
        )

        self.email_field = FactoryTextField(
            hint_text="Author email",
            value=self.email,
            read_only=False,
            expand=True,
            on_change=self._handle_email_change
        )
        
        return [self.author_field, self.email_field]
    
    def _handle_author_change(self, e):
        self.author = e.control.value
        self._trigger_on_change()
    
    def _handle_email_change(self, e):
        self.email = e.control.value
        self._trigger_on_change()
    
    def _trigger_on_change(self):
        if self.on_change:
            # Create a synthetic event with the current values
            e = type('obj', (object,), {
                'control': self,
                'data': self.value
            })
            self.on_change(e)
    
    @property
    def value(self):
        """Return the author information in the format expected by pyproject.toml"""
        if not self.author and not self.email:
            return None
        
        return {
            "name": self.author,
            "email": self.email
        }
    
    @value.setter
    def value(self, val):
        """Set values from a dictionary, string, or list"""
        if isinstance(val, dict):
            self.author = val.get("name", "")
            self.email = val.get("email", "")
        elif isinstance(val, str) and "(" in val and ")" in val:
            # Parse format like "John Doe (john@example.com)"
            parts = val.split("(")
            self.author = parts[0].strip()
            self.email = parts[1].strip().rstrip(")")
        elif isinstance(val, list) and len(val) >= 2:
            self.author = val[0]
            self.email = val[1]
        
        # Update the field values
        if hasattr(self, 'author_field'):
            self.author_field.value = self.author
            self.email_field.value = self.email
            self.update()
    
    @property
    def result(self):
        return self.value


# MARK: Settings
class FactorySettingsDialog(ft.AlertDialog):
    def __init__(self, title="Dialog Title", content=None, actions=None, settings_manager=None):
        self.settings_manager = settings_manager
        # Create references for components
        self.flutter_results_ref = ft.Ref[ft.Column]()
        self.flet_results_ref = ft.Ref[ft.Column]()
        
        self.verbose_v_ref = ft.Ref[FactoryCheckBox]()
        self.verbose_vv_ref = ft.Ref[FactoryCheckBox]()
        self.toast_position_ref = ft.Ref[ft.RadioGroup]()
        self.auto_save_ref = ft.Ref[FactoryCheckBox]()

        title_component = ft.Column(
            [
                ft.Text(
                    title,
                    size=20,
                    font_family="OpenRunde Semibold",
                    color=colors_map["text_secondary"]
                ),
                ft.Text(
                    "Customize your build experience",
                    size=12,
                    font_family="OpenRunde Regular",
                    color="#595b5d",
                )
            ],
            spacing=0,
        )
        
        # Default actions if none provided
        if actions is None:
            actions = [
                FactorySecondaryButton(
                    ft.Text("Cancel"),
                    on_click=lambda e: self.on_cancel(e),
                ),
                FactoryButton(
                    ft.Text("Save"),
                    on_click=lambda e: self.on_save(e),
                ),
            ]
        
        super().__init__(
            title=title_component,
            content=content,
            actions=actions,
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor="#ffffff",
            shape=ft.RoundedRectangleBorder(radius=6),
        )
        
        self.flutter_results = ft.Column(
            ref=self.flutter_results_ref,
            controls=[
                ft.Text("Run Flutter Doctor to see results", 
                       color=colors_map["text_secondary"],
                       size=12)
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=5,
        )

        self.flet_results = ft.Column(
            ref=self.flet_results_ref,
            controls=[
                ft.Text("Run Flet Doctor to see results",
                       color=colors_map["text_secondary"],
                       size=12)
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=5,
        )
        
        # Separate dictionaries for Flutter and Flet result rows
        self.flutter_result_rows = {}
        self.flet_result_rows = {}
        
        # Expected components for Flutter and Flet
        self.FLUTTER_EXPECTED_COMPONENTS = [
            "Flutter", "Android toolchain", "Xcode", "Chrome", 
            "Android Studio", "VS Code", "Connected device"
        ]
        
        self.FLET_EXPECTED_COMPONENTS = [
            "Flet Version", "Python Version", "Operating System"
        ]

        self._create_settings_content()

    def on_cancel(self, e):
        """Cancel button handler - revert to previous settings"""
        self.open = False
        self.update()

    def on_save(self, e):
        """Save button handler - save settings"""
        # Settings are already saved when changed, so just close the dialog
        self.open = False
        self.update()
    
    def _toggle_verbose_build(self, e):
        """Handle verbose build checkbox changes"""
        # Determine which checkbox was changed
        if e.control == self.verbose_v_ref.current:
            if e.control.value:
                # If -v is checked, uncheck -vv
                self.verbose_vv_ref.current.value = False
                self.verbose_vv_ref.current.update()
                # Set verbose level to 1
                self.settings_manager.set("verbose_build", 1)
            else:
                # If -v is unchecked, set verbose level to 0
                self.settings_manager.set("verbose_build", 0)
        elif e.control == self.verbose_vv_ref.current:
            if e.control.value:
                # If -vv is checked, uncheck -v
                self.verbose_v_ref.current.value = False
                self.verbose_v_ref.current.update()
                # Set verbose level to 2
                self.settings_manager.set("verbose_build", 2)
            else:
                # If -vv is unchecked, set verbose level to 0
                self.settings_manager.set("verbose_build", 0)
    
    def _on_toast_position_change(self, e):
        """Handle toast position radio changes"""
        self.settings_manager.set("toast_position", e.control.value)

    def _on_auto_save_change(self, e):
        """Handle auto save checkbox changes"""
        self.settings_manager.set("auto_save", e.control.value)

    def _create_settings_content(self):
        """Create the settings dialog content with controls"""
        # Get current settings
        verbose_level = self.settings_manager.get("verbose_build", 1)
        toast_position = self.settings_manager.get("toast_position", "BOTTOM_RIGHT")
        
        # Create verbose build checkboxes
        verbose_v_checkbox = FactoryCheckBox(
            ref=self.verbose_v_ref,
            value=verbose_level == 1,
            label="Show detailed build output (-v)",
            on_change=self._toggle_verbose_build
        )
        
        verbose_vv_checkbox = FactoryCheckBox(
            ref=self.verbose_vv_ref,
            value=verbose_level == 2,
            label="Show very detailed build output (-vv)",
            on_change=self._toggle_verbose_build
        )
        
        # Create toast position radio group
        toast_radio_group = ft.RadioGroup(
            ref=self.toast_position_ref,
            value=toast_position,
            on_change=self._on_toast_position_change,
            content=ft.Row(
                [
                    FactoryRadio(
                        value=position.value,
                        label=position.name.replace("_", " ").title(),
                    )
                    for position in ToastPosition
                ]
            )
        )

        autosave_checkbox = FactoryCheckBox(
            ref=self.auto_save_ref,
            value=self.settings_manager.get("auto_save", False),
            label="Automatically save changes to pyproject.toml",
            on_change=self._on_auto_save_change
        )
        
        # Flutter results
        
        # Create the content
        self.content = ft.Container(
            ft.Column(
                controls=[
                    ft.Text("Global settings", font_family="OpenRunde Regular", size=12, color="#595b5d"),
                    SettingsItemExpander(
                        header=ft.Text("Verbose Build", font_family="OpenRunde Regular", color=colors_map["text_secondary"]),
                        content=ft.Column([
                            ft.Row([verbose_v_checkbox]),
                            ft.Row([verbose_vv_checkbox]),
                        ])
                    ),
                    SettingsItemExpander(
                        header=ft.Text("Toasts Positions", font_family="OpenRunde Regular", color=colors_map["text_secondary"]),
                        content=toast_radio_group
                    ),
                    SettingsItemExpander(
                        header=ft.Text("Auto Save", font_family="OpenRunde Regular", color=colors_map["text_secondary"]),
                        content=autosave_checkbox
                    ),
                    ft.Text("Run checks", font_family="OpenRunde Regular", size=12, color="#595b5d"),
                    SettingsItemExpander(
                        "Run Flutter Doctor",
                        content=ft.Column(
                            [
                                ft.Row(
                                    controls=[
                                        ft.Text("❯ flutter doctor", font_family="FiraCode Retina", size=12, color=colors_map["text_secondary"]),
                                        FactoryButton(
                                            ft.Text("Run"),
                                            on_click=self.execute_flutter_doctor,
                                        )  
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                self.flutter_results,
                            ],
                            spacing=5
                        ),
                    ),
                    SettingsItemExpander(
                        "Run Flet Doctor",
                        content=ft.Column(
                            [
                                ft.Row(
                                    controls=[
                                        ft.Text("❯ flet doctor", font_family="FiraCode Retina", size=12, color=colors_map["text_secondary"]),
                                        FactoryButton(
                                            ft.Text("Run"),
                                            on_click=self.execute_flet_doctor,
                                        )  
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                self.flet_results,
                            ],
                            spacing=5
                        ),
                    ),
                ],
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
            ),
            margin=ft.margin.symmetric(vertical=10),
            expand=False,
            height=400
        )
    
    def create_loading_rows(self, doctor_type="flutter"):
        """Create initial loading rows for all expected components"""
        if doctor_type == "flutter":
            self.flutter_results_ref.current.controls.clear()
            self.flutter_result_rows.clear()
            expected_components = self.FLUTTER_EXPECTED_COMPONENTS
            result_rows = self.flutter_result_rows
            result_column = self.flutter_results_ref.current
        else:  # flet
            self.flet_results_ref.current.controls.clear()
            self.flet_result_rows.clear()
            expected_components = self.FLET_EXPECTED_COMPONENTS
            result_rows = self.flet_result_rows
            result_column = self.flet_results_ref.current
        
        for component in expected_components:
            # A row with a loading indicator for each expected component
            result_rows[component] = ft.Row([
                ft.ProgressRing(width=8, height=8, stroke_width=1, color=colors_map["primary"]),
                ft.Text(f"{component}", size=10, opacity=0.7)
            ], spacing=5)
            result_column.controls.append(result_rows[component])
    
    def update_result_row(self, component, status, doctor_type="flutter", version_info=""):
        """Update a row with the result status"""
        color = colors_map["primary"] if status == "PASSED" else \
                ft.Colors.AMBER if status == "WARNING" else \
                ft.Colors.RED if status == "FAILED" else \
                colors_map["text_secondary"]
                
        icon = ft.Icon(
            name=ft.Icons.CHECK_CIRCLE if status == "PASSED" else \
                ft.Icons.ERROR if status == "FAILED" else \
                ft.Icons.WARNING if status == "WARNING" else \
                ft.Icons.INFO,
            color=color,
            size=12
        )
        
        # Clean up component name - remove descriptions after dash or in parentheses
        display_name = component.split('-')[0].split('(')[0].strip()

        # Select the appropriate result rows and column
        if doctor_type == "flutter":
            result_rows = self.flutter_result_rows
            result_column = self.flutter_results_ref.current
        else:  # flet
            result_rows = self.flet_result_rows
            result_column = self.flet_results_ref.current
        
        # Find a matching component
        matching_component = component
        if component not in result_rows:
            for expected in result_rows.keys():
                if expected.lower() in component.lower() or component.lower() in expected.lower():
                    matching_component = expected
                    break
        
        # Create or update row with the status
        if matching_component in result_rows:
            result_rows[matching_component].controls = [
                icon,
                ft.Text(
                    f"{display_name}: {version_info}" if version_info else f"{display_name}", 
                    size=10, 
                    color=color
                )
            ]
        else:
            # New row for unexpected components
            new_row = ft.Row([
                icon,
                ft.Text(
                    f"{display_name}: {version_info}" if version_info else f"{display_name}", 
                    size=10, 
                    color=color
                )
            ], spacing=5)
            result_column.controls.append(new_row)
            result_rows[component] = new_row
        
    async def execute_flutter_doctor(self, e):
        """Run flutter doctor and display results"""
        self.create_loading_rows("flutter")
        self.update()
        
        # Run flutter doctor and update UI with results
        async for result_json in run_flutter_doctor():
            try:
                result = json.loads(result_json)
                # Update component statuses
                for component, status in result.items():
                    self.update_result_row(component, status, "flutter")
                    self.update()
            except json.JSONDecodeError:
                print(f"Failed to decode JSON: {result_json}")
        
        # Check for any remaining components that didn't get updated
        for component in list(self.flutter_result_rows.keys()):
            row = self.flutter_result_rows[component]
            # If the first control is still a ProgressRing, it means this component wasn't checked
            if isinstance(row.controls[0], ft.ProgressRing):
                self.update_result_row(component, "NOT CHECKED", "flutter")
                
        self.update()
    
    async def execute_flet_doctor(self, e):
        """Run flet doctor and display results"""
        self.create_loading_rows("flet")
        self.update()
        
        # Run flet doctor and update UI with results
        async for result_json in run_flet_doctor():
            try:
                result = json.loads(result_json)
                # Update component statuses
                for component, status in result.items():
                    if component != "version_info":  # Skip the version_info key
                        version_info = result.get("version_info", "")
                        self.update_result_row(component, status, "flet", version_info)
                        self.update()
            except json.JSONDecodeError:
                print(f"Failed to decode JSON: {result_json}")
        
        # Check for any remaining components that didn't get updated
        for component in list(self.flet_result_rows.keys()):
            row = self.flet_result_rows[component]
            # If the first control is still a ProgressRing, it means this component wasn't checked
            if isinstance(row.controls[0], ft.ProgressRing):
                self.update_result_row(component, "NOT CHECKED", "flet")
                
        self.update()

class SettingsItemExpander(ft.Container):
    def __init__(
        self,
        header: Union[str, ft.Control],
        content: ft.Control,
        expand: bool = False,
        width: int = 600,
        **kwargs,
    ):
        # Custom theme colors
        self.bg_color = "#ffffff"
        self.border_color = "#eceef1"
        self.text_color = "#000000"
        self.corner_radius = 8

        self._expanded = expand
        self._width = width
        self._header = (
            header
            if isinstance(header, ft.Control)
            else ft.Text(
                header,
                size=14,
                font_family="OpenRunde Regular",
                color=self.text_color,
            )
        )
        self._content = content
        # Create expand icon
        self._expand_icon = ft.IconButton(
            icon=ft.Icons.EXPAND_LESS if expand else ft.Icons.EXPAND_MORE,
            icon_size=12,
            icon_color=self.text_color,
            on_click=self._toggle
        )

        # Calculate the content height
        self._content_height = content.height if hasattr(content, "height") else None

        self._content_container = ft.Container(
            content=self._content,
            bgcolor=self.bg_color,
            border=ft.border.all(1, self.border_color),
            border_radius=ft.border_radius.only(
                bottom_left=self.corner_radius,
                bottom_right=self.corner_radius,
            ),
            padding=15,
            width=self._width,
            height=None if self._expanded else 0,
            animate=ft.animation.Animation(
                duration=300,
                curve=ft.AnimationCurve.EASE_OUT,
            ),
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )

        header_row = ft.Container(
            content=ft.Row(
                controls=[
                    self._header,
                    self._expand_icon,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            height=50,
            on_click=self._toggle,
            border_radius=ft.border_radius.only(
                top_left=self.corner_radius,
                top_right=self.corner_radius,
                bottom_left=self.corner_radius if not self._expanded else 0,
                bottom_right=self.corner_radius if not self._expanded else 0,
            ),
            padding=10,
            bgcolor=self.bg_color,
            border=ft.border.all(1, self.border_color),
            width=self._width,
            animate=ft.animation.Animation(
                duration=300,
                curve=ft.AnimationCurve.EASE_OUT,
            ),
        )

        self._header_row = header_row

        super().__init__(
            content=ft.Column(
                controls=[
                    header_row,
                    self._content_container,
                ],
                spacing=0,
                expand=True,
            ),
            expand=True,
            **kwargs,
        )

    def update_theme(self, bg_color=None, border_color=None, text_color=None):
        """Update expander theme colors"""
        # Update colors if provided
        if bg_color:
            self.bg_color = bg_color
        if border_color:
            self.border_color = border_color
        if text_color:
            self.text_color = text_color

        # Update header colors
        if isinstance(self._header, ft.Text):
            self._header.color = self.text_color

        # Update expand icon
        self._expand_icon.icon_color = self.text_color

        # Update container colors
        self._content_container.bgcolor = self.bg_color
        self._content_container.border = ft.border.all(1, self.border_color)
        self._header_row.bgcolor = self.bg_color
        self._header_row.border = ft.border.all(1, self.border_color)

        self.update()

    def _toggle(self, *_):
        self._expanded = not self._expanded

        if self._expanded:
            self._content_container.height = None
        else:
            self._content_container.height = 0

        self._expand_icon.icon = ft.Icons.EXPAND_LESS if self._expanded else ft.Icons.EXPAND_MORE

        self._header_row.border_radius = ft.border_radius.only(
            top_left=self.corner_radius,
            top_right=self.corner_radius,
            bottom_left=self.corner_radius if not self._expanded else 0,
            bottom_right=self.corner_radius if not self._expanded else 0,
        )

        self.update()

    @property
    def expanded(self) -> bool:
        return self._expanded

    @expanded.setter
    def expanded(self, value: bool):
        if self._expanded != value:
            self._expanded = value

            # Update content container height
            self._content_container.height = self._content_height if value else 0

            # Update the expand icon
            self._expand_icon.icon = ft.Icons.EXPAND_LESS if value else ft.Icons.EXPAND_MORE

            # Update header border radius
            self._header_row.border_radius = ft.border_radius.only(
                top_left=self.corner_radius,
                top_right=self.corner_radius,
                bottom_left=self.corner_radius if not value else 0,
                bottom_right=self.corner_radius if not value else 0,
            )

            self.update()

## title section
class FactoryHeader(ft.Row):
    def __init__(self, settings_manager: SettingsManager):
        super().__init__(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=10
        )
        self.settings_manager = settings_manager

        self._settings_dialog = FactorySettingsDialog(title="Settings", settings_manager=self.settings_manager)

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
            FactorySecondaryButton(
                content = ft.Image(
                    src = "/icons/settings.svg",
                    width=16,
                    height=16,
                    color=colors_map["text_secondary"],
                ),
                width=35,
                height=35,
                # on_click=self.open_settings_dialog,
            )
        ]

    def did_mount(self):
        self.controls[1].on_click = self.open_settings_dialog
    
    def open_settings_dialog(self, e):
        """Open the settings dialog when the button is clicked"""
        print("Opening settings dialog")
        self.page.open(self._settings_dialog)

    async def _execute_flutter_doctor(self, e):
        """Wrapper to call the dialog's execute_flutter_doctor method"""
        await self._settings_dialog.execute_flutter_doctor(e)

    async def _execute_flet_doctor(self, e):
        """Wrapper to call the dialog's execute_flet_doctor method"""
        await self._settings_dialog.execute_flet_doctor(e)


# Flutter doctor components that are typically checked
async def run_flutter_doctor():
    # env = os_environ.copy()

    process = await asyncio.create_subprocess_exec(
        'flutter', 'doctor', '-v',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        # env=env
    )

    # match check results
    check_pattern = re.compile(r'^\[(.)?\]\s*(.*?)(?:\s*\(.*\))?$')
    detected_components = set()
    
    while True:
        line_bytes = await process.stdout.readline()
        if not line_bytes:
            break
            
        line = line_bytes.decode('utf-8')
        if not line.strip():
            continue
            
        # check if this is a section header line
        match = check_pattern.match(line.strip())
        if match:
            status_symbol, description = match.groups()
            # determine status based on symbol
            status = "PASSED" if status_symbol == "✓" else "FAILED" if status_symbol == "✗" else "WARNING" if status_symbol == "!" else "UNKNOWN"
            component_name = description.strip()
            detected_components.add(component_name)
            result = {component_name: status}
            yield json.dumps(result)
    
    await process.wait() # wait for process to complete
    
    if process.returncode != 0:
        yield json.dumps({"Error": f"Flutter doctor exited with code {process.returncode}"})

async def run_flet_doctor():
    """Run flet doctor command and yield results line by line"""
    process = await asyncio.create_subprocess_shell(
        "flet doctor",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    # Read all output at once
    stdout_data, stderr_data = await process.communicate()
    
    if stdout_data:
        # Get the full output as a string
        full_output = stdout_data.decode().strip()
        
        # Extract the main components using regex
        flet_version_match = re.search(r'✔\s+Flet\s+Version:\s+(.*?)(?:\n|$)', full_output)
        python_version_match = re.search(r'✔\s+Python\s+Version:\s+(.*?)(?:\n✔|$)', full_output, re.DOTALL)
        os_version_match = re.search(r'✔\s+Operating\s+System:\s+(.*?)(?:\n|$)', full_output, re.DOTALL)
        
        # Yield the extracted information with PASSED status to match Flutter Doctor format
        if flet_version_match:
            result = {"Flet Version": "PASSED"}
            result["version_info"] = flet_version_match.group(1).strip()
            yield json.dumps(result)
        
        if python_version_match:
            # Clean up any line breaks in the Python version
            python_version = python_version_match.group(1).replace('\n', ' ').strip()
            result = {"Python Version": "PASSED"}
            result["version_info"] = python_version
            yield json.dumps(result)
        
        if os_version_match:
            # Clean up any line breaks in the OS version
            os_version = os_version_match.group(1).replace('\n', ' ').strip()
            result = {"Operating System": "PASSED"}
            result["version_info"] = os_version
            yield json.dumps(result)
    
    # Wait for the process to complete
    await process.wait()