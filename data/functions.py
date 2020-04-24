#! /usr/bin/python3
"""
Function definitions for cosmogon to work.
"""

import curses
import sys
import random
import subprocess
import data.data as data
from data.network import Network
from data.classes import *

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

################################################################################
# Main function: multiplayer

def cosmogon(stdscr):

    stdscr.nodelay(True)
    k = 0
    n = Network()

    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()
    stdscr.idcok(False)
    stdscr.idlok(False)

    # Start colors in curses
    col_dict = set_colors()

    # Load objects
    names = data.names
    random.shuffle(names)
    char_dict = data.char_dict
    type_dict = data.type_dict

    # Create a new world
    world = World(names.pop(), 30, 50)
    world.mat = data.testmat.copy()  # Use the provisional matrix 
    world.gen_map(char_dict)
    world.gen_col(col_dict)
    world.pad = gen_world_pad(world)
    pheight, pwidth = world.pad.getmaxyx()

    # Initialize factions
    # local faction
    try:
        u, calorigin = n.getP()
    except:
        main_menu(stdscr)

    world.factions[u["name"]] = Faction(u["name"])
    timer = 0

    # remote factions
    users = n.send(u)
    for user in users:
        if user != u:
            world.factions[user["name"]] = Faction(user["name"])

    # Start the calendar
    calendar = Calendar()
    calendar.origin = float(calorigin)

    # Define the starting position
    cursor_x = random.choice(range(9,pwidth-2))
    cursor_y = random.choice(range(9,pheight-2))
    wpshow = [cursor_y-10,cursor_x-10]

    # Start timer for growth and production
    grow_month = 1
    grow_year = 0

    # No settlements are currently selected
    selected = 0

    # No armies are currently selected
    armysel = 0

    # Nothing has been recieved from the server
    last_rt = 0
    last_mz = 0

    # The log string is empty
    logstr = ''

################################################################################
# Main loop where k is the last character pressed
    while True:

        height, width = stdscr.getmaxyx()

################################################################################
# Network operations

        # Send current faction and recieve all factions
        users = n.send(u)

        for user in users:
            if user['name'] != u['name']:

                if "b" in list(user.keys()): # Build the first settlement
                    world.create_pop(world,user["b"][0],user["b"][1],user["b"][2],user["name"])
                    if (user["b"][0],user["b"][1]) in world.factions[u["name"]].explored:
                        local_refresh_pad(user["b"][0],user["b"][1],char_dict,col_dict,world)
                    logstr = " "+user["name"]+" has settled. A new culture is born in "+ user["b"][2] +"!"
                    del user["b"]

                elif "bt" in list(user.keys()): # Build a town
                    world.pops[tuple(user["bt"])].build_town(world)
                    if tuple(user["bt"]) in world.factions[u["name"]].explored:
                        local_refresh_pad(user["bt"][0],user["bt"][1],char_dict,col_dict,world)
                    logstr = " "+ world.pops[tuple(user["bt"])].name+" ("+user["name"]+") is now a prosperous town."
                    del user["bt"]

                elif "bc" in list(user.keys()): # Build a city
                    world.pops[tuple(user["bc"])].build_city(world)
                    if tuple(user["bc"]) in world.factions[u["name"]].explored:
                        local_refresh_pad(user["bc"][0],user["bc"][1],char_dict,col_dict,world)
                    logstr = " All roads lead to "+world.pops[tuple(user["bc"])].name+", "+user["name"]+"'s metropolis."
                    del user["bc"]

                elif "e" in list(user.keys()): # Establish a colony
                    world.pops[tuple(user["e"][0])].colonize(user["e"][1],user["e"][2],world,user["e"][3])
                    if (user["e"][1],user["e"][2]) in world.factions[u["name"]].explored:
                        local_refresh_pad(user["e"][1],user["e"][2],char_dict,col_dict,world)
                    logstr = " "+user["name"]+" has established a colony: "+ world.pops[(user["e"][1],user["e"][2])].name
                    del user["e"]

                elif "o" in list(user.keys()): # Build a fort
                    world.pops[tuple(user["o"][0])].build_fort(user["o"][1],user["o"][2],world)
                    if (user["o"][1],user["o"][2]) in world.factions[u["name"]].explored:
                        local_refresh_pad(user["o"][1],user["o"][2],char_dict,col_dict,world)
                    logstr = " A fort has been erected to protect "+user["name"]+"'s people."
                    del user["o"]

                elif "uo" in list(user.keys()): # Upgrade a fort
                    world.pops[tuple(user["uo"][0])].upgrade_fort(user["uo"][1],user["uo"][2],world)
                    if (user["uo"][1],user["uo"][2]) in world.factions[u["name"]].explored:
                        local_refresh_pad(user["uo"][1],user["uo"][2],char_dict,col_dict,world)
                    logstr = " A mighty fortress now stands between "+user["name"]+" and her enemies!"
                    del user["uo"]

                elif "m" in list(user.keys()): # Muster
                    world.pops[tuple(user["m"][0])].muster(user["m"][1],user["m"][2],world)
                    if (user["m"][1],user["m"][2]) in world.factions[u["name"]].explored:
                        local_refresh_pad(user["m"][1],user["m"][2],char_dict,col_dict,world)
                    logstr = " Beware, "+user["name"]+" has called her banners!"
                    del user["m"]

                elif "z" in list(user.keys()): # Mobilize
                    if last_mz != user["z"][3]:
                        last_mz = user["z"][3]
                        world.armies[tuple(user["z"][0])].mobilize(user["z"][1],user["z"][2],world)
                        if (user["z"][1],user["z"][2]) in world.factions[u["name"]].explored:
                            local_refresh_pad(user["z"][1],user["z"][2],char_dict,col_dict,world)
                        if (user["z"][0][0],user["z"][0][1]) in world.factions[u["name"]].explored:
                            local_refresh_pad(user["z"][0][0],user["z"][0][1],char_dict,col_dict,world)
                        del user["z"]

                elif "r" in list(user.keys()): # Reinforce
                    if last_rt != user["r"][3]:
                        last_rt = user["r"][3]
                        world.pops[tuple(user["r"][0])].reinforce(user["r"][1],user["r"][2],world,calendar)
                        del user["r"]

                elif "f" in list(user.keys()): # Build a farm
                    world.pops[tuple(user["f"][0])].build_farm(user["f"][1],user["f"][2],world)
                    if (user["f"][1],user["f"][2]) in world.factions[u["name"]].explored:
                        local_refresh_pad(user["f"][1],user["f"][2],char_dict,col_dict,world)
                    del user["f"]

                elif "c" in list(user.keys()): # Claim wilderness
                    world.pops[tuple(user["c"][0])].claim(user["c"][1],user["c"][2], world)
                    logstr = " "+user["name"]+" is now exploiting new lands: " + type_dict[world.mat[user["c"][2]][user["c"][1]]]
                    del user["c"]

                elif "x" in list(user.keys()): # Explore
                    world.pops[tuple(user["x"][0])].explore(user["x"][1],user["x"][2], world)
                    del user["x"]

            elif timer > 0:
                timer += -1

            else:
                if "b" in list(u.keys()): # remove instruction Build the first settlement
                    del u["b"]
                elif "bt" in list(u.keys()): # remove instruction Build a town
                    del u["bt"]
                elif "bc" in list(u.keys()): # remove instruction Build a city
                    del u["bc"]
                elif "e" in list(u.keys()): # remove instruction Establish a colony
                    del u["e"]
                elif "o" in list(u.keys()): # remove instruction Build a fort
                    del u["o"]
                elif "uo" in list(u.keys()): # remove instruction Upgrade a fort
                    del u["uo"]
                elif "m" in list(u.keys()): # remove instruction Muster
                    del u["m"]
                elif "z" in list(u.keys()): # remove instruction Mobilize
                    del u["z"]
                elif "r" in list(u.keys()): # remove instruction Reinforce
                    del u["r"]
                elif "f" in list(u.keys()): # remove instruction Build a farm
                    del u["f"]
                elif "c" in list(u.keys()): # remove instruction Claim wilderness
                    del u["c"]
                elif "x" in list(u.keys()): # remove instruction Explore
                    del u["x"]

