# Third-Party Notices

IR Explorer includes or depends on third-party software. This file is a practical notice file for distribution; each dependency remains governed by its own license.

## Project License

IR Explorer itself is released under the MIT License. See `LICENSE`.

## Runtime and Bundled Dependencies

### Python

- Component: Python 3.10
- License: Python Software Foundation License
- Homepage: https://www.python.org/

### Tk / Tcl

- Component: Tk 8.6 / Tcl 8.6
- License: Tcl/Tk license terms distributed with Tcl/Tk
- Homepage: https://www.tcl.tk/

### NumPy

- Component: NumPy 1.26.4
- License: BSD-style license used by NumPy
- Homepage: https://numpy.org/
- Source: https://github.com/numpy/numpy

Note: NumPy binary distributions may also bundle additional components such as OpenBLAS and related runtime libraries under their own terms.

### PyMuPDF

- Component: PyMuPDF 1.27.2
- License: Dual licensed under GNU Affero General Public License v3.0 or an Artifex commercial license
- Documentation: https://pymupdf.readthedocs.io/
- Source: https://github.com/pymupdf/pymupdf

Important: PyMuPDF is not MIT-licensed. If you distribute IR Explorer with PyMuPDF included, review the AGPL obligations carefully or obtain a commercial license if needed.

### PyYAML

- Component: PyYAML 6.0
- License: MIT License
- Homepage: https://pyyaml.org/
- Source: https://github.com/yaml/pyyaml

## Build and Packaging Tools

### PyInstaller

- Component: PyInstaller 6.19.0
- License: GPLv2-or-later with PyInstaller's special exception for building and distributing packaged applications
- Homepage: https://pyinstaller.org/
- Source: https://github.com/pyinstaller/pyinstaller

### Inno Setup

- Component: Inno Setup
- Description: Windows installer builder used in the release pipeline
- Homepage: https://jrsoftware.org/isinfo.php

Note: Inno Setup is used as a build tool for Windows installers. Review its upstream license terms if you distribute commercial software or use it in organizational CI environments.

## Distribution Notes

- This notice file is informational and does not replace the original license texts of third-party dependencies.
- If you distribute packaged builds publicly, include the license texts required by the dependencies you bundle.
- The dependency that most warrants separate review in this project is PyMuPDF because of its AGPL/commercial licensing model.

## Suggested Next Step

For stricter compliance, add a `licenses/` folder with the full license texts for each bundled dependency you ship inside release artifacts.
