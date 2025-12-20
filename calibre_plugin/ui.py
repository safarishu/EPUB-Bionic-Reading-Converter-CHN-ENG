#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
UI components for Bionic Reading Plugin - toolbar button and menu integration

This plugin uses a toggle approach:
- "Apply Bionic" converts EPUB to bionic format, backing up the original as ORIGINAL_EPUB
- "Restore Original" restores the original EPUB from backup
- The EPUB format is always the "active" readable version
"""

from qt.core import QMenu, QToolButton, QProgressDialog, QMessageBox, Qt, QIcon, QPixmap

from calibre.gui2.actions import InterfaceAction
from calibre_plugins.bionic_reading import get_prefs, PLUGIN_NAME


class BionicReadingUI(InterfaceAction):
    """
    Main UI class that creates the toolbar button and handles user interaction.
    """
    
    name = PLUGIN_NAME
    action_spec = (PLUGIN_NAME, None, 'Convert books to Bionic Reading format', None)
    popup_type = QToolButton.ToolButtonPopupMode.MenuButtonPopup
    action_add_menu = True
    
    def genesis(self):
        """Called when plugin is initialized"""
        self.prefs = get_prefs()
        
        # Set up the main action (toolbar button click)
        self.qaction.triggered.connect(self.apply_bionic)
        
        # Create the dropdown menu
        self.menu = QMenu(self.gui)
        self.qaction.setMenu(self.menu)
        
        # Add menu items
        self.apply_action = self.create_menu_action(
            self.menu,
            'apply_bionic',
            'Apply Bionic Reading',
            description='Convert EPUB to Bionic Reading format (backs up original)',
            triggered=self.apply_bionic
        )
        
        self.restore_action = self.create_menu_action(
            self.menu,
            'restore_original',
            'Restore Original',
            description='Restore original EPUB from backup',
            triggered=self.restore_original
        )
        
        self.menu.addSeparator()
        
        self.config_action = self.create_menu_action(
            self.menu,
            'configure_bionic',
            'Configure...',
            description='Configure Bionic Reading settings',
            triggered=self.show_configuration
        )
        
        # Set the icon
        self.qaction.setIcon(self.get_icon())
    
    def get_icon(self):
        """Get the plugin icon"""
        # Try to load custom icon from plugin resources
        try:
            icon_data = self.load_resources(['images/icon.png']).get('images/icon.png')
            if icon_data:
                pixmap = QPixmap()
                pixmap.loadFromData(icon_data)
                return QIcon(pixmap)
        except Exception:
            pass
        
        # Fallback to built-in icon
        from calibre.gui2 import get_icons
        return get_icons('book.png')
    
    def apply_settings(self):
        """Called when settings are changed"""
        self.prefs = get_prefs()
    
    def apply_bionic(self):
        """Apply Bionic Reading format to selected books"""
        import io
        from calibre.gui2 import error_dialog, info_dialog
        from calibre_plugins.bionic_reading.main import BionicConverter
        
        # Get selected book IDs
        rows = self.gui.library_view.selectionModel().selectedRows()
        if not rows:
            error_dialog(
                self.gui,
                'No books selected',
                'Please select one or more books to convert.',
                show=True
            )
            return
        
        book_ids = list(map(self.gui.library_view.model().id, rows))
        db = self.gui.current_db.new_api
        
        # Check which books have EPUB format and don't already have bionic applied
        books_to_process = []
        already_bionic = []
        no_epub = []
        
        for book_id in book_ids:
            formats = db.formats(book_id)
            if not formats or 'EPUB' not in formats:
                no_epub.append(book_id)
            elif 'ORIGINAL_EPUB' in formats:
                already_bionic.append(book_id)
            else:
                books_to_process.append(book_id)
        
        if not books_to_process:
            msg = 'No books to convert.'
            if already_bionic:
                msg += f'\n\n{len(already_bionic)} book(s) already have Bionic applied.'
            if no_epub:
                msg += f'\n\n{len(no_epub)} book(s) have no EPUB format.'
            error_dialog(
                self.gui,
                'Nothing to convert',
                msg,
                show=True
            )
            return
        
        # Show progress dialog
        progress = QProgressDialog(
            'Applying Bionic Reading format...',
            'Cancel',
            0,
            len(books_to_process),
            self.gui
        )
        progress.setWindowTitle('Bionic Reading')
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        
        # Process books
        converter = BionicConverter(self.prefs)
        successful = 0
        failed = []
        
        for i, book_id in enumerate(books_to_process):
            if progress.wasCanceled():
                break
            
            title = db.field_for('title', book_id)
            progress.setLabelText(f'Processing: {title}')
            progress.setValue(i)
            
            try:
                # Get the original EPUB data
                epub_data = db.format(book_id, 'EPUB')
                if epub_data is None:
                    failed.append((title, 'Could not read EPUB'))
                    continue
                
                # Backup original as ORIGINAL_EPUB
                db.add_format(book_id, 'ORIGINAL_EPUB', io.BytesIO(epub_data))
                
                # Convert to bionic format
                bionic_data = converter.convert(epub_data)
                
                # Replace EPUB with bionic version
                db.add_format(book_id, 'EPUB', io.BytesIO(bionic_data))
                successful += 1
                
            except Exception as e:
                failed.append((title, str(e)))
        
        progress.setValue(len(books_to_process))
        progress.close()
        
        # Show result
        if successful > 0:
            msg = f'Successfully applied Bionic Reading to {successful} book(s).'
            msg += '\n\nOriginal EPUBs backed up as ORIGINAL_EPUB format.'
            msg += '\nUse "Restore Original" to revert.'
            if failed:
                msg += f'\n\nFailed for {len(failed)} book(s):'
                for title, error in failed[:5]:
                    msg += f'\n• {title}: {error}'
                if len(failed) > 5:
                    msg += f'\n... and {len(failed) - 5} more'
            
            info_dialog(
                self.gui,
                'Bionic Reading',
                msg,
                show=True
            )
        else:
            error_dialog(
                self.gui,
                'Conversion failed',
                'Failed to convert any books.',
                det_msg='\n'.join(f'{t}: {e}' for t, e in failed),
                show=True
            )
        
        # Refresh the library view
        self.gui.library_view.model().refresh_ids(books_to_process)
    
    def restore_original(self):
        """Restore original EPUB from backup"""
        import io
        from calibre.gui2 import error_dialog, info_dialog
        
        # Get selected book IDs
        rows = self.gui.library_view.selectionModel().selectedRows()
        if not rows:
            error_dialog(
                self.gui,
                'No books selected',
                'Please select one or more books.',
                show=True
            )
            return
        
        book_ids = list(map(self.gui.library_view.model().id, rows))
        db = self.gui.current_db.new_api
        
        # Find books with ORIGINAL_EPUB format
        books_with_backup = []
        for book_id in book_ids:
            formats = db.formats(book_id)
            if formats and 'ORIGINAL_EPUB' in formats:
                books_with_backup.append(book_id)
        
        if not books_with_backup:
            error_dialog(
                self.gui,
                'No backups found',
                'None of the selected books have an original EPUB backup.\n\n'
                'Backups are created when you apply Bionic Reading.',
                show=True
            )
            return
        
        # Confirm restoration
        confirm = QMessageBox.question(
            self.gui,
            'Confirm restoration',
            f'Restore original EPUB for {len(books_with_backup)} book(s)?\n\n'
            'This will replace the current EPUB with the original version.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if confirm != QMessageBox.StandardButton.Yes:
            return
        
        # Restore originals
        successful = 0
        failed = []
        
        for book_id in books_with_backup:
            title = db.field_for('title', book_id)
            try:
                # Get the original EPUB
                original_data = db.format(book_id, 'ORIGINAL_EPUB')
                if original_data is None:
                    failed.append((title, 'Could not read backup'))
                    continue
                
                # Restore as EPUB
                db.add_format(book_id, 'EPUB', io.BytesIO(original_data))
                
                # Remove the backup (new_api uses remove_formats with list)
                db.remove_formats({book_id: {'ORIGINAL_EPUB'}})
                successful += 1
                
            except Exception as e:
                failed.append((title, str(e)))
        
        if successful > 0:
            msg = f'Restored original EPUB for {successful} book(s).'
            if failed:
                msg += f'\n\nFailed for {len(failed)} book(s).'
            info_dialog(
                self.gui,
                'Bionic Reading',
                msg,
                show=True
            )
        else:
            error_dialog(
                self.gui,
                'Restoration failed',
                'Failed to restore any books.',
                det_msg='\n'.join(f'{t}: {e}' for t, e in failed),
                show=True
            )
        
        # Refresh the library view
        self.gui.library_view.model().refresh_ids(books_with_backup)
    
    def show_configuration(self):
        """Show the configuration dialog"""
        self.interface_action_base_plugin.do_user_config(self.gui)