################################################################################
# Input operations

        # Build the first settlement (b)
        if k == 98:
            if world.factions[u["name"]].startpop != 0:
                if (cursor_x,cursor_y) not in world.pops.keys():
                    nwpopname = names.pop()
                    flag = world.create_pop(world, cursor_x,cursor_y, nwpopname, u["name"])
                    if flag == 1:
                        logstr = " "+u["name"]+" has settled. A new culture is born in "+ nwpopname +"!"
                        world.pad = drop_fog(world)
                        local_refresh_pad(cursor_x, cursor_y, char_dict, col_dict, world)
                        surroundlist = surrounding(cursor_x, cursor_y, 1)
                        for pair in surroundlist:
                            local_refresh_pad(pair[0], pair[1], char_dict, col_dict, world)
                        u["b"] = (cursor_x, cursor_y, nwpopname)
                        timer = 5
                        flag = 0

        # Select and deselect a settlement (s)
        if k == 115:
            # Select a settlement
            if selected == 0 and (cursor_x, cursor_y) in world.factions[u["name"]].pops:
                selected_pos = (cursor_x, cursor_y)
                world.pad.addstr(cursor_y, cursor_x, str(world.map[(cursor_x,cursor_y)]), curses.color_pair(6))
                selected = 1
            # Select last selected settlement
            elif 'selected_pos' in locals() and selected == 0:
                if (cursor_x, cursor_y) not in world.factions[u["name"]].pops:
                    world.pad.addstr(selected_pos[1],selected_pos[0],str(world.map[selected_pos]), curses.color_pair(6))
                    selected = 1
            # Deselect settlement
            elif selected == 1:
                world.pad.addstr(selected_pos[1],selected_pos[0],str(world.map[selected_pos]), curses.color_pair(5))
                selected = 0

        # Explore tile (s, x)
        if k == 120 and selected == 1:
            selected = 0
            world.pad.addstr(selected_pos[1],selected_pos[0],str(world.map[selected_pos]), curses.color_pair(5))
            diffx = abs(cursor_x-selected_pos[0])
            diffy = abs(cursor_y-selected_pos[1])
            surroundlist = surrounding(cursor_x, cursor_y, 1)
            if world.factions[world.pops[selected_pos].owner].wealth >= 10*(diffx+diffy):
                if world.pops[selected_pos].size >= 10*(diffx+diffy):
                    if bool(set(world.factions[u["name"]].explored) & set(surroundlist)):
                        flag = world.pops[selected_pos].explore(cursor_x, cursor_y, world)
                        local_refresh_pad(cursor_x, cursor_y, char_dict, col_dict, world)
                        if flag == 1:
                            u["x"] = (selected_pos, cursor_x, cursor_y)
                            timer = 5
                            flag = 0

        # Applicable functions to charted world
        if (cursor_x,cursor_y) in world.factions[u["name"]].explored:

            # Claim wilderness (s, c)
            if k == 99 and selected == 1:
                selected = 0
                world.pad.addstr(selected_pos[1],selected_pos[0],str(world.map[selected_pos]), curses.color_pair(5))
                flag = world.pops[selected_pos].claim(cursor_x, cursor_y, world)
                if flag == 1:
                    logstr = " "+u["name"]+" is now exploiting new lands: " + type_dict[world.mat[cursor_y,cursor_x]]
                    world.factions[u["name"]].cells.sort()
                    u["c"] = (selected_pos, cursor_x, cursor_y)
                    timer = 5
                    flag = 0
        
            # Expand a settlement (s, b)
            if k == 98 and selected == 1:
                selected = 0
                world.pad.addstr(selected_pos[1],selected_pos[0],str(world.map[selected_pos]), curses.color_pair(5))
                popowner =  world.pops[selected_pos].owner
                # Build town
                if world.mat[selected_pos[1]][selected_pos[0]] == 7:
                    flag = world.pops[selected_pos].build_town(world)
                    local_refresh_pad(selected_pos[0],selected_pos[1],char_dict, col_dict, world)
                    world.factions[mainfac].settlements.sort()
                    if flag == 1:
                        logstr = " "+world.pops[selected_pos].name+" ("+u["name"]+") is now a prosperous town."
                        u["bt"] = selected_pos
                        timer = 5
                        flag = 0
                # Build city
                elif world.mat[selected_pos[1]][selected_pos[0]] == 8:
                    flag = world.pops[selected_pos].build_city(world)
                    local_refresh_pad(selected_pos[0],selected_pos[1],char_dict, col_dict, world)
                    world.factions[mainfac].settlements.sort()
                    if flag == 1:
                        logstr = " All roads lead to "+ world.pops[selected_pos].name+", "+u["name"]+"'s metropolis."
                        u["bc"] = selected_pos
                        timer = 5
                        flag = 0

            # Establish a colony (s, e)
            if k == 101 and selected == 1:
                selected = 0
                world.pad.addstr(selected_pos[1],selected_pos[0],str(world.map[selected_pos]), curses.color_pair(5))
                nwpopname = names.pop()
                flag = world.pops[selected_pos].colonize(cursor_x, cursor_y, world, nwpopname)
                local_refresh_pad(cursor_x, cursor_y, char_dict, col_dict, world)
                world.factions[mainfac].settlements.sort()
                if flag == 1:
                    logstr = " "+u["name"]+" has established a colony: "+ world.pops[selected_pos].name
                    u["e"] = (selected_pos,cursor_x,cursor_y,nwpopname)
                    timer = 5
                    flag = 0
     
            # Build a fort (s, o)
            if k == 111 and selected == 1:
                selected = 0
                flag = world.pops[selected_pos].build_fort(cursor_x, cursor_y, world)
                local_refresh_pad(cursor_x, cursor_y, char_dict, col_dict, world)
                world.pad.addstr(selected_pos[1],selected_pos[0],str(world.map[selected_pos]), curses.color_pair(5))
                world.factions[mainfac].fortlist.sort()
                if flag == 1:
                    logstr = " A fort has been erected to protect "+u["name"]+"'s people."
                    u["o"] = (selected_pos,cursor_x,cursor_y)
                    timer = 5
                    flag = 0

            # Upgrade a fort (s, u)
            if k == 117 and selected == 1:
                selected = 0
                world.pad.addstr(selected_pos[1],selected_pos[0],str(world.map[selected_pos]), curses.color_pair(5))
                if world.mat[cursor_y][cursor_x] == 10:
                    flag = world.pops[selected_pos].upgrade_fort(cursor_x, cursor_y, world)
                    local_refresh_pad(cursor_x, cursor_y, char_dict, col_dict, world)
                    world.factions[mainfac].fortlist.sort()
                    if flag == 1:
                        logstr = " A mighty fortress now stands between "+u["name"]+" and her enemies!"
                        u["uo"] = (selected_pos,cursor_x,cursor_y)
                        timer = 5
                        flag = 0

            # Reinforce (s, r)
            if k == 114 and selected == 1:
                selected = 0
                world.pad.addstr(selected_pos[1],selected_pos[0],str(world.map[selected_pos]), curses.color_pair(5))
                if world.mat[cursor_y][cursor_x] in (10, 11, 12):
                    flag = world.pops[selected_pos].reinforce(cursor_x, cursor_y, world, calendar)
                    if flag == 1:
                        u["r"] = (selected_pos,cursor_x,cursor_y,time.perf_counter())
                        timer = 5
                        flag = 0

            # Build a farm (s, f)
            if k == 102 and selected == 1:
                selected = 0
                world.pad.addstr(selected_pos[1],selected_pos[0],str(world.map[selected_pos]), curses.color_pair(5))
                flag = world.pops[selected_pos].build_farm(cursor_x, cursor_y, world)
                local_refresh_pad(cursor_x, cursor_y, char_dict, col_dict, world)
                if flag == 1:
                    u["f"] = (selected_pos, cursor_x, cursor_y)
                    timer = 5
                    flag = 0

            # Muster (s, m)
            if k == 109 and selected == 1:
                selected = 0
                flag = world.pops[selected_pos].muster(cursor_x, cursor_y, world)
                local_refresh_pad(cursor_x, cursor_y, char_dict, col_dict, world)
                world.pad.addstr(selected_pos[1],selected_pos[0],str(world.map[selected_pos]), curses.color_pair(5))
                world.factions[mainfac].armylist.sort()
                if flag == 1:
                    logstr = " Make way for "+u["name"]+"'s "+world.armies[(cursor_x,cursor_y)].name+" army!"
                    u["m"] = (selected_pos,cursor_x,cursor_y)
                    timer = 5
                    flag = 0


            # Select and deselect an army (a)
            if k == 97:
                # Select an army
                if armysel == 0 and (cursor_x, cursor_y) in world.factions[u["name"]].armies:
                    armysel_pos = (cursor_x, cursor_y)
                    world.pad.addstr(cursor_y, cursor_x, str(world.map[(cursor_x,cursor_y)]), curses.color_pair(8))
                    armysel = 1
                # Select last selected army
                elif 'armysel_pos' in locals() and armysel == 0:
                    if (cursor_x, cursor_y) not in world.factions[u["name"]].armies:
                        world.pad.addstr(armysel_pos[1],armysel_pos[0],str(world.map[armysel_pos]), curses.color_pair(8))
                        armysel = 1
                # Deselect army
                elif armysel == 1:
                    world.pad.addstr(armysel_pos[1],armysel_pos[0],str(world.map[armysel_pos]), curses.color_pair(7))
                    armysel = 0

            # Mobilize (a, z)
            if k == 122 and armysel == 1:
                if world.mat[cursor_y][cursor_x] in (3,4,5,6):
                    flag = world.armies[armysel_pos].mobilize(cursor_x, cursor_y, world)
                    local_refresh_pad(cursor_x, cursor_y, char_dict, col_dict, world)
                    local_refresh_pad(armysel_pos[0], armysel_pos[1], char_dict, col_dict, world)
                    if flag == 1:
                        u["z"] = (armysel_pos,cursor_x,cursor_y,time.perf_counter())
                        timer = 5
                        flag = 0
                        armysel_pos = (cursor_x, cursor_y)
                        world.pad.addstr(armysel_pos[1],armysel_pos[0],str(world.map[armysel_pos]), curses.color_pair(8))

        # Open menu (.)
        if k == 46:
            menu_pad = curses.newpad(10, 60)
            menu_pad.refresh( 0,0, 5,5, height-5,width-20)

        # Quit to menu (q)
        if k == 113:
            main_menu(stdscr)

