"""status_bar module"""
import curses
from window_manager import WinManager
from queue_window_refresh import QueueWinRefresh
from ssh import SSH

class StatusBar:
    """Creates a statusbar at the bottom of the main screen and can be called to update the bar"""
    status_bar_str = ''
    text = ''
    panel = ''
    def __init__(self, stdscr):
        self.height_main, self.width_main = stdscr.getmaxyx()
        self.status_bar_area = stdscr
        self.color = curses.color_pair(3)
        self.status_bar_area.move(self.height_main-1, len(self.status_bar_str))
        self.status_bar_area.clrtoeol()
        self.status_bar_str = ' '
        self.status_bar_area.addstr(self.height_main-1, 0, self.status_bar_str, self.color)
        self.statusbar_len = len(self.status_bar_str)
        self.statusbar_remaining = self.width_main - len(self.status_bar_str) - 1
        self.status_bar_area.addstr(
            self.height_main-1,
            self.statusbar_len,
            " " * self.statusbar_remaining,
            self.color
            )
        self.status_bar_area.redrawln(self.height_main-1,0)
        self.refresh('0')

    def update(self, panel):
        self.status_bar_area.move(self.height_main-1, 0)
        self.status_bar_area.clrtoeol()
        panel = 'active panel: ' + str(panel)
        if SSH.is_enabled:
            ssh_status = 'SSH Enabled'
        else:
            ssh_status = 'SSH Disabled'
        self.statusbar_remaining = self.width_main - len(panel) - len(ssh_status) - 1
        spaces = ' ' * self.statusbar_remaining
        self.status_bar_str = f'{panel}{spaces}{ssh_status}'
        self.statusbar_len = len(self.status_bar_str)
        if self.statusbar_len < self.width_main:
            self.status_bar_area.addstr(self.height_main-1, 0, self.status_bar_str, self.color)
        self.status_bar_area.redrawln(self.height_main-1,0)
        QueueWinRefresh(self.status_bar_area)

    def refresh(self, panel):
        self.update(panel)
        curses.doupdate()
