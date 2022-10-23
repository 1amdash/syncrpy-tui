"""key_press module."""
import curses
import constants as CONST
from reset_window import ResetWindow
from pop_ups import PopUpNewDir
from Func_Navigate import navigate

# CONST_LET_F_LWRCSE_KEY = ord('f')
# CONST_LET_O_LWRCSE_KEY = ord('o')
# CONST_ESCAPE_KEY = 27
# CONST_ENTER_KEY = ord('\n')
# CONST_TAB_KEY = ord('\t')
# CONST_LET_Q_KEY = ord('Q')
# CONST_LET_Q_LWRCSE_KEY = ord('q')
# CONST_NUM_9_KEY = ord('9')
# CONST_NUM_5_KEY = ord('5')
# CONST_NUM_9_KEY = ord('9')
# CONST_LET_X_LWRCSE_KEY = ord('x')
# CONST_LET_B_LWRCSE_KEY = ord('b')
# CONST_LET_T_LWRCSE_KEY = ord('t')
# CONST_LET_N_LWRCSE_KEY = ord('n')

class KeyPress:
    def event(self, key_press, explorer, items=None, position=None):
        self._exp = explorer
        event = self.key_or_arrow_event(self, key_press)
        return event(self, key_press, items, position)

    def key_or_arrow_event(self, key_press):
        if key_press in (curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_UP, curses.KEY_DOWN):
            return self.arrow_event
        else:
            return self.key_event

    def arrow_event(self, event, items, position):
        if event == curses.KEY_UP:
            self._exp.position = navigate(-1, items, position)
        elif event == curses.KEY_DOWN:
            self._exp.position = navigate(1, items, position)
        elif event == curses.KEY_RIGHT:
            self._exp.position = navigate(1, items, position)
        elif event == curses.KEY_LEFT:
            self._exp.position = navigate(-1, items, position)

    def key_event(self, event, items=None, position=None): 
        if event == CONST.CONST_ENTER_KEY:
            self.enter_key(self, event)
            return event
        elif event == 27:
            return event
        elif event == CONST.CONST_TAB_KEY:
            return event
        elif event in (CONST.CONST_LET_F_LWRCSE_KEY, CONST.CONST_LET_O_LWRCSE_KEY):
            return event
        elif event == CONST.CONST_LET_Q_LWRCSE_KEY:
            return event
        elif event == CONST.CONST_LET_X_LWRCSE_KEY:
            self.close_ssh_key(self, event)
        elif event == CONST.CONST_NUM_5_KEY:
            self.copy_key(self,event)
        elif event == CONST.CONST_LET_N_LWRCSE_KEY:
            self.new_dir_key(self, event)
        elif event == CONST.CONST_LET_B_LWRCSE_KEY:
            self.to_bottom_key(self)
        elif event == CONST.CONST_LET_T_LWRCSE_KEY:
            self.to_top_key(self)
        elif event == CONST.CONST_NUM_9_KEY:
            self.delete_key(self, items, position)
        else:
            pass

    def to_top_key(self):
        self._exp.go_to_top()

    def to_bottom_key(self):
        self._exp.go_to_bottom()

    def delete_key(self, items, position):
        item = items[position][0]
        self._exp.del_selected_items(self._exp.path + '/' + item)

    def new_dir_key(self, event):
        #self._exp.PopUpNewDir()
        PopUpNewDir()

    def enter_key(self, event):
        self._exp.enter()

    def close_ssh_key(self,event):
        if ssh_obj.is_enabled:
            ssh_obj.ssh.close()
            ssh_obj.enabled()
            win_manager.upd_panel()
            right_file_explorer.explorer(right_file_explorer.path)
            right_file_explorer.menu()
            ResetWindow(right_file_explorer)
        else:
            pass

    def copy_key(self,event):
            self._exp.copy_selected_items()
