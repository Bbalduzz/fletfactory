from enum import Enum
import platform

colors_map = {
    "primary": "#5b21b6",
    "secondary": "#ede9fe",
    "text_accent": "#ffffff",
    "text_secondary": "#000000",
    "border_normal": "#eceef1"
}


class Platform(Enum):
    WINDOWS = ("Windows", "windows")
    MACOS = ("macOS", "macos")
    LINUX = ("Linux", "linux")
    ANDROID_AAP = ("Android (AAP)", "aab")
    ANDROID_APK = ("Android (APK)", "apk")
    IOS = ("iOS", "ipa")
    WEB = ("Web", "web")
    
    def __init__(self, display_value, cmd_value):
        self.display_value = display_value
        self.cmd_value = cmd_value
    
    @property
    def value(self): 
        # default value, cmd_value is used only to build the cli command
        return self.display_value


current_os = platform.system().lower()
buildable_platforms_map = {
    "windows": [Platform.WINDOWS, Platform.ANDROID_APK, Platform.ANDROID_AAP, Platform.LINUX, Platform.WEB],
    "darwin": [Platform.MACOS, Platform.ANDROID_APK, Platform.ANDROID_AAP, Platform.IOS, Platform.WEB],
    "linux": [Platform.LINUX, Platform.ANDROID_APK, Platform.ANDROID_AAP, Platform.WEB],
}
# get the buildable platforms for the current os
buildable_platforms = buildable_platforms_map.get(current_os, [])