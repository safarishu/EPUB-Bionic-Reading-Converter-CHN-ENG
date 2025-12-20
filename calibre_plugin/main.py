#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Core conversion logic for Bionic Reading Plugin

Handles EPUB parsing and text transformation to bionic reading format.
"""

import re
import io
import os
from zipfile import ZipFile, ZIP_DEFLATED, ZIP_STORED
from copy import deepcopy

from lxml import etree

# Unicode word pattern - matches letters in any alphabet (Latin, Cyrillic, Greek, etc.)
WORD_PATTERN = re.compile(r'[a-zA-ZÀ-ÿĀ-žА-яЁёҐґЄєІіЇїЎўẞß\u0370-\u03FF\u1F00-\u1FFF]+', re.UNICODE)

# Tags whose text content should NOT be processed
SKIP_TAGS = frozenset([
    'script', 'style', 'code', 'pre', 'kbd', 'samp', 'var',
    'math', 'svg', 'title', 'meta', 'link', 'annotation',
    'nav',
])

# File extensions to process
CONTENT_EXTENSIONS = frozenset(['.xhtml', '.html', '.htm', '.xml'])

# Files/paths to skip entirely
SKIP_PATHS = frozenset([
    'mimetype',
    'META-INF/container.xml',
    'META-INF/encryption.xml',
    'META-INF/manifest.xml',
    'META-INF/metadata.xml',
    'META-INF/rights.xml',
    'META-INF/signatures.xml',
])

# XHTML namespace
XHTML_NS = 'http://www.w3.org/1999/xhtml'


class BionicConverter:
    """Converts EPUB content to Bionic Reading format"""
    
    def __init__(self, prefs):
        """
        Initialize converter with preferences.
        
        Args:
            prefs: Plugin preferences dict with boldness_ratio, min_word_length, skip_short_words
        """
        self.boldness_ratio = prefs.get('boldness_ratio', 50) / 100.0
        self.min_word_length = prefs.get('min_word_length', 1)
        self.skip_short_words = prefs.get('skip_short_words', False)
    
    def convert(self, epub_data):
        """
        Convert EPUB data to bionic reading format.
        
        Args:
            epub_data: bytes of the EPUB file
            
        Returns:
            bytes of the converted EPUB file
        """
        input_io = io.BytesIO(epub_data)
        output_io = io.BytesIO()
        
        with ZipFile(input_io, 'r') as zip_in:
            with ZipFile(output_io, 'w', ZIP_DEFLATED) as zip_out:
                for item in zip_in.infolist():
                    # Read the file content
                    content = zip_in.read(item.filename)
                    
                    # Check if this is a file we should process
                    if self._should_process(item.filename):
                        try:
                            content = self._process_xhtml(content)
                        except Exception as e:
                            # If processing fails, keep original content
                            pass
                    
                    # Handle mimetype specially - must be first and uncompressed
                    if item.filename == 'mimetype':
                        zip_out.writestr(item, content, compress_type=ZIP_STORED)
                    else:
                        zip_out.writestr(item, content)
        
        return output_io.getvalue()
    
    def _should_process(self, filename):
        """Check if a file should be processed for bionic conversion"""
        # Skip known special files
        if filename in SKIP_PATHS:
            return False
        
        # Skip META-INF directory
        if filename.startswith('META-INF/'):
            return False
        
        # Skip OPF files
        if filename.endswith('.opf'):
            return False
        
        # Skip NCX files (EPUB2 navigation)
        if filename.endswith('.ncx'):
            return False
        
        # Only process content files
        _, ext = os.path.splitext(filename.lower())
        return ext in CONTENT_EXTENSIONS
    
    def _process_xhtml(self, content):
        """
        Process XHTML content to add bionic reading formatting.
        
        Args:
            content: bytes of XHTML content
            
        Returns:
            bytes of processed XHTML content
        """
        # Parse the XHTML
        parser = etree.XMLParser(recover=True, remove_blank_text=False)
        tree = etree.parse(io.BytesIO(content), parser)
        root = tree.getroot()
        
        # Determine the namespace
        nsmap = root.nsmap
        default_ns = nsmap.get(None, '')
        
        # Process all text nodes
        self._process_element(root, default_ns)
        
        # Serialize back to bytes, preserving XML declaration
        output = etree.tostring(
            tree,
            encoding='utf-8',
            xml_declaration=True,
            pretty_print=False
        )
        
        return output
    
    def _process_element(self, element, default_ns):
        """
        Recursively process an element and its children.
        
        Args:
            element: lxml Element to process
            default_ns: default namespace URI
        """
        # Get local tag name (without namespace)
        if not isinstance(element.tag, str):
            return  # Skip comments, processing instructions, etc.
            
        tag = etree.QName(element.tag).localname
        
        # Skip elements that shouldn't be processed
        if tag.lower() in SKIP_TAGS:
            return
        
        # Process text content of this element
        if element.text:
            self._process_text_node(element, 'text', default_ns)
        
        # Process child elements
        for child in element:
            self._process_element(child, default_ns)
            
            # Process tail text (text after child element)
            if child.tail:
                self._process_text_node(child, 'tail', default_ns)
    
    def _process_text_node(self, element, attr, default_ns):
        """
        Process a text node (either element.text or element.tail) and replace
        it with bionic formatted content including <b> elements.
        
        Args:
            element: The element containing the text
            attr: 'text' or 'tail' indicating which attribute to process
            default_ns: default namespace URI for creating new elements
        """
        text = getattr(element, attr)
        if not text or not text.strip():
            return
        
        # Find all words and their positions
        parts = []
        last_end = 0
        
        for match in WORD_PATTERN.finditer(text):
            # Add any text before this word
            if match.start() > last_end:
                parts.append(('text', text[last_end:match.start()]))
            
            # Add the word (to be processed)
            word = match.group(0)
            bold_part, rest_part = self._split_word(word)
            if bold_part:
                parts.append(('bold', bold_part, rest_part))
            else:
                parts.append(('text', word))
            
            last_end = match.end()
        
        # Add any remaining text after the last word
        if last_end < len(text):
            parts.append(('text', text[last_end:]))
        
        # If no words were found, nothing to do
        if not any(p[0] == 'bold' for p in parts):
            return
        
        # Now we need to rebuild the element structure
        # Determine the namespace for <b> elements
        if default_ns:
            b_tag = '{%s}b' % default_ns
        else:
            b_tag = 'b'
        
        if attr == 'text':
            # Clear the text and add new content
            element.text = None
            
            # We need to insert new elements at the beginning
            first_text = True
            insert_index = 0
            
            for part in parts:
                if part[0] == 'text':
                    if first_text:
                        element.text = part[1]
                        first_text = False
                    else:
                        # Add to the tail of the previous element
                        if insert_index > 0:
                            prev = element[insert_index - 1]
                            prev.tail = (prev.tail or '') + part[1]
                        else:
                            element.text = (element.text or '') + part[1]
                else:  # bold
                    bold_text, rest_text = part[1], part[2]
                    b_elem = etree.Element(b_tag)
                    b_elem.text = bold_text
                    b_elem.tail = rest_text
                    element.insert(insert_index, b_elem)
                    insert_index += 1
                    first_text = False
        
        else:  # attr == 'tail'
            # Clear the tail
            element.tail = None
            
            # Get the parent and find our position
            parent = element.getparent()
            if parent is None:
                return
            
            elem_index = list(parent).index(element)
            insert_index = elem_index + 1
            
            first_text = True
            
            for part in parts:
                if part[0] == 'text':
                    if first_text:
                        element.tail = part[1]
                        first_text = False
                    else:
                        # Add to the tail of the previous inserted element
                        prev = parent[insert_index - 1]
                        prev.tail = (prev.tail or '') + part[1]
                else:  # bold
                    bold_text, rest_text = part[1], part[2]
                    b_elem = etree.Element(b_tag)
                    b_elem.text = bold_text
                    b_elem.tail = rest_text
                    parent.insert(insert_index, b_elem)
                    insert_index += 1
                    first_text = False
    
    def _split_word(self, word):
        """
        Split a word into bold and non-bold parts.
        
        Args:
            word: string word to split
            
        Returns:
            tuple of (bold_part, rest_part) or (None, None) if word should not be processed
        """
        length = len(word)
        
        # Skip short words if configured
        if self.skip_short_words and length <= 2:
            return None, None
        
        # Skip words shorter than minimum
        if length < self.min_word_length:
            return None, None
        
        # Calculate bold portion based on ratio
        if length == 1:
            return word, ''
        elif length <= 3:
            return word[0], word[1:]
        else:
            bold_len = max(1, round(length * self.boldness_ratio))
            # Make sure we don't bold the entire word
            bold_len = min(bold_len, length - 1)
            return word[:bold_len], word[bold_len:]
