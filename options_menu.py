"""OptionsMenu is a popup to setup global preferences/settings."""
import curses
import constants as CONST
from queue_window_refresh import QueueWinRefresh
from pop_ups import PopUpBase
from reset_window import ResetWindow
from key_press import KeyPress

class OptionsMenu(PopUpBase):
    """Popup menu meant to act as a 'preferences/settings' meant to affect the program globally"""
    menu_items = ['[ ] low bandwidth', '[ ] test item']
    def __init__(self, stdscr):
        self.position = 0
        self.low_bandwidth = None

    def __call__(self, stdscr):
        self.y, self.x = stdscr.getmaxyx()
        self.y = int(self.y/3)
        self.x = int (self.x/3)
        super().__init__(int(self.y), int(self.x), self.y, self.x, stdscr)

    def menu(self):
        for index, item in enumerate(self.menu_items):
            if index == self.position:
                mode = curses.A_REVERSE
            else:
                mode = curses.A_NORMAL
            msg = "%s" % (item)
            self.win.addstr(1 + index, 2, str(msg), mode)
        QueueWinRefresh(self.win)
        curses.doupdate()

    def enter(self):
        if self.position == 0:
            if self.low_bandwidth:
                self.menu_items = ['[ ] low bandwidth']
                self.low_bandwidth = False
            else:
                self.menu_items = ['[x] low bandwidth']
                self.low_bandwidth = True

    def close(self):
        self.win.erase()
        QueueWinRefresh(self.win) 
        ResetWindow(left_file_explorer)
        ResetWindow(right_file_explorer)
        curses.doupdate()

    def display(self):
        #self.__call__()
        self.win.keypad(1)
        #curses.set_escdelay(100)
        event = None
        while event not in (CONST.CONST_TAB_KEY, CONST.CONST_ESCAPE_KEY):
            self.menu()
            ### MenuBar getch
            event = self.win.getch()
            event = KeyPress.event(KeyPress, event, self, self.menu_items, self.position)  
        self.close()
