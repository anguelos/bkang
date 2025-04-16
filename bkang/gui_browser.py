import os
import sys
import subprocess
from typing import Optional
from PySide6.QtWidgets import (
    QSplitter,
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QListWidget, QListWidgetItem,
    QFileDialog, QStackedLayout, QComboBox, QListView, QStyle, QAbstractItemView,
    QMenu
)
from PySide6.QtGui import QIcon, QKeySequence, QClipboard, QAction, QPixmap, QPainter
from PySide6.QtCore import Qt, QSize, QEvent

import glob
#from PySide6.QtWidgets import QListWidgetItem, QListWidget


def get_present_version(p: str) -> Optional[str]:
    # Dummy placeholder logic — replace with real version check
    if os.path.exists(p) and p.endswith(".txt"):
        return p + ".present"
    return None

class FileManager(QWidget):
    def update_window_title(self):
        rel_path = os.path.relpath(self.current_path, self.fake_root)
        if rel_path == ".":
            rel_path = ""
        self.setWindowTitle(f"{os.path.basename(self.fake_root)}:{rel_path}")
    def get_fake_root(self):
        return self.fake_root

    def set_fake_root(self, new_root):
        subpath = os.path.relpath(self.current_path, self.fake_root)
        potential_new_path = os.path.join(new_root, subpath)
        if os.path.exists(potential_new_path):
            self.current_path = potential_new_path
        else:
            self.current_path = new_root

        self.fake_root = new_root
        self.path_edit.setText(self.current_path)
        self.update_window_title()
        self.update_window_title()
        self.populate_file_list(self.current_path)
    def closeEvent(self, event):
        QApplication.quit()
        if self.file_manager:
            self.file_manager.set_fake_root(item.text())



    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape:
            QApplication.quit()
            return True
        return super().eventFilter(obj, event)
    def __init__(self, root_path):
        super().__init__()
        self.fake_root = root_path
        self.current_path = root_path

        self.setWindowTitle("Advanced File Manager")
        self.resize(800, 600)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Top bar with path and view mode
        top_bar = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setText(self.current_path)

        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_folder)

        self.view_mode = QComboBox()
        self.view_mode.addItems(["List View", "Icon View"])
        self.view_mode.currentIndexChanged.connect(self.change_view_mode)

        top_bar.addWidget(QLabel("Path:"))
        top_bar.addWidget(self.path_edit)
        top_bar.addWidget(browse_button)
        top_bar.addWidget(self.view_mode)

        main_layout.addLayout(top_bar)

        # File view area
        self.file_view = QListWidget()
        self.file_view.setViewMode(QListView.ListMode)
        self.file_view.setIconSize(QSize(64, 64))
        self.file_view.setResizeMode(QListView.Adjust)
        self.file_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.file_view.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.file_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_view.customContextMenuRequested.connect(self.show_context_menu)

        main_layout.addWidget(self.file_view)

        # Shortcut for Copy (Ctrl+C)
        copy_shortcut = QKeySequence(Qt.CTRL | Qt.Key_C)
        self.copy_action = QAction("Copy Path", self)
        self.copy_action.setShortcut(copy_shortcut)
        self.copy_action.triggered.connect(self.copy_selected_item_path)
        self.addAction(self.copy_action)

        self.populate_file_list(self.current_path)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", self.fake_root)
        if folder and folder.startswith(self.fake_root):
            self.current_path = folder
            self.path_edit.setText(folder)
            self.populate_file_list(folder)

    def change_view_mode(self, index):
        if index == 0:
            self.file_view.setViewMode(QListView.ListMode)
        else:
            self.file_view.setViewMode(QListView.IconMode)

    def populate_file_list(self, folder):
        self.file_view.clear()

        # Add ".." item if not at fake root
        if os.path.abspath(folder) != os.path.abspath(self.fake_root):
            up_item = QListWidgetItem("..")
            up_item.setIcon(self.style().standardIcon(QStyle.SP_FileDialogToParent))
            self.file_view.addItem(up_item)

        try:
            for item_name in sorted(os.listdir(folder)):
                item_path = os.path.join(folder, item_name)
                icon = self.style().standardIcon(QStyle.SP_DirIcon if os.path.isdir(item_path) else QStyle.SP_FileIcon)
                item = QListWidgetItem(icon, item_name)
                self.file_view.addItem(item)
        except Exception as e:
            self.file_view.addItem(QListWidgetItem(f"Error: {e}"))

    def on_item_double_clicked(self, item):
        name = item.text()
        if name == "..":
            parent = os.path.dirname(self.current_path)
            if os.path.abspath(parent).startswith(os.path.abspath(self.fake_root)):
                self.current_path = parent
        else:
            new_path = os.path.join(self.current_path, name)
            if os.path.isdir(new_path):
                self.current_path = new_path

        self.path_edit.setText(self.current_path)
        self.populate_file_list(self.current_path)

    def show_context_menu(self, position):
        item = self.file_view.itemAt(position)
        if item and item.text() != "..":
            full_path = os.path.join(self.current_path, item.text())
            present_version = get_present_version(full_path)

            menu = QMenu()

            copy_action = menu.addAction("Copy Path")
            open_fm_action = menu.addAction("Open in File Manager")
            open_present_action = menu.addAction("Open in Present")
            open_terminal_action = menu.addAction("Open Terminal Here")

            # Enable/disable actions based on availability
            open_present_action.setEnabled(present_version is not None)
            open_terminal_action.setEnabled(os.path.isdir(os.path.dirname(full_path)))

            action = menu.exec(self.file_view.mapToGlobal(position))
            if action == copy_action:
                self.copy_item_path(item)
            elif action == open_fm_action:
                subprocess.run(["xdg-open", os.path.dirname(full_path)])
            elif action == open_present_action and present_version:
                subprocess.run(["xdg-open", present_version])
            elif action == open_terminal_action:
                subprocess.run(["gnome-terminal", "--working-directory", os.path.dirname(full_path)])

    def copy_item_path(self, item):
        full_path = os.path.join(self.current_path, item.text())
        QApplication.clipboard().setText(full_path)

    def copy_selected_item_path(self):
        selected_items = self.file_view.selectedItems()
        if selected_items:
            item = selected_items[0]
            if item.text() != "..":
                self.copy_item_path(item)


