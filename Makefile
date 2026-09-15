VENV := .venv
PY   := $(VENV)/bin/python
LABEL := com.theonlysinjin.windowmanager
PLIST := $(HOME)/Library/LaunchAgents/$(LABEL).plist

.PHONY: venv test run check icon app install-app install-agent uninstall-agent clean

venv:
	python3 -m venv $(VENV)
	$(PY) -m pip install -q --upgrade pip
	$(PY) -m pip install -q -r requirements.txt -r requirements-dev.txt

test:
	$(PY) -m pytest -q

run:
	$(PY) -m window_manager.app run --debug

check:
	$(PY) -m window_manager.app check

icon:
	$(PY) packaging/icon.py

app: icon
	$(PY) -m pip install -q py2app
	rm -rf build dist
	$(PY) setup_app.py py2app
	codesign --verify --deep --strict dist/WindowManager.app

install-app: app
	rm -rf /Applications/WindowManager.app
	cp -R dist/WindowManager.app /Applications/

install-agent:
	cp packaging/$(LABEL).plist $(PLIST)
	launchctl unload $(PLIST) 2>/dev/null || true
	launchctl load $(PLIST)

uninstall-agent:
	launchctl unload $(PLIST) 2>/dev/null || true
	rm -f $(PLIST)

clean:
	rm -rf build dist .pytest_cache
	find . -name __pycache__ -prune -exec rm -rf {} +