################################################################################
# Automatic operations

        # Yearly
        if calendar.year != grow_year:
            grow_year = calendar.year
            # Produce food
            for pop in world.poplist:
                world.pops[pop].get_food(world)

        # Monthly
        if calendar.month != grow_month:
            grow_month = calendar.month

            # Accumulate wealth
            for faction in world.factions.keys():
                world.factions[faction].get_wealth()

            # Army encounters
            for army in world.armies.keys():
                desertion = 1
                surroundlist = surrounding(army[0], army[1], world.armies[army].mr)

                # Raid settlement
                if bool(set(world.poplist) & set(surroundlist)):
                    inmr = list(set(world.poplist) & set(surroundlist))
                    for pob in inmr:
                        if world.armies[army].owner != world.pops[pob].owner:
                            world.pops[pob].size += -(world.armies[army].size*world.armies[army].s_damagerate)
                            world.pops[pob].food = 0 

                # Engage foreign army
                if bool(set(world.armies.keys()) & set(surroundlist)):
                    inmr = list(set(world.armies.keys()) & set(surroundlist))
                    for farmy in inmr:
                        # Assault foreign fortification
                        if world.armies[army].owner != world.armies[farmy].owner:
                            world.armies[farmy].damagetaken += world.armies[army].size*world.armies[army].a_damagerate

                # Interact with fortifications
                if bool(set(world.forts.keys()) & set(surroundlist)):
                    inmr = list(set(world.forts.keys()) & set(surroundlist))
                    for fort in inmr:
                        # Assault foreign fortification
                        if world.armies[army].owner != world.forts[fort].owner:
                            world.forts[fort].damagetaken += world.armies[army].size*world.armies[army].o_damagerate
                        # Avoid desertion if an allied fortification is in range
                        else:
                            desertion = 0
                if desertion == 1:
                    world.armies[army].grow()

            # Fortification actions
            for fort in world.forts.keys():
                surroundlist = surrounding(fort[0], fort[1], world.forts[fort].mr)
                # Harass army
                if bool(set(world.armies.keys()) & set(surroundlist)):
                    inmr = list(set(world.armies.keys()) & set(surroundlist))
                    for army in inmr:
                        if world.forts[fort].owner !=  world.armies[army].owner:
                            world.armies[army].damagetaken += world.forts[fort].size*world.forts[fort].a_damagerate
                # Sustain casualties
                world.forts[fort].size += -world.forts[fort].damagetaken
                world.forts[fort].damagetaken = 0
                if world.forts[fort].size < 0:
                    world.forts[fort].size = 0

            # Manage army sizes
            for army in list(world.armies.keys()):
                # Sustain casualties
                world.armies[army].size += -world.armies[army].damagetaken
                world.armies[army].damagetaken = 0
                # Disband
                if world.armies[army].size <= 0:
                    if 'armysel_pos' in locals() and army == armysel_pos:
                        armysel = 0
                        del armysel_pos
                    world.armies[army].disband(world)
                    local_refresh_pad(army[0], army[1], char_dict, col_dict, world)

            # Population grow
            for pop in world.poplist:
                world.pops[pop].grow(world)

        # Estimate faction sizes
        for faction in world.factions.keys():
            size = 0
            for pop in world.factions[faction].pops:
                size += int(world.pops[pop].size)
            world.factions[faction].size = size

