"""SYNCRPY-TUI. Main File"""
#!/usr/bin/env python3.6
from Class_QueueWinRefresh import QueueWinRefresh
from Class_PopUpBase import PopUpBase
from Class_OptionsMenu import OptionsMenu
from Class_KeyPress import KeyPress
from Class_SSH import SSH
from Class_SSH import SSHForm
from Class_WinManager import WinManager
from Class_FileExplorer import FileExplorer
from Class_Button import Button
from Class_ResetWindow import ResetWindow
from Class_TextBox import TextBox
from Class_ProgressChecker import ProgressChecker
from Class_SuspendCurses import SuspendCurses
from Class_MenuBar import MenuBar
from Class_StatusBar import StatusBar

import os
import curses
import curses.textpad
import curses.panel
import shutil
import threading
import subprocess
import shlex
import constants as CONST


class display:
    def __init__(self, obj):
        self.obj = obj
        self.window = self.obj.window
        self.event = None

    def run(self):
        event = None
        while event not in (CONST.CONST_TAB_KEY, CONST.CONST_LET_Q_LWRCSE_KEY, CONST.CONST_LET_F_LWRCSE_KEY, CONST.CONST_LET_O_LWRCSE_KEY):
            self.window.keypad(1)
            self.obj.menu()
            curses.doupdate()
            event = self.window.getch()         
            self.event = KeyPress.event(KeyPress, event, self.obj, self.obj.data, self.obj.position)
            if self.obj.scroll:
                self.obj.scroll()
            return event

def reset_winders():
    """Reset Windows"""
    # stdscr.bkgdset(curses.color_pair(4))
    screen_y = stdscr.getmaxyx()[0]
    stdscr.redrawln(0,screen_y)
    MenuBar(event=None)
    stdscr.noutrefresh()
    win_manager.left_win.border()
    win_manager.right_win.border()
    ResetWindow(left_file_explorer)
    ResetWindow(right_file_explorer)
    win_manager.upd_panel(win_manager.active_panel, '/')
    #win_manager.set_active_panel(1)

def callbackFunc(thread):
    thread._is_stopped = True

def PrepareCurses():
    """Setup basic curses configurations."""
    stdscr.erase()
    stdscr.keypad(1)
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_CYAN)
    stdscr.bkgdset(curses.color_pair(4))

def is_term_resized(self):
    #future function to detect if termainl is resized
    #resize_check = curses.is_term_resized(nlines, ncols)
    #self.height_main, self.width_main = stdscr.getmaxyx()
    #if resize_check == True:
        #self.term_resize()
    pass

def term_resize(self):
    #future function to detect if termainl is resized
    curses.resizeterm(self.height_main, self.width_main)

def EndCurses():
    stdscr.keypad(0)
    curses.echo()
    curses.nocbreak()
    curses.endwin()
    os.system('reset')

class Main:
    def __init__(self):
        current_panel = 0
        event = None
        while event != CONST.CONST_LET_Q_LWRCSE_KEY:
            while True:
                win_manager.upd_panel(current_panel, file_explorers[current_panel].path)
                #file_explorers[current_panel].display()
                event = display(file_explorers[current_panel]).run()
                #event = file_explorers[current_panel].event
                QueueWinRefresh(stdscr)
                test_item = CONST.CONST_TAB_KEY
                if event in (CONST.CONST_LET_F_LWRCSE_KEY, CONST.CONST_LET_O_LWRCSE_KEY):
                    MenuBar(stdscr, event)
                    ResetWindow(left_file_explorer)
                elif event in (CONST.CONST_TAB_KEY, CONST.CONST_LET_Q_LWRCSE_KEY):
                    current_panel = win_manager.switch_panels(current_panel)
                    status_bar.refresh(current_panel)
                    break
"""
Setup curses and begin initializing various packages to draw the menubar,
left and right windows, statusbar, a ssh object for storage, a global options object
for storage and setup the file explorers.
"""

if __name__ == '__main__':
    stdscr = curses.initscr()
    screen_height, screen_width = stdscr.getmaxyx()
    PrepareCurses()
    MenuBar(stdscr, event=None)
    win_manager = WinManager(stdscr)
    left_win = win_manager.draw_left_win()
    right_win = win_manager.draw_right_win()
    ssh_obj = SSH()
    start_path = os.path.curdir
    left_file_explorer = FileExplorer(win_manager, left_win, path=start_path)
    right_file_explorer = FileExplorer(win_manager, right_win, path=start_path, ssh_object=ssh_obj)
    file_explorers = [left_file_explorer, right_file_explorer]
    #reset_left_window = ResetWindow(left_file_explorer)
    #reset_right_window = ResetWindow(right_file_explorer)

    status_bar = StatusBar(stdscr)
    glbl_opts = OptionsMenu(stdscr)
    main = Main()
    ssh_obj.ssh_close()
    EndCurses()
