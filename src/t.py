"""
Enhanced Color Picker for Flet applications based on design reference
"""
from typing import Tuple, List, Dict, Callable, Optional, Union, Any
import flet as ft

# Constants
SLIDER_WIDTH = 15
CIRCLE_SIZE = 15
DEFAULT_WIDTH = 100
DEFAULT_HEIGHT = 175
SWATCH_SIZE = 30
GRID_COLUMNS = 4
GRID_ROWS = 2

class ColorUtils:
    """
    Utility class providing color conversion and manipulation methods.
    All methods are static and can be used independently.
    """
    
    @staticmethod
    def rgb_to_hex(rgb_color: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex color string."""
        return "#{:02x}{:02x}{:02x}".format(rgb_color[0], rgb_color[1], rgb_color[2])

    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color string to RGB tuple."""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    @staticmethod
    def rgb_to_hsl(r: int, g: int, b: int) -> Tuple[int, int, int]:
        """
        Convert RGB to HSL.
        
        Args:
            r: Red (0-255)
            g: Green (0-255)
            b: Blue (0-255)
            
        Returns:
            Tuple of (Hue [0-360], Saturation [0-100], Lightness [0-100])
        """
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        delta = max_c - min_c
        l = (max_c + min_c) / 2

        if delta == 0:
            h = 0
            s = 0
        else:
            s = delta / (1 - abs(2 * l - 1)) if l != 0 and l != 1 else 0
            if max_c == r:
                h = 60 * (((g - b) / delta) % 6)
            elif max_c == g:
                h = 60 * (((b - r) / delta) + 2)
            else:  # max_c == b
                h = 60 * (((r - g) / delta) + 4)

        return round(h), round(s * 100), round(l * 100)

    @staticmethod
    def hex_to_hsl(hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to HSL values."""
        r, g, b = ColorUtils.hex_to_rgb(hex_color)
        return ColorUtils.rgb_to_hsl(r, g, b)

    @staticmethod
    def rgb_to_hsv(r: int, g: int, b: int) -> Tuple[int, int, int]:
        """
        Convert RGB to HSV.
        
        Args:
            r: Red (0-255)
            g: Green (0-255)
            b: Blue (0-255)
            
        Returns:
            Tuple of (Hue [0-360], Saturation [0-100], Value [0-100])
        """
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        delta = max_c - min_c

        if delta == 0:
            h = 0
        elif max_c == r:
            h = (60 * ((g - b) / delta) + 360) % 360
        elif max_c == g:
            h = (60 * ((b - r) / delta) + 120) % 360
        else:  # max_c == b
            h = (60 * ((r - g) / delta) + 240) % 360

        s = delta / max_c if max_c != 0 else 0
        v = max_c

        return round(h), round(s * 100), round(v * 100)

    @staticmethod
    def hex_to_hsv(hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to HSV values."""
        r, g, b = ColorUtils.hex_to_rgb(hex_color)
        return ColorUtils.rgb_to_hsv(r, g, b)

    @staticmethod
    def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
        """
        Convert HSV to RGB.
        
        Args:
            h: Hue (0-1 or 0-360)
            s: Saturation (0-1)
            v: Value (0-1)
            
        Returns:
            Tuple of (Red [0-255], Green [0-255], Blue [0-255])
        """
        # Normalize h to 0-1 range if it's in degrees
        if h > 1:
            h = h / 360.0

        if s == 0:
            r = g = b = int(v * 255)
            return (r, g, b)

        h *= 6  # sector 0 to 5
        i = int(h)
        f = h - i  # fractional part of h
        p = int(255 * v * (1 - s))
        q = int(255 * v * (1 - s * f))
        t = int(255 * v * (1 - s * (1 - f)))
        v = int(255 * v)

        if i == 0:
            r, g, b = v, t, p
        elif i == 1:
            r, g, b = q, v, p
        elif i == 2:
            r, g, b = p, v, t
        elif i == 3:
            r, g, b = p, q, v
        elif i == 4:
            r, g, b = t, p, v
        else:  # i == 5
            r, g, b = v, p, q

        return (r, g, b)

    @staticmethod
    def hsl_to_rgb(h: float, s: float, l: float) -> Tuple[int, int, int]:
        """
        Convert HSL to RGB.
        
        Args:
            h: Hue (0-360)
            s: Saturation (0-100)
            l: Lightness (0-100)
            
        Returns:
            Tuple of (Red [0-255], Green [0-255], Blue [0-255])
        """
        # Normalize values
        h = h / 360.0
        s = s / 100.0
        l = l / 100.0
        
        if s == 0:
            r = g = b = int(l * 255)
            return (r, g, b)
            
        def hue_to_rgb(p, q, t):
            if t < 0:
                t += 1
            if t > 1:
                t -= 1
            if t < 1/6:
                return p + (q - p) * 6 * t
            if t < 1/2:
                return q
            if t < 2/3:
                return p + (q - p) * (2/3 - t) * 6
            return p
            
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        
        r = int(hue_to_rgb(p, q, h + 1/3) * 255)
        g = int(hue_to_rgb(p, q, h) * 255)
        b = int(hue_to_rgb(p, q, h - 1/3) * 255)
        
        return (r, g, b)

    @staticmethod
    def mix_colors(color1: Tuple[int, int, int], color2: Tuple[int, int, int], ratio: float) -> List[int]:
        """
        Mix two RGB colors with the specified ratio.
        
        Args:
            color1: First RGB color
            color2: Second RGB color
            ratio: Mixing ratio (0-1), where 0 is 100% color1 and 1 is 100% color2
            
        Returns:
            Mixed RGB color
        """
        return [
            int(color1[0] + (color2[0] - color1[0]) * ratio),
            int(color1[1] + (color2[1] - color1[1]) * ratio),
            int(color1[2] + (color2[2] - color1[2]) * ratio),
        ]


class HueSlider(ft.GestureDetector):
    """
    A custom slider for selecting hue values.
    
    This is a vertical slider showing the color spectrum that allows users
    to select a hue value between 0 and 1.
    """
    
    def __init__(self, on_change_hue: Callable[[], None], hue: float = 0, height: int = 250):
        """
        Initialize a new HueSlider.
        
        Args:
            on_change_hue: Callback function to call when hue value changes
            hue: Initial hue value (0-1)
            height: Height of the slider
        """
        super().__init__()
        self.__hue = self._normalize_hue(hue)
        self.__number_of_hues = 12  # Increased for smoother gradient
        self.__height = height
        self.content = ft.Stack(width=SLIDER_WIDTH, height=height)
        self.generate_slider()
        self.on_change_hue = on_change_hue
        self.on_pan_start = self.drag_start
        self.on_pan_update = self.drag_update
        self.on_tap = self.on_slider_tap

    def _normalize_hue(self, hue: float) -> float:
        """Convert hue from degrees (0-360) to fraction (0-1) if needed."""
        if hue > 1:
            return (hue % 360) / 360
        return max(0, min(hue, 1))

    @property
    def hue(self) -> float:
        """Get the current hue value (0-1)."""
        return self.__hue

    @hue.setter
    def hue(self, value: float):
        """Set the hue value (0-1)."""
        if not isinstance(value, (int, float)):
            raise TypeError("Hue value should be a number")
        self.__hue = self._normalize_hue(value)

    def _before_build_command(self):
        super()._before_build_command()
        # Called every time on self.update()
        self.thumb.top = self.__hue * (self.track.height - CIRCLE_SIZE)
        self.thumb.bgcolor = ColorUtils.rgb_to_hex(
            ColorUtils.hsv_to_rgb(self.__hue, 1, 1)
        )

    def __update_selected_hue(self, y: float):
        """Update the hue based on the y position."""
        normalized_y = max(0, min(y, self.track.height))
        self.__hue = normalized_y / self.track.height
        self.thumb.top = self.__hue * (self.track.height - CIRCLE_SIZE)
        self.thumb.bgcolor = ColorUtils.rgb_to_hex(
            ColorUtils.hsv_to_rgb(self.__hue, 1, 1)
        )

    def update_selected_hue(self, y: float):
        """Update the hue and call the change callback."""
        self.__update_selected_hue(y)
        self.thumb.update()
        self.on_change_hue()

    def drag_start(self, e: ft.DragStartEvent):
        """Handle the start of a drag event."""
        self.update_selected_hue(y=e.local_y)

    def drag_update(self, e: ft.DragUpdateEvent):
        """Handle drag update events."""
        self.update_selected_hue(y=e.local_y)
        
    def on_slider_tap(self, e: ft.TapEvent):
        """Handle tap events on the slider."""
        self.update_selected_hue(y=e.local_y)

    def generate_gradient_colors(self) -> List[str]:
        """Generate a list of colors for the gradient."""
        colors = []
        for i in range(0, self.__number_of_hues + 1):
            color = ColorUtils.rgb_to_hex(
                ColorUtils.hsv_to_rgb(i / self.__number_of_hues, 1, 1)
            )
            colors.append(color)
        return colors

    def generate_slider(self):
        """Create the slider UI components."""
        self.track = ft.Container(
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=self.generate_gradient_colors(),
            ),
            width=SLIDER_WIDTH - CIRCLE_SIZE/2,
            height=self.__height,
            border_radius=ft.border_radius.all(10),
            left=CIRCLE_SIZE/4,
        )

        self.thumb = ft.Container(
            width=CIRCLE_SIZE,
            height=CIRCLE_SIZE,
            border_radius=CIRCLE_SIZE,
            border=ft.border.all(width=2, color="white"),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=2,
                color=ft.colors.with_opacity(0.5, ft.colors.BLACK),
                offset=ft.Offset(0, 1),
            ),
            left=0,
        )

        self.content.controls.append(self.track)
        self.content.controls.append(self.thumb)