################################################################################
# Screen operations

        # Initialization
        curses.curs_set(True)
        curses.napms(41) #41
        stdscr.erase()
        height, width = stdscr.getmaxyx()

        # The cursor will be moving in the pad
        cursor_y, cursor_x = trace_cursor(k, cursor_y, cursor_x)
        cursor_x = max(0, cursor_x)
        cursor_x = min(pwidth-2, cursor_x)
        cursor_y = max(0, cursor_y)
        cursor_y = min(pheight-2, cursor_y)

        # Scroll the world pad
        if world.factions[u["name"]].startpop == 0:
            if cursor_y <= wpshow[0]-1:
                wpshow[0] = cursor_y
            elif cursor_y >= wpshow[0]+11:
                wpshow[0] = cursor_y-10
            if cursor_x <= wpshow[1]-1:
                wpshow[1] = cursor_x
            elif cursor_x >= wpshow[1]+11:
                wpshow[1] = cursor_x-10

        # Update and print date
        calendar.update()
        calstr = str(calendar)
        datstr = "╣ "+ u["name"] +", "+ calstr +" ╠"
        centpos = int((width // 2) - (len(datstr) // 2) - len(datstr) % 2)
        stdscr.addstr(0, centpos, datstr, curses.color_pair(7))

        # View faction data
        mainfac = list(world.factions.keys())[0]
        factstr = " ║ Size: "
        factstr += str(int(world.factions[mainfac].size))
        factstr += " ║ Wealth: "
        factstr += str(int(world.factions[mainfac].wealth))
        factstr += " ║"
        stdscr.addstr(1, 0, factstr)
        settlementstr = " ║ Settlements: "
        settlementstr += " ".join(world.factions[mainfac].settlements + world.factions[mainfac].fortlist)
        settlementstr += " ║"
        stdscr.addstr(2, 0, settlementstr)
        claimedstr0 = " ║ Domains: "
        for cell in world.factions[mainfac].cells:
            claimedstr0 += char_dict[cell] +" "
        claimedstr0 += "║"
        stdscr.addstr(3, 0, claimedstr0)

        # View information on the map
        if (cursor_x,cursor_y) in world.factions[u["name"]].explored:
            stdscr.addstr(6, 18, type_dict[world.mat[cursor_y,cursor_x]])
            if (cursor_x,cursor_y) in world.pops.keys():
                stdscr.addstr(7, 18, world.pops[(cursor_x,cursor_y)].name)
                stdscr.addstr(8, 18, "("+world.pops[(cursor_x,cursor_y)].owner+")")
                stdscr.addstr(9, 18, str(int(world.pops[(cursor_x,cursor_y)].size))+" inhabitants")
                stdscr.addstr(10, 18,"Food: "+str(int(world.pops[(cursor_x,cursor_y)].food)))
                claimedstr = "Claimed territories: "
                for cell in world.pops[(cursor_x,cursor_y)].claimed:
                    claimedstr += char_dict[cell] +" "
                stdscr.addstr(11,18, claimedstr)

            elif (cursor_x,cursor_y) in world.forts.keys(): 
                stdscr.addstr(7, 18, "("+world.forts[(cursor_x,cursor_y)].owner+")")
                stdscr.addstr(8, 18, str(int(world.forts[(cursor_x,cursor_y)].size))+" strong")

            elif (cursor_x,cursor_y) in world.armies.keys(): 
                stdscr.addstr(7, 18, world.armies[(cursor_x,cursor_y)].name)
                stdscr.addstr(8, 18, "("+world.armies[(cursor_x,cursor_y)].owner+")")
                stdscr.addstr(9, 18, str(int(world.armies[(cursor_x,cursor_y)].size))+" strong")

            else:
                stdscr.addstr(7, 18,"Unpopulated")

        else:
            stdscr.addstr(6, 18, "Uncharted")

        # Selected information
        if armysel == 0:
            stdscr.addstr(18, 1, "'a': select army.")
        else:
            selstr = "Selected army: "+world.armies[(armysel_pos[0],armysel_pos[1])].name+", "
            selstr += str(int(world.armies[(armysel_pos[0],armysel_pos[1])].size)) +" strong"
            stdscr.addstr(18, 1, selstr)
            stdscr.addstr(19, 1, "'z': mobilize.")

        if selected == 0:
            stdscr.addstr(21, 1, "'s': select settlement.")
        else:
            selstr = "Selected settlement: "+world.pops[(selected_pos[0],selected_pos[1])].name+", "
            selstr += str(int(world.pops[(selected_pos[0],selected_pos[1])].size))+" inhabitants"
            stdscr.addstr(21, 1, selstr)
            selstr = "'x': explore; 'c': claim; 'f': build farm."
            stdscr.addstr(22, 1, selstr)
            if world.mat[selected_pos[1]][selected_pos[0]] in (8,9):
                selstr = "'e': colonyze; 'o': build fort; 'm': muster; 'r': reinforce."
                stdscr.addstr(23, 1, selstr)
            if world.mat[selected_pos[1]][selected_pos[0]] == 9:
                selstr = "'u': upgrade fort."
                stdscr.addstr(24, 1, selstr)

        # Announcements
        if world.factions[u["name"]].startpop == 1:
            wellcomestr = " Choose a tile with the cursor and press 'b' to establish a settlement."
            stdscr.addstr(height-3, 0, wellcomestr, curses.color_pair(1))
        else:
            stdscr.addstr(height-3, 0, logstr, curses.color_pair(1))

        # Render lower bar
        usernames = []
        for user in users:
            usernames.append(user['name']) 
        #statusbarstr = " ║ Quit 'q' ║ "+ ' ╦ '.join(usernames) +" ║ Last: {} Pos: {}, {} ║"
        #statusbarstr = statusbarstr.format(k , cursor_y, cursor_x)
        statusbarstr = " Quit 'q' ║ "+ ' ╦ '.join(usernames) +" ║ Pos: {}, {}"
        statusbarstr = statusbarstr.format(cursor_y, cursor_x)
        stdscr.attron(curses.color_pair(4))
        stdscr.addstr(height-1, 0, statusbarstr)
        stdscr.addstr(height-1, len(statusbarstr), " " * (width - len(statusbarstr) - 1))
        stdscr.attroff(curses.color_pair(4))

        # Move the cursor
        world.pad.move(cursor_y, cursor_x)

        # Refresh the screen
        stdscr.refresh()

        # Refresh the world
        #world_pad.refresh( 0,0, 6,5, height-14,width-5)
        world.pad.refresh(wpshow[0],wpshow[1],6,5,16,15)

        # Get next input
        k = stdscr.getch()

################################################################################
# Main function: single player

def cosmogon_single(stdscr):

    stdscr.nodelay(True)
    k = 0

    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()
    stdscr.idcok(False)
    stdscr.idlok(False)

    # Start colors in curses
    col_dict = set_colors()

    # Load objects
    names = data.names
    random.shuffle(names)
    char_dict = data.char_dict
    type_dict = data.type_dict

    # Create a new world
    world = World(names.pop(), 30, 50)
    world.mat = data.testmat.copy()  # Use the provisional matrix 
    world.gen_map(char_dict)
    world.gen_col(col_dict)
    world.pad = gen_world_pad(world)
    pheight, pwidth = world.pad.getmaxyx()

    # Initialize factions
    # local faction
    u = {"name":names.pop()}
    calorigin = time.perf_counter()
    world.factions[u["name"]] = Faction(u["name"])

    # additional factions
    users = [u,{"name":names.pop()}]
    for user in users:
        if user != u:
            world.factions[user["name"]] = Faction(user["name"])

    # Start the calendar
    calendar = Calendar()
    calendar.origin = float(calorigin)

    # Define the starting position
    cursor_x = random.choice(range(9,pwidth-2))
    cursor_y = random.choice(range(9,pheight-2))
    wpshow = [cursor_y-10,cursor_x-10]

    # Start timer for growth and production
    grow_month = 1
    grow_year = 0

    # No settlements are currently selected
    selected = 0

    # No armies are currently selected
    armysel = 0

    # The log string is empty
    logstr = ''

################################################################################
# Main loop where k is the last character pressed
    while True:

        height, width = stdscr.getmaxyx()

################################################################################
# Input operations

        # Build the first settlement (b)
        if k == 98:
            if world.factions[u["name"]].startpop != 0:
                if (cursor_x,cursor_y) not in world.pops.keys():
                    nwpopname = names.pop()
                    flag = world.create_pop(world, cursor_x,cursor_y, nwpopname, u["name"])
                    if flag == 1:
                        logstr = " "+u["name"]+" has settled. A new culture is born in "+ nwpopname +"!"
                        world.pad = drop_fog(world)
                        local_refresh_pad(cursor_x, cursor_y, char_dict, col_dict, world)
                        surroundlist = surrounding(cursor_x, cursor_y, 1)
                        for pair in surroundlist:
                            local_refresh_pad(pair[0], pair[1], char_dict, col_dict, world)
                        flag = 0

        # Select and deselect a settlement (s)
        if k == 115:
            # Select a settlement
            if selected == 0 and (cursor_x, cursor_y) in world.factions[u["name"]].pops:
                selected_pos = (cursor_x, cursor_y)
                world.pad.addstr(cursor_y, cursor_x, str(world.map[(cursor_x,cursor_y)]), curses.color_pair(6))
                selected = 1
            # Select last selected settlement
            elif 'selected_pos' in locals() and selected == 0:
                if (cursor_x, cursor_y) not in world.factions[u["name"]].pops:
                    world.pad.addstr(selected_pos[1],selected_pos[0],str(world.map[selected_pos]), curses.color_pair(6))
                    selected = 1
            # Deselect settlement
            elif selected == 1:
                world.pad.addstr(selected_pos[1],selected_pos[0],str(world.map[selected_pos]), curses.color_pair(5))
                selected = 0

        # Explore tile (s, x)
        if k == 120 and selected == 1:
            selected = 0
            world.pad.addstr(selected_pos[1],selected_pos[0],str(world.map[selected_pos]), curses.color_pair(5))
            diffx = abs(cursor_x-selected_pos[0])
            diffy = abs(cursor_y-selected_pos[1])
            surroundlist = surrounding(cursor_x, cursor_y, 1)
            if world.factions[world.pops[selected_pos].owner].wealth >= 10*(diffx+diffy):
                if world.pops[selected_pos].size >= 10*(diffx+diffy):
                    if bool(set(world.factions[u["name"]].explored) & set(surroundlist)):
                        flag = world.pops[selected_pos].explore(cursor_x, cursor_y, world)
                        local_refresh_pad(cursor_x, cursor_y, char_dict, col_dict, world)
                        if flag == 1:
                            flag = 0

        # Applicable functions to charted world
        if (cursor_x,cursor_y) in world.factions[u["name"]].explored:

            # Claim wilderness (s, c)
            if k == 99 and selected == 1:
                selected = 0
                world.pad.addstr(selected_pos[1],selected_pos[0],str(world.map[selected_pos]), curses.color_pair(5))
                flag = world.pops[selected_pos].claim(cursor_x, cursor_y, world)
                if flag == 1:
                    logstr = " "+u["name"]+" is now exploiting new lands: " + type_dict[world.mat[cursor_y,cursor_x]]
                    world.factions[u["name"]].cells.sort()
                    flag = 0
        
            # Expand a settlement (s, b)
            if k == 98 and selected == 1:
                selected = 0
                world.pad.addstr(selected_pos[1],selected_pos[0],str(world.map[selected_pos]), curses.color_pair(5))
                popowner =  world.pops[selected_pos].owner
                # Build town
                if world.mat[selected_pos[1]][selected_pos[0]] == 7:
                    flag = world.pops[selected_pos].build_town(world)
                    local_refresh_pad(selected_pos[0],selected_pos[1],char_dict, col_dict, world)
                    world.factions[mainfac].settlements.sort()
                    if flag == 1:
                        logstr = " "+world.pops[selected_pos].name+" ("+u["name"]+") is now a prosperous town."
                        flag = 0
                # Build city
                elif world.mat[selected_pos[1]][selected_pos[0]] == 8:
                    flag = world.pops[selected_pos].build_city(world)
                    local_refresh_pad(selected_pos[0],selected_pos[1],char_dict, col_dict, world)
                    world.factions[mainfac].settlements.sort()
                    if flag == 1:
                        logstr = " All roads lead to "+ world.pops[selected_pos].name+", "+u["name"]+"'s metropolis."
                        flag = 0

            # Establish a colony (s, e)
            if k == 101 and selected == 1:
                selected = 0
                world.pad.addstr(selected_pos[1],selected_pos[0],str(world.map[selected_pos]), curses.color_pair(5))
                nwpopname = names.pop()
                flag = world.pops[selected_pos].colonize(cursor_x, cursor_y, world, nwpopname)
                local_refresh_pad(cursor_x, cursor_y, char_dict, col_dict, world)
                world.factions[mainfac].settlements.sort()
                if flag == 1:
                    logstr = " "+u["name"]+" has established a colony: "+ world.pops[selected_pos].name
                    flag = 0
     
            # Build a fort (s, o)
            if k == 111 and selected == 1:
                selected = 0
                flag = world.pops[selected_pos].build_fort(cursor_x, cursor_y, world)
                local_refresh_pad(cursor_x, cursor_y, char_dict, col_dict, world)
                world.pad.addstr(selected_pos[1],selected_pos[0],str(world.map[selected_pos]), curses.color_pair(5))
                world.factions[mainfac].fortlist.sort()
                if flag == 1:
                    logstr = " A fort has been erected to protect "+u["name"]+"'s people."
                    flag = 0

            # Upgrade a fort (s, u)
            if k == 117 and selected == 1:
                selected = 0
                world.pad.addstr(selected_pos[1],selected_pos[0],str(world.map[selected_pos]), curses.color_pair(5))
                if world.mat[cursor_y][cursor_x] == 10:
                    flag = world.pops[selected_pos].upgrade_fort(cursor_x, cursor_y, world)
                    local_refresh_pad(cursor_x, cursor_y, char_dict, col_dict, world)
                    world.factions[mainfac].fortlist.sort()
                    if flag == 1:
                        logstr = " A mighty fortress now stands between "+u["name"]+" and her enemies!"
                        flag = 0

            # Reinforce (s, r)
            if k == 114 and selected == 1:
                selected = 0
                world.pad.addstr(selected_pos[1],selected_pos[0],str(world.map[selected_pos]), curses.color_pair(5))
                if world.mat[cursor_y][cursor_x] in (10, 11, 12):
                    flag = world.pops[selected_pos].reinforce(cursor_x, cursor_y, world, calendar)
                    if flag == 1:
                        flag = 0

            # Build a farm (s, f)
            if k == 102 and selected == 1:
                selected = 0
                world.pad.addstr(selected_pos[1],selected_pos[0],str(world.map[selected_pos]), curses.color_pair(5))
                flag = world.pops[selected_pos].build_farm(cursor_x, cursor_y, world)
                local_refresh_pad(cursor_x, cursor_y, char_dict, col_dict, world)
                if flag == 1:
                    flag = 0

            # Muster (s, m)
            if k == 109 and selected == 1:
                selected = 0
                flag = world.pops[selected_pos].muster(cursor_x, cursor_y, world)
                local_refresh_pad(cursor_x, cursor_y, char_dict, col_dict, world)
                world.pad.addstr(selected_pos[1],selected_pos[0],str(world.map[selected_pos]), curses.color_pair(5))
                world.factions[mainfac].armylist.sort()
                if flag == 1:
                    logstr = " Make way for "+u["name"]+"'s "+world.armies[(cursor_x,cursor_y)].name+" army!"
                    flag = 0

            # Select and deselect an army (a)
            if k == 97:
                # Select an army
                if armysel == 0 and (cursor_x, cursor_y) in world.factions[u["name"]].armies:
                    armysel_pos = (cursor_x, cursor_y)
                    world.pad.addstr(cursor_y, cursor_x, str(world.map[(cursor_x,cursor_y)]), curses.color_pair(8))
                    armysel = 1
                # Select last selected army
                elif 'armysel_pos' in locals() and armysel == 0:
                    if (cursor_x, cursor_y) not in world.factions[u["name"]].armies:
                        world.pad.addstr(armysel_pos[1],armysel_pos[0],str(world.map[armysel_pos]), curses.color_pair(8))
                        armysel = 1
                # Deselect army
                elif armysel == 1:
                    world.pad.addstr(armysel_pos[1],armysel_pos[0],str(world.map[armysel_pos]), curses.color_pair(7))
                    armysel = 0

            # Mobilize (a, z)
            if k == 122 and armysel == 1:
                if world.mat[cursor_y][cursor_x] in (3,4,5,6):
                    flag = world.armies[armysel_pos].mobilize(cursor_x, cursor_y, world)
                    local_refresh_pad(cursor_x, cursor_y, char_dict, col_dict, world)
                    local_refresh_pad(armysel_pos[0], armysel_pos[1], char_dict, col_dict, world)
                    if flag == 1:
                        flag = 0
                        armysel_pos = (cursor_x, cursor_y)
                        world.pad.addstr(armysel_pos[1],armysel_pos[0],str(world.map[armysel_pos]), curses.color_pair(8))

        # Open menu (.)
        if k == 46:
            menu_pad = curses.newpad(10, 60)
            menu_pad.refresh( 0,0, 5,5, height-5,width-20)

        # Quit to menu (q)
        if k == 113:
            main_menu(stdscr)

################################################################################
# Automatic operations

        # Yearly
        if calendar.year != grow_year:
            grow_year = calendar.year
            # Produce food
            for pop in world.poplist:
                world.pops[pop].get_food(world)

        # Monthly
        if calendar.month != grow_month:
            grow_month = calendar.month

            # Accumulate wealth
            for faction in world.factions.keys():
                world.factions[faction].get_wealth()

            # Army encounters
            for army in world.armies.keys():
                desertion = 1
                surroundlist = surrounding(army[0], army[1], world.armies[army].mr)

                # Raid settlement
                if bool(set(world.poplist) & set(surroundlist)):
                    inmr = list(set(world.poplist) & set(surroundlist))
                    for pob in inmr:
                        if world.armies[army].owner != world.pops[pob].owner:
                            world.pops[pob].size += -(world.armies[army].size*world.armies[army].s_damagerate)
                            world.pops[pob].food = 0 

                # Engage foreign army
                if bool(set(world.armies.keys()) & set(surroundlist)):
                    inmr = list(set(world.armies.keys()) & set(surroundlist))
                    for farmy in inmr:
                        # Assault foreign fortification
                        if world.armies[army].owner != world.armies[farmy].owner:
                            world.armies[farmy].damagetaken += world.armies[army].size*world.armies[army].a_damagerate

                # Interact with fortifications
                if bool(set(world.forts.keys()) & set(surroundlist)):
                    inmr = list(set(world.forts.keys()) & set(surroundlist))
                    for fort in inmr:
                        # Assault foreign fortification
                        if world.armies[army].owner != world.forts[fort].owner:
                            world.forts[fort].damagetaken += world.armies[army].size*world.armies[army].o_damagerate
                        # Avoid desertion if an allied fortification is in range
                        else:
                            desertion = 0
                if desertion == 1:
                    world.armies[army].grow()

            # Fortification actions
            for fort in world.forts.keys():
                surroundlist = surrounding(fort[0], fort[1], world.forts[fort].mr)
                # Harass army
                if bool(set(world.armies.keys()) & set(surroundlist)):
                    inmr = list(set(world.armies.keys()) & set(surroundlist))
                    for army in inmr:
                        if world.forts[fort].owner !=  world.armies[army].owner:
                            world.armies[army].damagetaken += world.forts[fort].size*world.forts[fort].a_damagerate
                # Sustain casualties
                world.forts[fort].size += -world.forts[fort].damagetaken
                world.forts[fort].damagetaken = 0
                if world.forts[fort].size < 0:
                    world.forts[fort].size = 0

            # Manage army sizes
            for army in list(world.armies.keys()):
                # Sustain casualties
                world.armies[army].size += -world.armies[army].damagetaken
                world.armies[army].damagetaken = 0
                # Disband
                if world.armies[army].size <= 0:
                    if 'armysel_pos' in locals() and army == armysel_pos:
                        armysel = 0
                        del armysel_pos
                    world.armies[army].disband(world)
                    local_refresh_pad(army[0], army[1], char_dict, col_dict, world)

            # Population grow
            for pop in world.poplist:
                world.pops[pop].grow(world)

        # Estimate faction sizes
        for faction in world.factions.keys():
            size = 0
            for pop in world.factions[faction].pops:
                size += int(world.pops[pop].size)
            world.factions[faction].size = size

################################################################################
# Screen operations

        # Initialization
        curses.curs_set(True)
        curses.napms(41) #41
        stdscr.erase()
        height, width = stdscr.getmaxyx()

        # The cursor will be moving in the pad
        cursor_y, cursor_x = trace_cursor(k, cursor_y, cursor_x)
        cursor_x = max(0, cursor_x)
        cursor_x = min(pwidth-2, cursor_x)
        cursor_y = max(0, cursor_y)
        cursor_y = min(pheight-2, cursor_y)

        # Scroll the world pad
        if world.factions[u["name"]].startpop == 0:
            if cursor_y <= wpshow[0]-1:
                wpshow[0] = cursor_y
            elif cursor_y >= wpshow[0]+11:
                wpshow[0] = cursor_y-10
            if cursor_x <= wpshow[1]-1:
                wpshow[1] = cursor_x
            elif cursor_x >= wpshow[1]+11:
                wpshow[1] = cursor_x-10

        # Update and print date
        calendar.update()
        calstr = str(calendar)
        datstr = "╣ "+ u["name"] +", "+ calstr +" ╠"
        centpos = int((width // 2) - (len(datstr) // 2) - len(datstr) % 2)
        stdscr.addstr(0, centpos, datstr, curses.color_pair(7))

        # View faction data
        mainfac = list(world.factions.keys())[0]
        factstr = " ║ Size: "
        factstr += str(int(world.factions[mainfac].size))
        factstr += " ║ Wealth: "
        factstr += str(int(world.factions[mainfac].wealth))
        factstr += " ║"
        stdscr.addstr(1, 0, factstr)
        settlementstr = " ║ Settlements: "
        settlementstr += " ".join(world.factions[mainfac].settlements + world.factions[mainfac].fortlist)
        settlementstr += " ║"
        stdscr.addstr(2, 0, settlementstr)
        claimedstr0 = " ║ Domains: "
        for cell in world.factions[mainfac].cells:
            claimedstr0 += char_dict[cell] +" "
        claimedstr0 += "║"
        stdscr.addstr(3, 0, claimedstr0)

        # View information on the map
        if (cursor_x,cursor_y) in world.factions[u["name"]].explored:
            stdscr.addstr(6, 18, type_dict[world.mat[cursor_y,cursor_x]])
            if (cursor_x,cursor_y) in world.pops.keys():
                stdscr.addstr(7, 18, world.pops[(cursor_x,cursor_y)].name)
                stdscr.addstr(8, 18, "("+world.pops[(cursor_x,cursor_y)].owner+")")
                stdscr.addstr(9, 18, str(int(world.pops[(cursor_x,cursor_y)].size))+" inhabitants")
                stdscr.addstr(10, 18,"Food: "+str(int(world.pops[(cursor_x,cursor_y)].food)))
                claimedstr = "Claimed territories: "
                for cell in world.pops[(cursor_x,cursor_y)].claimed:
                    claimedstr += char_dict[cell] +" "
                stdscr.addstr(11,18, claimedstr)

            elif (cursor_x,cursor_y) in world.forts.keys(): 
                stdscr.addstr(7, 18, "("+world.forts[(cursor_x,cursor_y)].owner+")")
                stdscr.addstr(8, 18, str(int(world.forts[(cursor_x,cursor_y)].size))+" strong")

            elif (cursor_x,cursor_y) in world.armies.keys(): 
                stdscr.addstr(7, 18, world.armies[(cursor_x,cursor_y)].name)
                stdscr.addstr(8, 18, "("+world.armies[(cursor_x,cursor_y)].owner+")")
                stdscr.addstr(9, 18, str(int(world.armies[(cursor_x,cursor_y)].size))+" strong")

            else:
                stdscr.addstr(7, 18,"Unpopulated")

        else:
            stdscr.addstr(6, 18, "Uncharted")

        # Selected information
        if armysel == 0:
            stdscr.addstr(18, 1, "'a': select army.")
        else:
            selstr = "Selected army: "+world.armies[(armysel_pos[0],armysel_pos[1])].name+", "
            selstr += str(int(world.armies[(armysel_pos[0],armysel_pos[1])].size)) +" strong"
            stdscr.addstr(18, 1, selstr)
            stdscr.addstr(19, 1, "'z': mobilize.")

        if selected == 0:
            stdscr.addstr(21, 1, "'s': select settlement.")
        else:
            selstr = "Selected settlement: "+world.pops[(selected_pos[0],selected_pos[1])].name+", "
            selstr += str(int(world.pops[(selected_pos[0],selected_pos[1])].size))+" inhabitants"
            stdscr.addstr(21, 1, selstr)
            selstr = "'x': explore; 'c': claim; 'f': build farm."
            stdscr.addstr(22, 1, selstr)
            if world.mat[selected_pos[1]][selected_pos[0]] in (8,9):
                selstr = "'e': colonyze; 'o': build fort; 'm': muster; 'r': reinforce."
                stdscr.addstr(23, 1, selstr)
            if world.mat[selected_pos[1]][selected_pos[0]] == 9:
                selstr = "'u': upgrade fort."
                stdscr.addstr(24, 1, selstr)

        # Announcements
        if world.factions[u["name"]].startpop == 1:
            wellcomestr = " Choose a tile with the cursor and press 'b' to establish a settlement."
            stdscr.addstr(height-3, 0, wellcomestr, curses.color_pair(1))
        else:
            stdscr.addstr(height-3, 0, logstr, curses.color_pair(1))

        # Render lower bar
        usernames = []
        for user in users:
            usernames.append(user['name']) 
        #statusbarstr = " ║ Quit 'q' ║ "+ ' ╦ '.join(usernames) +" ║ Last: {} Pos: {}, {} ║"
        #statusbarstr = statusbarstr.format(k , cursor_y, cursor_x)
        statusbarstr = " Quit 'q' ║ "+ ' ╦ '.join(usernames) +" ║ Pos: {}, {}"
        statusbarstr = statusbarstr.format(cursor_y, cursor_x)
        stdscr.attron(curses.color_pair(4))
        stdscr.addstr(height-1, 0, statusbarstr)
        stdscr.addstr(height-1, len(statusbarstr), " " * (width - len(statusbarstr) - 1))
        stdscr.attroff(curses.color_pair(4))

        # Move the cursor
        world.pad.move(cursor_y, cursor_x)

        # Refresh the screen
        stdscr.refresh()

        # Refresh the world
        #world_pad.refresh( 0,0, 6,5, height-14,width-5)
        world.pad.refresh(wpshow[0],wpshow[1],6,5,16,15)

        # Get next input
        k = stdscr.getch()

################################################################################
# Main menu

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

        if k == 10 and cursor_y == (height // 2) + 1:
            cosmogon_single(stdscr)

        if k == 10 and cursor_y == (height // 2) + 2:
            cosmogon(stdscr)

        if k == 10 and cursor_y == (height // 2) + 3:
            #child = subprocess.Popen('xterm -e "python3.6 data/manage_server.py"')
            child = subprocess.Popen('xterm -e "python3.6 data/manage_server.py"', shell = True)

        if k == 10 and cursor_y == (height // 2) + 4:
            sys.exit()


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
        cursor_y = min(int((height // 2) + 4), cursor_y)

        # Strings
        statusbarstr = " Miguel Romero 2020 | github.com/miferg "
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
            stdscr.addstr(start_y + 3, (width // 2) - 6, 'Single-user', curses.A_STANDOUT)
        else:
            stdscr.addstr(start_y + 3, (width // 2) - 6, 'Single-user')
        if cursor_y == (height // 2) + 2:
            stdscr.addstr(start_y + 4, (width // 2) - 5, 'Multi-user', curses.A_STANDOUT)
        else:
            stdscr.addstr(start_y + 4, (width // 2) - 5, 'Multi-user')
        if cursor_y == (height // 2) + 3:
            stdscr.addstr(start_y + 5, (width // 2) - 4, 'Server', curses.A_STANDOUT)
        else:
            stdscr.addstr(start_y + 5, (width // 2) - 4, 'Server')
        if cursor_y == (height // 2) + 4:
            stdscr.addstr(start_y + 6, (width // 2) - 3, 'Exit', curses.A_STANDOUT)
        else:
            stdscr.addstr(start_y + 6, (width // 2) - 3, 'Exit')

        # Move the cursor
        stdscr.move(cursor_y, cursor_x)

        # Refresh the screen
        stdscr.refresh()

        # Wait for next input
        k = stdscr.getch()

