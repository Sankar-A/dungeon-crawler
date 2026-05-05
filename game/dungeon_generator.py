import random
from typing import List, Tuple, Dict

class Room:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.center = (x + width // 2, y + height // 2)
    
    def intersects(self, other):
        return (self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)

class DungeonGenerator:
    def __init__(self, width=50, height=50, seed=None):
        self.width = width
        self.height = height
        self.seed = seed or random.randint(0, 999999)
        random.seed(self.seed)
        self.grid = [[1 for _ in range(width)] for _ in range(height)]
        self.rooms = []
        
    def generate(self, num_rooms=15):
        """Generate a dungeon using BSP-inspired room placement"""
        attempts = 0
        max_attempts = 100
        
        while len(self.rooms) < num_rooms and attempts < max_attempts:
            room_width = random.randint(4, 10)
            room_height = random.randint(4, 10)
            x = random.randint(1, self.width - room_width - 1)
            y = random.randint(1, self.height - room_height - 1)
            
            new_room = Room(x, y, room_width, room_height)
            
            can_place = True
            for other_room in self.rooms:
                if new_room.intersects(other_room):
                    can_place = False
                    break
            
            if can_place:
                self._carve_room(new_room)
                if self.rooms:
                    self._create_corridor(self.rooms[-1].center, new_room.center)
                self.rooms.append(new_room)
            
            attempts += 1
        
        return self._place_entities()
    
    def _carve_room(self, room):
        """Carve out a room in the grid (0 = floor, 1 = wall)"""
        for y in range(room.y, room.y + room.height):
            for x in range(room.x, room.x + room.width):
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.grid[y][x] = 0
    
    def _create_corridor(self, start, end):
        """Create L-shaped corridor between two points"""
        x1, y1 = start
        x2, y2 = end
        
        if random.random() < 0.5:
            # Horizontal then vertical
            for x in range(min(x1, x2), max(x1, x2) + 1):
                if 0 <= x < self.width and 0 <= y1 < self.height:
                    self.grid[y1][x] = 0
            for y in range(min(y1, y2), max(y1, y2) + 1):
                if 0 <= x2 < self.width and 0 <= y < self.height:
                    self.grid[y][x2] = 0
        else:
            # Vertical then horizontal
            for y in range(min(y1, y2), max(y1, y2) + 1):
                if 0 <= x1 < self.width and 0 <= y < self.height:
                    self.grid[y][x1] = 0
            for x in range(min(x1, x2), max(x1, x2) + 1):
                if 0 <= x < self.width and 0 <= y2 < self.height:
                    self.grid[y2][x] = 0
    
    def _place_entities(self):
        """Place enemies, items, and stairs"""
        entities = {
            'spawn': self.rooms[0].center,
            'stairs': self.rooms[-1].center,
            'enemies': [],
            'items': []
        }
        
        # Place enemies in rooms (skip first and last)
        for room in self.rooms[1:-1]:
            num_enemies = random.randint(1, 3)
            for _ in range(num_enemies):
                x = random.randint(room.x + 1, room.x + room.width - 2)
                y = random.randint(room.y + 1, room.y + room.height - 2)
                entities['enemies'].append({'x': x, 'y': y, 'type': 'enemy'})
        
        # Place items randomly
        for room in self.rooms[1:]:
            if random.random() < 0.3:  # 30% chance per room
                x = random.randint(room.x + 1, room.x + room.width - 2)
                y = random.randint(room.y + 1, room.y + room.height - 2)
                entities['items'].append({'x': x, 'y': y, 'type': 'item'})
        
        return entities
