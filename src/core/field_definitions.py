from .field_registry import FieldDefinition

def get_building_fields():
    return [
        FieldDefinition(
            name="python_app_path",
            property_name="python_app_path",
            title="Python App Path",
            hint_text="Path to a directory with the flet project",
            hint_widget="My project",
            widget_type="text"
        ),
        FieldDefinition(
            name="output_directory",
            property_name="output_directory",
            title="Output directory",
            hint_text="Where to put resulting executable or bundle",
            hint_widget="Default: <python_app_directory>/build/<target_platform>",
            widget_type="text"
        ),
        FieldDefinition(
            name="module_path",
            property_name="app_path",
            title="Module path",
            hint_text="Path to a directory with the flet project",
            hint_widget="e.g. src",
            widget_type="text"
        ),
        FieldDefinition(
            name="module_name",
            property_name="module_name",
            title="Module name",
            hint_text="Python module name with an app entry point",
            hint_widget="e.g main",
            widget_type="text"
        ),
        FieldDefinition(
            name="architecture",
            property_name="arch",
            title="Architecture",
            hint_text="package for specific architectures only. Used with Android and macOS builds only.",
            widget_type="dropdown",
            options=[
                {"key": "arm64", "text": "arm64"},
                {"key": "x86_64", "text": "x86_64"}
            ]
        ),
        FieldDefinition(
            name="flutter_args",
            property_name="flutter_args",
            title="Flutter args",
            hint_text="Additional arguments for flutter build command",
            hint_widget="e.g --no-tree-shake-icons",
            widget_type="badges"
        ),
        FieldDefinition(
            name="clear_build_cache",
            property_name="clear_build_cache",
            title="Clear build cache",
            widget_type="checkbox"
        )
    ]

def get_app_info_fields():
    return [
        FieldDefinition(
            name="project_name",
            property_name="project_name",
            title="Project name",
            hint_text="Project name for executable or bundle",
            hint_widget="e.g my_flet_app",
            widget_type="text"
        ),
        FieldDefinition(
            name="product_name",
            property_name="product_name",
            title="Product name",
            hint_text="Display name shown in window titles and about dialogs",
            hint_widget="e.g My Flet App",
            widget_type="text"
        ),
        FieldDefinition(
            name="description",
            property_name="description",
            title="Description",
            hint_text="The description to use for executable or bundle",
            hint_widget="A short description of your app",
            widget_type="text"
        ),
        FieldDefinition(
            name="organization",
            property_name="organization",
            title="Organization",
            hint_text="Org name in reverse domain name notation",
            hint_widget="e.g com.mycompany",
            widget_type="text"
        ),
        FieldDefinition(
            name="author",
            property_name="author",
            title="Author",
            hint_text="Author information for the project",
            hint_widget="e.g. John Doe (john@example.com)",
            widget_type="author_info",
        )
    ]

def get_versioning_fields():
    return [
        FieldDefinition(
            name="build_number",
            property_name="build_number",
            title="Build number",
            hint_text="Identifier used as an internal version number (as int)",
            hint_widget="0",
            widget_type="text"
        ),
        FieldDefinition(
            name="build_version",
            property_name="build_version",
            title="Build version",
            hint_text='A "x.y.z" string shown to users',
            hint_widget="1.0.0",
            widget_type="text"
        )
    ]

def get_appearance_fields():
    return [
        FieldDefinition(
            name="splash_screen_color",
            property_name="splash_screen_color",
            title="Splash Screen Color",
            hint_text="Background color of splash screen",
            hint_widget="e.g. #5b21b6",
            widget_type="text"
        ),
        FieldDefinition(
            name="splash_screen_dark_color",
            property_name="splash_screen_dark_color",
            title="Splash Screen Dark Color",
            hint_text="Background color in dark mode",
            hint_widget="e.g. #1e1b4b",
            widget_type="text"
        ),
        FieldDefinition(
            name="disable_web_splash",
            property_name="disable_web_splash_screen",
            title="Disable web splash screen",
            widget_type="checkbox"
        ),
        FieldDefinition(
            name="disable_ios_splash",
            property_name="disable_ios_splash_screen",
            title="Disable iOS splash screen",
            widget_type="checkbox"
        ),
        FieldDefinition(
            name="disable_android_splash",
            property_name="disable_android_splash_screen",
            title="Disable Android splash screen",
            widget_type="checkbox"
        ),
        FieldDefinition(
            name="app_icon",
            property_name="app_icon",
            title="App Icon",
            hint_text="Icon for all platforms (png, jpg, webp)",
            widget_type="icon"
        ),
    ]