class PathSlider(QListWidget):
    def __init__(self, backdrop, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.backdrop = backdrop
        self.setStyleSheet("background-color: rgba(0, 0, 0, 250); color: white;")
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.itemClicked.connect(self.on_slider_item_selected)

    def populate(self, glob_pattern):
        self.clear()
        matches = sorted(glob.glob(glob_pattern))
        for path in matches:
            if os.path.isdir(path):
                self.addItem(QListWidgetItem(path))

    def on_slider_item_selected(self, item):
        if self.backdrop.file_manager:
            self.backdrop.file_manager.set_fake_root(item.text())
            self.backdrop.file_manager.raise_()
            self.backdrop.file_manager.activateWindow()


class FullscreenBackdrop(QWidget):
    def on_slider_item_selected(self, item):
        if self.file_manager:
            self.file_manager.set_fake_root(item.text())
            self.file_manager.raise_()
            self.file_manager.activateWindow()

    def __init__(self, wallpaper_path: Optional[str] = None, file_manager: Optional[FileManager] = None, glob_pattern: Optional[str] = None):
        super().__init__()
        self.wallpaper = wallpaper_path
        self.file_manager = file_manager
        self.glob_pattern = glob_pattern or "*"

        self.slider = PathSlider(self, self)
        self.slider.setFixedWidth(int(self.width() * 0.1))
        self.slider.move(0, 0)
        self.slider.populate(self.glob_pattern)
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setWindowTitle("Time Machine Style")
        self.installEventFilter(self)

    def resizeEvent(self, event):
        if self.slider:
            self.slider.setFixedHeight(self.height())
        super().resizeEvent(event)

    def paintEvent(self, event):
        if self.wallpaper and os.path.exists(self.wallpaper):
            painter = QPainter(self)
            pixmap = QPixmap(self.wallpaper).scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            painter.drawPixmap(self.rect(), pixmap)
            painter.end()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape:
            QApplication.quit()
            return True
        return super().eventFilter(obj, event)

    def populate_slider(self):
        matches = sorted(glob.glob(self.glob_pattern))
        for path in matches:
            if os.path.isdir(path):
                self.slider.addItem(QListWidgetItem(path))


def main_browse_gui():
    app = QApplication(sys.argv)
    #fake_root = QFileDialog.getExistingDirectory(None, "Select Fake Root")
    fake_root = "/mnt/btrfs/tmp/snapshots"
    #wallpaper = QFileDialog.getOpenFileName(None, "Select Background Wallpaper", "", "Images (*.png *.jpg *.jpeg *.bmp)")[0]
    wallpaper = "/usr/share/backgrounds/Milkyway_by_mizuno_as.png"
  
    if fake_root:
        glob_expr = "/mnt/btrfs/tmp/snapshots/*"  # Example glob expression
        manager = FileManager(fake_root)
        manager.installEventFilter(manager)
        screen = app.primaryScreen().geometry()
        manager.resize(1280, 1024)
        manager.move(
            screen.center().x() - manager.width() // 2,
            screen.center().y() - manager.height() // 2
        )
        backdrop = FullscreenBackdrop(wallpaper_path=wallpaper, file_manager=manager, glob_pattern=glob_expr)
        # Show backdrop fullscreen
        backdrop.showFullScreen()

        # Show file manager as a floating top-level window
        manager.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        manager.show()
        manager.raise_()
        manager.activateWindow()

        sys.exit(app.exec())


if __name__ == "__main__":
    main_browse_gui()