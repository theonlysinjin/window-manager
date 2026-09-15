# Packaging

Bundle inputs for `make app`.

| File | Purpose |
|---|---|
| `main.py` | Bundle entry point. py2app runs it as `__main__`, so it only calls `main()`. |
| `icon.py` | Draws the app icon and the status bar glyph. |
| `com.theonlysinjin.windowmanager.plist` | launchd agent. `make install-agent` copies it. |

## Artwork

`icon.py` draws both files with Quartz. There is no binary source file to edit — change the
constants at the top of the script and run it again.

```bash
make icon      # or: .venv/bin/python packaging/icon.py
```

| Output | Used by |
|---|---|
| `WindowManager.icns` | The app bundle. Generated, so git ignores it. |
| `../window_manager/resources/statusbar.pdf` | The status bar item. Vector and committed. |

Both drawings share one layout: a left pane beside two stacked right panes.

- The **app icon** fills the panes in white on a blue gradient plate.
- The **status bar glyph** strokes a frame and two dividers. Filled panes merge into a black
  block at 18 pt, so the glyph outlines them instead.

The glyph is a template image. macOS recolours it for a light or dark menu bar, so it holds
no colour of its own.
