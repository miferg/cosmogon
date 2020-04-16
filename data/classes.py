#! /usr/bin/python3
"""
Class definitions for cosmogon to work.
"""

import time

################################################################################

class Calendar(object):
    def __init__(self):
        self.month = 0
        self.year = 0
        self.origin = 0

    def __str__(self):
        return "Year: {}, Month: {}".format(self.year, self.month + 1)

    def update(self):
        change = time.perf_counter() - self.origin
        # month duration in seconds
        dur = 0.5
        self.year = int(change // (12 * dur))
        self.month = int((change % (12 * dur)) // dur)

################################################################################

class World(object):
    def __init__(self, name, h, w):
        self.name = name
        self.mat = "" #numpy.random.randint(1,size=(h,w)) + 1
        self.h = h
        self.w = w
        self.pops = {}
        self.map = {}
        self.col = {}
        self.factions = {}
        self.poplist = []
        self.pad = False
        self.forts = {}

    def __str__(self):
        return name

    def gen_terr(self): # generate terrain with probability functions, eventually...
        pass

    def gen_map(self, char_dict):
        for x in range(0,self.w):
            for y in range (0,self.h):
                self.map[(x,y)] = char_dict[self.mat[y,x]]

    def gen_col(self, col_dict):
        for x in range(0,self.w):
            for y in range (0,self.h):
                self.col[(x,y)] = col_dict[self.mat[y,x]]

    def create_pop(self,world,x,y,name,owner):
        if self.factions[owner].startpop == 1:
            if world.mat[y][x] in (3, 4, 5):
                self.pops[(x,y)] = Population(name, owner, x,y)
                self.mat[y][x] = 7
                self.poplist.append((x,y))
                self.factions[owner].pops.append((x,y))
                self.factions[owner].wealthrate += 1
                self.factions[owner].startpop = 0
                self.factions[owner].settlements.append('ᵃ')

################################################################################

class Faction(object):
    def __init__(self, name):
        self.name = name
        self.size = 0
        self.knowfor = 0
        self.workfor = 0
        self.warfor = 0
        self.wealth = 0
        self.pops =[]
        self.wealthrate = 0
        self.startpop = 1
        self.availpops = 0
        self.availcities = 1
        self.availtowns = 3
        self.cells = []
        self.settlements = []
        self.fortifications = []
        self.availfortresses = 1
        self.fortresscost = 10000

    def __srt__(self):
        return self.name +", "+ str(self.size) +" inhabitants."

    def get_wealth(self):
        self.wealth = self.wealth + self.wealthrate

################################################################################

class Population(object):
    def __init__(self, name, owner, x, y):
        self.name = name
        self.size = 1000
        self.growth = 0.006
        self.owner = owner
        self.influence = {self.owner:100}
        self.cap = 10000
        self.farms = 2
        self.farmcost = 50
        self.pos_x = x
        self.pos_y = y
        self.claimslots = 2
        self.claimed = []
        self.claimedpos = []
        self.claimcost = 10
        self.ar = 1  # aggro range for farms and claims
        self.colonizecost = 1000
        self.food = 1
        self.foodprod = 0
        self.fortcost = 1500
        self.availforts = 1

    def grow(self):
        self.size = self.size + (self.size*self.growth*((self.cap-self.size)/self.cap))
        if self.size > self.cap:
            self.size = self.cap
        if self.size < 0:
            self.size = 0
        if self.food == 0:
            self.size = self.size - self.size*0.01

    def get_food(self, world):
        world.factions[self.owner].wealth += self.food
        self.food = self.foodprod

    def build_town(self, world):
        if world.factions[self.owner].wealth >= 1000:
            if world.factions[self.owner].availtowns > 0:
                if self.size >= 9000:
                    if self.food >= 2:
                        world.mat[self.pos_y][self.pos_x] = 8
                        self.cap = 100000
                        self.farms += 1
                        self.claimslots += 1
                        self.ar += 2
                        self.food += -2
                        world.factions[self.owner].wealth += -1000
                        world.factions[self.owner].wealthrate += 2
                        world.factions[self.owner].availtowns += -1
                        world.factions[self.owner].availpops += 2
                        world.factions[self.owner].settlements.remove('ᵃ')
                        world.factions[self.owner].settlements.append('a')

    def build_city(self, world):
        if world.factions[self.owner].wealth >= 10000:
            if world.factions[self.owner].availcities > 0:
                if self.size >= 90000:
                    if self.food >= 3:
                        world.mat[self.pos_y][self.pos_x] = 9
                        self.cap = 1000000
                        self.farms += 2
                        self.claimslots += 1
                        self.ar += 4
                        self.food += -3
                        world.factions[self.owner].wealth += -10000
                        world.factions[self.owner].wealthrate += 4
                        world.factions[self.owner].availcities += -1
                        world.factions[self.owner].settlements.remove('a')
                        world.factions[self.owner].settlements.append('A')

    def colonize(self, x, y, world, name):
        if self.pos_x + self.ar+3 >= x >= self.pos_x - self.ar-3:
            if self.pos_y + self.ar+3 >= y >= self.pos_y - self.ar-3:
                if world.factions[self.owner].wealth >= self.colonizecost:
                    if world.factions[self.owner].availpops > 0:
                        if world.mat[y][x] in (3, 4, 5):
                            if self.size >= 10000:
                                world.pops[(x,y)] = Population(name, self.owner, x,y)
                                world.mat[y][x] = 7
                                world.poplist.append((x,y))
                                world.factions[self.owner].pops.append((x,y))
                                world.factions[self.owner].availpops += -1
                                world.factions[self.owner].wealthrate += 1
                                world.factions[self.owner].wealth += -self.colonizecost
                                world.factions[self.owner].settlements.append('ᵃ')
                                self.colonizecost = self.colonizecost*2
                                self.size = self.size - 2000

    def build_fort(self, x, y, world):
        if self.pos_x + self.ar+4 >= x >= self.pos_x - self.ar-4:
            if self.pos_y + self.ar+4 >= y >= self.pos_y - self.ar-4:
                if world.factions[self.owner].wealth >= self.fortcost:
                    if self.availforts > 0:
                        if world.mat[y][x] in (3, 4, 5):
                            if self.size >= 10000:
                                world.forts[(x,y)] = Fortification(self.owner, x, y)
                                world.mat[y][x] = 10
                                world.factions[self.owner].fortifications.append((x,y))
                                world.factions[self.owner].wealthrate += -0.5
                                world.factions[self.owner].wealth += -self.fortcost
                                world.factions[self.owner].settlements.append('ø')
                                self.availforts += -1
                                self.size = self.size - 2000

    def upgrade_fort(self, x, y, world):
        if world.factions[self.owner].wealth >= world.factions[self.owner].fortresscost:
            if world.factions[self.owner].availfortresses > 0:
                if world.mat[y][x] == 10:
                    if self.size >= 100000:
                        world.mat[y][x] = 11
                        world.forts[(x,y)].cap = 15000
                        world.forts[(x,y)].mr += 4
                        world.forts[(x,y)].size += 9000
                        world.factions[self.owner].wealthrate += -1
                        world.factions[self.owner].wealth += -world.factions[self.owner].fortresscost
                        world.factions[self.owner].settlements.remove('ø')
                        world.factions[self.owner].settlements.append('Ø')
                        world.factions[self.owner].availfortresses += -1
                        self.size = self.size - 20000

    def build_farm(self, x, y, world):
        if self.farms > 0 and world.factions[self.owner].wealth >= self.farmcost:
            if self.pos_x + self.ar >= x >= self.pos_x - self.ar:
                if self.pos_y + self.ar >= y >= self.pos_y - self.ar:
                    if world.mat[y][x] in (3,4):
                        world.mat[y][x] = 6
                        self.growth += 0.002
                        self.farms += -1
                        world.factions[self.owner].wealthrate += 1
                        world.factions[self.owner].wealth += -self.farmcost
                        self.farmcost += 100
                        self.foodprod += 1

    def claim(self, x, y, world):
        if world.mat[y][x] in (1,2,3,4,5):
            if self.claimslots > 0:
                if self.pos_x + self.ar >= x >= self.pos_x - self.ar:
                    if self.pos_y + self.ar >= y >= self.pos_y - self.ar:
                        if (x,y) not in self.claimedpos:
                            if world.factions[self.owner].wealth >= self.claimcost:
                                world.factions[self.owner].wealth += -self.claimcost
                                world.factions[self.owner].cells.append(world.mat[y][x])
                                self.claimcost = self.claimcost*10
                                world.factions[self.owner].wealthrate += 0.5
                                self.claimed.append(world.mat[y][x])
                                self.claimslots += -1
                                self.claimedpos.append((x,y))
                                if  world.mat[y][x] in (1,2,3):
                                    self.food += 1

    def turn(self):
        if len(list(self.influence.keys())) > 1:
            for other in list(self.influence.keys())[1:]:
                if self.influence[other] > self.influence[owner]:
                    self.owner = other

################################################################################

class Fortification(object):
    def __init__(self, owner, x, y):
        self.size = 1000
        self.owner = owner
        self.influence = {self.owner:100}
        self.cap = 3000
        self.pos_x = x
        self.pos_y = y
        self.mr = 4  # manuveur range




