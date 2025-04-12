import flet as ft
from typing import List
from .utils import colors_map, Platform, buildable_platforms, current_os

class FactoryButton(ft.TextButton):
    def __init__(self, content, on_click=None, **kwargs):
        super().__init__(
            content=content,
            on_click=on_click,
            **kwargs
        )
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
            # width=100
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