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
    WINDOWS = "Windows"
    MACOS = "macOS"
    LINUX = "Linux"
    ANDROID_AAP = "Android (AAP)"
    ANDROID_APK = "Android (APK)"
    IOS = "iOS"
    WEB = "Web"


current_os = platform.system().lower()
buildable_platforms_map = {
    "windows": [Platform.WINDOWS, Platform.ANDROID_APK, Platform.ANDROID_AAP, Platform.LINUX, Platform.WEB],
    "darwin": [Platform.MACOS, Platform.ANDROID_APK, Platform.ANDROID_AAP, Platform.IOS, Platform.LINUX, Platform.WEB],
    "linux": [Platform.LINUX, Platform.ANDROID_APK, Platform.ANDROID_AAP, Platform.WEB],
}
# get the buildable platforms for the current os
buildable_platforms = buildable_platforms_map.get(current_os, [])