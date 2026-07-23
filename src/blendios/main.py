"""Main entry point for the BlendiOS desktop environment."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from blendios.common.paths import ensure_data_dirs
from blendios.desktop.desktop_shell import DesktopShell
from blendios.kernel.kernel import Kernel


def main() -> int:
    """Bootstrap and run the BlendiOS desktop shell."""
    ensure_data_dirs()

    app = QApplication(sys.argv)
    app.setApplicationName("BlendiOS")
    app.setApplicationVersion("0.1.0")

    kernel = Kernel()
    kernel.bootstrap()

    shell = DesktopShell(kernel=kernel)
    shell.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
