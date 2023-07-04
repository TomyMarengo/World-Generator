import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from enum import Enum


class Terrain(Enum):
    Ocean = (0, '#010070')
    Land = (1, '#8EB35F')

    def to_rgb(self):
        return mcolors.to_rgba(self.value[1])


class BiomeMap:
    BE_LAND = 1 / 10
    ADD_LAND = BE_LAND * 5
    REMOVE_OCEAN = 1 / 2
    PIXEL_LENGTH = 4096
    MAP_LENGTH = PIXEL_LENGTH * 4

    def __init__(self):
        self.map = None
        self.steps = [
            (f'Oceans ({self.PIXEL_LENGTH})', self.oceans, self.MAP_LENGTH),
            (f'First Islands ({self.PIXEL_LENGTH})', self.islands, self.PIXEL_LENGTH),
            (f'Add Islands ({self.PIXEL_LENGTH / 2})', self.add_islands, int(self.PIXEL_LENGTH / 2)),
            (f'Add Islands ({self.PIXEL_LENGTH / 4})', self.add_islands, int(self.PIXEL_LENGTH / 4)),
            (f'Remove Too Much Ocean ({self.PIXEL_LENGTH / 4})', self.remove_too_much_ocean, int(self.PIXEL_LENGTH / 4)),
        ]

    def generate(self, b_plot: bool):
        for step in self.steps:
            fun = step[1]
            args = step[2:]
            fun(*args)
            if b_plot:
                self.plot(step[0])

        if not b_plot:
            self.plot("Final result")

    def oceans(self, zoom):
        self.map = np.zeros((zoom, zoom))

    def islands(self, zoom):
        for i in range(0, self.map.shape[0], zoom):
            for j in range(0, self.map.shape[1], zoom):
                if np.random.random() < self.BE_LAND:
                    self.map[i:i + zoom, j:j + zoom] = Terrain.Land.value[0]

    def add_islands(self, zoom):
        # zoom start -> zoom param
        # adds mistakes to islands
        map_copy = np.copy(self.map)

        for i in range(0, self.map.shape[0], zoom * 2):
            for j in range(0, self.map.shape[1], zoom * 2):
                if map_copy[i, j] == Terrain.Land.value[0]:
                    for k in [i - zoom, i, i + zoom, i + zoom * 2]:
                        for m in [j - zoom, j, j + zoom, j + zoom * 2]:
                            if 0 <= k <= self.MAP_LENGTH - zoom and 0 <= m <= self.MAP_LENGTH - zoom:
                                self.map[k: k + zoom, m: m + zoom] = np.random.random() < self.ADD_LAND

    def remove_too_much_ocean(self, zoom):
        map_copy = np.copy(self.map)

        for i in range(0, self.map.shape[0], zoom):
            for j in range(0, self.map.shape[1], zoom):
                if self.__verify_neighbors(map_copy, i, j, zoom, lambda x: x == 0):
                    self.map[i: i + zoom, j: j + zoom] = np.random.random() < self.REMOVE_OCEAN

    def __verify_neighbors(self, map_copy, row, col, zoom, fun):
        neighbors = []

        if row > 0:
            neighbors.append((row - zoom, col))  # Upper neighbor
        if row < self.map.shape[0] - zoom:
            neighbors.append((row + zoom, col))  # Lower neighbor
        if col > 0:
            neighbors.append((row, col - zoom))  # Left neighbor
        if col < self.map.shape[1] - zoom:
            neighbors.append((row, col + zoom))  # Right neighbor

        for r, c in neighbors:
            if not fun(map_copy[r, c]):
                return False

        return True

    def plot(self, title):
        plt.imshow(self.map, cmap=plt.cm.colors.ListedColormap([terrain.to_rgb() for terrain in Terrain]))
        plt.xticks([])
        plt.yticks([])
        plt.axis('off')
        plt.title(title)
        plt.figure(figsize=(8, 8))
        plt.show()
