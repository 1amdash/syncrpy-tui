"""GetInput Class"""
import constants as CONST


class GetInput:
    """Waits for, gets, and returns keyboard input."""
    def __init__(self, obj):
        obj.window.keypad(True)
        event = obj.window.getch()
        return event
