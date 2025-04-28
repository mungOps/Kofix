from setuptools import setup

APP = ['main.py']  # Your main entry point script
DATA_FILES = [('resources', ['resources/kofix.png', 'resources/icon.png', 'resources/icon.icns'])]  # 리소스를 포함시킬 경로 설정
OPTIONS = {
    'argv_emulation': False,  # argv_emulation을 False로 설정
    'packages': ['rumps', 'PyQt5', 'watchdog'],
    'includes': ['file_operations', 'ui', 'jaraco.text'],
    'iconfile': 'resources/kofix.png',  # .icns 파일을 아이콘으로 설정
    'strip': True,  # Strip unnecessary symbols from binaries to reduce size
    'excludes': ['PyQt5', 'PyQt5.QtCore', 'PyQt5.QtWidgets', 'PyQt5.QtGui'],  # Exclude unnecessary PyQt5 components
    'optimize': 2,  # Optimize the app for smaller size and faster runtime
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    name='Kofix',  # Specify the app name here
)
