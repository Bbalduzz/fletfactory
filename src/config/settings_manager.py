import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class SettingsManager:
    """Singleton class to manage application settings"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SettingsManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the settings manager"""
        self._settings = {}
        self._default_settings = {
            "verbose_build": 1,  # 0: none, 1: -v, 2: -vv
            "toast_position": "TOP_RIGHT",
            # Add other default settings here
        }
        self._settings_file = self._get_settings_file_path()
        self._load_settings()
        self._page = None
        self._callbacks = []

    def set_page(self, page):
        """Set the page reference for updates"""
        self._page = page
    
    def _get_settings_file_path(self) -> Path:
        """Get the path to the settings file"""
        # Use user's home directory for settings
        home_dir = Path.home()
        app_dir = home_dir / ".fletfactory"
        
        # Create directory if it doesn't exist
        if not app_dir.exists():
            app_dir.mkdir(parents=True, exist_ok=True)
            
        return app_dir / "settings.json"
    
    def _load_settings(self):
        """Load settings from file"""
        # Start with default settings
        self._settings = self._default_settings.copy()
        
        # Try to load from file
        if self._settings_file.exists():
            try:
                with open(self._settings_file, "r") as f:
                    loaded_settings = json.load(f)
                    # Update settings with loaded values
                    self._settings.update(loaded_settings)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading settings: {e}")
    
    def add_callback(self, callback):
        """Add a callback function to be called when settings change"""
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def remove_callback(self, callback):
        """Remove a callback function"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def save_settings(self):
        """Save current settings to file"""
        try:
            with open(self._settings_file, "w") as f:
                json.dump(self._settings, f, indent=2)
        except IOError as e:
            print(f"Error saving settings: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        return self._settings.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a setting value"""
        old_value = self._settings.get(key)
        self._settings[key] = value
        self.save_settings()
        
        # notify about settings changes
        if self._page:
            try:
                self._page.pubsub.send_all({
                    "type": "settings_changed", 
                    "key": key, 
                    "value": value, 
                    "old_value": old_value
                })
            except Exception as e:
                print(f"Error sending pubsub message: {e}")
            
        for callback in self._callbacks:
            try:
                callback(key, value)
            except Exception as e:
                print(f"Error in settings callback: {e}")
    
    def get_all(self) -> Dict[str, Any]:
        """Get all settings"""
        return self._settings.copy()
    
    def reset_to_defaults(self):
        """Reset settings to defaults"""
        self._settings = self._default_settings.copy()
        self.save_settings()