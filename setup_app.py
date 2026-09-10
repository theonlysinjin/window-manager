"""py2app build. Produces dist/WindowManager.app with no Dock icon.

    python setup_app.py py2app
"""

from setuptools import setup

setup(
    app=["window_manager/app.py"],
    name="WindowManager",
    setup_requires=["py2app"],
    options={
        "py2app": {
            "argv_emulation": False,
            "packages": ["window_manager", "yaml"],
            "plist": {
                "CFBundleName": "WindowManager",
                "CFBundleIdentifier": "com.theonlysinjin.windowmanager",
                "CFBundleShortVersionString": "0.1.0",
                "LSUIElement": True,  # background agent, no Dock icon
                "NSAppleEventsUsageDescription": "Move and resize windows of other apps.",
            },
        }
    },
)
