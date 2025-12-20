#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Build script to create the Calibre plugin ZIP file.

Usage:
    python build.py

This creates 'BionicReading.zip' which can be installed in Calibre via:
    Preferences -> Plugins -> Load plugin from file
    
Or via command line:
    calibre-customize -a BionicReading.zip
"""

import os
import zipfile

PLUGIN_NAME = 'BionicReading'
PLUGIN_FILES = [
    '__init__.py',
    'ui.py',
    'main.py',
    'config.py',
    'plugin-import-name-bionic_reading.txt',
]

# Optional files
OPTIONAL_FILES = [
    'images/icon.png',
]


def build_plugin():
    """Build the plugin ZIP file"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    zip_path = os.path.join(script_dir, f'{PLUGIN_NAME}.zip')
    
    print(f'Building {PLUGIN_NAME} plugin...')
    print(f'Output: {zip_path}')
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for filename in PLUGIN_FILES:
            filepath = os.path.join(script_dir, filename)
            if os.path.exists(filepath):
                zf.write(filepath, filename)
                print(f'  Added: {filename}')
            else:
                print(f'  WARNING: Missing required file: {filename}')
        
        for filename in OPTIONAL_FILES:
            filepath = os.path.join(script_dir, filename)
            if os.path.exists(filepath):
                zf.write(filepath, filename)
                print(f'  Added: {filename}')
            else:
                print(f'  Skipped optional: {filename}')
    
    print(f'\nPlugin built successfully!')
    print(f'\nTo install in Calibre:')
    print(f'  1. Open Calibre')
    print(f'  2. Go to Preferences -> Plugins')
    print(f'  3. Click "Load plugin from file"')
    print(f'  4. Select: {zip_path}')
    print(f'  5. Restart Calibre')
    print(f'\nOr via command line:')
    print(f'  calibre-customize -a "{zip_path}"')


if __name__ == '__main__':
    build_plugin()

