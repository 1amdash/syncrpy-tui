import constants as CONST

class GetInput:
    """Waits, gets, and returns keyboard input."""
    def __init__(self, file_explorer_obj):
        self.file_explorer_obj = file_explorer_obj

    def run(self):
        event = None
        while event not in (
            CONST.CONST_TAB_KEY,
            CONST.CONST_LET_Q_LWRCSE_KEY,
            CONST.CONST_LET_F_LWRCSE_KEY,
            CONST.CONST_LET_O_LWRCSE_KEY
            ):
            self.file_explorer_obj.window.keypad(True)
            event = self.file_explorer_obj.window.getch()
            return event
