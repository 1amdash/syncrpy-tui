"""Used to prepare for a screen refresh, noutrefresh is a precurser to doupdate"""
class QueueWinRefresh:
    def __init__(self, win):
        win.noutrefresh() # noutrefresh is a method from curses
