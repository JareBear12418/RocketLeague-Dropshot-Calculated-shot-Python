import cv2 # pip install opencv-python
import map_coords
import numpy as np # pip install numpy
import math
import random

TEAM: str = 'blue' # This is the team you are one
if TEAM == 'blue': 
    team_tiles = map_coords.ORANGE_TILES
    tiles_to_avoid = [0,1,2,3,4,5,6,7,14,15,23,24,33,34,44,45,56,57,58,59,60,61,62,63,64,65,66,67,68,69] # blue tiles
    map_coordinates = map_coords.ORANGE_MAP_COORDS
else: 
    team_tiles = map_coords.BLUE_TILES
    tiles_to_avoid = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,24,25,35,36,45,46,54,55,62,63,64,65,66,67,68,69] # Orange tiles
    map_coordinates = map_coords.BLUE_MAP_COORDS

class Hexagon:
    def __init__(self, id: int, center: list=[int, int]) -> None:
        self.center = center
        self.id = id
        self.state: int = 1
        self.color = (100,100,100)
        # Drawing a hexagon
        self.points = np.array([
            (self.center[0], self.center[1]+443),
            (self.center[0]+384, self.center[1]+222),
            (self.center[0]+384, self.center[1]-222),
            (self.center[0], self.center[1]-443),
            (self.center[0]-384, self.center[1]-222),
            (self.center[0]-384, self.center[1]+222),
        ])
        
    def draw(self, img):
        if self.state == 2:
            self.color = (0, 110, 255) if TEAM == 'blue' else (255, 110, 0)
        elif self.state == 3:
            self.color = (0, 70, 255) if TEAM == 'blue' else (255, 70, 0)
        cv2.line(img, (self.points[0][0], self.points[0][1]), (self.points[1][0], self.points[1][1]), (0, 0, 0), thickness=10)
        cv2.line(img, (self.points[1][0], self.points[1][1]), (self.points[2][0], self.points[2][1]), (0, 0, 0), thickness=10)
        cv2.line(img, (self.points[2][0], self.points[2][1]), (self.points[3][0], self.points[3][1]), (0, 0, 0), thickness=10)
        cv2.line(img, (self.points[3][0], self.points[3][1]), (self.points[4][0], self.points[4][1]), (0, 0, 0), thickness=10)
        cv2.line(img, (self.points[4][0], self.points[4][1]), (self.points[5][0], self.points[5][1]), (0, 0, 0), thickness=10)
        cv2.line(img, (self.points[5][0], self.points[5][1]), (self.points[0][0], self.points[0][1]), (0, 0, 0), thickness=10)
        cv2.drawContours(img, [self.points], -1, self.color, -1)
        return img
    
    def fill(self, img, color: tuple, alpha: float):
        overlay = img.copy()
        cv2.drawContours(img, [self.points], -1, color, -1)
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
        return overlay
    
    def draw_id(self, img):
        return cv2.putText(img, str(self.id), (self.center[0]-80*len(str(self.id)), self.center[1]+90), cv2.FONT_HERSHEY_SIMPLEX, 10, (255, 255, 255), 10, cv2.LINE_AA)

    def get_origin(self):
        return self.center
    
    def get_id(self):
        return self.id
    
    def get_state(self):
        return self.state

def fix_tile_positions():
    '''
    Because Rocket League's map origin is at the center,
    we need to offset everything to map everything properly.
    
    cv2's origin is top left, so we need to account for that.
    '''
    MAX_MAP_SIZE_X: int = 10052
    MAX_MAP_SIZE_Y: int = 9110
    for index, boost_pad in enumerate(team_tiles):
        x: int = int(boost_pad[0])
        y: int = int(boost_pad[1])
        x = int((MAX_MAP_SIZE_X/2) + abs(x) if x >= 0 else (MAX_MAP_SIZE_X/2) - abs(x))
        y = int((MAX_MAP_SIZE_Y/2) + abs(y) if y >= 0 else (MAX_MAP_SIZE_Y/2) - abs(y))
        team_tiles[index][0] = x
        team_tiles[index][1] = y
    
fix_tile_positions()
all_tiles: list[Hexagon] = []
img = np.zeros((9110, 10052, 3), dtype = "uint8") # Crazy big but deal with it.

def draw_map():
    def is_odd(number):
        return number % 2 == 1
    for i, coord in enumerate(team_tiles):
        hexagon = Hexagon(id=i, center=[int(coord[0]), int(coord[1])])
        all_tiles.append(hexagon)
        hexagon.draw(img)
        
def find_neighbor_tile(id: int, charge: str = 'Normal'):
    radius: int = 0
    if charge == 'Normal':
        return [all_tiles[id]]
    elif charge == 'Charged':
        radius = 1000
    elif charge == 'Super Charged': 
        radius = 1650
    selected_tile = all_tiles[id]
    neighbors = []
    for hexagon in all_tiles:
        dist = math.hypot(hexagon.get_origin()[0] - selected_tile.get_origin()[0], hexagon.get_origin()[1] - selected_tile.get_origin()[1])
        if dist < radius:
            neighbors.append(hexagon)
    return neighbors

