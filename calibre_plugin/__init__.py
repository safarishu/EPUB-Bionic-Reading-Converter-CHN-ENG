#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bionic Reading Plugin for Calibre
Converts EPUB books to bionic reading format by bolding the first portion of each word.
"""

from calibre.customize import InterfaceActionBase

PLUGIN_NAME = 'Bionic Reading'
PLUGIN_VERSION = (1, 0, 1)
PLUGIN_AUTHORS = 'dobrosketchkun'
PLUGIN_DESCRIPTION = 'Convert EPUB books to Bionic Reading format for faster reading'


class BionicReadingPlugin(InterfaceActionBase):
    """
    Main plugin class that provides metadata and configuration.
    The actual UI implementation is in ui.py (specified in actual_plugin).
    """
    
    name = PLUGIN_NAME
    description = PLUGIN_DESCRIPTION
    supported_platforms = ['windows', 'osx', 'linux']
    author = PLUGIN_AUTHORS
    version = PLUGIN_VERSION
    minimum_calibre_version = (5, 0, 0)
    
    # Points to the actual UI plugin class
    actual_plugin = 'calibre_plugins.bionic_reading.ui:BionicReadingUI'
    
    def is_customizable(self):
        """Enable configuration via Preferences -> Plugins"""
        return True
    
    def config_widget(self):
        """Return the configuration widget"""
        from calibre_plugins.bionic_reading.config import ConfigWidget
        return ConfigWidget()
    
    def save_settings(self, config_widget):
        """Save the settings from the configuration widget"""
        config_widget.save_settings()
        
        # Apply settings to running instance if UI is active
        ac = self.actual_plugin_
        if ac is not None:
            ac.apply_settings()


def get_prefs():
    """Get plugin preferences with defaults"""
    from calibre.utils.config import JSONConfig
    
    prefs = JSONConfig('plugins/bionic_reading')
    
    # Set defaults
    prefs.defaults['boldness_ratio'] = 50  # Percentage of word to bold (25-75)
    prefs.defaults['min_word_length'] = 1  # Minimum word length to process
    prefs.defaults['skip_short_words'] = False  # Skip 1-2 letter words entirely
    
    return prefs
