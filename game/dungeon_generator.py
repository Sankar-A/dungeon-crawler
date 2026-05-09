import random
from typing import List, Tuple, Dict

class Room:
    def __init__(self, x, y, width, height, is_bonus=False, has_special_boss=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.center = (x + width // 2, y + height // 2)
        self.is_bonus = is_bonus
        self.has_special_boss = has_special_boss
    
    def intersects(self, other):
        return (self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)

class DungeonGenerator:
    def __init__(self, width=80, height=80, seed=None):
        self.width = width
        self.height = height
        self.seed = seed or random.randint(0, 999999)
        random.seed(self.seed)
        self.grid = [[1 for _ in range(width)] for _ in range(height)]
        self.rooms = []
        
    def generate(self, num_rooms=25):
        """Generate a dungeon with main path and bonus branches"""
        # Calculate room distribution
        main_path_rooms = int(num_rooms * 0.65)  # 65% on main path
        bonus_rooms = num_rooms - main_path_rooms
        
        # Track room types
        main_path = []
        bonus_branches = []
        
        # Step 1: Generate main path (linear progression)
        
        # First room (spawn) - centered
        room_width = random.randint(6, 10)
        room_height = random.randint(6, 10)
        x = self.width // 2 - room_width // 2
        y = self.height // 2 - room_height // 2
        
        root_room = Room(x, y, room_width, room_height)
        self._carve_room(root_room)
        self.rooms.append(root_room)
        main_path.append(root_room)
        
        # Generate main path rooms
        current_room = root_room
        for i in range(main_path_rooms - 1):
            new_room = self._try_place_room_near(current_room, min_distance=4, max_distance=10, 
                                                   room_size_range=(5, 10), max_attempts=50)
            
            if new_room:
                self._carve_room(new_room)
                self._create_corridor(current_room.center, new_room.center)
                self.rooms.append(new_room)
                main_path.append(new_room)
                current_room = new_room
            else:
                # If we can't place near current room, try from any main path room
                for fallback_room in reversed(main_path[-5:]):  # Try last 5 rooms
                    new_room = self._try_place_room_near(fallback_room, min_distance=4, max_distance=10,
                                                          room_size_range=(5, 10), max_attempts=30)
                    if new_room:
                        self._carve_room(new_room)
                        self._create_corridor(fallback_room.center, new_room.center)
                        self.rooms.append(new_room)
                        main_path.append(new_room)
                        current_room = new_room
                        break
        
        # Step 2: Add bonus branches off main path rooms
        # Only branch from main path rooms (not from bonus rooms)
        for main_room in main_path[1:-1]:  # Skip first and last
            # 40% chance to have a bonus branch
            if random.random() < 0.4 and len(bonus_branches) < bonus_rooms:
                # Create 1-2 bonus rooms branching from this main room
                num_bonus = random.randint(1, min(2, bonus_rooms - len(bonus_branches)))
                
                for _ in range(num_bonus):
                    if len(bonus_branches) >= bonus_rooms:
                        break
                    
                    bonus_room = self._try_place_room_near(main_room, min_distance=3, max_distance=7,
                                                            room_size_range=(4, 8), max_attempts=30)
                    
                    if bonus_room:
                        bonus_room.is_bonus = True
                        
                        # 1% chance for bonus room to have special boss
                        if random.random() < 0.01:
                            bonus_room.has_special_boss = True
                        
                        self._carve_room(bonus_room)
                        self._create_corridor(main_room.center, bonus_room.center)
                        self.rooms.append(bonus_room)
                        bonus_branches.append(bonus_room)
        
        return self._place_entities()
    
    def _carve_room(self, room):
        """Carve out a room in the grid (0 = floor, 1 = wall)"""
        for y in range(room.y, room.y + room.height):
            for x in range(room.x, room.x + room.width):
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.grid[y][x] = 0
    
    def _try_place_room_near(self, base_room, min_distance=3, max_distance=10, 
                             room_size_range=(4, 8), max_attempts=50):
        """Try to place a room near the base room, trying multiple positions and directions"""
        directions = ['north', 'south', 'east', 'west']
        
        for attempt in range(max_attempts):
            # Shuffle directions each attempt for variety
            if attempt % 4 == 0:
                random.shuffle(directions)
            
            direction = directions[attempt % 4]
            
            # Random room size
            room_width = random.randint(room_size_range[0], room_size_range[1])
            room_height = random.randint(room_size_range[0], room_size_range[1])
            
            # Random distance within range
            distance = random.randint(min_distance, max_distance)
            
            # Calculate position based on direction with some randomness
            offset = random.randint(-3, 3)
            
            if direction == 'north':
                x = base_room.center[0] - room_width // 2 + offset
                y = base_room.y - room_height - distance
            elif direction == 'south':
                x = base_room.center[0] - room_width // 2 + offset
                y = base_room.y + base_room.height + distance
            elif direction == 'east':
                x = base_room.x + base_room.width + distance
                y = base_room.center[1] - room_height // 2 + offset
            else:  # west
                x = base_room.x - room_width - distance
                y = base_room.center[1] - room_height // 2 + offset
            
            # Ensure room is within bounds with margin
            if x < 1 or y < 1 or x + room_width >= self.width - 1 or y + room_height >= self.height - 1:
                continue
            
            new_room = Room(x, y, room_width, room_height)
            
            # Check if room intersects with existing rooms (with small buffer)
            can_place = True
            for other_room in self.rooms:
                if self._rooms_too_close(new_room, other_room, buffer=1):
                    can_place = False
                    break
            
            if can_place:
                return new_room
        
        return None
    
    def _rooms_too_close(self, room1, room2, buffer=1):
        """Check if two rooms are too close (intersect or within buffer distance)"""
        return (room1.x - buffer < room2.x + room2.width and
                room1.x + room1.width + buffer > room2.x and
                room1.y - buffer < room2.y + room2.height and
                room1.y + room1.height + buffer > room2.y)
    
    def _create_corridor(self, start, end):
        """Create L-shaped corridor between two points (2 tiles wide)"""
        x1, y1 = start
        x2, y2 = end
        
        if random.random() < 0.5:
            # Horizontal then vertical
            for x in range(min(x1, x2), max(x1, x2) + 1):
                if 0 <= x < self.width and 0 <= y1 < self.height:
                    self.grid[y1][x] = 0
                    # Make corridor 2 tiles wide
                    if 0 <= y1 + 1 < self.height:
                        self.grid[y1 + 1][x] = 0
            for y in range(min(y1, y2), max(y1, y2) + 1):
                if 0 <= x2 < self.width and 0 <= y < self.height:
                    self.grid[y][x2] = 0
                    # Make corridor 2 tiles wide
                    if 0 <= x2 + 1 < self.width:
                        self.grid[y][x2 + 1] = 0
        else:
            # Vertical then horizontal
            for y in range(min(y1, y2), max(y1, y2) + 1):
                if 0 <= x1 < self.width and 0 <= y < self.height:
                    self.grid[y][x1] = 0
                    # Make corridor 2 tiles wide
                    if 0 <= x1 + 1 < self.width:
                        self.grid[y][x1 + 1] = 0
            for x in range(min(x1, x2), max(x1, x2) + 1):
                if 0 <= x < self.width and 0 <= y2 < self.height:
                    self.grid[y2][x] = 0
                    # Make corridor 2 tiles wide
                    if 0 <= y2 + 1 < self.height:
                        self.grid[y2 + 1][x] = 0
    
    def _place_entities(self):
        """Place enemies, items, and stairs"""
        entities = {
            'spawn': self.rooms[0].center,
            'stairs': self.rooms[-1].center,
            'enemies': [],
            'items': [],
            'special_boss_rooms': []  # Track rooms with special bosses
        }
        
        # Place enemies in rooms (skip first and last)
        for room in self.rooms[1:-1]:
            # Check if this is a special boss room
            if hasattr(room, 'has_special_boss') and room.has_special_boss:
                # Mark this room for special boss spawn
                x = room.center[0]
                y = room.center[1]
                entities['special_boss_rooms'].append({
                    'x': x, 
                    'y': y, 
                    'type': 'special_boss',
                    'guaranteed_legendary': True
                })
            else:
                # Normal enemy spawns
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
