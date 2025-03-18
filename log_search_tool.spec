# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['/Users/dee/Documents/Side/log_search_tool.py'],
    pathex=['/Users/dee/Documents/Side'],
    binaries=[],
    datas=[],  # 保持不变
    hiddenimports=['PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets', 'pyperclip'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='日志搜索工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# 移除macOS特有的BUNDLE部分
# app = BUNDLE(
#     exe,
#     name='日志搜索工具.app',
#     icon=None,
#     bundle_identifier=None,
# )