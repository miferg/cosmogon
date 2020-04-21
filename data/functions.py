#! /usr/bin/python3
"""
Function definitions for cosmogon to work.
"""

import curses

################################################################################

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

################################################################################

def gen_world_pad(world):  # used when the matrix changed
    worldpad = curses.newpad(world.h+1, world.w+1)
    for i in range(0, world.h):
        for j in range(0, world.w):
            worldpad.addstr(i, j, str(world.map[(j,i)]), world.col[(j,i)])
    return(worldpad)

################################################################################

def drop_fog(world):  # darken the map
    worldpad = curses.newpad(world.h+1, world.w+1)
    for i in range(0, world.h):
        for j in range(0, world.w):
            worldpad.addstr(i, j, str("·"),curses.color_pair(5))
    return(worldpad)

################################################################################

def surrounding(x, y, rng):
    srlist = []
    for i in range(x-rng,x+rng+1):
        for j in range(y-rng,y+rng+1):
            srlist.append((i,j))
    return srlist

################################################################################

def refresh_pad(char_dict, col_dict, world):
     world.gen_map(char_dict)
     world.gen_col(col_dict)
     return gen_world_pad(world)

################################################################################

def local_refresh_pad(x, y, char_dict, col_dict, world):
    world.map[(x,y)] = char_dict[world.mat[y][x]]
    world.col[(x,y)] = col_dict[world.mat[y][x]]
    world.pad.addstr(y, x, str(world.map[(x,y)]), world.col[(x,y)])

################################################################################

def set_colors():
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(7, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_RED)

    col_dict = {
        1: curses.color_pair(1), # water ~
        2: curses.color_pair(1), # river ╬
        3: curses.color_pair(2), # plains ░
        4: curses.color_pair(3), # forest ¶
        5: curses.color_pair(4), # mountain ^
        6: curses.color_pair(2), # farms #
        7: curses.color_pair(5), # village ᵃ
        8: curses.color_pair(5), # town a
        9: curses.color_pair(5), # city A
        10: curses.color_pair(5), # Fort ø
        11: curses.color_pair(5), # Fortress Ø
        12: curses.color_pair(7), # Army ¥
        }

    return col_dict
