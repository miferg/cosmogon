#! /usr/bin/python3

import curses
import sys
import time
import numpy

class Calendar(object):

    def __init__(self):
        self.month = 0
        self.year = 0
        self.origin = time.perf_counter()

    def __str__(self):
        return " Year: {} Month: {}".format(self.year, self.month)

    def update(self):
        change = time.perf_counter() - self.origin
        self.year = int(change // 36)
        self.month = int((change % 36) // 3)

class World(object):

    def __init__(self, name, h, w):
        self.name = name
        self.mat = numpy.random.randint(9,size=(h,w))
        self.h = h
        self.w = w

    def __str__(self):
        return name

def trace_cursor(k, cursor_y, cursor_x):

    if k == 258:
        cursor_y = cursor_y + 1
    elif k == 336:
        cursor_y = cursor_y + 5
    elif k == 259:
        cursor_y = cursor_y - 1
    elif k == 337:
        cursor_y = cursor_y - 5
    elif k == 261:
        cursor_x = cursor_x + 1
    elif k == 402:
        cursor_x = cursor_x + 5
    elif k == 260:
        cursor_x = cursor_x - 1
    elif k == 393:
        cursor_x = cursor_x - 5
    return(cursor_y, cursor_x)

def world_pad(source):

    world = curses.newpad(source.h+1, source.w+1)
    for i in range(0, source.h):
        for j in range(0, source.w):
            world.addch(i, j, str(source.mat[i,j]))
    return(world)

def cosmogon(stdscr):

    k = 0
    cursor_x = 0
    cursor_y = 0

    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()

    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # Begin the count of time
    calendar = Calendar()

    # Create a new world
    world = World("Alpha", 30, 50)
    world_pad = world_pad(world)

    # Loop where k is the last character pressed
    while True:

        if k == 113:
            main_menu(stdscr)

        # Initialization
        curses.curs_set(True)
        stdscr.nodelay(True)
        curses.napms(41)
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # The cursor will be moving in the pad
        pheight, pwidth = world_pad.getmaxyx()

        cursor_y, cursor_x = trace_cursor(k, cursor_y, cursor_x)

        cursor_x = max(0, cursor_x)
        cursor_x = min(pwidth-2, cursor_x)

        cursor_y = max(0, cursor_y)
        cursor_y = min(pheight-2, cursor_y)

        # Declaration of strings
        view = " You are looking at : {}".format(str(world.mat[cursor_y,cursor_x]))
        statusbarstr = " Press 'q' to exit | Last key pressed: {} | Pos: {}, {}"
        statusbarstr = statusbarstr.format(k , cursor_y, cursor_x)
        calstr = str(calendar)

        # Update and print date
        calendar.update()
        stdscr.addstr(0, 0, calstr, curses.color_pair(1))

        # Render information
        stdscr.addstr(height-4, 0, view)

        # Render status bar
        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(height-1, 0, statusbarstr)
        stdscr.addstr(height-1, len(statusbarstr), " " * (width - len(statusbarstr) - 1))
        stdscr.attroff(curses.color_pair(3))

        # Move the cursor
        world_pad.move(cursor_y, cursor_x)

        # Refresh the screen
        stdscr.refresh()

        # Refresh the world
        world_pad.refresh( 0,0, 5,5, height-5,width-20)

        # Get next input
        k = stdscr.getch()

def main_menu(stdscr):

    k = 0
    cursor_x = 0
    cursor_y = 0

    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # Loop where k is the last character pressed
    while True:

        if k == 10 and cursor_y == (height // 2) + 2:
            sys.exit()

        if k == 10 and cursor_y == (height // 2) + 1:
            cosmogon(stdscr)

        # Initialization
        curses.curs_set(False)
        stdscr.nodelay(False)
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        if k == curses.KEY_DOWN:
            cursor_y = cursor_y + 1
        elif k == curses.KEY_UP:
            cursor_y = cursor_y - 1

        cursor_x = (width // 2)

        cursor_y = max(int((height // 2) + 1), cursor_y)
        cursor_y = min(int((height // 2) + 2), cursor_y)

        # Strings
        statusbarstr = " Miguel Romero 2020 | github.com/romeromig"
        title = "COSMOGON"
        subtitle = "We are the chosen ones"

        # Centering calculations
        start_x_title = int((width // 2) - (len(title) // 2) - len(title) % 2)
        start_x_subtitle = int((width // 2) - (len(subtitle) // 2) - len(subtitle) % 2)
        start_y = int((height // 2) - 2)

        # Render status bar
        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(height-1, 0, statusbarstr)
        stdscr.addstr(height-1, len(statusbarstr), " " * (width - len(statusbarstr) - 1))
        stdscr.attroff(curses.color_pair(3))

        # Turning on attributes for title
        stdscr.attron(curses.color_pair(2))
        stdscr.attron(curses.A_BOLD)

        # Rendering title
        stdscr.addstr(start_y-2, start_x_title, title)

        # Turning off attributes for title
        stdscr.attroff(curses.color_pair(2))
        stdscr.attroff(curses.A_BOLD)

        # Print rest of text
        stdscr.addstr(start_y, start_x_subtitle, subtitle)
        if cursor_y == (height // 2) + 1:
            stdscr.addstr(start_y + 3, (width // 2) - 2, 'Begin', curses.A_STANDOUT)
        else:
            stdscr.addstr(start_y + 3, (width // 2) - 2, 'Begin')
        if cursor_y == (height // 2) + 2:
            stdscr.addstr(start_y + 4, (width // 2) - 2, 'Exit', curses.A_STANDOUT)
        else:
            stdscr.addstr(start_y + 4, (width // 2) - 2, 'Exit')

        # Move the cursor
        stdscr.move(cursor_y, cursor_x)

        # Refresh the screen
        stdscr.refresh()

        # Wait for next input
        k = stdscr.getch()


def main():
    curses.wrapper(main_menu)

if __name__ == "__main__":
    main()
