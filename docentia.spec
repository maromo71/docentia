# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None

if sys.platform.startswith("win"):
    app_icon = "assets/logo.ico" if os.path.exists("assets/logo.ico") else None
elif sys.platform == "darwin":
    app_icon = "assets/logo.icns" if os.path.exists("assets/logo.icns") else None
else:
    app_icon = "assets/logo.png" if os.path.exists("assets/logo.png") else None

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[("assets", "assets")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "onnxruntime",
        "pymupdf_layout",
        "pymupdf4llm",
        "tkinter",
        "matplotlib",
        "scipy",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Docentia",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=app_icon,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="Docentia",
)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="Docentia.app",
        icon=app_icon,
        bundle_identifier="io.github.maromo71.docentia",
        info_plist={
            "CFBundleDisplayName": "Docentia",
            "CFBundleShortVersionString": os.environ.get("DOCENTIA_VERSION", "1.0.0"),
            "NSHighResolutionCapable": True,
        },
    )
