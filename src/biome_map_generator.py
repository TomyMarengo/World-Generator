import numpy as np
import random
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, Normalize
from enum import Enum


class Terrain(Enum):
    Ocean = (0, '#010070')
    Land = (1, '#8EB35F')
    Warm = (2, '#FA9417')
    Cold = (3, '#056720')
    Freezing = (4, '#FFFFFF')
    DeepOcean = (5, '#00002E')


class BiomeMap:
    BE_LAND = 1 / 10
    ADD_LAND = BE_LAND * 5
    REMOVE_OCEAN = 1 / 2
    BE_WARM = 4 / 6
    BE_COLD = 1 / 6
    BE_FREEZING = 1 - BE_WARM - BE_COLD
    PIXEL_LENGTH = 4096
    MAP_LENGTH = PIXEL_LENGTH * 4

    def __init__(self):
        self.map = None
        self.steps = [
            # First
            (f'Oceans (Zoom: {self.PIXEL_LENGTH})', self.oceans),
            (f'First Islands (Zoom: {self.PIXEL_LENGTH})', self.islands, self.PIXEL_LENGTH),

            # Zoom
            (f'Add Islands (Zoom: {self.PIXEL_LENGTH // 2})', self.add_islands, self.PIXEL_LENGTH // 2),

            # Zoom
            (f'Add Islands (Zoom: {self.PIXEL_LENGTH // 4})', self.add_islands, self.PIXEL_LENGTH // 4),
            (f'Remove Too Much Ocean (Zoom: {self.PIXEL_LENGTH // 4})', self.remove_too_much_ocean,
             self.PIXEL_LENGTH // 4),

            # Zoom
            (f'Add Islands (Zoom: {self.PIXEL_LENGTH // 8})', self.add_islands, self.PIXEL_LENGTH // 8),

            # Zoom
            (f'Add Islands (Zoom: {self.PIXEL_LENGTH // 16})', self.add_islands, self.PIXEL_LENGTH // 16),
            (f'Add Deep Oceans (Zoom: {self.PIXEL_LENGTH // 16})', self.add_deep_ocean, self.PIXEL_LENGTH // 16),
            (f'Add Temperatures (Zoom: {self.PIXEL_LENGTH // 16})', self.add_temperatures, self.PIXEL_LENGTH // 16)
            #
            # Change temperatures
            # Add biome variants
            #

        ]

    def generate(self, b_plot: bool):
        for step in self.steps:
            print(f"Step {step[0]}")
            fun = step[1]
            args = step[2:]
            fun(*args)
            if b_plot:
                self.plot(step[0])

        if not b_plot:
            self.plot("Final result")

    def oceans(self):
        self.map = np.zeros_like(np.zeros((self.MAP_LENGTH, self.MAP_LENGTH))).astype(int)

    def islands(self, zoom):
        for i in range(0, self.map.shape[0], zoom):
            for j in range(0, self.map.shape[1], zoom):
                if np.random.random() < self.BE_LAND:
                    self.map[i:i + zoom, j:j + zoom] = Terrain.Land.value[0]

    def add_islands(self, zoom):
        # adds mistakes to islands
        map_copy = np.copy(self.map)

        for i in range(0, self.map.shape[0], zoom * 2):
            for j in range(0, self.map.shape[1], zoom * 2):
                if map_copy[i, j] == Terrain.Land.value[0]:
                    for k in [i - zoom, i, i + zoom, i + zoom * 2]:
                        for m in [j - zoom, j, j + zoom, j + zoom * 2]:
                            if 0 <= k <= self.MAP_LENGTH - zoom and 0 <= m <= self.MAP_LENGTH - zoom:
                                self.map[k: k + zoom, m: m + zoom] = np.random.random() < self.ADD_LAND

    def add_temperatures(self, zoom):
        options = [Terrain.Warm, Terrain.Cold, Terrain.Freezing]
        probs = [self.BE_WARM, self.BE_COLD, self.BE_FREEZING]

        for i in range(0, self.map.shape[0], zoom):
            for j in range(0, self.map.shape[1], zoom):
                if self.map[i, j] == Terrain.Land.value[0]:
                    terrain = random.choices(options, probs)[0]
                    self.map[i: i + zoom, j: j + zoom] = terrain.value[0]

    def remove_too_much_ocean(self, zoom):
        # 50% to become land if it is surrounded by all ocean
        map_copy = np.copy(self.map)

        for i in range(0, self.map.shape[0], zoom):
            for j in range(0, self.map.shape[1], zoom):
                if self.__verify_neighbors(map_copy, i, j, zoom, lambda x: x == 0):
                    self.map[i: i + zoom, j: j + zoom] = np.random.random() < self.REMOVE_OCEAN

    def add_deep_ocean(self, zoom):
        map_copy = np.copy(self.map)

        for i in range(0, self.map.shape[0], zoom):
            for j in range(0, self.map.shape[1], zoom):
                if map_copy[i, j] == Terrain.Ocean.value[0] and self.__verify_neighbors(map_copy, i, j, zoom, lambda x: x == 0):
                    self.map[i: i + zoom, j: j + zoom] = Terrain.DeepOcean.value[0]

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
        values = np.unique(self.map)
        colors = []

        for i in range(max(values)+1):
            if i in values:
                colors.append(list(Terrain)[i].value[1])
            else:
                colors.append('#000000')

        cmap = ListedColormap(colors)

        plt.title(title)
        plt.imshow(self.map, cmap=cmap,  interpolation='nearest')
        plt.axis('off')
        plt.show()
