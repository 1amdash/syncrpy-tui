"""MenuBar Class"""
import curses
import constants as CONST
from pop_ups import PopUpBase
from queue_window_refresh import QueueWinRefresh
from ssh import SSH


class MenuBar(PopUpBase):
    """Creates the menubar

    Used to create either the File or Options menu, draws a window depending
    on if f or o is called.
    """
    position = 0
    sub_menu = ['ssh','rsync','exit']
    sub_menu2 = ['settings']
    menubarwindow = ''

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.screen_height, self.screen_width = stdscr.getmaxyx()
        self.draw_menu_bar()
        self.is_menu_open = False

    def __call__(self, event):
        if event is not None:
            if event in (CONST.CONST_LET_F_LWRCSE_KEY, CONST.CONST_LET_O_LWRCSE_KEY) and self.is_menu_open is False:
                open_menu = self.open(event)
                return open_menu(event)
            elif event in (CONST.CONST_LET_F_LWRCSE_KEY, CONST.CONST_LET_O_LWRCSE_KEY) and self.is_menu_open is True:
                return self.close_menu()

    def draw_menu_bar(self):
        """Draws menu_bar in normal state, used to reset the menu bar as well."""
        menu_bar_color = curses.color_pair(2)
        self.stdscr.addstr(0,0, ' ', menu_bar_color)
        string = 'File Options'
        string_length = len(string) + 1
        remainder_of_menu_bar = self.screen_width - string_length
        self.stdscr.addstr(0,1, string, menu_bar_color | curses.A_NORMAL)
        self.stdscr.addstr(0,string_length, ' ' * remainder_of_menu_bar, menu_bar_color)
        QueueWinRefresh(self.stdscr)

    def open(self, event=None):
        """Opens the file or options menu based on key press."""
        if event == CONST.CONST_LET_F_LWRCSE_KEY:
            return self.file_menu
        elif event == CONST.CONST_LET_O_LWRCSE_KEY:
            return self.options_menu
        else:
            return self.open_program
    
    def open_program(self, event):
        if event == 'ssh':
            return 'start'           
            # if SSH.is_enabled is False:
            #     ssh_obj.start(win_manager, self.stdscr, status)
            #     reset_winders()
            #     QueueWinRefresh(self.win) 
            #     ResetWindow(left_file_explorer)
            #     ResetWindow(right_file_explorer)
            #     curses.doupdate()
            # CALL rsync
            # RSync('m')
            #glbl_opts.display()

    def file_menu(self, event):
        super().__init__(10, 15, 1, 1, self.stdscr)
        self.window = self.win
        self.stdscr.addstr(0,1, 'File', curses.color_pair(2) | curses.A_STANDOUT)
        self.menu_item = self.sub_menu
        QueueWinRefresh(self.stdscr)
        self.is_menu_open = True

    def options_menu(self, event):
        super().__init__(10, 15, 1, 6, self.stdscr)
        self.window = self.win
        self.stdscr.addstr(0,4+2, 'Options', curses.color_pair(2) | curses.A_STANDOUT)
        self.menu_item = self.sub_menu2
        QueueWinRefresh(self.stdscr)
        self.is_menu_open = True

    def close_menu(self):
        #self.window.clear()
        self.window.erase()
        self.window.noutrefresh()
        self.draw_menu_bar()
        self.stdscr.addstr(0,1, 'File Options', curses.color_pair(2) | curses.A_NORMAL)

        QueueWinRefresh(self.stdscr)
        curses.doupdate()
        self.is_menu_open = False

    def menu(self):
        """print list as basis for menu, the item selector is the A_REVERSE (highlighted) item"""
        for index, item in enumerate(self.menu_item):
            if index == self.position:
                mode = curses.A_REVERSE
            else:
                mode = curses.A_NORMAL
            self.window.addstr(1+ index, 1, item, mode)
        self.window.noutrefresh()
        curses.doupdate()

    def enter(self):
        """Called from KeyPressed"""
        item = self.menu_item[self.position]
        if item != 'exit':
            return item
        elif item == 'exit':
            return CONST.CONST_LET_Q_KEY
        else: pass
        self.close_menu()