class ColorPicker(ft.Container):
    """
    A comprehensive color picker component for Flet applications.
    
    Features:
    - 2x6 color palette grid
    - Color selection from a 2D gradient
    - Hue selection with a vertical slider
    - RGB input fields
    - "Get Color" button
    """
    
    def __init__(
        self,
        color: str = "#ff0000",
        on_color_select: Optional[Callable[[Dict[str, Any]], None]] = None,
        width: int = DEFAULT_WIDTH,
        height: int = DEFAULT_HEIGHT,
        **kwargs
    ):
        """
        Initialize a new ColorPicker.
        
        Args:
            color: Initial color in hex format (#RRGGBB)
            on_color_select: Callback function when a color is selected
            width: Width of the color picker
            height: Height of the color picker
            **kwargs: Additional keyword arguments for the Container
        """
        self.picker_color = color
        self._on_color_select = on_color_select
        self._width = width
        self._height = height
        
        # UI references
        self.button_ref = ft.Ref[ft.TextButton]()
        self.color_display_ref = ft.Ref[ft.Container]()
        self.r_field_ref = ft.Ref[ft.TextField]()
        self.g_field_ref = ft.Ref[ft.TextField]()
        self.b_field_ref = ft.Ref[ft.TextField]()
        
        # Predefined colors for the palette grid
        self.predefined_colors = [
            "#ffffff", "#ffff00", "#0000ff", "#ff9933", "#66ff66", "#ff3300",
            "#000000", "#666666", "#dd5555", "#cc66cc", "#6699cc", "#ff66cc"
        ]
        
        # Initialize hue slider with proper conversion
        h, s, v = ColorUtils.hex_to_hsv(self.picker_color)
        self.hue_slider = HueSlider(
            on_change_hue=self.update_picker_color,
            hue=h / 360.0,  # Convert from degrees to 0-1 range
            height=height
        )
        
        self.button_visibility = False
        self.selected_color = {
            "hex": self.picker_color,
            "rgb": ColorUtils.hex_to_rgb(self.picker_color),
            "hsl": ColorUtils.hex_to_hsl(self.picker_color),
        }
        
        # Build the UI
        content = self._build_ui()
        
        # Initialize the container with the built UI
        super().__init__(
            content=content,
            bgcolor="#252a31",
            border_radius=10,
            padding=10,
            width=self._width + 100,  # Add space for the button
            **kwargs
        )
        
        # Register for the did_mount event
        # self.did_mount_callback = self._did_mount

    def _build_color_palette(self):
        """Build the color palette grid."""
        color_grid = ft.GridView(
            runs_count=GRID_ROWS,
            max_extent=SWATCH_SIZE,
            child_aspect_ratio=1.0,
            spacing=5,
            run_spacing=5,
        )
        
        for color in self.predefined_colors:
            color_grid.controls.append(
                ft.Container(
                    bgcolor=color,
                    border_radius=5,
                    on_click=lambda e, c=color: self.on_palette_color_selected(c),
                )
            )
            
        return color_grid

    def _build_ui(self):
        """Build the color picker UI."""
        # Cursor for the color selection
        self.cursor = ft.TextButton(
            ref=self.button_ref,
            content=ft.Container(),
            style=ft.ButtonStyle(
                bgcolor=ft.colors.BLACK,
                shape=ft.CircleBorder(),
                side=ft.border.BorderSide(width=3, color=ft.colors.WHITE),
                elevation=3,
                padding=0,
            ),
            visible=self.button_visibility,
            on_click=self.on_button_click,
            left=0,
            top=0,
        )

        # Vertical gradient (brightness)
        self.vertical_gradient_container = ft.Container(
            width=self._width,
            height=self._height,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=["transparent", "#000000"],
                stops=[0.0, 1.0],
            ),
        )

        # Horizontal gradient (saturation)
        self.horizontal_gradient_container = ft.Container(
            gradient=ft.LinearGradient(
                begin=ft.alignment.center_left,
                end=ft.alignment.center_right,
                colors=["#ffffff", self.picker_color],
                stops=[0.0, 1.0],
            ),
            width=self._width,
            height=self._height,
            border_radius=ft.border_radius.all(5),
        )

        # Stack for the color selection area
        stack = ft.Stack(
            controls=[
                self.horizontal_gradient_container,
                self.vertical_gradient_container,
                self.cursor,
            ],
            width=self._width,
            height=self._height,
        )

        # Add gesture detection
        color_picker_selector = ft.GestureDetector(
            mouse_cursor=ft.MouseCursor.CLICK,
            on_hover=self.on_hover,
            on_exit=self.on_exit,
            on_tap=self.on_tap,
            content=stack,
        )
        
        # Build RGB input fields
        rgb_fields = ft.Row(
            controls=[
                ft.Text("R:", color="#999999", size=16),
                ft.Container(
                    ft.TextField(
                        ref=self.r_field_ref,
                        value="255",
                        border_color="#3d424d",
                        text_align=ft.TextAlign.CENTER,
                        width=70,
                        height=40,
                        on_submit=self.on_rgb_submit,
                        text_size=16,
                        content_padding=5,
                    ),
                    padding=ft.padding.only(right=10),
                ),
                ft.Text("G:", color="#999999", size=16),
                ft.Container(
                    ft.TextField(
                        ref=self.g_field_ref,
                        value="255",
                        border_color="#3d424d",
                        text_align=ft.TextAlign.CENTER,
                        width=70,
                        height=40,
                        on_submit=self.on_rgb_submit,
                        text_size=16,
                        content_padding=5,
                    ),
                    padding=ft.padding.only(right=10),
                ),
                ft.Text("B:", color="#999999", size=16),
                ft.TextField(
                    ref=self.b_field_ref,
                    value="255",
                    border_color="#3d424d",
                    text_align=ft.TextAlign.CENTER,
                    width=70,
                    height=40,
                    on_submit=self.on_rgb_submit,
                    text_size=16,
                    content_padding=5,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        
        # Get Color button
        get_color_button = ft.Container(
            content=ft.Text("Get\nColor", size=18, text_align=ft.TextAlign.CENTER),
            width=80,
            height=80,
            bgcolor="#252a31",
            border_radius=5,
            alignment=ft.alignment.center,
            on_click=self.on_get_color_click,
        )

        # Build the main layout
        main_column = ft.Column(
            controls=[
                # Color palette grid
                self._build_color_palette(),
                
                # Main picker area with slider
                ft.Container(
                    content=ft.Row(
                        controls=[
                            color_picker_selector,
                            ft.Container(width=10),  # Spacer
                            self.hue_slider,
                            ft.Container(width=10),  # Spacer
                            get_color_button,
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    margin=ft.margin.only(top=10, bottom=10),
                ),
                
                # RGB input fields
                rgb_fields,
            ],
            spacing=10,
        )

        return main_column

    def did_mount(self, e):
        """Called when the control is added to the page."""
        # Update UI with initial color
        rgb = ColorUtils.hex_to_rgb(self.picker_color)
        if self.r_field_ref.current:
            self.r_field_ref.current.value = str(rgb[0])
        if self.g_field_ref.current:
            self.g_field_ref.current.value = str(rgb[1])
        if self.b_field_ref.current:
            self.b_field_ref.current.value = str(rgb[2])
        self.update()

    def on_hover(self, e: ft.HoverEvent):
        """Handle hover events on the color picker."""
        button = self.button_ref.current
        # Adjust button position accounting for its size
        button.left = e.local_x - 10
        button.top = e.local_y - 10
        
        # Calculate and set the color
        calculated_color = self.calculate_color(e.local_x, e.local_y)
        button.style.bgcolor = calculated_color
        button.visible = True
        
        # Update the RGB display
        self.update_rgb_display(calculated_color)
        self.update()

    def on_exit(self, e: ft.HoverEvent):
        """Handle mouse exit events."""
        self.button_ref.current.visible = False
        self.update()
    
    def on_tap(self, e: ft.TapEvent):
        """Handle tap events on the color picker."""
        # Simulate a button click
        button = self.button_ref.current
        button.left = e.local_x - 10
        button.top = e.local_y - 10
        calculated_color = self.calculate_color(e.local_x, e.local_y)
        button.style.bgcolor = calculated_color
        button.visible = True
        self.update()
        
        # Call the button click handler
        self.on_button_click(e)

    def on_button_click(self, e):
        """Handle button click events."""
        hex_color = self.button_ref.current.style.bgcolor
        self.update_rgb_display(hex_color)
        
        # Update the selected color information
        self.selected_color = {
            "hex": hex_color,
            "rgb": ColorUtils.hex_to_rgb(hex_color),
            "hsl": ColorUtils.hex_to_hsl(hex_color),
        }
        self.picker_color = hex_color

    def on_palette_color_selected(self, color):
        """Handle color selection from the palette."""
        self.picker_color = color
        rgb = ColorUtils.hex_to_rgb(color)
        
        # Update RGB fields
        if self.r_field_ref.current:
            self.r_field_ref.current.value = str(rgb[0])
        if self.g_field_ref.current:
            self.g_field_ref.current.value = str(rgb[1])
        if self.b_field_ref.current:
            self.b_field_ref.current.value = str(rgb[2])
            
        # Update the hue slider
        h, s, v = ColorUtils.hex_to_hsv(color)
        self.hue_slider.hue = h / 360.0
        
        # Update the color gradient
        self.horizontal_gradient_container.gradient.colors = ["#ffffff", color]
        
        # Update the selected color
        self.selected_color = {
            "hex": color,
            "rgb": rgb,
            "hsl": ColorUtils.hex_to_hsl(color),
        }
        
        self.update()

    def on_rgb_submit(self, e):
        """Handle RGB input field submissions."""
        try:
            r = int(self.r_field_ref.current.value)
            g = int(self.g_field_ref.current.value)
            b = int(self.b_field_ref.current.value)
            
            # Validate RGB values
            r = max(0, min(r, 255))
            g = max(0, min(g, 255))
            b = max(0, min(b, 255))
            
            # Update the fields with validated values
            self.r_field_ref.current.value = str(r)
            self.g_field_ref.current.value = str(g)
            self.b_field_ref.current.value = str(b)
            
            # Set the color
            hex_color = ColorUtils.rgb_to_hex((r, g, b))
            self.picker_color = hex_color
            
            # Update the hue slider
            h, s, v = ColorUtils.rgb_to_hsv(r, g, b)
            self.hue_slider.hue = h / 360.0
            
            # Update the color gradient
            self.horizontal_gradient_container.gradient.colors = ["#ffffff", hex_color]
            
            # Update the selected color
            self.selected_color = {
                "hex": hex_color,
                "rgb": (r, g, b),
                "hsl": ColorUtils.rgb_to_hsl(r, g, b),
            }
            
            self.update()
            
        except ValueError:
            # Revert to the current color on error
            rgb = ColorUtils.hex_to_rgb(self.picker_color)
            self.r_field_ref.current.value = str(rgb[0])
            self.g_field_ref.current.value = str(rgb[1])
            self.b_field_ref.current.value = str(rgb[2])
            self.update()

    def on_get_color_click(self, e):
        """Handle the Get Color button click."""
        if self._on_color_select:
            self._on_color_select(self.selected_color)

    def update_rgb_display(self, hex_color: str):
        """Update RGB input fields with the selected color."""
        rgb = ColorUtils.hex_to_rgb(hex_color)
        if self.r_field_ref.current:
            self.r_field_ref.current.value = str(rgb[0])
        if self.g_field_ref.current:
            self.g_field_ref.current.value = str(rgb[1])
        if self.b_field_ref.current:
            self.b_field_ref.current.value = str(rgb[2])

    def calculate_color(self, x: float, y: float) -> str:
        """
        Calculate the color at the given position in the color picker.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Hex color string
        """
        # Calculate the horizontal gradient color (saturation)
        horizontal_ratio = min(max(x / self._width, 0), 1)
        start_color = ColorUtils.hex_to_rgb("#ffffff")
        end_color = ColorUtils.hsv_to_rgb(self.hue_slider.hue, 1, 1)
        horizontal_color = ColorUtils.mix_colors(
            start_color, end_color, horizontal_ratio
        )

        # Calculate the vertical gradient color (brightness)
        vertical_ratio = min(max(y / self._height, 0), 1)
        black_color = ColorUtils.hex_to_rgb("#000000")
        vertical_color = ColorUtils.mix_colors(
            horizontal_color, black_color, vertical_ratio
        )

        return ColorUtils.rgb_to_hex(vertical_color)

    def update_picker_color(self):
        """Update the picker color based on the hue slider value."""
        h = self.hue_slider.hue
        rgb = ColorUtils.hsv_to_rgb(h, 1, 1)
        self.picker_color = ColorUtils.rgb_to_hex(rgb)
        
        # Update the gradient
        self.horizontal_gradient_container.gradient.colors = ["#ffffff", self.picker_color]
        self.update()


def main(page: ft.Page):
    """
    Example usage of the ColorPicker.
    
    Args:
        page: The Flet page
    """
    page.title = "Flet Color Picker Demo"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#1f1f1f"
    
    # Define callback function for color selection
    def on_color_select(color_info):
        result_text.value = f"Selected color: {color_info['hex']}"
        rgb = color_info['rgb']
        result_rgb.value = f"RGB: ({rgb[0]}, {rgb[1]}, {rgb[2]})"
        color_preview.bgcolor = color_info['hex']
        page.update()
    
    # Create the color picker
    color_picker = ColorPicker(
        color="#ff0000",
        on_color_select=on_color_select,
        width=300,
        height=300,
    )
    
    # Result display
    result_text = ft.Text("Select a color...", size=16, color="#ffffff")
    result_rgb = ft.Text("RGB: (255, 0, 0)", size=14, color="#cccccc")
    color_preview = ft.Container(
        width=80,
        height=80,
        bgcolor="#ff0000",
        border_radius=10,
        margin=10,
        border=ft.border.all(1, "#3d424d"),
    )
    
    # Layout
    page.add(
        ft.Container(
            ft.Column([
                ft.Text("Color Picker Demo", size=24, weight=ft.FontWeight.BOLD, color="#ffffff"),
                ft.Container(height=10),  # Spacer
                color_picker,
                ft.Container(height=20),  # Spacer
                ft.Row([color_preview, 
                       ft.Column([result_text, result_rgb])
                      ], 
                      alignment=ft.MainAxisAlignment.START
                ),
            ]),
            padding=20
        )
    )


if __name__ == "__main__":
    ft.app(target=main)