import curses
from enum import Enum
import csv
import time
import os

import terminal_map

def read_csv(file) -> list[list[str]]:
    rows = []
    with open(file, "r") as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            rows.append([cell for cell in row])
    return rows

def lpadalign(text:str, length:int) -> str:
    if len(text) > length:
        return text[0:length]
    else:
        return text.ljust(length)


def lerp(out_min: float, out_max: float, in_min: float, in_max: float, value: float) -> float:
    if in_max == in_min:
        return out_min
    return out_min + (out_max - out_min) * ((value - in_min) / (in_max - in_min))

def has_file(file_name) :
    return os.path.isfile(file_name)

def make_file(file_name):
    file = open(file_name, "+a")
    file.close()

class WindowNavigation(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3
    RETURN = 4
    TAB = 5
    NOMOVE = 6

class CurrentScene(Enum):
    LOGIN = 0
    LISTSEARCH = 1
    LOCATIONSEARCH = 2

class Window:

    width = 0
    height = 0

    xpos = 0
    ypos = 0

    def __init__(self, parent_window : curses.window, **kwargs):
        self.__dict__.update(kwargs)
        self._window = parent_window.subwin(self.height, self.width, 0, 0)

        self.height, self.width = self._window.getmaxyx()
    
    def redraw(self):
        """Redraws the entire window"""
        self._window.clear()
        self._window.redrawwin()
        self._window.refresh()

    def move(self, x : int, y : int):
        """Moves the curser"""
        if x == self.xpos and y == self.ypos:
            return
        self.xpos = x
        self.ypos = y
        self._window.move(self.ypos, self.xpos)

    def movewindow(self, x : int, y : int):
        self._window.mvwin(y, x)

    def resize(self, width: int, height: int):
        self.width = width
        self.height = height
        self._window.resize(height, width)

    def handle_keyinput(self, ch : int) -> WindowNavigation:
        return True
    
    def place(self, x: int, y: int, width: int, height: int):
        self.resize(width, height)
        self.movewindow(x, y)
        self._window.clear()
        self._window.redrawwin()

    def write(self, y:int, x:int, text: str, attr = None):

        if y >= self.height - 1 or x >= self.width or y < 0:
            return
        if x + len(text) > self.width:
            text = text[:self.width - x]
        if x < 0:
            text = text[-x:]
            x = 0
        if attr is None:
            self._window.addstr(y, x, text)
        else:
            self._window.addstr(y, x, text, attr)

class PreLoginScreen(Window):

    def __init__(self, parent_window, **kwargs):
        super().__init__(parent_window, **kwargs)
        curses.curs_set(0)
        self._window.bkgd(' ', curses.color_pair(1))
        self.redraw()

    def get_positions(self):

        height, width = self._window.getmaxyx()
        start_y = height // 2
        start_x = width // 2
        text_start_x = start_x + 12

        return height, width, start_y, start_x

    def get_dots_string(self):
        return "..."

    def redraw(self):
        self._window.clear()

        height, width, start_y, start_x = self.get_positions()


        self.write(3, 3, " +                      + ", curses.color_pair(0) | curses.A_BOLD)
        self.write(4, 3, "*##                    ##*", curses.color_pair(0) | curses.A_BOLD)
        self.write(5, 3, " *#.                  .#* ", curses.color_pair(0) | curses.A_BOLD)
        self.write(6, 3, "  *###.            .###*  ", curses.color_pair(0) | curses.A_BOLD)
        self.write(7, 3, "  .  *##+        +##*  .  ", curses.color_pair(0) | curses.A_BOLD)
        self.write(8, 3, "   ###.            .###   ", curses.color_pair(0) | curses.A_BOLD)
        self.write(9, 3, "    *####::*  *::####*    ", curses.color_pair(0) | curses.A_BOLD)
        self.write(10, 3, "         .  @@  .         ", curses.color_pair(0) | curses.A_BOLD)
        self.write(11, 3, "        ##: @@ :##        ", curses.color_pair(0) | curses.A_BOLD)
        self.write(12, 3, "       *##  ..  ##*       ", curses.color_pair(0) | curses.A_BOLD)
        self.write(13, 3, "           *##*           ", curses.color_pair(0) | curses.A_BOLD)
        self.write(14, 3, "            **            ", curses.color_pair(0) | curses.A_BOLD)

        self.write(start_y - 1, start_x - 23, "Waiting for Mainframe to start remote accesses.", curses.color_pair(0) | curses.A_BOLD)
        self.write(start_y + 1, start_x - 23, self.get_dots_string(), curses.color_pair(0) | curses.A_BOLD)


        self._window.refresh()

    
    def handle_keyinput(self, ch: int) -> WindowNavigation:
        out: WindowNavigation = WindowNavigation.NOMOVE
        return out

class LoginScreen(Window):
    username : str = ""
    password: str = ""
    max_width: int = 20
    on_username = True
    display_results = False

    def __init__(self, parent_window, **kwargs):
        curses.curs_set(1)
        super().__init__(parent_window, **kwargs)
        self._window.bkgd(' ', curses.color_pair(1))
        self.redraw()
        self.set_curser_location()


    def select(self) -> None:
        curses.curs_set(1)

    def set_curser_location(self) -> None:
        """Position cursor at the end of active input."""
        height, width, start_y, start_x, text_start_x = self.get_positions()
        
        if self.on_username:
            self._window.move(start_y + 4, text_start_x + len(self.username))
        else:
            self._window.move(start_y + 6, text_start_x + len(self.password))

    def get_positions(self):

        height, width = self._window.getmaxyx()
        start_y = height // 2 - 5
        start_x = width // 2 - 24
        text_start_x = start_x + 12

        return height, width, start_y, start_x, text_start_x

    def draw_username(self):
        height, width, start_y, start_x, text_start_x = self.get_positions()
        self.write(start_y + 4, text_start_x, self.username.ljust(self.max_width))


    def draw_password(self):
        height, width, start_y, start_x, text_start_x = self.get_positions()
        masked_password = "*" * len(self.password)
        self.write(start_y + 6, text_start_x, masked_password.ljust(self.max_width))

    def redraw(self):
        self._window.clear()
        height, width, start_y, start_x, text_start_x = self.get_positions()

        # Title
#        self.write(
#            start_y, start_x + 5, "▄▄▄ LOGIN ▄▄▄",
#            curses.color_pair(2) | curses.A_BOLD)
        

        self.write(3, 3, " +                      + ", curses.color_pair(0) | curses.A_BOLD)
        self.write(4, 3, "*##                    ##*", curses.color_pair(0) | curses.A_BOLD)
        self.write(5, 3, " *#.                  .#* ", curses.color_pair(0) | curses.A_BOLD)
        self.write(6, 3, "  *###.            .###*  ", curses.color_pair(0) | curses.A_BOLD)
        self.write(7, 3, "  .  *##+        +##*  .  ", curses.color_pair(0) | curses.A_BOLD)
        self.write(8, 3, "   ###.            .###   ", curses.color_pair(0) | curses.A_BOLD)
        self.write(9, 3, "    *####::*  *::####*    ", curses.color_pair(0) | curses.A_BOLD)
        self.write(10, 3, "         .  @@  .         ", curses.color_pair(0) | curses.A_BOLD)
        self.write(11, 3, "        ##: @@ :##        ", curses.color_pair(0) | curses.A_BOLD)
        self.write(12, 3, "       *##  ..  ##*       ", curses.color_pair(0) | curses.A_BOLD)
        self.write(13, 3, "           *##*           ", curses.color_pair(0) | curses.A_BOLD)
        self.write(14, 3, "            **            ", curses.color_pair(0) | curses.A_BOLD)

        self.write(start_y, start_x + 3, "┏━━━━━━━┓", curses.color_pair(0) | curses.A_BOLD)
        self.write(start_y + 1, start_x, "┏━━┫ LOGIN ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓", curses.color_pair(0) | curses.A_BOLD)
        self.write(start_y + 2, start_x, "┃  ┗━━━━━━━┛                               ┃", curses.color_pair(0) | curses.A_BOLD)
        self.write(start_y + 3, start_x, "┃                                          ┃", curses.color_pair(0) | curses.A_BOLD)
        self.write(start_y + 4, start_x, "┃ Username:                                ┃", curses.color_pair(0) | curses.A_BOLD)
        self.write(start_y + 5, start_x, "┃                                          ┃", curses.color_pair(0) | curses.A_BOLD)
        self.write(start_y + 6, start_x, "┃ Password:                                ┃", curses.color_pair(0) | curses.A_BOLD)
        self.write(start_y + 7, start_x, "┃                                          ┃", curses.color_pair(0) | curses.A_BOLD)
        self.write(start_y + 8, start_x, "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛", curses.color_pair(0) | curses.A_BOLD)

        # Username label and input
        self.write(start_y + 4, start_x + 2, "Username: ")

        # Password label and input
        self.write(start_y + 6, start_x + 2, "Password: ")

        self.draw_username()
        self.draw_password()

        # Display result
        if self.display_results:
            self.write(start_y + 9, start_x, f"Username: {self.username}")
            self.write(start_y + 10, start_x, f"Password: {self.password}")

            self.write(start_y + 11, start_x, "Not correct try again")

        self.set_curser_location()
        # this will redraw the whole frame
        self._window.refresh()

    
    def handle_keyinput(self, ch: int) -> WindowNavigation:
    
        height, width, start_y, start_x, text_start_x = self.get_positions()

        out: WindowNavigation = WindowNavigation.NOMOVE
        if ch == ord('\n'):
            # this should more down
            if self.on_username:
                self.on_username = False
            else:
                self.display_results = True
                # test input
                if self.username == "user" and self.password == "password":
                    out = WindowNavigation.RETURN
                else:
                    self.redraw()
                # on success return 
                # on failure
        elif ch == curses.KEY_UP or ch == curses.KEY_DOWN:
            self.on_username = not self.on_username

        elif ch == curses.KEY_BACKSPACE or ch == 127:  # backspace character
            if (self.on_username):
                if self.username:
                    self.username = self.username[:-1]
                    self.draw_username()
            else:
                if self.password:
                    self.password = self.password[:-1]
                    self.draw_password()


        elif ch >= 32 and ch <= 126:  # printable ASCII only
            if self.on_username and len(self.username) < self.max_width:
                self.username += chr(ch)
                self.draw_username()
            elif len(self.password) < self.max_width:
                self.password += chr(ch)
                self.draw_password()

        
        # redraw line of user name or password

        
        if self.on_username:
            self._window.redrawln(start_y + 2, 1)
        else:
            self._window.redrawln(start_y + 4, 1)
        
        self.set_curser_location()

        self._window.refresh()

        return out

class Scene:
    windows = []

    def __init__(self, manager):
        pass
        
    def handle_keyinput(self, ch: int) -> WindowNavigation:
        pass

    def close(self):
        pass

    def redraw(self):
        pass

class LogInScene(Scene):

    #loginwindow

    def __init__(self, manager):
        self.manager = manager
        self.loginwindow = LoginScreen(manager.top_level_window)

    def handle_keyinput(self, ch: int) -> WindowNavigation:
        
        result = self.loginwindow.handle_keyinput(ch)
        if result == WindowNavigation.RETURN:
            return WindowNavigation.RETURN
        return WindowNavigation.NOMOVE
    
    def close(self):
        self.loginwindow._window.clear()
        self.loginwindow._window.redrawwin()
        self.loginwindow._window.refresh()
        del self.loginwindow._window
        del self.loginwindow

    def redraw(self):
        height, width = self.manager.top_level_window.getmaxyx()
        
        # Create windows for layout
        self.loginwindow.place(0, 0, width, height)

        self.loginwindow.redraw()


class PreListScreen(Window):

    def __init__(self, parent_window, **kwargs):
        super().__init__(parent_window, **kwargs)
        curses.curs_set(0)
        self._window.bkgd(' ', curses.color_pair(1))
        self.redraw()

    def get_positions(self):

        height, width = self._window.getmaxyx()
        start_y = height // 2
        start_x = width // 2
        text_start_x = start_x + 12

        return height, width, start_y, start_x

    def get_dots_string(self):
        return "..."

    def redraw(self):
        self._window.clear()

        height, width, start_y, start_x = self.get_positions()


        self.write(3, 3, " +                      + ", curses.color_pair(0) | curses.A_BOLD)
        self.write(4, 3, "*##                    ##*", curses.color_pair(0) | curses.A_BOLD)
        self.write(5, 3, " *#.                  .#* ", curses.color_pair(0) | curses.A_BOLD)
        self.write(6, 3, "  *###.            .###*  ", curses.color_pair(0) | curses.A_BOLD)
        self.write(7, 3, "  .  *##+        +##*  .  ", curses.color_pair(0) | curses.A_BOLD)
        self.write(8, 3, "   ###.            .###   ", curses.color_pair(0) | curses.A_BOLD)
        self.write(9, 3, "    *####::*  *::####*    ", curses.color_pair(0) | curses.A_BOLD)
        self.write(10, 3, "         .  @@  .         ", curses.color_pair(0) | curses.A_BOLD)
        self.write(11, 3, "        ##: @@ :##        ", curses.color_pair(0) | curses.A_BOLD)
        self.write(12, 3, "       *##  ..  ##*       ", curses.color_pair(0) | curses.A_BOLD)
        self.write(13, 3, "           *##*           ", curses.color_pair(0) | curses.A_BOLD)
        self.write(14, 3, "            **            ", curses.color_pair(0) | curses.A_BOLD)

        self.write(start_y - 1, start_x - 23, "Waiting for Mainframe to start file transfer.", curses.color_pair(0) | curses.A_BOLD)
        self.write(start_y + 1, start_x - 23, self.get_dots_string(), curses.color_pair(0) | curses.A_BOLD)

        self._window.refresh()

    
    def handle_keyinput(self, ch: int) -> WindowNavigation:
        out: WindowNavigation = WindowNavigation.NOMOVE
        return out


location_of_change = 440

class ListSceneTop(Window):

    def __init__(self, parent_scene, parent_window, **kwargs):
        self.parent_scene = parent_scene
        super().__init__(parent_window, **kwargs)
        self._window.bkgd(' ', curses.color_pair(1))
        super().redraw()

    def redraw(self):
        super().redraw()
        self.draw()

    def draw(self):
#        self.write(1, 1, "Flavor Text", curses.A_BOLD)
        self._window.clear()

        heigh, width = self._window.getmaxyx()
        display_width = width // 3 - 14

        location_1 = 6
        location_2 = location_1 + display_width + 7
        display_width_2 = width - location_2 - 6

        self.write(1, location_1, " Flavor ", curses.color_pair(3))
        self.write(1, location_2, f" {"So Much Flavor".ljust(display_width_2-2)} ", curses.color_pair(3))
        self.write(3, location_1, " Text   ", curses.color_pair(3))
        self.write(3, location_2, f" {"I Just can't get enough flavor".ljust(display_width_2-2)} ", curses.color_pair(3))

class ListSceneLeft(Window):

    selected_button:int = 1

    def __init__(self, parent_scene, parent_window, **kwargs):
        self.parent_scene = parent_scene
        super().__init__(parent_window, **kwargs)
        self._window.bkgd(' ', curses.color_pair(1))
        self.redraw()

    def redraw(self):
        self._window.clear()
        self._window.redrawwin()
        self.draw()

    def draw(self):
        heigh, width = self._window.getmaxyx()

        location_1 = 6

        if self.selected_button == 0:
            self.write(3, location_1, " UP     ", curses.A_BOLD | curses.color_pair(2))
        else:
            self.write(3, location_1, " UP     ", curses.A_BOLD | curses.color_pair(4))

        if self.selected_button == 1:
            self.write(heigh // 2, location_1, " SELECT ", curses.A_BOLD | curses.color_pair(2))
        else:
            self.write(heigh // 2, location_1, " SELECT ", curses.A_BOLD | curses.color_pair(4))


        if self.selected_button == 2:
            self.write(heigh - 4, location_1, " DOWN   ", curses.A_BOLD | curses.color_pair(2))
        else:
            self.write(heigh - 4, location_1, " DOWN   ", curses.A_BOLD | curses.color_pair(4))

    def handle_keyinput(self, ch: int) -> WindowNavigation:
        out: WindowNavigation = WindowNavigation.NOMOVE
        if ch == ord('\n'):
            # run current button
            if self.selected_button == 0:
                # up button
                self.parent_scene.move(-1)
                return WindowNavigation.NOMOVE
                pass
            elif self.selected_button == 1:
                if self.parent_scene.correct_selected():
                    return WindowNavigation.RETURN
                # this is the selected button
                # if hit on the location go to the next section
                pass
            elif self.selected_button == 2:
                # down button
                self.parent_scene.move(1)
                return WindowNavigation.NOMOVE

        elif ch == curses.KEY_UP:
            self.selected_button -=1
            if self.selected_button < 0:
                out = WindowNavigation.UP
            self.draw()
            self._window.refresh()

        elif ch == curses.KEY_DOWN:
            self.selected_button += 1
            if self.selected_button > 2:
                out = WindowNavigation.DOWN
            self.draw()
            self._window.refresh()
        return out

class ListSceneRight(Window):

    current_selected = 0

    spacing_char = "│"
    vertical_space_char = "─"
    corner_space_char = "┼"
    header_height = 2

    def __init__(self, parent_scene, parent_window, **kwargs):
        self.parent_scene = parent_scene
        super().__init__(parent_window, **kwargs)
        self._window.bkgd(' ', curses.color_pair(0))

        self.data = read_csv("./location_flavortext.csv")


    def redraw(self):
        self._window.clear()
        self.draw()

    def draw(self):
#        self._window.clear()

        height, width = self._window.getmaxyx()

        list_height = height - self.header_height

        data_line = min(max(0, self.current_selected - height//2 + self.header_height), len(self.data) - list_height + 1)

        for window_line in range(self.header_height, height):
            if data_line >= len(self.data):
                break

            # format according to Time Date Location
            data_row = self.data[data_line]

            width_1 = width // 3 - 3
            width_2 = width // 3 - 3
            width_3 = width - width_1 - width_2 - 9

            formatted_string = f" {lpadalign(str(data_row[1]), width_1)} {self.spacing_char} {lpadalign(str(data_row[2]), width_2)} {self.spacing_char} {lpadalign(str(data_row[0]), width_3)}"

            if data_line == self.current_selected:
                self.write(window_line, 1, formatted_string, curses.A_BOLD | curses.color_pair(2))
            else:
                self.write(window_line, 1, formatted_string, curses.A_BOLD | curses.color_pair(1))
            data_line += 1

        formatted_label = f" {lpadalign("Date", width_1)} {self.spacing_char} {lpadalign("Time", width_2)} {self.spacing_char} {lpadalign("Location", width_3)}"
        formatted_spacer = self.vertical_space_char * (width_1 + 2) +self.corner_space_char +self.vertical_space_char * (width_2 + 2) +self.corner_space_char +self.vertical_space_char * (width_3) + " "
        self.write(0, 1, formatted_label, curses.A_BOLD | curses.color_pair(0))
        self.write(1, 1, formatted_spacer, curses.A_BOLD | curses.color_pair(1))


    def update(self):
        new_selected = 0 # read from file or something
        if self.current_selected == new_selected:
            return
        else:
            self.current_selected = new_selected
            self.draw()

    def correct_selected(self):
        # TODO need to get flavor text and set the correct tomorrow
        return self.current_selected == location_of_change
    
    def move(self, n : int):
        new = self.current_selected+n
        new = max(0, new)
        new = min(len(self.data)-1, new)
        self.current_selected = new

        self.draw()
        self._window.refresh()

class ListSceneBottom(Window):

    entries: int = None
    current_entre: int = 0 # point to something
    search_location: int = None
    search_bar_length: int = 0
    search_text: str = ""

    _display_width:int = 7


    def __init__(self, parent_scene, parent_window, **kwargs):
        self.parent_scene = parent_scene
        super().__init__(parent_window, **kwargs)
        self._window.bkgd(' ', curses.color_pair(1))

    def redraw(self):
        super().redraw()
        self.draw()

    def get_display_text(self):
        self.current_entre = self.parent_scene.window_body.current_selected
        self.entries = len(self.parent_scene.window_body.data)
        current_location = f" {self.current_entre:5} " if self.current_entre is not None else " XXXXX "
        search_location = f" {self.search_location:5} " if self.search_location is not None else " XXXXX "
        total_entries = f" {self.entries:5} " if self.entries is not None else " XXXXX "

        return current_location, search_location, total_entries

    def draw(self):
        heigh, width = self._window.getmaxyx()
        location_1 = 10
        location_2 = location_1 + self._display_width * 2
        location_3 = max(location_2 + self._display_width * 2, int(width * .4))
        location_4 = width - 10 - self._display_width 

        self.search_bar_length = location_4 - self._display_width - location_3

        display_text = self.get_display_text()

        self.write(1, location_1, display_text[0], curses.color_pair(3))
        self.write(1, location_2, display_text[1], curses.color_pair(3))
        self.write(1, location_4, display_text[2], curses.color_pair(3))
        self.draw_search_text()

    def update_search(self, data):
        if self.search_text.upper == "TOMORROW" or self.search_text.upper() == "CALTECH":
#            self.entries = len(data)
            self.search_location = location_of_change
        else:
            self.search_location = None
    
    def draw_search_text(self):
        heigh, width = self._window.getmaxyx()
        location_1 = 10
        location_2 = location_1 + self._display_width * 2
        location_3 = max(location_2 + self._display_width * 2, int(width * .4))

        print_text = f" {self.search_text.ljust(self.search_bar_length - 2)} "

        self.write(1, location_3, print_text, curses.color_pair(3))
        
        self._window.move(1, location_3 + min(len(self.search_text), self.search_bar_length - 2) + 1)



    def handle_keyinput(self, ch):
        out = WindowNavigation.NOMOVE
        
        if ch == curses.KEY_UP:
            out = WindowNavigation.UP
        elif ch == curses.KEY_DOWN:
            out = WindowNavigation.DOWN

        
        elif ch == ord('\n'):
            # redraw window with new status
            out = WindowNavigation.RETURN
            self.draw()
            self._window.refresh()

        elif ch == curses.KEY_BACKSPACE or ch == 127:
            self.search_text = self.search_text[:-1]
            self.draw_search_text()
            self._window.refresh()
            
        elif ch >= 32 and ch <= 126:  # printable ASCII only
            if len(self.search_text) < self.search_bar_length:
                self.search_text += chr(ch)
                self.draw_search_text()
                self._window.refresh()

        return out

class ListScene(Scene):
    """Displays date time location entries and has an interface to search those entries"""

    selected_window: Window = None

    def __init__(self, manager):
        self.manager = manager

        # hide curser
        curses.curs_set(0)

        # Create windows for layout
        self.window_header : ListSceneTop = ListSceneTop(self, self.manager.top_level_window)
        self.window_body_left: ListSceneLeft = ListSceneLeft(self, self.manager.top_level_window)
        self.window_body: ListSceneRight = ListSceneRight(self, self.manager.top_level_window)
        self.window_footer: ListSceneBottom = ListSceneBottom(self, self.manager.top_level_window)

        self.windows = [self.window_header, self.window_body_left, self.window_body, self.window_footer]
        self.manager.top_level_window.refresh()

        self.selected_window = self.window_body_left

        self.redraw()

    def redraw(self):
        height, width = self.manager.top_level_window.getmaxyx()
        
        # Calculate dimensions for layout
        header_height = 5
        footer_height = 3
        body_height = height - header_height - footer_height
        
        body_left_width = int(width * 0.2)
        body_right_width = width - body_left_width

        # Create windows for layout
        self.window_header.place(0, 0, width, header_height)
        self.window_body_left.place(0, header_height, body_left_width, body_height)
        self.window_body.place(body_left_width, header_height, body_right_width, body_height)
        self.window_footer.place(0, height - footer_height, width, footer_height)

#        self.manager.top_level_window.redrawwin()
#        self.manager.top_level_window.refresh()


        self.draw_layout()

    def correct_selected(self):
        return self.window_body.correct_selected()

    def draw_layout(self):
        """Draw the main layout structure"""

        for window in self.windows:
#            window._window.clear()
            window.redraw()
            window._window.refresh()

    def handle_keyinput(self, ch):
        if self.selected_window:
            navigation = self.selected_window.handle_keyinput(ch)
        elif self.window_body_left:
            self.selected_window = self.window_body_left
            curses.curs_set(0)
            navigation = self.selected_window.handle_keyinput(ch)
        else:
            return WindowNavigation.NOMOVE
        

        if navigation == WindowNavigation.UP or navigation == WindowNavigation.DOWN:
            if self.selected_window == self.window_body_left:
                self.selected_window = self.window_footer
                self.window_body.redraw()
                curses.curs_set(1)
                self.window_footer.redraw()
                self.window_footer._window.refresh()
                return WindowNavigation.NOMOVE
            if self.selected_window == self.window_footer:
                self.selected_window = self.window_body_left
                curses.curs_set(0)
                if navigation == WindowNavigation.UP:
                    self.window_body_left.selected_button = 2
                else:
                    self.window_body_left.selected_button = 0
                self.window_body_left.draw()
                self.window_body_left._window.refresh()
                self.window_footer.redraw()
                self.window_footer._window.refresh()

        elif navigation == WindowNavigation.RETURN:
            if self.selected_window == self.window_body_left:
                return WindowNavigation.RETURN
            elif self.selected_window == self.window_footer:
                self.window_footer.update_search(self.window_body.data)

        return WindowNavigation.NOMOVE
    
    def move(self, movement: int):
        self.window_body.move(movement)
        self.window_footer.redraw()
        self.window_footer._window.refresh()

    def close(self):
        for window in self.windows:
            del window


class MapSceneTop(Window):

    def __init__(self, parent_scene, parent_window, **kwargs):
        self.parent_scene = parent_scene
        super().__init__(parent_window, **kwargs)
        self._window.bkgd(' ', curses.color_pair(1))
        super().redraw()

    def redraw(self):
        super().redraw()
        self.draw()

    def draw(self):
#        self.write(1, 1, "Flavor Text", curses.A_BOLD)
        self._window.clear()

        heigh, width = self._window.getmaxyx()
        display_width = width // 3 - 14

        location_1 = 6
        location_2 = location_1 + display_width + 7
        display_width_2 = width - location_2 - 6

        self.write(1, location_1, " TOP SECRET           ", curses.color_pair(3))
        self.write(1, location_2, f" {"Miramar Air Base Interface".ljust(display_width_2-2)} ", curses.color_pair(3))
        self.write(3, location_1, " ACCESS: RESTRICTED   ", curses.color_pair(3))
        self.write(3, location_2, f" {"Project Crossbow Manual Control".ljust(display_width_2-2)} ", curses.color_pair(3))

class MapSceneLeft(Window):

    display_char = '▄'

    map_of_campus : terminal_map.TerminalMap = terminal_map.TerminalMap(5)

    def __init__(self, parent_scene, parent_window, **kwargs):
        self.parent_scene = parent_scene
        super().__init__(parent_window, **kwargs)
        self._window.bkgd(' ', curses.color_pair(1))
        self.map_of_campus.complete()

    def redraw(self):
        self._window.clear()
#        self._window.redrawwin()
        self.draw()
        self._window.refresh()


    def draw(self):

        height, width = self._window.getmaxyx()

        for y in range(height):
            for x in range(width):
                color = self.map_of_campus.get_color(x, y)
                self.write(y, x, self.display_char, curses.color_pair(color))
                #self.write(y, x*4 + 1, str(color))

    def handle_keyinput(self, ch):
        out = WindowNavigation.NOMOVE
        
        if ch == curses.KEY_UP:
            out = WindowNavigation.UP
        elif ch == curses.KEY_DOWN:
            out = WindowNavigation.DOWN
        return out
    
class MapSceneRight(Window):

    entries: int = 0
    location_x: int = 0
    location_y: int = 0
    zoom_scale: int = 1
    min_zoom: int = 1
    max_zoom: int = 4

    max_x: int = 1
    max_y: int = 1

    def __init__(self, parent_scene, parent_window, **kwargs):
        self.parent_scene = parent_scene
        super().__init__(parent_window, **kwargs)
        self._window.bkgd(' ', curses.color_pair(1))

        map_ref = self.parent_scene.window_body_left.map_of_campus
        self.location_y = 1600 # location of Dabney on map
        self.location_x = 1350
        self.zoom_scale = 1
        self.max_y = map_ref.width
        self.max_x = map_ref.height
        map_ref.set_location(self.location_x, self.location_y, self.zoom_scale)


    def redraw(self):
        #super().redraw()
        self._window.clear()
        self.draw()
        self._window.refresh()


    def get_position_e(self):
        x = self.location_x
        map_width = self.parent_scene.window_body_left.map_of_campus.width
        longitude = lerp(34.13197925451806, 34.142950223079026, 0.0, float(map_width), float(x))
        return self._degrees_from_fraction(longitude)

    def get_position_w(self):
        y = self.location_y
        map_height = self.parent_scene.window_body_left.map_of_campus.height
        latitude = lerp(-118.12957086390163, -118.12052903692687, 0.0, float(map_height), float(y))
        return self._degrees_from_fraction(latitude)

    def _degrees_from_fraction(self, value: float):
        d = int(value)
        remainder = value - d
        m = int(remainder * 60)
        remainder = remainder * 60 - m
        s = int(remainder * 60)
        remainder = remainder * 60 - s
        ms = round(remainder * 1000)
        return d, m, s, ms

    def move_up(self):
        step = max(1, int(2 * self.zoom_scale))
        self.location_y = max(0, self.location_y - step)

    def move_down(self):
        step = max(1, int(2 * self.zoom_scale))
        self.location_y = min(self.max_y, self.location_y + step)

    def move_left(self):
        step = max(1, int(2 * self.zoom_scale))
        self.location_x = max(0, self.location_x - step)

    def move_right(self):
        step = max(1, int(2 * self.zoom_scale))
        self.location_x = min(self.max_x, self.location_x + step)

    def zoom_in(self):
        self.zoom_scale = max(self.min_zoom, self.zoom_scale - 1)

    def zoom_out(self):
        self.zoom_scale = min(self.max_zoom, self.zoom_scale + 1)

    def draw(self):
        e_D, e_M, e_S, e_MS = self.get_position_e()
        w_D, w_M, w_S, w_MS = self.get_position_w()

        self.write(1, 3, " Location: ", curses.color_pair(3))
        self.write(2, 3, f"E: {e_D:4}D {e_M:4}M {e_S:4}S {e_MS:4}MS", curses.color_pair(3))
        self.write(4, 3, f"W: {w_D:4}D {w_M:4}M {w_S:4}S {w_MS:4}MS", curses.color_pair(3))

    def update_search(self, data):
        self.entries = len(data)

    def handle_keyinput(self, ch):
        out = WindowNavigation.NOMOVE
        
        # todo prevent scroll
        if ch == curses.KEY_UP:
            self.move_up()
        elif ch == curses.KEY_DOWN:
            self.move_down()
        elif ch == curses.KEY_LEFT:
            self.move_left()
        elif ch == curses.KEY_RIGHT:
            self.move_right()
        elif ch == ord('-') or ch == ord('_'):
            self.zoom_in()
        elif ch == ord('=') or ch == ord('+'):
            self.zoom_out()
        elif ch == ord('\n'):
            if ((self.location_x - 805)**2 + (self.location_y - 1032)**2)**.5 < 100:
                return WindowNavigation.RETURN
            else:
                return out
        else:
            return out

        self.parent_scene.window_body_left.map_of_campus.set_location(self.location_x, self.location_y, self.zoom_scale)

        self.parent_scene.window_body_left.draw()
        self.parent_scene.window_body_left._window.refresh()
        self.draw()
        self._window.refresh()

        return out

class MapScene(Scene):
    """Displays date time location entries and has an interface to search those entries"""

    selected_window: Window = None

    def __init__(self, manager):
        self.manager = manager

        # hide curser
        curses.curs_set(0)

        # Create windows for layout
        self.window_header : MapSceneTop = MapSceneTop(self, self.manager.top_level_window)
        self.window_body_left: MapSceneLeft = MapSceneLeft(self, self.manager.top_level_window)
        self.window_body: MapSceneRight = MapSceneRight(self, self.manager.top_level_window)

        self.windows = [self.window_header, self.window_body_left, self.window_body]
        self.manager.top_level_window.refresh()

        self.selected_window = self.window_body_left

        self.redraw()

    def redraw(self):
        height, width = self.manager.top_level_window.getmaxyx()
        
        # Calculate dimensions for layout
        header_height = 5
        body_height = height - header_height
        
        body_left_width = int(width - 33)
        body_right_width = width - body_left_width

        # Create windows for layout
        self.window_header.place(0, 0, width, header_height)
        self.window_body_left.place(0, header_height, body_left_width, body_height)
        self.window_body.place(body_left_width, header_height, body_right_width, body_height)

        self.draw_layout()

    def draw_layout(self):
        """Draw the main layout structure"""

        for window in self.windows:
#            window._window.clear()
            window.redraw()
            window._window.refresh()

    def handle_keyinput(self, ch):
        return self.window_body.handle_keyinput(ch)

    def close(self):
        for window in self.windows:
            del window
    
class PostScreen(Window):

    def __init__(self, parent_window, **kwargs):
        super().__init__(parent_window, **kwargs)
        curses.curs_set(0)
        self._window.bkgd(' ', curses.color_pair(1))
        self.redraw()

    def get_positions(self):

        height, width = self._window.getmaxyx()
        start_y = height // 2
        start_x = width // 2
        text_start_x = start_x + 12

        return height, width, start_y, start_x

    def get_dots_string(self):
        return "..."

    def redraw(self):
        self._window.clear()

        height, width, start_y, start_x = self.get_positions()

        self.write(start_y - 1, start_x - 17, "Target reprogrammed. Data uploaded.", curses.color_pair(0) | curses.A_BOLD)

        self._window.refresh()

    
    def handle_keyinput(self, ch: int) -> WindowNavigation:
        out: WindowNavigation = WindowNavigation.NOMOVE
        return out

class Manager:
    # selected_scene : Scene = None
    top_level_window : curses.window = None
    current_scene: CurrentScene = CurrentScene.LOGIN

    def __init__(self, window : curses.window):
        self.top_level_window = window
        # here we wait for local
        self.wait_for_local_1()
        self.scene = LogInScene(self)

    def next_scene(self) -> bool:
        if self.current_scene == CurrentScene.LOGIN:
            make_file("./runtime_data/file_l_1")
            self.wait_for_local_2()
            self.init_list_search()
            return True
        elif self.current_scene == CurrentScene.LISTSEARCH:
            make_file("./runtime_data/file_l_2")
            self.wait_for_local_3()
            self.init_location_search()
            return True
        else:
            self.wait_for_local_3()
            return False

    def init_list_search(self):
            self.current_scene = CurrentScene.LISTSEARCH
            self.scene.close()
            # here we wait
            self.scene = ListScene(self)

    def init_location_search(self):
            self.current_scene = CurrentScene.LOCATIONSEARCH
            self.scene.close()
            
            self.scene = MapScene(self)

    def wait_for_local_1(self):
        wait_screen = PreLoginScreen(self.top_level_window)
        while not has_file("./runtime_data/file_r_1"):

            height, width = self.top_level_window.getmaxyx()
            wait_screen.place(0,0, width, height)
            wait_screen.redraw()

            time.sleep(1)


    def wait_for_local_2(self):
        wait_screen = PreListScreen(self.top_level_window)
        while not has_file("./runtime_data/file_r_2"):

            height, width = self.top_level_window.getmaxyx()
            wait_screen.place(0,0, width, height)
            wait_screen.redraw()

            time.sleep(1)

    def wait_for_local_3(self):
        wait_screen = PostScreen(self.top_level_window)
#        while not has_file("./runtime_data/file_r_3"):

        height, width = self.top_level_window.getmaxyx()
        wait_screen.place(0,0, width, height)
        wait_screen.redraw()

        time.sleep(20)

    def redraw(self):
        self.top_level_window.refresh()
        self.scene.redraw()

    def handle_keyinput(self) -> bool:
        if self.top_level_window:
            ch = self.top_level_window.getch()
            if ch == 3: # control C (^C)
                return False
            elif ch == curses.KEY_RESIZE:
                self.redraw()
            else:
                if self.scene:
                    signal = self.scene.handle_keyinput(ch)
                    if signal == WindowNavigation.RETURN:
                        return self.next_scene()
                else:
                    # IDK this might not be best
                    return False
        return True
