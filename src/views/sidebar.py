import flet as ft
from components.widgets import *
import subprocess
import re
import json
import asyncio

# Flutter doctor components that are typically checked
EXPECTED_COMPONENTS = [
    "Flutter",
    "Android toolchain",
    "Xcode",
    "Chrome",
    "Android Studio",
    "VS Code",
    "Connected device",
    "Network resources"
]

async def run_flutter_doctor():
    process = await asyncio.create_subprocess_exec(
        'flutter', 'doctor', '-v',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
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
    
    await process.wait() # process to complete
    
    if process.returncode != 0:
        yield json.dumps({"Error": f"Flutter doctor exited with code {process.returncode}"})


class FactorySidebar(ft.Container):
    def __init__(self, version="v0.0.1", command_ref=None):
        super().__init__()
        self.version = version

        self.bgcolor = "#f9fafb"
        self.alignment = ft.alignment.center
        self.border = ft.border.all(1, colors_map["border_normal"])
        self.width = 250
        self.padding = 10
        
        self._flet_command_ref = command_ref
        self._flutter_results_ref = ft.Ref[ft.Column]()
        self._flutter_progress_ref = ft.Ref[ft.ProgressRing]()
        
        self.result_rows = {}

        self._build_sidebar()
        
    def _build_sidebar(self):
        header = ft.Row(
            [
                ft.Container(
                    ft.Text(
                        self.version,
                        style=ft.TextStyle(
                            size=12,
                            color=ft.Colors.BLACK12
                        )
                    ),
                    # margin=ft.margin.only(left=50),
                ),
                ft.Row([
                    ft.Image(
                        src="https://raw.githubusercontent.com/flet-dev/flet/e3f4d16d6f9412175c29e8b982146230ecc1a7d5/media/logo/flet-logo-no-text.svg",
                        color=ft.Colors.BLACK12,
                        width=16,
                        height=16,
                    ),
                    ft.Image(
                        src="https://upload.wikimedia.org/wikipedia/commons/9/91/Octicons-mark-github.svg",
                        color=ft.Colors.BLACK12,
                        width=16,
                        height=16,
                    ),
                ])
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        # Version text at the bottom
        footer = ft.Text(
            self.version,
            style=ft.TextStyle(
                size=12,
                color=ft.Colors.BLACK26
            )
        )
        
        # Flutter doctor results container
        flutter_results = ft.Column(ref=self._flutter_results_ref, spacing=5, visible=False)
        flutter_progress = ft.ProgressRing(ref=self._flutter_progress_ref, visible=False, width=16, height=16)
        
        flutter_doctor_section = ft.ExpansionTile(
            title = ft.Text("Flutter Doctor", font_family="OpenRunde Medium", size=14, color=ft.Colors.BLACK87),
            show_trailing_icon=False,
            shape = ft.ContinuousRectangleBorder(radius=6),
            controls = [
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            flutter_results,
                            padding=ft.padding.only(left=10),
                        ),
                        ft.Row([
                            FactoryButton(ft.Text("Run"), on_click=self.execute_flutter_doctor, expand=True)  
                        ], expand=True),
                    ]),
                    expand=True,
                    padding=ft.margin.all(5),
                ),
            ]
        )

        # Main content area for sidebar items
        content_area = ft.Column(
            controls=[
                flutter_doctor_section,
                FactoryTextField("terminal pipeline", multiline=True),
                FactoryTextField("current command", ref=self._flet_command_ref, multiline=True, read_only=True),
                FactoryButton(
                    ft.Row(
                        [
                            ft.Image(
                                src='<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-cuboid-icon lucide-cuboid"><path d="m21.12 6.4-6.05-4.06a2 2 0 0 0-2.17-.05L2.95 8.41a2 2 0 0 0-.95 1.7v5.82a2 2 0 0 0 .88 1.66l6.05 4.07a2 2 0 0 0 2.17.05l9.95-6.12a2 2 0 0 0 .95-1.7V8.06a2 2 0 0 0-.88-1.66Z"/><path d="M10 22v-8L2.25 9.15"/><path d="m10 14 11.77-6.87"/></svg>',
                                width=16,
                                height=16,
                                color=ft.Colors.WHITE
                            ),
                            ft.Text("Build")
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ), 
                    height=50
                ),
            ],
            spacing=5,
            expand=True,
            alignment=ft.MainAxisAlignment.END,
            horizontal_alignment=ft.CrossAxisAlignment.END,
        )
        
        # Combine all elements into the sidebar
        self.content = ft.Column(
            controls=[
                header,
                content_area,
                footer
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=10,
            expand=True,
        )
    
    def create_loading_rows(self):
        """Create initial loading rows for all expected components"""
        results_container = self._flutter_results_ref.current
        results_container.controls.clear()
        self.result_rows.clear()
        
        for component in EXPECTED_COMPONENTS:
            # Create a row with a loading indicator for each expected component
            self.result_rows[component] = ft.Row([
                ft.ProgressRing(width=10, height=10, stroke_width=1, color=colors_map["primary"]),
                ft.Text(f"{component}", size=12, opacity=0.7)
            ], spacing=5)
            results_container.controls.append(self.result_rows[component])
    
    def update_result_row(self, component, status):
        """Update a row with the result status"""
        # Create a color based on status using colors_map
        color = colors_map["primary"] if status == "PASSED" else \
                ft.Colors.GREY_300 if status == "FAILED" else \
                ft.Colors.GREY_300 if status == "WARNING" else \
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

        matching_component = component
        if component not in self.result_rows:
            for expected in self.result_rows.keys():
                if expected.lower() in component.lower() or component.lower() in expected.lower():
                    matching_component = expected
                    break
        
        # Replace the row with the updated one
        if matching_component in self.result_rows:
            # Update existing row
            self.result_rows[matching_component].controls = [
                icon,
                ft.Text(f"{display_name}", size=12, color=color)
            ]
        else:
            # Create new row for unexpected components
            new_row = ft.Row([
                icon,
                ft.Text(f"{display_name}", size=12, color=color)
            ], spacing=5)
            self._flutter_results_ref.current.controls.append(new_row)
            self.result_rows[component] = new_row
    
    async def execute_flutter_doctor(self, e):
        # Get references to UI elements
        results_container = self._flutter_results_ref.current
        progress_button = self._flutter_progress_ref.current
        
        # Make results container visible
        results_container.visible = True
        
        # Show progress indicator by changing the icon button to a progress ring
        progress_button.icon = None
        progress_button.content = ft.ProgressRing(width=12, height=12, stroke_width=1, color=colors_map["primary"])
        progress_button.disabled = True
        self.update()
        
        # Create initial loading rows
        self.create_loading_rows()
        self.update()
        
        # Run flutter doctor and update UI with results
        async for result in run_flutter_doctor():
            result_json = json.loads(result)
            for component, status in result_json.items():
                self.update_result_row(component, status)
                self.update()
        
        # Check for any remaining components that didn't get updated
        for component in list(self.result_rows.keys()):
            row = self.result_rows[component]
            # If the first control is still a ProgressRing, it means this component wasn't checked
            if isinstance(row.controls[0], ft.ProgressRing):
                self.update_result_row(component, "NOT CHECKED")
        
        # Restore the refresh icon when done
        progress_button.content = None
        progress_button.icon = ft.Icons.REFRESH
        progress_button.disabled = False
        self.update()
    
    def did_mount(self):
        """Called when the control is added to the page"""
        # Adjust height to match page height
        if self.page:
            self.height = self.page.window.height
            self.update()