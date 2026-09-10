VENV := .venv
PY   := $(VENV)/bin/python
LABEL := com.theonlysinjin.windowmanager
PLIST := $(HOME)/Library/LaunchAgents/$(LABEL).plist

.PHONY: venv test run check app install-agent uninstall-agent clean

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

app:
	$(PY) -m pip install -q py2app
	$(PY) setup_app.py py2app

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
