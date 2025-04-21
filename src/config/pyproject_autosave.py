from core.pyproject_writer import PyProjectWriter
from ui.components.form import FormState
import threading
import time

class AutoSaveManager:
    def __init__(self, form_state: FormState, project_path_getter, settings_manager):
        self.form_state = form_state
        self.project_path_getter = project_path_getter
        self.settings_manager = settings_manager
        self.save_delay_timer = None
        self.save_delay_ms = 1000  # 1 second delay
        
        # Initialize based on current setting
        self.auto_save_enabled = self.settings_manager.get("auto_save", False)
        
        # Store the original update method of FormState
        self.original_update = form_state.update
        
        # Override the update method to include auto-save
        form_state.update = self._wrap_update_method(form_state.update)
    
    def _wrap_update_method(self, original_method):
        """Wrap the original update method to add auto-save functionality"""
        def wrapped_update(field_name, value):
            # Call the original update method
            result = original_method(field_name, value)
            
            # Auto-save if enabled
            if self.auto_save_enabled:
                self._schedule_save()
                
            return result
        
        return wrapped_update
    
    def update_from_settings(self):
        """Update auto-save state from settings"""
        self.auto_save_enabled = self.settings_manager.get("auto_save", False)
    
    def _schedule_save(self):
        """Schedule a save after a delay to avoid saving too frequently"""
        # Cancel existing timer if there is one
        if self.save_delay_timer and self.save_delay_timer.is_alive():
            self.save_delay_timer.cancel()
            
        # Create a new timer
        self.save_delay_timer = threading.Timer(self.save_delay_ms / 1000, self._delayed_save)
        self.save_delay_timer.daemon = True  # Allow the thread to exit when the main program exits
        self.save_delay_timer.start()
    
    def _delayed_save(self):
        """Save the pyproject.toml file after a delay"""
        # Get the project path
        project_path = self.project_path_getter()
        if not project_path:
            print("Cannot auto-save: No project path specified")
            return
            
        # Save the pyproject.toml file
        success = PyProjectWriter.save_to_path(project_path, self.form_state)
        if success:
            print(f"Auto-saved pyproject.toml to {project_path}")
        else:
            print(f"Failed to auto-save pyproject.toml to {project_path}")
    
    def manual_save(self):
        """Manually save the pyproject.toml file immediately"""
        project_path = self.project_path_getter()
        if not project_path:
            return False
            
        return PyProjectWriter.save_to_path(project_path, self.form_state)
        
    def save_on_build(self):
        """Save before building and return whether save was successful"""
        # Always try to save when building, regardless of auto-save setting
        return self.manual_save()