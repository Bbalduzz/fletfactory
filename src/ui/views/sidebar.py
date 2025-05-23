import flet as ft
import flet_cli.utils.processes as processes
import subprocess
import re
import json
import asyncio
import shlex
from os import environ as os_environ
from ui.components.widgets import *
from config.settings_manager import SettingsManager

class FactorySidebar(ft.Container):
    def __init__(self, version="v0.0.1", command_ref=None, auto_save_manager=None, icons_manager=None):
        super().__init__()
        self.version = version

        self.bgcolor = "#f9fafb"
        self.alignment = ft.alignment.center
        self.border = ft.border.all(1, colors_map["border_normal"])
        self.width = 250
        self.padding = 10
        
        self._flet_command_ref = command_ref
        self.auto_save_manager = auto_save_manager
        self.icons_manager = icons_manager
        self._flet_build_output_ref = ft.Ref[ft.TextField]()
        self._build_button_ref = ft.Ref[FactoryButton]()
        
        self.result_rows = {}

        self._build_sidebar()
        
    def _build_sidebar(self):
        header = ft.WindowDragArea(
            ft.Row(
                [
                    ft.Container(
                        ft.Text(
                            self.version,
                            style=ft.TextStyle(
                                size=12,
                                color=ft.Colors.BLACK12
                            )
                        ),
                    ),
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Image(
                                    src="/icons/logos/flet-logo.svg",
                                    color=ft.Colors.BLACK12,
                                    width=15,
                                    height=15,
                                ),
                                on_click=lambda e: self.page.launch_url("https://flet.dev")
                            ),
                            ft.Container(
                                content=ft.Image(
                                    src="/icons/logos/github-logo.svg",
                                    color=ft.Colors.BLACK12,
                                    width=15,
                                    height=15,
                                ),
                                on_click=lambda e: self.page.launch_url("https://github.com/Bbalduzz/fletfactory")
                            )
                        ],
                        # spacing=5
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )
        )

        # Main content area for sidebar items
        content_area = ft.Column(
            controls=[
                FactoryTextField(
                    "terminal pipeline",
                    ref=self._flet_build_output_ref,
                    text_style=ft.TextStyle(font_family="FiraCode Light", size=6),
                    content_padding=ft.padding.all(10),
                    multiline=True,
                    max_lines=20
                ),
                FactoryTextField(
                    "current command",
                    ref=self._flet_command_ref,
                    text_style=ft.TextStyle(font_family="FiraCode Retina", size=10),
                    content_padding=ft.padding.all(10),
                    multiline=True,
                    read_only=True
                ),
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
                    height=50,
                    ref=self._build_button_ref,
                    on_click=self.execute_build_command
                ),
            ],
            spacing=5,
            expand=True,
            alignment=ft.MainAxisAlignment.END,
            horizontal_alignment=ft.CrossAxisAlignment.END,
        )
        
        # Combine all elements into the sidebar
        self.content = ft.Container(
            ft.Column(
                controls=[
                    header,
                    content_area,
                    # ft.Container(height=20)
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                spacing=10,
                expand=True,
            ),
            padding=ft.padding.only(bottom=30),
        )
    
    def did_mount(self):
        """Called when the control is added to the page"""
        # Adjust height to match page height
        if self.page:
            self.height = self.page.window.height
            self.update()
        
    async def execute_build_command(self, e):
        """Handle build button click"""
        if not self._flet_command_ref.current or not self._flet_command_ref.current.value:
            # No command to execute
            self.page.pubsub.send_all({
                "type": "toast",
                "message": "No build command to execute",
                "toast_type": "error",
                "duration": 10,
            })
            return
        
        # First, save the pyproject.toml file if an auto_save_manager is provided
        saved = True
        if self.auto_save_manager:
            saved = self.auto_save_manager.save_on_build()
            if saved:
                self.page.pubsub.send_all({
                    "type": "toast",
                    "message": "Saved pyproject.toml before building",
                    "toast_type": "success",
                    "duration": 10,
                })
        
        # Copy icons to assets directory if icons_manager is provided
        if self.icons_manager:
            copied_files = self.icons_manager.copy_icons_to_assets()
            if copied_files:
                # Show toast with copied files
                self.page.pubsub.send_all({
                    "type": "toast",
                    "message": f"Copied {len(copied_files)} icon files to assets directory",
                    "toast_type": "success",
                    "duration": 10,
                })

        # Get references to UI elements
        build_button = self._build_button_ref.current
        active_btn_icon = build_button.content.controls[0]
        output_field = self._flet_build_output_ref.current
        command_field = self._flet_command_ref.current
        
        # Get the command to execute
        command = shlex.split(command_field.value)
        if not command:
            output_field.value = "No command to execute. Please select a platform and configure build options."
            output_field.update()
            self.show_toast("No command to execute", "error")
            return
        
        # Clear previous output
        output_field.value = f"Executing: {command}\n\n"
        output_field.update()
        
        # Disable the build button
        build_button.disabled = True
        build_button.content.controls[0] = ft.ProgressRing(width=12, height=12, stroke_width=1, color=colors_map["primary"])
        build_button.update()

        build_toast_id = "build_progress_toast"
        if self.page:
            self.page.pubsub.send_all({
                "type": "toast",
                "message": "Building application...",
                "toast_type": "promise",
                "duration": 0,
                "toast_id": build_toast_id
            })  # Duration 0 means it won't auto-dismiss
        
        try:
            if isinstance(command, list):
                args = command
            else:
                args = shlex.split(command)
            
            # Create and start the process
            process = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                env={
                    **os_environ, 
                    "LINES": "40",
                    "COLUMNS": "40",
                    # "CHROME_EXECUTABLE": "/Applications/Thorium.app/Contents/MacOS/Thorium"
                }
            )
            
            # Stream output to the text field
            while True:
                line_bytes = await process.stdout.readline()
                if not line_bytes:
                    break
                    
                line = line_bytes.decode('utf-8')
                output_field.value += line
                output_field.update()
            
            # Wait for process to complete
            await process.wait()

            if self.page:
                self.page.pubsub.send_all({
                    "type": "remove_toast",
                    "toast_id": build_toast_id
                })
            
            # Add final status
            if process.returncode == 0:
                output_field.value += "\n✅ Build completed successfully!"
                self.show_toast("Build completed successfully!", "success")
            else:
                output_field.value += f"\n❌ Build failed with exit code {process.returncode}"
                self.show_toast(f"Build failed with exit code {process.returncode}", "error")
            
            output_field.update()
            
        except Exception as e:
            output_field.value += f"\n❌ Error executing command: {str(e)}"
            output_field.update()
            self.show_toast(f"Error: {str(e)}", "error")
        
        finally:
            # Re-enable the build button
            build_button.disabled = False
            build_button.content.controls[0] = active_btn_icon
            build_button.update()

    def show_toast(self, message, toast_type="default", duration=3):
        """Send a toast notification via pubsub"""
        if self.page:
            self.page.pubsub.send_all({
                "type": "toast",
                "message": message,
                "toast_type": toast_type,
                "duration": duration
            })