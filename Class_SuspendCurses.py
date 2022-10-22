from Class_QueueWinRefresh import QueueWinRefresh
import curses
import os
from time import sleep

class SuspendCurses:
    def __init__(self, stdscr):
        self.stdscr = stdscr
    """Temporarily leave curses while rsync runs"""
    def __enter__(self):
        self.stdscr.clear()
        QueueWinRefresh(self.stdscr) #stdscr.noutrefresh()
        curses.doupdate()
        self.stdscr.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()
        os.system('reset')
        print('Leaving curses...')
        sleep(.5)

    def __exit__(self, exc_type, exc_val, tb):
        print('\nReturning to curses...')
        print('\n')
        sleep(.5)
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(1)