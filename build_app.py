"""Builds a standalone Windows executable for PyInvest.

Usage:
    python build_app.py

Produces dist/PyInvest.exe. Requires PyInstaller (see requirements-dev.txt).
"""
import PyInstaller.__main__

PyInstaller.__main__.run(
    [
        "main.py",
        "--name=PyInvest",
        "--windowed",
        "--onefile",
        "--clean",
        "--noconfirm",
        "--icon=assets/icon.ico",
        "--add-data=assets/icon.ico;assets",
        "--collect-all=pandas",
        "--collect-all=openpyxl",
        "--hidden-import=bs4",
        "--hidden-import=lxml",
        "--hidden-import=lxml.etree",
        "--hidden-import=html5lib",
        "--hidden-import=selenium",
        "--hidden-import=undetected_chromedriver",
    ]
)
