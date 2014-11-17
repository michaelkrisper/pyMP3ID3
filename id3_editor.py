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
    options = QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks
    directory = QtWidgets.QFileDialog.getExistingDirectory(widget, "Open Directory", os.path.expanduser("~/Music"), options)
    widget.dirLineEdit.setText(directory)

    fileNames = []
    for dirpath, dirnames, filenames in os.walk(directory):
        fileNames.extend(os.path.join(os.path.relpath(dirpath, directory), filename) for filename in filenames if
                         os.path.splitext(filename)[1] == ".mp3")
    global model
    model.setStringList(fileNames)


def store_current_selection(widget):
    selected_items = [index.data() for index in sorted(widget.listView.selectedIndexes(), key=lambda x: x.row())]
    if selected_items:
        updateSong(widget, os.path.join(widget.dirLineEdit.text(), selected_items[0]))


def updateSong(widget, filename):
    tag = id3.ID3Tag(filename)
    widget.titleLineEdit.setText(tag.title)
    widget.artistLineEdit.setText(tag.artist)
    widget.albumLineEdit.setText(tag.album)


def main():
    app = QtWidgets.QApplication(sys.argv)

    ui = uic.loadUi("id3_editor.ui")

    ui.selectDirectoryButton.clicked.connect(lambda: openFile(ui))

    ui.saveButton.clicked.connect(lambda: print("saved... NOT"))

    ui.listView.setModel(model)
    ui.listView.selectionModel().selectionChanged.connect(lambda: store_current_selection(ui))

    ui.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()