def get_package_options_fields():
    return [
        FieldDefinition(
            name="dependencies",
            property_name="dependencies",
            title="Dependencies",
            hint_text="Add python dependencies",
            hint_widget="e.g. flet",
            widget_type="badges"
        ),
        FieldDefinition(
            name="include_controls",
            property_name="include_optional_controls",
            title="Include Optional Controls",
            hint_text="Add Flutter packages with optional Flet controls",
            hint_widget="e.g. flet_video",
            widget_type="badges"
        ),
        FieldDefinition(
            name="exclude_files",
            property_name="exclude_additional_files",
            title="Exclude Additional Files",
            hint_text="Exclude files and directories from Python app package",
            hint_widget="e.g. __pycache__/",
            widget_type="badges"
        ),
        FieldDefinition(
            name="template_config",
            property_name="template_config",
            title="Template",
            hint_text="Configure custom template for Flutter project generation",
            widget_type="template_config"
        ),
        FieldDefinition(
            name="compile_app_py",
            property_name="compile_app_py_files",
            title="Compile app's .py files to .pyc",
            widget_type="checkbox"
        ),
        FieldDefinition(
            name="compile_site_packages",
            property_name="compile_site_packages_py_files",
            title="Compile site packages' .py files to .pyc",
            widget_type="checkbox"
        ),
        FieldDefinition(
            name="remove_app_files",
            property_name="remove_unnecessary_app_files",
            title="Remove unnecessary app files",
            widget_type="checkbox"
        ),
        FieldDefinition(
            name="remove_package_files",
            property_name="remove_unnecessary_package_files",
            title="Remove unnecessary package files",
            widget_type="checkbox"
        )
    ]

def get_web_specific_fields():
    return [
        FieldDefinition(
            name="base_url",
            property_name="base_url",
            title="Base URL",
            hint_text="Base URL for the app",
            hint_widget="e.g. /myapp",
            widget_type="text"
        ),
        FieldDefinition(
            name="web_renderer",
            property_name="web_renderer",
            title="Web Renderer",
            hint_text="Renderer to use",
            widget_type="dropdown",
            options=[
                {"key": "canvaskit", "text": "CanvasKit"},
                {"key": "html", "text": "HTML"}
            ]
        ),
        FieldDefinition(
            name="url_strategy",
            property_name="route_url_strategy",
            title="Route URL Strategy",
            hint_text="URL routing strategy",
            widget_type="dropdown",
            options=[
                {"key": "path", "text": "Path"},
                {"key": "hash", "text": "Hash"}
            ]
        ),
        FieldDefinition(
            name="pwa_bg_color",
            property_name="pwa_background_color",
            title="PWA Background color",
            hint_text="Initial background color for your web application",
            hint_widget="e.g. #5b21b6",
            widget_type="text"
        ),
        FieldDefinition(
            name="pwa_theme_color",
            property_name="pwa_theme_color",
            title="PWA Theme color",
            hint_text="Default color for your web application's user interface",
            hint_widget="e.g. #000000",
            widget_type="text"
        ),
        FieldDefinition(
            name="enable_color_emojis",
            property_name="enable_color_emojis",
            title="Enable color emojis with CanvasKit",
            widget_type="checkbox"
        )
    ]

def get_ios_specific_fields():
    return [
        FieldDefinition(
            name="team_id",
            property_name="team_id",
            title="Team ID",
            hint_text="Team ID to sign iOS bundle (10 characters)",
            hint_widget="e.g. e.g. A1B2C3D4E5",
            widget_type="text"
        ),
        FieldDefinition(
            name="export_method",
            property_name="export_method",
            title="Export Method",
            hint_text="Export method for iOS app",
            widget_type="dropdown",
            options=[
                {"key": "debugging", "text": "Debugging"},
                {"key": "release-testing", "text": "Release-Testing"},
                {"key": "app-store-connect", "text": "App Store"},
                {"key": "enterprise", "text": "Enterprise"}
            ]
        ),
        FieldDefinition(
            name="signing_certificate",
            property_name="signing_certificate",
            title="Signing Certificate",
            hint_text="Certificate name, SHA-1 hash, or automatic selector to use for signing iOS app bundle",
            hint_widget="e.g. Apple Distribution",
            widget_type="text"
        ),
        FieldDefinition(
            name="provisioning_profile",
            property_name="provisioning_profile",
            title="Provisioning Profile",
            hint_text="Provisioning profile name or UUID that used to sign and export iOS app",
            hint_widget="e.g. <export-method> com.mycompamy.myapp",
            widget_type="text"
        ),
        FieldDefinition(
            name="ios_info_plist",
            property_name="ios_info_plist",
            title="Info plist",
            hint_text='the list of "<key>=<value>|True|False" pairs to add to Info.plist',
            hint_widget="e.g. <key>=<value>",
            widget_type="badges"
        ),
        FieldDefinition(
            name="ios_deep_linking_scheme",
            property_name="ios_deep_linking_scheme",
            title="Deep Linking Scheme",
            hint_text="Deep linking URL scheme to configure for iOS and Android builds",
            hint_widget='e.g. "https" or "myapp"',
            widget_type="text"
        ),
        FieldDefinition(
            name="ios_deep_linking_host",
            property_name="ios_deep_linking_host",
            title="Deep Linking Host",
            hint_text="Deep linking URL host for iOS and Android builds",
            widget_type="text"
        )
    ]

