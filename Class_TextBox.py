from Class_QueueWinRefresh import QueueWinRefresh

import curses
import curses.textpad

CONST_LET_F_LWRCSE_KEY = ord('f')
CONST_LET_O_LWRCSE_KEY = ord('o')
CONST_ESCAPE_KEY = 27
CONST_ENTER_KEY = ord('\n')
CONST_TAB_KEY = ord('\t')
CONST_LET_Q_KEY = ord('Q')
CONST_LET_Q_LWRCSE_KEY = ord('q')
CONST_NUM_9_KEY = ord('9')
CONST_NUM_5_KEY = ord('5')
CONST_NUM_9_KEY = ord('9')
CONST_LET_X_LWRCSE_KEY = ord('x')
CONST_LET_B_LWRCSE_KEY = ord('b')
CONST_LET_T_LWRCSE_KEY = ord('t')
CONST_LET_N_LWRCSE_KEY = ord('n')

class TextBox:
    """create single text box, meant to be portable"""
    def __init__(self, width, start_y, start_x):
        self.width = width
        self.start_y = start_y
        self.start_x = start_x
        self.text_box_ready = False

        self.win = curses.newwin(3, width, start_y+1, start_x)
        self.win.bkgdset(curses.color_pair(2))
        self.win.border()
        QueueWinRefresh(self.win) 
        curses.curs_set(2)
        curses.doupdate()
        self.text_window()

    def text_window(self):
        self.text_win = curses.newwin(1, self.width-2, self.start_y+2, self.start_x+1)
        self.text_win.keypad(1)
        self.text_win.bkgdset(curses.color_pair(2))
        self.text_win.bkgd(curses.color_pair(2))
        self.text_win.attron(curses.color_pair(2))
        QueueWinRefresh(self.text_win) #self.text_win.noutrefresh()
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
        if ch == CONST_ENTER_KEY:
            self.text_box_ready = True
            curses.curs_set(0)
            return ch
        elif ch in (CONST_TAB_KEY, curses.KEY_DOWN):
            return CONST_ENTER_KEY
        else: 
            return ch
