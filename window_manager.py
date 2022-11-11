"""window_manager module"""
import curses
from queue_window_refresh import QueueWinRefresh


class WinManager:
    """Window manager to setup left and right window panels

    This class is meant to setup the left and right windows (panels) for the file explorers,
    select and set the active panel, and update the panels respective file path.
    """
    active_panel = 0
    cur_win = None
    def __init__(self, stdscr):
        self.left_head_path = ''
        self.right_head_path = ''
        self.stdscr = stdscr
        self.screen_size()
        self.window_height = self.screen_height -2
        self.window_width = int(self.screen_width/2)
        self.other_panel = 1

    def screen_size(self):
        max_y_x = self.stdscr.getmaxyx()
        self.screen_height = max_y_x[0]
        self.screen_width = max_y_x[1]
        return max_y_x

    def draw_win(self, height, width, y_start, x_start, title):
        #draws the initial left and right windows
        window = self.stdscr.derwin(height, width, y_start, x_start)
        window.bkgd(curses.color_pair(1))
        window.box(0,0)
        window.keypad(1)
        window.addstr(0,2,str(title))
        return window

    def draw_left_win(self):
        #calls draw window and adds parameters for the left panel
        left_win_x_start = 0
        self.left_win = self.draw_win(
                self.window_height,
                self.window_width,
                1,
                left_win_x_start,
                title=str('/')
                )
        QueueWinRefresh(self.left_win)
        return self.left_win

    def draw_right_win(self):
        #calls draw window and adds parameters for the right panel
        right_win_x_start = int(self.screen_width/2)
        self.right_win = self.draw_win(
                self.window_height,
                self.window_width,
                1,
                right_win_x_start,
                title=str('/')
                )
        QueueWinRefresh(self.right_win)
        return self.right_win

    def panel_headers(self):
        #needed to update the left and right panel headers/curent workding directory paths
        #also keeps the headers updated when switching windows
        path = self.trim_header_path(self.path)
        if self.active_panel == 0:
            self.left_head_path = path
        else:
            self.right_head_path = path
        #if ssh_obj.is_enabled:
        #        try:
        #            self.right_head_path =
        #               ssh_obj.server_info[0] + ':' + right_file_explorer.ssh_abs_path
        #        except AttributeError:
        #            pass

    def trim_header_path(self, path):
        panel_widths = int(self.stdscr.getmaxyx()[1]/2) - 2
        header_length = len(path)
        if header_length > panel_widths:
            trimmed_chars = header_length - panel_widths
            path = path[trimmed_chars:]
        return path

    def left_panel_sel(self):
        #redraws the panel headers and borders when switching windows
        self.left_win.move(0,1)
        self.left_win.clrtoeol()
        self.left_win.border()
        self.left_win.addstr(0,1,str(self.left_head_path),curses.A_STANDOUT | curses.color_pair(3))
        self.right_win.border()
        self.right_win.addstr(0,1,str(self.right_head_path),curses.A_NORMAL)

    def refreshln1(self):
        self.left_win.untouchwin()
        self.right_win.untouchwin()
        self.left_win.redrawln(0,1)
        self.right_win.redrawln(0,1)
        QueueWinRefresh(self.left_win)
        QueueWinRefresh(self.right_win)

    def right_panel_sel(self):
        #redraws the panel headers and borders when switching windows
        self.left_win.border()
        self.left_win.addstr(0,1,str(self.left_head_path),curses.A_NORMAL)
        self.right_win.move(0,1)
        self.right_win.clrtoeol()
        self.right_win.border()
        self.right_win.addstr(
            0,
            1,
            str(self.right_head_path),curses.A_STANDOUT |
            curses.color_pair(3)
            )

    def update_headers(self, active_panel):
        self.panel_headers()
        if active_panel == 0:
            self.left_panel_sel()
        else:
            self.right_panel_sel()
        self.refreshln1()
        curses.doupdate()

    def set_active_panel(self, active_panel):
        if active_panel == 0:
            active_panel += 1
        else:
            active_panel = 0
        self.active_panel = active_panel
        return active_panel

    def upd_panel(self, active_panel, path):
        self.path = path
        self.update_headers(active_panel)
