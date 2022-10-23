"""RSync - Python - Terminal User Interface (rsyncpy_tui)"""
#!/usr/bin/env python3.6
import os
import curses
import curses.textpad
import curses.panel
import constants as CONST
from queue_window_refresh import QueueWinRefresh
from options_menu import OptionsMenu
from ssh import SSH
from window_manager import WinManager
from file_explorer import FileExplorer
from reset_window import ResetWindow
from menu_bar import MenuBar
from status_bar import StatusBar
from get_input import GetInput
from key_press import KeyPress
from display import Display

def prepare_curses():
    """Setup terminal for curses operations."""
    stdscr.erase()
    stdscr.keypad(True)
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_CYAN)
    stdscr.bkgdset(curses.color_pair(4))

def end_curses():
    """Gracefully reset terminal to normal settings."""
    stdscr.keypad(0)
    curses.echo()
    curses.nocbreak()
    curses.endwin()
    os.system('reset')

class Main:
    """Main function handles high-level switching between windows and file menus."""
    def __init__(self):
        current_panel = 0
        event = None
        while event != CONST.CONST_LET_Q_LWRCSE_KEY:
            while True:
                win_manager.upd_panel(current_panel, file_explorers[current_panel].path)
                Display(file_explorers[current_panel])
                keyboard_input = GetInput(file_explorers[current_panel]).run()
                event = KeyPress.event(KeyPress, keyboard_input, file_explorers[current_panel], file_explorers[current_panel].data, file_explorers[current_panel].position)
                file_explorers[current_panel].scroll()
                QueueWinRefresh(stdscr)
                if event in (CONST.CONST_LET_F_LWRCSE_KEY, CONST.CONST_LET_O_LWRCSE_KEY):
                    MenuBar(stdscr, event)
                    ResetWindow(left_file_explorer)
                elif event in (CONST.CONST_TAB_KEY, CONST.CONST_LET_Q_LWRCSE_KEY):
                    current_panel = win_manager.switch_panels(current_panel)
                    status_bar.refresh(current_panel)
                    break

if __name__ == '__main__':
    #Setup curses and begin initializing various packages to draw the menubar,
    #left and right windows, statusbar, a ssh object for storage, a global options object
    #for storage and setup the file explorers.
    stdscr = curses.initscr()
    screen_height, screen_width = stdscr.getmaxyx()
    prepare_curses()
    MenuBar(stdscr, event=None)
    win_manager = WinManager(stdscr)
    left_win = win_manager.draw_left_win()
    right_win = win_manager.draw_right_win()
    ssh_obj = SSH()
    START_PATH = os.path.curdir
    left_file_explorer = FileExplorer(win_manager, left_win, path=START_PATH)
    right_file_explorer = FileExplorer(win_manager, right_win, path=START_PATH, ssh_object=ssh_obj)
    file_explorers = [left_file_explorer, right_file_explorer]
    left_file_explorer.get_file_explorers(file_explorers)
    right_file_explorer.get_file_explorers(file_explorers)
    status_bar = StatusBar(stdscr)
    glbl_opts = OptionsMenu(stdscr)
    main = Main()
    ssh_obj.ssh_close()
    end_curses()
