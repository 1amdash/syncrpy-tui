"""Button Class"""
import curses
import constants as CONST
from queue_window_refresh import QueueWinRefresh
from key_press import KeyPress


class Button:
    """Portable Button"""
    def __init__(self, window, item_list):
        self.window = window
        self.item_list = item_list

        self.button_press_ok = False
        self.button_press_cancel = False
        self.position = 0
        self.client_ready = None
        self.window.keypad(1)
        self.menu()

    def enter(self):
        """Position 0 == Ok, 1 == Cancel."""
        if self.position == 0:
            self.button_press_ok = True
        else:
            self.button_press_cancel = True
        return

    def display(self):
        event = None
        while event not in (CONST.CONST_ESCAPE_KEY, CONST.CONST_TAB_KEY, CONST.CONST_ENTER_KEY):
            self.menu()
            if self.client_ready:
                event = CONST.CONST_ENTER_KEY
                return
            else:
                event = self.window.getch()
                event = KeyPress.event(KeyPress, self.item_list, self.position)

    def event(self, action):
        self.client_ready = action

    def menu(self):
        space = 10
        for index, item in enumerate(self.item_list):
            if index == self.position:
                mode = curses.A_REVERSE
            else:
                mode = curses.A_NORMAL
            self.window.addstr(5, space, str(item), mode)
            space += 10
        QueueWinRefresh(self.window)
        curses.doupdate()
        