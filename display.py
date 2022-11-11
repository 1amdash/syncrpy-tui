"""Display Class"""
import curses


class Display:
    """Displays list of items (menu, files, etc) by calling objects menu method."""
    def __init__(self, obj):
        self.obj = obj
        self.obj.menu()
        curses.doupdate()