def get_ball_charge(rand_state: int) -> str:
    if rand_state == 1:
        return 'Normal'
    elif rand_state == 2:
        return 'Charged'
    else:
        return 'Super Charged'

draw_map()


# SIMULATING GAME EVENTS
neighbors = find_neighbor_tile(id=20, charge='Normal')
for n in neighbors:
    n.state += 1
    n.draw(img)
neighbors = find_neighbor_tile(id=29, charge='Normal')
for n in neighbors:
    n.state += 1
    n.draw(img)
neighbors = find_neighbor_tile(id=37, charge='Normal')
for n in neighbors:
    n.state += 1
    n.draw(img)
neighbors = find_neighbor_tile(id=18, charge='Charged')
for n in neighbors:
    n.state += 1
    n.draw(img)
neighbors = find_neighbor_tile(id=41, charge='Charged')
for n in neighbors:
    n.state += 1
    n.draw(img)
# for _ in range(random.randint(1, 5)):
#     rand_id = random.randint(0, 69)
#     rand_state: str = get_ball_charge(random.randint(1, 3))
#     print(f'SIMULATING SHOT - ID: {rand_id} STATE: {rand_state}')
#     neighbors = find_neighbor_tile(rand_id, charge=rand_state)
#     for n in neighbors:
#         n.state += 1
#         n.draw(img)

def find_best_shot(ball_state: str):
    tiles_with_most_damaged_neighbors: list[int] = []
    most_damaged_counter: float = -math.inf
    normal_counter: int = 0
    damaged_counter: int = 0
    opened_counter: int = 0
    ratio: float = 0
    best_ratio: list[int] = []
    for tile in all_tiles:
        if tile.get_id() in tiles_to_avoid: continue
        if ball_state != "Normal":
            n = find_neighbor_tile(tile.get_id(), ball_state)
            opened_counter = sum(t.get_state() == 3 for t in n)
            damaged_counter = sum(t.get_state() == 2 and tile.get_state() != 3 for t in n)
            normal_counter = sum(t.get_state() == 1 and t.get_state() != 2 and t.get_state() != 3 for t in n)
            try:
                ratio = damaged_counter/normal_counter
            except ZeroDivisionError: # There are no undamaged cell so its all damaged
                ratio = damaged_counter
            if (ratio >= 1.1 and ball_state == 'Super Charged' or ratio >= 4 and ball_state == 'Charged'):
                tiles_with_most_damaged_neighbors.append(tile.get_id())
        else:
            n = find_neighbor_tile(tile.get_id(), 'Charged')
            damaged_counter = sum(t.get_state() == 2 for t in n)
            normal_counter = sum(t.get_state() == 1 and t.get_state() != 2 and t.get_state() != 3 for t in n)
            try:
                ratio = damaged_counter/normal_counter
            except ZeroDivisionError: 
                continue
            if ratio >= 0.35 and ratio < 1.4 and tile.get_state() != 2 and tile.get_state() != 3 and tile.get_id() not in [55, 46]:
                tiles_with_most_damaged_neighbors.append(tile.get_id())
                most_damaged_counter = damaged_counter
        print(f'ID: {tile.get_id()} RATIO: {ratio}')
    if tiles_with_most_damaged_neighbors:
        for id in tiles_with_most_damaged_neighbors:
            all_tiles[id].fill(img=img, color=(0,255,0), alpha=0.6)
    else:
        print('No move could be found.')
    print(f'BEST SHOT - ID: {tiles_with_most_damaged_neighbors} DAMAGED NEIGHBORS: {most_damaged_counter} NORMAL NEIGHBORS: {normal_counter}')

# HOW TO GET THE BEST SHOT
# find_best_shot(get_ball_charge(random.randint(1, 3)))
find_best_shot('Normal')
# find_best_shot('Charged')
# find_best_shot('Super Charged')

# Making background pretty
np_map_coordinates = np.array(map_coordinates)
poly = np.zeros(img.shape[:-1]).astype(np.uint8)
cv2.fillPoly(poly, [np_map_coordinates], 255)
sel = poly != 255 # select everything that is not mask_value
img[sel] = [0,0,0]

cv2.line(img, (map_coordinates[0]), (map_coordinates[1]), (0, 50, 255) if TEAM == 'blue' else (255, 50, 0), 40)
cv2.line(img, (map_coordinates[1]), (map_coordinates[2]), (0, 50, 255) if TEAM == 'blue' else (255, 50, 0), 40)
cv2.line(img, (map_coordinates[2]), (map_coordinates[3]), (0, 50, 255) if TEAM == 'blue' else (255, 50, 0), 40)
cv2.line(img, (map_coordinates[3]), (map_coordinates[0]), (0, 50, 255) if TEAM == 'blue' else (255, 50, 0), 40)

for hexagon in all_tiles:
    hexagon.draw_id(img=img)

cv2.imwrite("out.png", img)