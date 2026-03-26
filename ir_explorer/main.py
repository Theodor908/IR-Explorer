import sys
import os


def main():
    # on Windows, set AppUserModelID BEFORE creating any tkinter window
    # this gives IR Explorer its own taskbar identity instead of grouping under Python
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "irexplorer.app.1.0"
            )
        except Exception:
            pass

    from ir_explorer.app import App
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
