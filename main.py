import curses
import window
from time import sleep

terminal_colors = [30,131,244,10,251,2,22,145,3,4,98,59,248,1]

def init_colors():
    counter = 5
    for color_bg in terminal_colors:
        for color_fg in terminal_colors:
#            if (color_bg >= color_fg): TODO
                curses.init_pair(counter, color_fg, color_bg)
                counter += 1

def main(stdscr : curses.window):
    curses.start_color()
    curses.use_default_colors()
    # init colors
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(2, 16, curses.COLOR_CYAN) # black on cyan
    curses.init_pair(3, 16, 8) # black on gray
    curses.init_pair(4, 8, curses.COLOR_BLACK) # gray on black

    # curses.COLOR_CYAN -> 8


    init_colors()


    curses.noecho()
    curses.cbreak()
    stdscr.clear()

    width, height = stdscr.getmaxyx()
    stdscr.redrawln(0, height)
    stdscr.bkgd(' ', curses.color_pair(1))
    stdscr.refresh()

    my_manager = window.Manager(stdscr)

    while my_manager.handle_keyinput():
#        my_manager.set_curser()
#        sleep(0.05)
        pass

if __name__ == "__main__":
    curses.wrapper(main)
