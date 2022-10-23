import constants as CONST
import curses
from pop_ups import PopUpBase
from queue_window_refresh import QueueWinRefresh
from key_press import KeyPress
from reset_window import ResetWindow

class MenuBar(PopUpBase):
    """Creates the menubar

    Used to create either the File or Options menu, draws a window depending
    on if f or o is called.
    """
    position = 0
    sub_menu = ['ssh','rsync','exit']
    sub_menu2 = ['settings']
    menubarwindow = ''

    def __init__(self, stdscr, event):
        self.stdscr = stdscr
        self.screen_height, self.screen_width = stdscr.getmaxyx()
        self.draw_menu_bar()
        if event is not None:
            open_menu = self.open(event)
            return open_menu(event)

    def draw_menu_bar(self):
        """Draws menu_bar in normal state, used to reset the menu bar as well."""
        menu_bar_color = curses.color_pair(4)
        self.stdscr.addstr(0,0, ' ', menu_bar_color)
        string = 'File Options'
        string_length = len(string) + 1
        remainder_of_menu_bar = self.screen_width - string_length
        self.stdscr.addstr(0,1, string, menu_bar_color)
        self.stdscr.addstr(0,string_length, ' ' * remainder_of_menu_bar, menu_bar_color)
        QueueWinRefresh(self.stdscr) #

    def open(self, event=None):
        if event == CONST.CONST_LET_F_LWRCSE_KEY:
            return self.file_menu
        elif event == CONST.CONST_LET_O_LWRCSE_KEY:
            return self.options_menu
    
    def file_menu(self, event):
        super().__init__(10, 15, 1, 1, self.stdscr)
        #now using self.win from base
        self.stdscr.addstr(0,1, 'File', curses.A_STANDOUT)
        self.menu_item = self.sub_menu
        QueueWinRefresh(self.stdscr)
        self.display()

    def options_menu(self, event):
        super().__init__(10, 15, 1, 6, self.stdscr)
        self.stdscr.addstr(0,4+2, 'Options', curses.A_STANDOUT)
        self.menu_item = self.sub_menu2
        QueueWinRefresh(self.stdscr)
        self.display()

    def close(self):
        self.win.clear()
        self.stdscr.addstr(0,1, 'File Options', curses.A_NORMAL)
        QueueWinRefresh(self.stdscr)
        curses.doupdate()

    def menu(self):
        #print list as basis for menu, the item selector is the A_REVERSE (highlighted) item
        for index, item in enumerate(self.menu_item):
            if index == self.position:
                mode = curses.A_REVERSE
            else:
                mode = curses.A_NORMAL
            self.win.addstr(1+ index, 1, item, mode)
        self.win.noutrefresh()
        curses.doupdate()

    def enter(self):
        """Called from KeyPressed"""
        item = self.menu_item[self.position]
        self.win.erase()
        self.win.noutrefresh()
        ResetWindow(left_file_explorer)
        if item == 'ssh':
            if SSH.is_enabled is False:
                ssh_obj.start(win_manager, self.stdscr, status)
                reset_winders()
                QueueWinRefresh(self.win) 
                ResetWindow(left_file_explorer)
                ResetWindow(right_file_explorer)
                curses.doupdate()
        elif item == 'rsync':
            RSync('m')
        elif item == 'settings':
            glbl_opts.display()
        elif item == 'exit':
            return CONST.CONST_LET_Q_KEY
        else: pass
        self.close()
        
    def display(self):
        self.win.keypad(1)
        event = None
        while event not in (
            CONST.CONST_LET_F_LWRCSE_KEY,
            CONST.CONST_LET_O_LWRCSE_KEY,
            CONST.CONST_ENTER_KEY,
            CONST.CONST_ESCAPE_KEY
            ):
            self.menu()
            ### menuBar getch
            event = self.win.getch()
            event = KeyPress.event(KeyPress, event, self, self.menu_item, self.position)
        self.close()