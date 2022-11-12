"""KeyPress Class"""
import curses
import constants as CONST
from pop_ups import PopUpNewDir
from navigate import navigate
from get_input import GetInput


class KeyPress:
    """Call function based on keypress

    This Class utilizes the curses module to evaluate a keypress (arrow keys, enter, escape, etc)
    and complete an action."""
    def __init__(self, obj, items=None, position=None):
        self.obj = obj
        self.items = items
        self.tab_event = False
        self.menu_event = False
        self.position = position
        self.get_input(obj)
        self.key_or_arrow_event()

    def __call__(self, *args, **kwds):
        return self.key

    def get_input(self, obj):
        obj.window.keypad(True)
        try:
            self.key = obj.window.getch()
        except KeyboardInterrupt:
            return


    def key_or_arrow_event(self):
        if self.key in (curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_UP, curses.KEY_DOWN):
            self.arrow_event()
        else:
            self.key_event()
        
    def arrow_event(self):
        if self.key == curses.KEY_UP:
            self.obj.position = navigate(-1, self.items, self.position)
        elif self.key == curses.KEY_DOWN:
            self.obj.position = navigate(1, self.items, self.position)
        elif self.key == curses.KEY_RIGHT:
            self.obj.position = navigate(1, self.items, self.position)
        elif self.key == curses.KEY_LEFT:
            self.obj.position = navigate(-1, self.items, self.position)

    def key_event(self):
        event = self.key
        if event == CONST.CONST_ENTER_KEY:
            enter_key_event = KeyPress.enter_key(obj)
            if enter_key_event is not None:
                event = enter_key_event
            return event
        #elif event == 'ssh':
        #    return self.open_program(event)
        elif event == CONST.CONST_ESCAPE_KEY:
            return event
        elif event == CONST.CONST_TAB_KEY:
            self.tab_event = True
        elif event in (CONST.CONST_LET_F_LWRCSE_KEY, CONST.CONST_LET_O_LWRCSE_KEY):
            self.menu_event = True
        elif event == CONST.CONST_LET_Q_LWRCSE_KEY:
            return event
        elif event == CONST.CONST_LET_X_LWRCSE_KEY:
            KeyPress.close_ssh_key(event)
        elif event == CONST.CONST_NUM_5_KEY:
            KeyPress.copy_key(obj)
        elif event == CONST.CONST_LET_N_LWRCSE_KEY:
            KeyPress.new_dir_key(obj, event)
        elif event == CONST.CONST_LET_B_LWRCSE_KEY:
            KeyPress.to_bottom_key(obj)
        elif event == CONST.CONST_LET_T_LWRCSE_KEY:
            KeyPress.to_top_key(obj)
        elif event == CONST.CONST_NUM_9_KEY:
            KeyPress.delete_key(obj, items, position)
        else:
            pass

    @staticmethod
    def to_top_key(obj):
        obj.go_to_top()

    @staticmethod
    def to_bottom_key(obj):
        obj.go_to_bottom()

    @staticmethod
    def delete_key(obj, items, position):
        item = items[position][0]
        obj.del_selected_items(obj._exp.path + '/' + item)

    @staticmethod
    def new_dir_key():
        PopUpNewDir()

    @staticmethod
    def enter_key(obj):
        item = obj.enter()
        if item is not None:
            return item

    @staticmethod
    def close_ssh_key(obj):
        if KeyPress.ssh_obj.is_enabled:
            ssh_obj.ssh.close()
            ssh_obj.enabled()
            win_manager.upd_panel()
            #right_file_explorer.explorer(right_file_explorer.path)
            #right_file_explorer.menu()
            #ResetWindow(right_file_explorer)
        else:
            pass

    @staticmethod
    def copy_key(obj):
        obj.copy_selected_items()
