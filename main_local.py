import curses
import window_local
from time import sleep

def main(stdscr : curses.window):
    curses.start_color()
    curses.use_default_colors()
    # init colors
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(2, 16, curses.COLOR_CYAN) # black on cyan
    curses.init_pair(3, 16, 8) # black on gray
    curses.init_pair(4, 8, curses.COLOR_BLACK) # gray on black


    curses.noecho()
    curses.cbreak()
    stdscr.clear()

    width, height = stdscr.getmaxyx()
    stdscr.redrawln(0, height)
    stdscr.bkgd(' ', curses.color_pair(1))
    stdscr.refresh()

    my_manager = window_local.Manager(stdscr)

    while my_manager.handle_keyinput():
        pass

if __name__ == "__main__":
    curses.wrapper(main)
