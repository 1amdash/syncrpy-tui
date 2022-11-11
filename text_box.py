"""TextBox Class"""
import curses
import curses.textpad
import constants as CONST
from queue_window_refresh import QueueWinRefresh


class TextBox:
    """create single text box, meant to be portable"""
    def __init__(self, width, start_y, start_x):
        self.width = width
        self.start_y = start_y
        self.start_x = start_x
        self.text_box_ready = False
        self.window = curses.newwin(3, width, start_y+1, start_x)
        self.window.bkgdset(curses.color_pair(2))
        self.window.border()
        QueueWinRefresh(self.window)
        curses.curs_set(2)
        curses.doupdate()
        self.text_window()

    def text_window(self):
        self.text_win = curses.newwin(1, self.width-2, self.start_y+2, self.start_x+1)
        self.text_win.keypad(True)
        self.text_win.bkgdset(curses.color_pair(2))
        self.text_win.bkgd(curses.color_pair(2))
        self.text_win.attron(curses.color_pair(2))
        QueueWinRefresh(self.text_win)
        curses.doupdate()
        self.tb = self.text_box(self.text_win)

    def text_box(self, win):
        return curses.textpad.Textbox(win)

    def action(self):
        while self.text_box_ready != True:
            self.text = self.tb.edit(self.validate)
            self.text = self.text.strip()
            return (self.text, self.text_box_ready)

    def validate(self, ch):
        if ch == CONST.CONST_ENTER_KEY:
            self.text_box_ready = True
            curses.curs_set(0)
            return ch
        elif ch in (CONST.CONST_TAB_KEY, curses.KEY_DOWN):
            return CONST.CONST_ENTER_KEY
        else:
            return ch
