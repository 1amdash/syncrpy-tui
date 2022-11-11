"""RSync - Python - Terminal User Interface (rsyncpy_tui)"""
#!/usr/bin/env python3.6
import os
import curses
import curses.textpad
import curses.panel
import constants as CONST
from options_menu import OptionsMenu
from ssh import SSH
from window_manager import WinManager
from file_explorer import FileExplorer
from reset_window import ResetWindow
from menu_bar import MenuBar
from status_bar import StatusBar
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
    stdscr.bkgdset(curses.color_pair(3))


def end_curses():
    """Gracefully reset terminal to normal settings."""
    stdscr.keypad(0)
    curses.echo()
    curses.nocbreak()
    curses.endwin()
    os.system('reset')


class Main:
    """Main function handles high-level switching between windows and file menus."""
    def __init__(self, menu_bar, win_manager, file_explorers, status_bar):
        _menu_bar = menu_bar
        _win_manager = win_manager
        _file_explorers = file_explorers
        _status_bar = status_bar
        _current_panel = 0
        ready_to_exit = False
        while ready_to_exit is not True:
            _win_manager.upd_panel(_current_panel, _file_explorers[_current_panel].path)
            Display(_file_explorers[_current_panel])
            key_press = KeyPress(
                _file_explorers[_current_panel],
                _file_explorers[_current_panel].data,
                _file_explorers[_current_panel].position,
                )
            _file_explorers[_current_panel].scroll()
            event = self.call_menu(key_press.menu_event, _menu_bar, self.call_ssh)
            _current_panel = self.switch_panels(key_press.tab_event, _current_panel, _status_bar)
            ready_to_exit = self.exit_main_loop(key_press)
            curses.doupdate()

    def exit_main_loop(self, event):
        if event == CONST.CONST_LET_Q_LWRCSE_KEY:
            return True

    def call_menu(self, call_menu_event, _menu_bar, _call_ssh):
        ready_to_return = False
        if call_menu_event is True:
            while ready_to_return is not True:
                _menu_bar(menu_event)
                Display(_menu_bar)
                _menu_event = KeyPress(
                    _menu_bar,
                    _menu_bar.menu_item,
                    _menu_bar.position
                    )
                _call_ssh(_menu_event)
                _ssh_is_enabled = ssh_enabled()
                ready_to_return = self.return_to_main_loop(_menu_event, _ssh_is_enabled)
        else:
            return call_menu_event

    def update_all_views(self, _menu_bar, _file_explorers, _status_bar):
        _left_file_explorer = _file_explorers[0]
        _right_file_explorer = _file_explorers[1]
        _menu_bar.draw_menu_bar()
        ResetWindow(_left_file_explorer)
        ResetWindow(_right_file_explorer)
        _status_bar.refresh(1)
        curses.doupdate()

    def call_ssh(self, event, _status_bar):
        if event == 'ssh':
            ssh_object.start(win_manager, stdscr, None)

    def ssh_enabled(self):
        return ssh_object.is_enabled

    def return_to_main_loop(self,event, ssh_is_enabled):
        if event in (
            CONST.CONST_LET_F_LWRCSE_KEY,
            CONST.CONST_LET_O_LWRCSE_KEY,
            CONST.CONST_LET_Q_LWRCSE_KEY
            ) or ssh_is_enabled is True:
            return True

    def switch_panels(self, tab_event, _current_panel, _status_bar):
        if tab_event is True:
            _current_panel = win_manager.set_active_panel(_current_panel)
            _status_bar.refresh(_current_panel)
            return _current_panel
        else:
            return _current_panel


if __name__ == '__main__':
    #Setup curses and begin initializing various packages to draw the menubar,
    #left and right windows, statusbar, a ssh object for storage, a global options object
    #for storage and setup the file explorers.
    stdscr = curses.initscr()
    screen_height, screen_width = stdscr.getmaxyx()
    prepare_curses()
    menu_bar = MenuBar(stdscr)
    win_manager = WinManager(stdscr)
    left_win = win_manager.draw_left_win()
    right_win = win_manager.draw_right_win()
    ssh_object = SSH()
    left_file_explorer = FileExplorer(win_manager, left_win)
    right_file_explorer = FileExplorer(win_manager, right_win, ssh_object=ssh_object)
    file_explorers = [left_file_explorer, right_file_explorer]
    left_file_explorer.get_file_explorers(file_explorers)
    right_file_explorer.get_file_explorers(file_explorers)
    status_bar = StatusBar(stdscr)
    global_options = OptionsMenu(stdscr)
    main = Main(menu_bar, win_manager, file_explorers, status_bar)
    ssh_object.ssh_close()
    end_curses()
