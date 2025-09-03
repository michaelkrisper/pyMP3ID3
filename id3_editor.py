#! /usr/bin/env python3
# coding=utf-8
"""
Script for ID3v2 Tag Editor
"""

from PyQt5 import uic, QtWidgets, QtCore
import sys
import os
import id3

__author__ = "Michael Krisper"
__email__ = "michael.krisper@gmail.com"
__date__ = "2014-11-17"

model = QtCore.QStringListModel()


def openFile(widget):
    """
    Opens a dialog to select a directory, then lists all MP3 files in that directory.
    The file list is then displayed in the GUI's list view.

    Args:
        widget: The main UI widget.
    """
    options = QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks
    directory = QtWidgets.QFileDialog.getExistingDirectory(widget, "Open Directory", os.path.expanduser("~/Music"), options)
    widget.dirLineEdit.setText(directory)

    # Walk through the directory and find all .mp3 files
    fileNames = []
    for dirpath, dirnames, filenames in os.walk(directory):
        fileNames.extend(os.path.join(os.path.relpath(dirpath, directory), filename) for filename in filenames if
                         os.path.splitext(filename)[1] == ".mp3")
    # Update the model with the file list
    global model
    model.setStringList(fileNames)


def store_current_selection(widget):
    """
    Gets the currently selected item in the list view and calls updateSong to display its tags.

    Args:
        widget: The main UI widget.
    """
    selected_items = [index.data() for index in sorted(widget.listView.selectedIndexes(), key=lambda x: x.row())]
    if selected_items:
        # Construct the full path to the selected file
        updateSong(widget, os.path.join(widget.dirLineEdit.text(), selected_items[0]))


def updateSong(widget, filename):
    """
    Reads the ID3 tag of the given file and updates the line edits in the GUI.

    Args:
        widget: The main UI widget.
        filename (str): The path to the MP3 file.
    """
    try:
        tag = id3.ID3Tag(filename)
        widget.titleLineEdit.setText(tag.title)
        widget.artistLineEdit.setText(tag.artist)
        widget.albumLineEdit.setText(tag.album)
    except Exception as e:
        print(f"Error reading tag from {filename}: {e}")
        widget.titleLineEdit.setText("")
        widget.artistLineEdit.setText("")
        widget.albumLineEdit.setText("")


def main():
    """
    The main entry point of the application.
    Initializes the Qt application, loads the UI, connects the signals and slots,
    and shows the main window.
    """
    app = QtWidgets.QApplication(sys.argv)

    # Load the UI from the .ui file
    ui = uic.loadUi("id3_editor.ui")

    # Connect the "Select Directory" button to the openFile function
    ui.selectDirectoryButton.clicked.connect(lambda: openFile(ui))

    # Connect the "Save" button to a placeholder function
    ui.saveButton.clicked.connect(lambda: print("saved... NOT"))

    # Set the model for the list view and connect the selection change signal
    ui.listView.setModel(model)
    ui.listView.selectionModel().selectionChanged.connect(lambda: store_current_selection(ui))

    # Show the main window
    ui.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()