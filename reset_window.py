from queue_window_refresh import QueueWinRefresh
class ResetWindow:
    """When called, redraws windows, touched method is not used right now"""
    def __init__(self, explorer):
        self.argument_type(explorer)
        self.redraw()

    def __getattr__(self, attr):
        return getattr(self.explorer, attr)

    #def touched(self):
    #    touched = self.window.is_wintouched()
    #    self.redraw()

    def argument_type(self, explorer):
        if explorer is type(list):
            self.explorer = explorer[0]
            self.redraw()
            self.explorer = explorer[1]
        else:
            self.explorer = explorer

    def redraw(self):
        self.window.redrawwin()
        QueueWinRefresh(self.window) #self.window.noutrefresh()
        self.pad_refresh()
        self.menu()
