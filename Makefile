.PHONY: all soft_clean clean

all: soft_clean project\icon\icon.ico status_enhancer.py
	pyinstaller -F -w --icon="project\icon\icon.ico" status_enhancer.py

soft_clean:
	if exist dist (rd /s /q dist)

clean: soft_clean
	if exist build (rd /s /q build)
	del /f /q status_enhancer.spec >nul 2>&1
