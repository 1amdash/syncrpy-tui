class PopUpBase:
    """Creates a new window with basic sizing and formatting for various popups"""
    def __init__(self, nlines, ncols, begin_y, begin_x):
        self.par_win_size_y, self.par_win_size_x = stdscr.getmaxyx()
        self.y = int(self.par_win_size_y/4)
        self.x = int(self.par_win_size_x/4)
        self.h = int(self.par_win_size_y/2)
        self.w = 25 # int(self.par_win_size_x*.5)
        self.win = curses.newwin(nlines, ncols, begin_y, begin_x)
        self.win.attron(curses.color_pair(2))
        self.win.bkgd(curses.color_pair(2))
        self.win.border()
        queue_win_refresh(self.win) 

    def msg(self, msg):
        """Will act as an alert/error window, where the msg argument can be an exception to print"""
        self.win.addstr(1,1, msg, curses.color_pair(2))
        queue_win_refresh(self.win) 