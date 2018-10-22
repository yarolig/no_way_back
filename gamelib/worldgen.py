import numpy as np
import random
import logging
import math
import time
import noise.perlin


class Cell:
    # islands, ocean, coast, plains, hills, mountains, ice
    # belongs to one of 6 continents
    # has terrain height
    # may be a port
    # may be a special place
    # ports and some special places should have safe path to sp0
    # some special places should have only dangerous path to ports
    # one continent should have a roads between ports
    # one continent should have a rivers
    # two continents should have a space for continental races
    continent = 0
    z = 0


class World:
    def __init__(self):
        w = 100
        h = 100
        self.width = w
        self.height = h
        self.z = np.ndarray(shape=(w, h), dtype=float)
        self.continent = np.ndarray(shape=(w, h), dtype=int)
        self.elevation = np.ndarray(shape=(w, h), dtype=int)
        self.marks = np.ndarray(shape=(w, h), dtype=int)
        self.base = 0

    def create_continent_map(self):
        def continent_noise(x, y):
            return noise.pnoise3(
                float(x) / self.width,
                float(y) / self.height,
                1.0,
                octaves=6, persistence=0.84123, lacunarity=2.412,
                repeatx=1, repeaty=1, repeatz=1,
                base=self.base)

        s = ""
        for i in range(100):
            for j in range(100):
                c = continent_noise(i, j)

                print (c)
                ch = ' '

                if c < -0.2:
                    self.elevation[i][j] = -1
                    ch = '='
                elif c < 0.1:
                    self.elevation[i][j] = 0
                    ch = '~'
                elif c < 0.3:
                    self.elevation[i][j] = 2
                    ch = '.'
                else:
                    self.elevation[i][j] = 3
                    ch = '^'
                s += ch
            s += '\n'
        print(s)
        # print(help(noise.pnoise3))
        # print(help(noise.pnoise2))

    def generate(self):
        logging.info('creating continent map')
        random.seed()
        self.create_continent_map()
        logging.info('placing random markers on terrain')

        def increase(x, y):
            x += 1
            if x == self.width:
                x = 0
                y += 1
            if y == self.height:
                y = 0
            return x, y

        for i in range(1, 20):
            for t in range(200):
                x, y = random.randint(1, 99), random.randint(1, 99)
                if self.elevation[x][y] >= 1:
                    self.marks[x][y] = i
                    logging.info("placing mark {} on {} {}".format(i, x, y))
                    break
            else:
                logging.info("not placing mark {}".format(i))

        def print_marks():
            s = ""
            for i in range(100):
                for j in range(100):
                    m = self.marks[i][j]
                    if 1 <= m <= ord('z'):
                        ch = chr(ord('a') + m - 1)
                    else:
                        ch = chr(ord('.') - 2 + self.elevation[i][j])
                    s += ch
                s += '\n'
            print(s)

        print_marks()
        logging.info('expanding markers')

        dirs = [
            (-1, 0),
            (1, 0),
            (0, 1),
            (0, -1),
            (-1, -1),
            (1, 1),
            (-1, 1),
            (1, -1),
        ]
        for cycle in range(100):
            fills = 0
            for i in range(0, 100):
                for j in range(0, 100):
                    if self.marks[i][j] == 0 and self.elevation[i][j] >= 1:
                        for dx, dy in dirs:
                            m = self.marks[(i + dx + 100) % 100][(j + dy + 100) % 100]
                            if m != 0:
                                self.marks[i][j] = m
                                fills += 1
                                break
            logging.info('cycle {} ends. {} fills'.format(cycle, fills))
            # print_marks()
            if fills == 0:
                break
                # time.sleep(0.1)

        logging.info('checking if there is enough expanded markers to form a continent')
        mark_sizes = [0] * 100
        for i in range(0, 100):
            for j in range(0, 100):
                m = self.marks[i][j]
                if 0 < m < 21:
                    mark_sizes[m] += 1
        for m in range(1, 20):
            print("mark {} size = {}".format(chr(ord('a') + m - 1), mark_sizes[m]))
        logging.info('assigning continents')
        logging.info('creating heightmap')

        def z_noise(x, y):
            if self.elevation[int(x)%self.width][int(y)%self.height] <=0:
                return -200.0 * math.fabs(noise.pnoise3(
                    float(x) / self.width,
                    float(y) / self.height,
                    1.2,
                    octaves=6, persistence=0.84123, lacunarity=2.41212,
                    repeatx=1, repeaty=1, repeatz=1,
                    base=self.base))
            return 200.0 * noise.pnoise3(
                float(x) / self.width,
                float(y) / self.height,
                1.2,
                octaves=6, persistence=0.74123, lacunarity=3.41212,
                repeatx=1, repeaty=1, repeatz=1,
                base=self.base)
        self.getz = z_noise
        logging.info('placing special place 0')
        logging.info('placing ports')
        logging.info('placing special places')
        logging.info('placing premade races')
        logging.info('saving world')
        logging.info('done')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    w = World()
    w.generate()