def get_android_specific_fields():
    return [
        FieldDefinition(
            name="android_metadata",
            property_name="android_metadata",
            title="Android metadata",
            hint_text='the list of "<name>=<value>" app meta-data entries to add to AndroidManifest.xml',
            hint_widget="e.g. <name>=<value>",
            widget_type="badges"
        ),
        FieldDefinition(
            name="android_features",
            property_name="android_features",
            title="Android features",
            hint_text='the list of "<feature_name>=True|False" features to add to AndroidManifest.xml',
            hint_widget="e.g. <name>=<value>",
            widget_type="badges"
        ),
        FieldDefinition(
            name="android_permissions",
            property_name="android_permissions",
            title="Android Permissions",
            hint_text='the list of "<uses-permission android:name=\'...\'/>" permissions to add to AndroidManifest.xml',
            hint_widget="e.g. <uses-permission android:name='...'/>",
            widget_type="badges"
        ),
        FieldDefinition(
            name="android_key_store",
            property_name="android_key_store",
            title="Android Signing Key Store",
            hint_text="Path to an upload keystore .jks file",
            hint_widget="e.g. /path/to/keystore.jks",
            widget_type="text"
        ),
        FieldDefinition(
            name="android_key_store_password",
            property_name="android_key_store_password",
            title="Android Signing Key Store Password",
            hint_text="Android signing key store password",
            hint_widget="e.g. mypassword",
            widget_type="text"
        ),
        FieldDefinition(
            name="android_key_password",
            property_name="android_key_password",
            title="Android Signing Key Password",
            hint_text="Android signing key password",
            hint_widget="e.g. myalias",
            widget_type="text"
        ),
        FieldDefinition(
            name="android_key_alias",
            property_name="android_key_alias",
            title="Android Signing Key Alias",
            hint_text='Android signing key alias. Default is "upload"',
            hint_widget="e.g. upload",
            widget_type="text"
        ),
        FieldDefinition(
            name="android_deep_linking_scheme",
            property_name="android_deep_linking_scheme",
            title="Deep Linking Scheme",
            hint_text="Deep linking URL scheme to configure for iOS and Android builds",
            hint_widget='e.g. "https" or "myapp"',
            widget_type="text"
        ),
        FieldDefinition(
            name="android_deep_linking_host",
            property_name="android_deep_linking_host",
            title="Deep Linking Host",
            hint_text="Deep linking URL host for iOS and Android builds",
            widget_type="text"
        ),
        FieldDefinition(
            name="split_apk_per_abi",
            property_name="split_apk_per_abi",
            title="Split APK per ABIs",
            widget_type="checkbox"
        )
    ]

def get_macos_specific_fields():
    return [
        FieldDefinition(
            name="macos_entitlements",
            property_name="macos_entitlements",
            title="Entitlements",
            hint_text='the list of "<key>=<value>|True|False" entitlements for macOS builds',
            hint_widget="e.g. <key>=<value>",
            widget_type="badges"
        ),
        FieldDefinition(
            name="macos_info_plist",
            property_name="macos_info_plist",
            title="Info plist",
            hint_text='the list of "<key>=<value>|True|False" pairs to add to Info.plist',
            hint_widget="e.g. <key>=<value>",
            widget_type="badges"
        )
    ]

def get_permissions_fields():
    return [
        FieldDefinition(
            name="location_permission",
            property_name="permission_location",
            title="Location",
            widget_type="checkbox"
        ),
        FieldDefinition(
            name="camera_permission",
            property_name="permission_camera",
            title="Camera",
            widget_type="checkbox"
        ),
        FieldDefinition(
            name="microphone_permission",
            property_name="permission_microphone",
            title="Microphone",
            widget_type="checkbox"
        ),
        FieldDefinition(
            name="photo_library_permission",
            property_name="permission_photo_library",
            title="Photo Library",
            widget_type="checkbox"
        )
    ]