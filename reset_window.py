from queue_window_refresh import QueueWinRefresh
class ResetWindow:
    """When called, redraws windows"""
    def __init__(self, explorer):
        self.explorer = explorer
        self.redraw()

    def __getattr__(self, attr):
        return getattr(self.explorer, attr)

    def redraw(self):
        self.window.redrawwin()
        QueueWinRefresh(self.window)
        self.pad_refresh()
        self.menu()
