#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Configuration dialog for Bionic Reading Plugin
"""

from qt.core import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, 
    QCheckBox, QSpinBox, QGroupBox, Qt
)

from calibre_plugins.bionic_reading import get_prefs


class ConfigWidget(QWidget):
    """Configuration widget for plugin settings"""
    
    def __init__(self):
        super().__init__()
        self.prefs = get_prefs()
        self._init_ui()
        self._load_settings()
    
    def _init_ui(self):
        """Initialize the configuration UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Boldness ratio group
        boldness_group = QGroupBox('Boldness Settings')
        boldness_layout = QVBoxLayout()
        boldness_group.setLayout(boldness_layout)
        
        # Boldness ratio slider
        ratio_layout = QHBoxLayout()
        ratio_layout.addWidget(QLabel('Boldness ratio:'))
        
        self.ratio_slider = QSlider(Qt.Orientation.Horizontal)
        self.ratio_slider.setMinimum(25)
        self.ratio_slider.setMaximum(75)
        self.ratio_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.ratio_slider.setTickInterval(5)
        self.ratio_slider.valueChanged.connect(self._on_ratio_changed)
        ratio_layout.addWidget(self.ratio_slider)
        
        self.ratio_label = QLabel('50%')
        self.ratio_label.setMinimumWidth(40)
        ratio_layout.addWidget(self.ratio_label)
        
        boldness_layout.addLayout(ratio_layout)
        
        # Explanation
        explanation = QLabel(
            '<i>Percentage of each word to make bold. '
            'Lower = subtler effect, Higher = more prominent.</i>'
        )
        explanation.setWordWrap(True)
        boldness_layout.addWidget(explanation)
        
        layout.addWidget(boldness_group)
        
        # Word processing group
        words_group = QGroupBox('Word Processing')
        words_layout = QVBoxLayout()
        words_group.setLayout(words_layout)
        
        # Skip short words checkbox
        self.skip_short_cb = QCheckBox('Skip very short words (1-2 letters)')
        words_layout.addWidget(self.skip_short_cb)
        
        # Minimum word length
        min_len_layout = QHBoxLayout()
        min_len_layout.addWidget(QLabel('Minimum word length to process:'))
        self.min_length_spin = QSpinBox()
        self.min_length_spin.setMinimum(1)
        self.min_length_spin.setMaximum(5)
        min_len_layout.addWidget(self.min_length_spin)
        min_len_layout.addStretch()
        words_layout.addLayout(min_len_layout)
        
        layout.addWidget(words_group)
        
        # Info section
        info_group = QGroupBox('How It Works')
        info_layout = QVBoxLayout()
        info_group.setLayout(info_layout)
        
        info_text = QLabel(
            'Bionic Reading helps your eyes glide through text by bolding the '
            'beginning of each word. This creates artificial fixation points '
            'that can improve reading speed and focus.\n\n'
            'The plugin creates a new BIONIC format alongside your original EPUB. '
            'You can switch between formats in the book details panel.'
        )
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        
        layout.addWidget(info_group)
        
        layout.addStretch()
    
    def _on_ratio_changed(self, value):
        """Update the ratio label when slider changes"""
        self.ratio_label.setText(f'{value}%')
    
    def _load_settings(self):
        """Load current settings into the UI"""
        self.ratio_slider.setValue(self.prefs['boldness_ratio'])
        self.ratio_label.setText(f"{self.prefs['boldness_ratio']}%")
        self.skip_short_cb.setChecked(self.prefs['skip_short_words'])
        self.min_length_spin.setValue(self.prefs['min_word_length'])
    
    def save_settings(self):
        """Save settings from UI to preferences"""
        self.prefs['boldness_ratio'] = self.ratio_slider.value()
        self.prefs['skip_short_words'] = self.skip_short_cb.isChecked()
        self.prefs['min_word_length'] = self.min_length_spin.value()
    
    def validate(self):
        """Validate settings (called before save)"""
        return True
