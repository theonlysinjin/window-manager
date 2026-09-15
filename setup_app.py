"""py2app build. Produces dist/WindowManager.app with no Dock icon.

    python setup_app.py py2app
"""

from py2app.build_app import py2app as build_app
from setuptools import setup


class Build(build_app):
    """py2app rejects install_requires, which setuptools fills from pyproject.toml."""

    def finalize_options(self):
        self.distribution.install_requires = None
        super().finalize_options()


setup(
    app=["packaging/main.py"],
    name="WindowManager",
    cmdclass={"py2app": Build},
    options={
        "py2app": {
            "argv_emulation": False,
            "iconfile": "packaging/WindowManager.icns",
            "packages": ["window_manager", "yaml"],
            "plist": {
                "CFBundleName": "WindowManager",
                "CFBundleIconFile": "WindowManager.icns",
                "CFBundleIdentifier": "com.theonlysinjin.windowmanager",
                "CFBundleShortVersionString": "0.1.0",
                "LSUIElement": True,  # background agent, no Dock icon
                "NSAppleEventsUsageDescription": "Move and resize windows of other apps.",
            },
        }
    },
)
