from __future__ import print_function
import numpy as np
import random
import math
import logging
import time


class NameGen(object):
    generated = {}
    town_prefixes = '''
Bay Beaver Beer Brew Bubble Boulder Brave
Cent Crew Copper Corn Cram Cool Coal
Dubber Donut Dough Dumb Drunk Dunk Duck
'''.split()
    town_suffixes = '''
burg town yard haven hill
bridge mouth ham ford
mund furt
hall tunnel crest
'''.split()

    @staticmethod
    def gen_town_name():
        for x in range(1000):
            p = random.choice(NameGen.town_prefixes)
            s = random.choice(NameGen.town_suffixes)
            name = p + s
            if name in NameGen.generated:
                pp = random.choice('New Old Upper Another'.split())
                name = pp + " " + name
                if name in NameGen.generated:
                    continue
            NameGen.generated[name] = True
            return name
        else:
            return "Watburg"

    @staticmethod
    def clear():
        NameGen.generated = {}


class Port(object):
    def __init__(self):
        self.name = NameGen

    def visit(self, player):
        pass


QS_INITIAL = 0
QS_KNOWN = 10
QS_SUCCESS = 80
QS_FAIL = 90


class Quest(object):
    def __init__(self):
        self.name = 'Quest Name'
        self.description = 'Description'
        self.state = QS_INITIAL

    def onPortVisit(self, port, player):
        pass

    def onSpecialSiteVisit(self, site, player):
        pass

    def onTimer(self):
        pass


# Regions:
# Hilland - home
# Sandland - dangerous, sinks, airships
# Riverland - rich
# Swampland - geyser
# Showland - far
# Rainland - exotic
REGION_HILLAND = 1
REGION_SANDLAND = 2
REGION_RIVERLAND = 3
REGION_SWAMPLAND = 4
REGION_SNOWLAND = 5
REGION_RAINLAND = 6
REGIONS = '''Random Hilland Sandland Riverland Swampland Showland Rainland'''.split()


class Quest1(object):
    def __init__(self):
        self.name = 'Visit HQ'
        self.description = 'Visit Great Logistics Company HQ'

    def onPortVisit(self, port, game):
        pass

    def onSpecialSiteVisit(self, site, game):
        pass


class Town(object):
    pass
    name = ""
    region = 0

    def __str__(self):
        return "{} {}".format(REGIONS[self.region], self.name)


def make_town(continental=None, region=0):
    t = Town()
    t.name = NameGen.gen_town_name()
    if region == 0:
        region = random.randint(1, 6)
    t.region = region
    # TODO: find placement in region
    return t


# 0. Depart. (t0) Hilland
# 1. Visit Great Logistics Company HQ (t1) Hilland
# 2. Finish the course around one island (s0,s1) Hilland
# 3. Visit 3 reliability managers. (t1,t2,t3,t4) Hilland
# 4. Finish the route without fuel. (t2,s2,s3) Hilland
# 5. Finish the route with dangerous currents (t3,s4,s5,s6). Sandland
# 6. Find 3 towns with cheap fuel / Make money in limited time (t4,t5,t6,t7,t4). Riverland
# 7. Visit 4 towns to prepare the new Regatta. (t8,t9,t10,t11)Riverland Swampland Sandland Showland
# 8. Race around the continent. (On rails!) (t0,s7,s8,s9) Hilland
# 9. Participate in Regatta. (t1) Hilland
# 10. River race (t12) Riverland
# 11. Swamp race (t13) Swampland
# 12. Channel race (t14) Sandland
# 13. Ice pool race (t15) Showland
# 14. Strange flow. (Alien biology!) (t1, s99) Hilland, Showland
# - Bring the exotic good from a far port. (t4,t16) Riverland, Rainland
# - Rescue crew/goods from stranded! ship. (t3) Sandland
# - Traver around the world. (Sphere!) (t2) Hilland
def prepare_quests(game):
    game.towns = []
    game.towns.append(make_town(region=REGION_HILLAND))  # 0
    game.towns.append(make_town(region=REGION_HILLAND))  # 1
    game.towns.append(make_town(region=REGION_HILLAND))  # 2
    game.towns.append(make_town(region=REGION_SANDLAND))  # 3
    game.towns.append(make_town(region=REGION_RIVERLAND))  # 4

    game.towns.append(make_town(region=REGION_RIVERLAND))  # 5
    game.towns.append(make_town(region=REGION_SWAMPLAND))  # 6
    game.towns.append(make_town(region=REGION_SANDLAND))  # 7

    game.towns.append(make_town(region=REGION_RIVERLAND))  # 8
    game.towns.append(make_town(region=REGION_SWAMPLAND))  # 9
    game.towns.append(make_town(region=REGION_SANDLAND))  # 10
    game.towns.append(make_town(region=REGION_SNOWLAND))  # 11

    game.towns.append(make_town(region=REGION_RIVERLAND))  # 12
    game.towns.append(make_town(region=REGION_SWAMPLAND))  # 13
    game.towns.append(make_town(region=REGION_SANDLAND))  # 14
    game.towns.append(make_town(region=REGION_SNOWLAND))  # 15

    game.towns.append(make_town(region=REGION_RAINLAND))  # 16

    for i in range(32):
        game.towns.append(make_town())
    game.quests = []


def port_visited(game, port):
    for q in game.quests:
        q.onPortVisit(port, game)


def site_visited(game, site):
    for q in game.quests:
        q.onPortVisit(site, game)


class Blank:
    pass


if __name__ == '__main__':
    ng = NameGen
    for i in range(100):
        print(ng.gen_town_name())
    ng.clear()
    print('\n\n\n')
    game = Blank()
    prepare_quests(game)
    i = 0
    for t in game.towns:
        print(i, t)
        i += 1
