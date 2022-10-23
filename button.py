class Button:
    """Meant to be a portable Button"""
    def __init__(self, window, list):
        self.window = window
        self.list = list

        self.button_press_ok = False
        self.button_press_cancel = False
        self.position = 0
        self.client_ready = None
        self.window.keypad(1)
        self.menu()

    def enter(self):
        """Position 0 == Ok, 1 == Cancel."""
        if self.position == 0:
            self.button_press_ok = True
        else:
            self.button_press_cancel = True
        return

    def display(self):
        event = None
        while event not in (CONST.CONST_ESCAPE_KEY, CONST.CONST_TAB_KEY, CONST.CONST_ENTER_KEY):
            self.menu()
            if self.client_ready:
                event = CONST.CONST_ENTER_KEY
                return
            else:
                event = self.window.getch()
                event = KeyPress.event(KeyPress, event, self, self.list, self.position)

    def event(self, action):
        self.client_ready = action

    def menu(self):
        space = 10
        for index, x in enumerate(self.list):
            if index == self.position:
                mode = curses.A_REVERSE
            else:
                mode = curses.A_NORMAL
            self.window.addstr(5, space, str(x), mode)
            space += 10
        QueueWinRefresh(self.window)
        curses.doupdate()