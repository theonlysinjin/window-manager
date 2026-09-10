"""Importing this package registers every built-in action."""

from . import keyboard, tiling  # noqa: F401
from .registry import action, get, names  # noqa: F401
