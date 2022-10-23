import curses

class Display:
    """Displays list of items (menu, files, etc)."""
    def __init__(self, file_explorer_obj):
        self.file_explorer_obj = file_explorer_obj
        self.file_explorer_obj.menu()
        curses.doupdate()
