# ID3 Tag Editor

[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

This project is a simple ID3 tag editor for MP3 files, written in Python. It consists of a core library for reading ID3 tag data and a graphical user interface (GUI) for viewing and editing the tags.

## Components

- `id3.py`: A library for parsing ID3v2 tags from MP3 files. It can read metadata such as title, artist, and album.
- `id3_editor.py`: A GUI application built with PyQt5 that allows users to select a directory, view all the MP3 files within it, and see their corresponding ID3 tag information.

## Dependencies

The GUI application requires the PyQt5 library. You can install it using pip:

```bash
pip install PyQt5
```

## Usage

To run the ID3 tag editor, execute the `id3_editor.py` script:

```bash
python3 id3_editor.py
```

This will open a window where you can select a directory containing your MP3 files. The application will then list all the MP3s, and you can click on a file to view its title, artist, and album information.

**Note:** The save functionality is not yet implemented.

## ID3 Standard

The text files included in the repository (`id3v2.4.0-*.txt`) contain detailed information about the ID3v2.4.0 standard, which this application is based on. They describe the structure of ID3 tags, the different frames available, and the changes from previous versions.

## Requirements

- Python 3.9 or newer
- PyQt5 — only for the GUI; `id3.py` works standalone

## Project structure

| File | Purpose |
|---|---|
| `id3.py` | ID3v2 parsing library, no third-party dependencies |
| `id3_editor.py` | PyQt5 GUI to browse a directory and inspect tags |
| `id3_editor.ui` | Qt Designer layout for the GUI |
| `id3v2.4.0-*.txt` | Copies of the ID3v2.4 specification for reference |

## Related

A standalone PyQt5 demo built around the same editor UI lives in
[pyGUI_qt](https://github.com/michaelkrisper/pyGUI_qt).

## License

MIT — see [LICENSE](LICENSE).
