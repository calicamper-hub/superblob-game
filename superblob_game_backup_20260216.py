import pygame
import math
import random

pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Super Blob Slingshot")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)
tiny_font = pygame.font.Font(None, 24)

# Colors
WHITE = (255, 255, 255)
BLUE = (200, 200, 200)  # Light gray for Super Blob skin
RED = (180, 180, 181)  # Gray skin for Evil Mob (slightly different for code recognition)
GREEN = (180, 181, 180)  # Gray skin for Lucy (slightly different for code recognition)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (181, 180, 180)  # Gray skin for Alex (slightly different for code recognition)
DARK_RED = (180, 0, 0)
GOLD = (255, 215, 0)
BRIGHT_RED = (255, 0, 0)  # Actual red color for buttons
BRIGHT_BLUE = (0, 100, 255)  # Actual blue color for buttons

# Game state
game_state = "menu"  # "menu", "character_select", "world_select", "upgrades", "playing", "comic_panel", "level_failed"
show_instructions = False  # Toggle for instructions dropdown
show_upgrades = False  # Toggle for upgrades tab
level = 1
current_world = "city"  # "city" or "village"
city_max_level = 1  # Track highest level reached in city
village_unlocked = False  # Unlocked after beating city level 12
blobs_rescued = 0  # Total saved currency for unlocking characters
blobs_collected_run = 0  # Blobs collected in current game run (for power increase)
blobs_collected_level = 0  # Blobs collected in current level (for size increase)
power = 100  # Power bar (0-100)
max_power = 100
power_drain_rate = 0.5  # Power lost per frame (slow drain)

# Characters with unique properties (ordered by cost: least to greatest)
characters = [
    {
        "name": "SUPERBLOB",
        "color": BLUE,
        "description": "Balanced hero",
        "power_drain": 0.5,
        "bounce": 0.7,
        "can_pierce": False,
        "magnetic": False,
        "cost": 0,  # Free starter character
        "unlocked": True,
        "upgraded": False,
        "upgrade_cost": 0,  # No upgrade for free character
        "upgrade_desc": "No upgrade"
    },
    {
        "name": "ALEX",
        "color": PURPLE,
        "description": "Super bouncy!",
        "power_drain": 0.5,
        "bounce": 0.9,
        "can_pierce": False,
        "magnetic": False,
        "cost": 20,
        "unlocked": False,
        "upgraded": False,
        "upgrade_cost": 40,  # Double the cost
        "upgrade_desc": "Even bouncier! (0.95)"
    },
    {
        "name": "LUCY",
        "color": GREEN,
        "description": "Efficient",
        "power_drain": 0.3,
        "bounce": 0.8,
        "can_pierce": False,
        "magnetic": False,
        "cost": 25,
        "unlocked": False,
        "upgraded": False,
        "upgrade_cost": 50,  # Double the cost
        "upgrade_desc": "Super efficient! (0.15)"
    },
    {
        "name": "EVIL MOB",
        "color": RED,
        "description": "Smash through!",
        "power_drain": 0.8,
        "bounce": 0.6,
        "can_pierce": True,
        "magnetic": False,
        "cost": 35,
        "unlocked": False,
        "upgraded": False,
        "upgrade_cost": 70,  # Double the cost
        "upgrade_desc": "Smash bosses faster!"
    },
    {
        "name": "RICHARD",
        "color": (180, 180, 182),  # Gray skin (slightly different for code recognition)
        "description": "Magnetic pull!",
        "power_drain": 0.5,
        "bounce": 0.7,
        "can_pierce": False,
        "magnetic": True,
        "cost": 50,
        "unlocked": False,
        "upgraded": False,
        "upgrade_cost": 100,  # Double the cost
        "upgrade_desc": "Stronger magnet! (7.5)"
    }
]
selected_character = 0  # Index of selected character
player_color = characters[0]["color"]
can_pierce_buildings = characters[0]["can_pierce"]
has_magnetic_ability = characters[0]["magnetic"]

# Menu animation blobs
menu_blobs = []
for i in range(8):
    menu_blobs.append({
        "x": random.randint(100, WIDTH - 100),
        "y": random.randint(100, HEIGHT - 100),
        "vel_x": random.uniform(-2, 2),
        "vel_y": random.uniform(-2, 2),
        "radius": random.randint(15, 35),
        "color": random.choice([BLUE, RED, PURPLE, GREEN, (180, 180, 182)])  # Richard's gray instead of orange
    })

# Blob properties
blob_x, blob_y = 100, 450
blob_radius = 20
blob_vel_x, blob_vel_y = 0, 0
dragging = False
flying = False
can_catch = False
launch_x, launch_y = blob_x, blob_y
gravity = 0.5
bounce_damping = 0.7  # Energy loss on bounce

# Mini blobs to rescue (x, y, radius, alive)
mini_blobs = []

# Upgrade tracking
mini_blob_upgrade_level = 0  # 0-4, each adds 1 mini blob (6 base + upgrades = max 10)
mini_blob_upgrade_costs = [150, 300, 600, 1200]  # Costs for upgrades 1-4

# Village gas clouds (moving hazards)
gas_clouds = []

def spawn_mini_blobs():
    """Create mini blobs scattered across the level (6 base + upgrades)"""
    blobs = []
    num_blobs = 6 + mini_blob_upgrade_level  # Base 6, can go up to 10
    for i in range(num_blobs):
        blobs.append({
            "x": random.randint(250, 750),
            "y": random.randint(150, 400),
            "r": 8,
            "alive": True
        })
    return blobs

def spawn_gas_clouds(level_num):
    """Create moving gas clouds for village levels - increases with level"""
    clouds = []
    # Start with 2 clouds, add 1 at level 5, add another at level 8
    num_clouds = 2
    if level_num >= 8:
        num_clouds = 4
    elif level_num >= 5:
        num_clouds = 3

    for i in range(num_clouds):
        clouds.append({
            "x": random.randint(200 + i * 150, 350 + i * 100),
            "y": random.randint(150, 400),
            "r": 25,
            "vel_x": random.choice([-1, 1]) * random.uniform(0.8, 1.2),
            "vel_y": random.choice([-1, 1]) * random.uniform(0.8, 1.2)
        })
    return clouds

mini_blobs = spawn_mini_blobs()

# Buildings (x, y, width, height, is_boss)
buildings = []

# Gate obstacle (for level 10+)
gate = {
    "x": 250,
    "y": 0,  # Start from top of screen
    "width": 30,
    "height": 600,  # Full screen height
    "open": False,
    "timer": 0,
    "open_duration": 120,  # Frames gate stays open
    "close_duration": 90   # Frames gate stays closed
}

def create_level_buildings(level_num, world="city"):
    """Create buildings for the level - last one is the boss"""
    bldgs = []

    if world == "village":
        # Village has houses instead of skyscrapers (taller houses!)
        if level_num <= 4:
            # 2 taller houses
            for i in range(2):
                bldgs.append({
                    "x": 350 + i * 150,
                    "y": 380,  # Higher up (taller)
                    "w": 80,
                    "h": 220,  # Taller (was 180)
                    "alive": True,
                    "is_boss": False,
                    "pieces": [],
                    "hit_count": 0
                })
        elif level_num <= 9:
            # 4 taller houses (was 3)
            for i in range(4):
                bldgs.append({
                    "x": 280 + i * 100,
                    "y": 380,  # Higher up (taller)
                    "w": 80,
                    "h": 220,  # Taller (was 180)
                    "alive": True,
                    "is_boss": False,
                    "pieces": [],
                    "hit_count": 0
                })
        else:
            # Level 10+: 4 houses with varied heights
            for i in range(4):
                height = random.randint(220, 270)
                y_pos = 600 - height
                bldgs.append({
                    "x": 280 + i * 100,
                    "y": y_pos,
                    "w": 80,
                    "h": height,
                    "alive": True,
                    "is_boss": False,
                    "pieces": [],
                    "hit_count": 0
                })

        # Boss house (larger, taller)
        bldgs.append({
            "x": 650,
            "y": 320,  # Higher up (taller)
            "w": 120,
            "h": 280,  # Taller (was 250)
            "alive": True,
            "is_boss": True,
            "pieces": [],
            "required_power": level_num * 15  # 15, 30, 45, 60, etc. (harder than city)
        })
        return bldgs

    # City buildings (original code)
    # Regular buildings (can be destroyed by any hit)

    if level_num <= 4:
        # Levels 1-4: 2 buildings in a line
        for i in range(2):
            bldgs.append({
                "x": 350 + i * 150,
                "y": 350,
                "w": 70,
                "h": 250,
                "alive": True,
                "is_boss": False,
                "pieces": [],
                "hit_count": 0  # Track hits
            })
    elif level_num <= 9:
        # Levels 5-9: 3 buildings in a line
        for i in range(3):
            bldgs.append({
                "x": 300 + i * 120,
                "y": 350,
                "w": 70,
                "h": 250,
                "alive": True,
                "is_boss": False,
                "pieces": [],
                "hit_count": 0
            })
    else:
        # Level 10+: 3 buildings with varied heights and positions
        num_obstacles = 3
        for i in range(num_obstacles):
            height = random.randint(200, 300)
            y_pos = 600 - height
            x_spacing = (600 - 350) // (num_obstacles + 1)
            bldgs.append({
                "x": 350 + (i + 1) * x_spacing - 35,
                "y": y_pos,
                "w": 70,
                "h": height,
                "alive": True,
                "is_boss": False,
                "pieces": [],
                "hit_count": 0
            })

    # Boss building (taller, wider, different color)
    bldgs.append({
        "x": 650,
        "y": 250,
        "w": 100,
        "h": 350,
        "alive": True,
        "is_boss": True,
        "pieces": [],
        "required_power": level_num * 10  # 10, 20, 30, 40, etc.
    })
    return bldgs

buildings = create_level_buildings(level, current_world)

def draw_building(building, world="city"):
    """Draw a building with windows and details"""
    if not building["alive"]:
        return

    x, y, w, h = building["x"], building["y"], building["w"], building["h"]

    if world == "village":
        # Draw village houses
        if building.get("is_boss"):
            # Boss house - large brown house with red roof and details
            house_body_y = y + h // 3
            house_body_h = h * 2 // 3

            # Main house body with shading
            pygame.draw.rect(screen, (139, 69, 19), (x, house_body_y, w, house_body_h))
            # Add darker left side for depth
            pygame.draw.rect(screen, (100, 50, 10), (x, house_body_y, 8, house_body_h))
            # Add lighter right side for depth
            pygame.draw.rect(screen, (160, 85, 30), (x + w - 8, house_body_y, 8, house_body_h))

            # Red triangular roof with shading
            roof_points = [(x - 10, house_body_y), (x + w // 2, y), (x + w + 10, house_body_y)]
            pygame.draw.polygon(screen, (180, 0, 0), roof_points)
            # Roof ridge detail
            pygame.draw.line(screen, (120, 0, 0), (x + w // 2, y), (x + w // 2, house_body_y), 3)
            pygame.draw.polygon(screen, BLACK, roof_points, 3)

            # Chimney
            pygame.draw.rect(screen, (139, 69, 19), (x + w - 20, y + 20, 15, 30))
            pygame.draw.rect(screen, BLACK, (x + w - 20, y + 20, 15, 30), 2)
            pygame.draw.rect(screen, (80, 40, 10), (x + w - 18, y + 18, 11, 8))  # Chimney cap

            # Door with details
            door_x = x + w // 2 - 15
            door_y = y + h - 50
            pygame.draw.rect(screen, (101, 67, 33), (door_x, door_y, 30, 50))
            pygame.draw.rect(screen, BLACK, (door_x, door_y, 30, 50), 2)
            # Door panels
            pygame.draw.rect(screen, (80, 50, 20), (door_x + 3, door_y + 3, 11, 20))
            pygame.draw.rect(screen, (80, 50, 20), (door_x + 16, door_y + 3, 11, 20))
            pygame.draw.rect(screen, (80, 50, 20), (door_x + 3, door_y + 27, 11, 20))
            pygame.draw.rect(screen, (80, 50, 20), (door_x + 16, door_y + 27, 11, 20))
            # Doorknob
            pygame.draw.circle(screen, (212, 175, 55), (door_x + 24, door_y + 30), 3)

            # Windows with frames
            for row in range(2):
                for col in range(2):
                    wx = x + 15 + col * 50
                    wy = house_body_y + 30 + row * 40
                    # Window with yellow glow
                    pygame.draw.rect(screen, (255, 255, 200), (wx, wy, 25, 25))
                    pygame.draw.rect(screen, (139, 69, 19), (wx - 2, wy - 2, 29, 29), 2)  # Frame
                    pygame.draw.rect(screen, BLACK, (wx, wy, 25, 25), 2)
                    # Window panes
                    pygame.draw.line(screen, (139, 69, 19), (wx + 12, wy), (wx + 12, wy + 25), 2)
                    pygame.draw.line(screen, (139, 69, 19), (wx, wy + 12), (wx + 25, wy + 12), 2)
            # Outline
            pygame.draw.rect(screen, BLACK, (x, house_body_y, w, house_body_h), 3)
        else:
            # Regular house - smaller brown house with red roof and details
            house_body_y = y + h // 3
            house_body_h = h * 2 // 3

            # Main house body with shading
            pygame.draw.rect(screen, (160, 82, 45), (x, house_body_y, w, house_body_h))
            # Darker left side
            pygame.draw.rect(screen, (120, 60, 30), (x, house_body_y, 6, house_body_h))
            # Lighter right side
            pygame.draw.rect(screen, (180, 100, 55), (x + w - 6, house_body_y, 6, house_body_h))

            # Red triangular roof with ridge
            roof_points = [(x - 8, house_body_y), (x + w // 2, y), (x + w + 8, house_body_y)]
            pygame.draw.polygon(screen, (200, 50, 50), roof_points)
            pygame.draw.line(screen, (150, 30, 30), (x + w // 2, y), (x + w // 2, house_body_y), 2)
            pygame.draw.polygon(screen, BLACK, roof_points, 2)

            # Door with panels
            door_x = x + w // 2 - 12
            door_y = y + h - 40
            pygame.draw.rect(screen, (101, 67, 33), (door_x, door_y, 24, 40))
            pygame.draw.rect(screen, BLACK, (door_x, door_y, 24, 40), 2)
            # Door panels
            pygame.draw.rect(screen, (80, 50, 20), (door_x + 2, door_y + 2, 9, 16))
            pygame.draw.rect(screen, (80, 50, 20), (door_x + 13, door_y + 2, 9, 16))
            pygame.draw.rect(screen, (80, 50, 20), (door_x + 2, door_y + 21, 9, 16))
            pygame.draw.rect(screen, (80, 50, 20), (door_x + 13, door_y + 21, 9, 16))
            # Doorknob
            pygame.draw.circle(screen, (212, 175, 55), (door_x + 19, door_y + 24), 2)

            # Windows with frames and panes
            for col in range(2):
                wx = x + 12 + col * 35
                wy = house_body_y + 30
                pygame.draw.rect(screen, (255, 255, 200), (wx, wy, 20, 20))
                pygame.draw.rect(screen, (160, 82, 45), (wx - 2, wy - 2, 24, 24), 2)  # Frame
                pygame.draw.rect(screen, BLACK, (wx, wy, 20, 20), 2)
                # Window panes
                pygame.draw.line(screen, (160, 82, 45), (wx + 10, wy), (wx + 10, wy + 20), 2)
                pygame.draw.line(screen, (160, 82, 45), (wx, wy + 10), (wx + 20, wy + 10), 2)

            # Outline
            pygame.draw.rect(screen, BLACK, (x, house_body_y, w, house_body_h), 2)
        return

    # City buildings
    if building.get("is_boss"):
        # Boss building - golden skyscraper with extra details
        # Main building body
        pygame.draw.rect(screen, GOLD, (x, y, w, h))
        # Darker gold accent on sides
        pygame.draw.rect(screen, (200, 170, 0), (x, y, 8, h))
        pygame.draw.rect(screen, (200, 170, 0), (x + w - 8, y, 8, h))

        # Add decorative horizontal bands every few floors
        for band in range(int(h / 80)):
            band_y = y + 40 + band * 80
            pygame.draw.rect(screen, (180, 150, 0), (x, band_y, w, 4))

        # Windows pattern for boss
        for row in range(int(h / 25)):
            for col in range(2):
                win_x = x + 15 + col * 35
                win_y = y + 15 + row * 25
                if win_y + 15 < y + h:
                    pygame.draw.rect(screen, (255, 255, 200), (win_x, win_y, 20, 15))
                    pygame.draw.rect(screen, BLACK, (win_x, win_y, 20, 15), 1)
                    # Window cross-bars for detail
                    pygame.draw.line(screen, BLACK, (win_x + 10, win_y), (win_x + 10, win_y + 15), 1)

        # Rooftop details - antenna and helipad
        # Antenna
        pygame.draw.rect(screen, (150, 150, 150), (x + w // 2 - 2, y - 20, 4, 20))
        pygame.draw.circle(screen, BRIGHT_RED, (int(x + w // 2), int(y - 20)), 4)
        # Helipad marking
        pygame.draw.circle(screen, (200, 180, 0), (int(x + w // 2), int(y + 15)), 12, 2)

        # Building outline
        pygame.draw.rect(screen, BLACK, (x, y, w, h), 3)
    else:
        # Regular building with more details
        # Main body - gray with slight variation
        base_gray = (120, 120, 120)
        pygame.draw.rect(screen, base_gray, (x, y, w, h))
        # Darker side for depth
        pygame.draw.rect(screen, (80, 80, 80), (x, y, 6, h))
        # Lighter highlight on other side
        pygame.draw.rect(screen, (140, 140, 140), (x + w - 6, y, 6, h))

        # Windows pattern with more detail
        for row in range(int(h / 20)):
            for col in range(2):
                win_x = x + 10 + col * 30
                win_y = y + 10 + row * 20
                if win_y + 12 < y + h:
                    # Lit window with gradient
                    pygame.draw.rect(screen, (255, 255, 150), (win_x, win_y, 18, 12))
                    pygame.draw.rect(screen, (60, 60, 60), (win_x, win_y, 18, 12), 1)
                    # Window frame cross
                    pygame.draw.line(screen, (60, 60, 60), (win_x + 9, win_y), (win_x + 9, win_y + 12), 1)
                    pygame.draw.line(screen, (60, 60, 60), (win_x, win_y + 6), (win_x + 18, win_y + 6), 1)

        # Rooftop AC unit
        if h > 100:
            pygame.draw.rect(screen, (100, 100, 100), (x + w // 2 - 8, y + 5, 16, 12))
            pygame.draw.rect(screen, BLACK, (x + w // 2 - 8, y + 5, 16, 12), 1)
            # AC vent lines
            for vent_line in range(3):
                vent_y = y + 7 + vent_line * 3
                pygame.draw.line(screen, (70, 70, 70), (x + w // 2 - 6, vent_y), (x + w // 2 + 6, vent_y), 1)

        # Building outline
        pygame.draw.rect(screen, BLACK, (x, y, w, h), 2)

def draw_village_background():
    """Draw a village countryside background"""
    # Sky gradient - warmer colors
    sky_top = (135, 180, 235)  # Slightly darker blue
    sky_bottom = (200, 220, 255)  # Lighter blue
    for i in range(HEIGHT // 2):
        ratio = i / (HEIGHT // 2)
        r = int(sky_top[0] + (sky_bottom[0] - sky_top[0]) * ratio)
        g = int(sky_top[1] + (sky_bottom[1] - sky_top[1]) * ratio)
        b = int(sky_top[2] + (sky_bottom[2] - sky_top[2]) * ratio)
        pygame.draw.line(screen, (r, g, b), (0, i), (WIDTH, i))

    # Green grass ground
    pygame.draw.rect(screen, (34, 139, 34), (0, HEIGHT // 2, WIDTH, HEIGHT // 2))

    # Draw simple background trees/bushes
    tree_positions = [(100, 300), (200, 320), (600, 310), (700, 295)]
    for tx, ty in tree_positions:
        # Tree trunk
        pygame.draw.rect(screen, (101, 67, 33), (tx - 5, ty, 10, 40))
        # Tree top (circle)
        pygame.draw.circle(screen, (34, 100, 34), (tx, ty - 10), 25)
        pygame.draw.circle(screen, BLACK, (tx, ty - 10), 25, 1)

def draw_city_background():
    """Draw a city skyline background"""
    # Sky gradient (simplified)
    sky_top = (135, 206, 235)  # Light blue
    sky_bottom = (200, 230, 255)  # Lighter blue
    for i in range(HEIGHT // 2):
        ratio = i / (HEIGHT // 2)
        r = int(sky_top[0] + (sky_bottom[0] - sky_top[0]) * ratio)
        g = int(sky_top[1] + (sky_bottom[1] - sky_top[1]) * ratio)
        b = int(sky_top[2] + (sky_bottom[2] - sky_top[2]) * ratio)
        pygame.draw.line(screen, (r, g, b), (0, i), (WIDTH, i))

    # Ground
    pygame.draw.rect(screen, (100, 100, 100), (0, HEIGHT // 2, WIDTH, HEIGHT // 2))

    # Background buildings (distant)
    bg_buildings = [
        (50, 250, 60, 150),
        (130, 200, 70, 200),
        (220, 230, 55, 170),
        (600, 220, 65, 180),
        (680, 260, 50, 140),
    ]

    for bx, by, bw, bh in bg_buildings:
        # Building body
        pygame.draw.rect(screen, (90, 90, 110), (bx, by, bw, bh))
        # Simple windows
        for row in range(int(bh / 25)):
            for col in range(2):
                win_x = bx + 8 + col * 25
                win_y = by + 10 + row * 25
                if win_y + 8 < by + bh:
                    pygame.draw.rect(screen, (180, 180, 100), (win_x, win_y, 15, 8))

def draw_blob_with_cape(x, y, radius, color):
    """Draw the Super Blob with a flowing cape"""

    # Long blonde hair for Green Blob (drawn behind the body)
    if color == GREEN:
        hair_color = (255, 215, 0)  # Brighter gold/blonde color
        # Left side long hair - made wider and longer
        left_hair = [
            (x - radius * 0.9, y - radius * 0.8),
            (x - radius * 1.0, y - radius * 0.2),
            (x - radius * 1.3, y + radius * 0.5),
            (x - radius * 1.2, y + radius * 1.1),
            (x - radius * 0.7, y + radius * 0.6),
        ]
        pygame.draw.polygon(screen, hair_color, left_hair)
        pygame.draw.polygon(screen, BLACK, left_hair, 3)

        # Right side long hair - made wider and longer
        right_hair = [
            (x + radius * 0.9, y - radius * 0.8),
            (x + radius * 1.0, y - radius * 0.2),
            (x + radius * 1.3, y + radius * 0.5),
            (x + radius * 1.2, y + radius * 1.1),
            (x + radius * 0.7, y + radius * 0.6),
        ]
        pygame.draw.polygon(screen, hair_color, right_hair)
        pygame.draw.polygon(screen, BLACK, right_hair, 3)

        # Top hair - made taller and wider
        top_hair = [
            (x - radius * 0.8, y - radius * 0.9),
            (x, y - radius * 1.3),
            (x + radius * 0.8, y - radius * 0.9),
            (x + radius * 0.6, y - radius * 0.7),
            (x - radius * 0.6, y - radius * 0.7),
        ]
        pygame.draw.polygon(screen, hair_color, top_hair)
        pygame.draw.polygon(screen, BLACK, top_hair, 3)

    # Short messy black hair for Purple Blob (drawn behind the body, but bangs drawn after body)
    elif color == PURPLE:
        hair_color = (30, 30, 30)  # Black hair
        # Draw multiple spiky tufts for messy hair (back layer)
        # Left tuft
        pygame.draw.polygon(screen, hair_color, [
            (x - radius * 0.6, y - radius * 0.7),
            (x - radius * 0.8, y - radius * 1.0),
            (x - radius * 0.4, y - radius * 0.8)
        ])
        # Center-left tuft
        pygame.draw.polygon(screen, hair_color, [
            (x - radius * 0.3, y - radius * 0.8),
            (x - radius * 0.3, y - radius * 1.1),
            (x - radius * 0.1, y - radius * 0.8)
        ])
        # Center tuft
        pygame.draw.polygon(screen, hair_color, [
            (x - radius * 0.1, y - radius * 0.8),
            (x, y - radius * 1.2),
            (x + radius * 0.1, y - radius * 0.8)
        ])
        # Center-right tuft
        pygame.draw.polygon(screen, hair_color, [
            (x + radius * 0.1, y - radius * 0.8),
            (x + radius * 0.3, y - radius * 1.1),
            (x + radius * 0.3, y - radius * 0.8)
        ])
        # Right tuft
        pygame.draw.polygon(screen, hair_color, [
            (x + radius * 0.4, y - radius * 0.8),
            (x + radius * 0.8, y - radius * 1.0),
            (x + radius * 0.6, y - radius * 0.7)
        ])
        # Draw outlines for back hair
        for tuft in [
            [(x - radius * 0.6, y - radius * 0.7), (x - radius * 0.8, y - radius * 1.0), (x - radius * 0.4, y - radius * 0.8)],
            [(x - radius * 0.3, y - radius * 0.8), (x - radius * 0.3, y - radius * 1.1), (x - radius * 0.1, y - radius * 0.8)],
            [(x - radius * 0.1, y - radius * 0.8), (x, y - radius * 1.2), (x + radius * 0.1, y - radius * 0.8)],
            [(x + radius * 0.1, y - radius * 0.8), (x + radius * 0.3, y - radius * 1.1), (x + radius * 0.3, y - radius * 0.8)],
            [(x + radius * 0.4, y - radius * 0.8), (x + radius * 0.8, y - radius * 1.0), (x + radius * 0.6, y - radius * 0.7)]
        ]:
            pygame.draw.polygon(screen, BLACK, tuft, 2)

    # Orange curly hair for Richard (gray blob with orange hair)
    elif color == (180, 180, 182):  # Richard's gray color
        hair_color = (255, 140, 0)  # Orange hair (same as Super Blob's cape)
        # Draw curly hair using circles to create curl effect
        # Top curls
        curl_positions = [
            (x - radius * 0.7, y - radius * 0.9, radius * 0.3),
            (x - radius * 0.4, y - radius * 1.0, radius * 0.35),
            (x - radius * 0.1, y - radius * 1.1, radius * 0.4),
            (x + radius * 0.2, y - radius * 1.0, radius * 0.35),
            (x + radius * 0.5, y - radius * 0.9, radius * 0.35),
            (x + radius * 0.7, y - radius * 0.8, radius * 0.3),
        ]
        for curl_x, curl_y, curl_r in curl_positions:
            pygame.draw.circle(screen, hair_color, (int(curl_x), int(curl_y)), int(curl_r))
            pygame.draw.circle(screen, BLACK, (int(curl_x), int(curl_y)), int(curl_r), 2)

        # Side curls
        left_curls = [
            (x - radius * 0.9, y - radius * 0.6, radius * 0.25),
            (x - radius * 1.0, y - radius * 0.3, radius * 0.25),
            (x - radius * 0.95, y, radius * 0.25),
        ]
        right_curls = [
            (x + radius * 0.9, y - radius * 0.6, radius * 0.25),
            (x + radius * 1.0, y - radius * 0.3, radius * 0.25),
            (x + radius * 0.95, y, radius * 0.25),
        ]
        for curl_x, curl_y, curl_r in left_curls + right_curls:
            pygame.draw.circle(screen, hair_color, (int(curl_x), int(curl_y)), int(curl_r))
            pygame.draw.circle(screen, BLACK, (int(curl_x), int(curl_y)), int(curl_r), 2)

    # Cape for non-Green, non-Purple, non-Orange blobs (drawn behind the blob)
    elif color != GREEN and color != PURPLE and color != (180, 180, 182):
        cape_points = [
            (x - radius * 0.7, y - radius * 0.5),  # Left shoulder
            (x + radius * 0.7, y - radius * 0.5),  # Right shoulder
            (x + radius * 1.2, y + radius * 1.8),  # Right bottom
            (x - radius * 1.2, y + radius * 1.8),  # Left bottom
        ]

        # Cape color - Orange cape for Blue Blob (Super Blob), navy blue for Red Blob, regular colors for others
        if color == BLUE:
            cape_color = (255, 140, 0)  # Orange cape for Super Blob
        elif color == RED:
            cape_color = (0, 0, 128)  # Navy blue cape for Red Blob
        elif color == ORANGE:
            cape_color = (200, 100, 0)
        else:
            cape_color = (100, 100, 100)

        pygame.draw.polygon(screen, cape_color, cape_points)
        pygame.draw.polygon(screen, BLACK, cape_points, 2)

        # Draw "SB" letters on cape for Blue Blob (Super Blob)
        if color == BLUE and radius >= 20:
            # Position SB letters in center of cape
            letter_y = int(y + radius * 0.8)
            letter_font = pygame.font.Font(None, max(int(radius * 0.8), 20))
            sb_text = letter_font.render("SB", True, RED)
            screen.blit(sb_text, (int(x - sb_text.get_width() // 2), letter_y - sb_text.get_height() // 2))

    # Main blob body
    pygame.draw.circle(screen, color, (int(x), int(y)), radius)
    pygame.draw.circle(screen, BLACK, (int(x), int(y)), radius, 2)

    # Face mask for Blue Blob (Super Blob)
    if color == BLUE:
        # Draw orange face mask across eyes
        mask_y = int(y - radius * 0.2)
        mask_height = int(radius * 0.4)
        mask_rect = pygame.Rect(int(x - radius * 0.6), mask_y - mask_height // 2,
                                int(radius * 1.2), mask_height)
        pygame.draw.ellipse(screen, (255, 140, 0), mask_rect)
        pygame.draw.ellipse(screen, BLACK, mask_rect, 2)

        # Eyes with white circles and black pupils (like mini blobs in comic)
        eye_y = mask_y
        eye_size = max(3, int(radius * 0.18))
        pupil_size = max(2, int(radius * 0.12))
        # Left eye
        pygame.draw.circle(screen, WHITE, (int(x - radius * 0.3), eye_y), eye_size)
        pygame.draw.circle(screen, BLACK, (int(x - radius * 0.3), eye_y), pupil_size)
        # Right eye
        pygame.draw.circle(screen, WHITE, (int(x + radius * 0.3), eye_y), eye_size)
        pygame.draw.circle(screen, BLACK, (int(x + radius * 0.3), eye_y), pupil_size)
    elif color == RED:
        # Draw dark green rectangular mask across eyes (like Super Blob but square and green)
        mask_y = int(y - radius * 0.2)
        mask_height = int(radius * 0.4)
        mask_rect = pygame.Rect(int(x - radius * 0.6), mask_y - mask_height // 2,
                                int(radius * 1.2), mask_height)
        pygame.draw.rect(screen, (0, 100, 0), mask_rect)  # Dark green
        pygame.draw.rect(screen, BLACK, mask_rect, 2)

        # Eyes with white circles and black pupils (like mini blobs in comic)
        eye_y = mask_y
        eye_size = max(3, int(radius * 0.18))
        pupil_size = max(2, int(radius * 0.12))
        # Left eye
        pygame.draw.circle(screen, WHITE, (int(x - radius * 0.3), eye_y), eye_size)
        pygame.draw.circle(screen, BLACK, (int(x - radius * 0.3), eye_y), pupil_size)
        # Right eye
        pygame.draw.circle(screen, WHITE, (int(x + radius * 0.3), eye_y), eye_size)
        pygame.draw.circle(screen, BLACK, (int(x + radius * 0.3), eye_y), pupil_size)
    else:
        # Eyes with white circles and black pupils (like mini blobs in comic)
        eye_y = int(y - radius * 0.2)
        eye_size = max(3, int(radius * 0.18))
        pupil_size = max(2, int(radius * 0.12))
        # Left eye
        pygame.draw.circle(screen, WHITE, (int(x - radius * 0.3), eye_y), eye_size)
        pygame.draw.circle(screen, BLACK, (int(x - radius * 0.3), eye_y), pupil_size)
        # Right eye
        pygame.draw.circle(screen, WHITE, (int(x + radius * 0.3), eye_y), eye_size)
        pygame.draw.circle(screen, BLACK, (int(x + radius * 0.3), eye_y), pupil_size)

        # Glasses for Orange Blob (Richard)
        if color == (180, 180, 182):  # Orange Blob's gray color
            glasses_color = (50, 50, 50)  # Dark gray/black frames
            # Left lens (circle)
            pygame.draw.circle(screen, glasses_color, (int(x - radius * 0.3), eye_y), int(eye_size * 1.4), 2)
            # Right lens (circle)
            pygame.draw.circle(screen, glasses_color, (int(x + radius * 0.3), eye_y), int(eye_size * 1.4), 2)
            # Bridge connecting the lenses
            pygame.draw.line(screen, glasses_color,
                           (int(x - radius * 0.3 + eye_size * 1.4), eye_y),
                           (int(x + radius * 0.3 - eye_size * 1.4), eye_y), 2)
            # Left temple arm
            pygame.draw.line(screen, glasses_color,
                           (int(x - radius * 0.3 - eye_size * 1.4), eye_y),
                           (int(x - radius * 0.7), eye_y), 2)
            # Right temple arm
            pygame.draw.line(screen, glasses_color,
                           (int(x + radius * 0.3 + eye_size * 1.4), eye_y),
                           (int(x + radius * 0.7), eye_y), 2)

    # No additional hair drawn over eyes for Alex - just the spiky back hair

def retry_level():
    """Retry current level without losing progress"""
    global power, buildings, mini_blobs, gate, gas_clouds, max_power
    global blob_x, blob_y, blob_vel_x, blob_vel_y, flying, dragging, can_catch, collision_cooldown
    global level, blobs_rescued, blobs_collected_run, blobs_collected_level, blob_radius

    # Keep level, blobs_rescued, blobs_collected_run, and blobs_collected_level (for size)
    # Start at full health (based on blobs collected in this run)
    max_power = 100 + (blobs_collected_run // 10) * 10
    power = max_power

    buildings = create_level_buildings(level, current_world)
    mini_blobs = spawn_mini_blobs()

    # Spawn gas clouds for village
    if current_world == "village":
        gas_clouds = spawn_gas_clouds(level)
    else:
        gas_clouds = []

    # Reset gate
    gate["open"] = False
    gate["timer"] = 0

    blob_x, blob_y = 100, 450
    blob_vel_x, blob_vel_y = 0, 0
    flying = False
    dragging = False
    can_catch = False
    collision_cooldown = 0

def reset_game():
    """Reset game to initial state (start from level 1)"""
    global level, blobs_rescued, blobs_collected_run, blobs_collected_level, power, buildings, mini_blobs, gate, gas_clouds
    global blob_x, blob_y, blob_vel_x, blob_vel_y, flying, dragging, can_catch, collision_cooldown
    global power_drain_rate, bounce_damping, player_color, can_pierce_buildings, has_magnetic_ability

    level = 1
    blobs_collected_run = 0  # Reset run counter (currency stays)
    blobs_collected_level = 0  # Reset level counter for size
    power = 100
    buildings = create_level_buildings(level, current_world)
    mini_blobs = spawn_mini_blobs()

    # Spawn gas clouds for village
    if current_world == "village":
        gas_clouds = spawn_gas_clouds(level)
    else:
        gas_clouds = []

    # Reset gate
    gate["open"] = False
    gate["timer"] = 0

    blob_x, blob_y = 100, 450
    blob_vel_x, blob_vel_y = 0, 0
    flying = False
    dragging = False
    can_catch = False
    collision_cooldown = 0

    # Apply selected character stats (with upgrades)
    char = characters[selected_character]

    # Apply base stats
    power_drain_rate = char["power_drain"]
    bounce_damping = char["bounce"]
    player_color = char["color"]
    can_pierce_buildings = char["can_pierce"]
    has_magnetic_ability = char["magnetic"]

    # Apply upgrades if purchased
    if char["upgraded"]:
        if char["name"] == "ALEX":
            bounce_damping = 0.95  # Even bouncier
        elif char["name"] == "LUCY":
            power_drain_rate = 0.15  # Super efficient
        # EVIL MOB and RICHARD upgrades applied in gameplay code

def create_debris(building):
    """Create falling pieces when building is destroyed"""
    pieces = []
    piece_count = 12 if building.get("is_boss") else 8
    for i in range(piece_count):
        piece = {
            "x": building["x"] + random.randint(0, building["w"]),
            "y": building["y"] + random.randint(0, building["h"]),
            "w": random.randint(15, 35),
            "h": random.randint(15, 35),
            "vel_x": random.uniform(-4, 4),
            "vel_y": random.uniform(-8, -2),
            "rotation": random.uniform(0, 360),
            "rot_speed": random.uniform(-10, 10)
        }
        pieces.append(piece)
    return pieces

collision_cooldown = 0  # Prevent multiple collisions in same frame

# Button dimensions
button_width = 200
button_height = 60
play_button_rect = pygame.Rect(WIDTH//2 - button_width//2, HEIGHT//2, button_width, button_height)
quit_button_rect = pygame.Rect(WIDTH//2 - button_width//2, HEIGHT//2 + 90, button_width, button_height)
instructions_button_rect = pygame.Rect(WIDTH//2 - button_width//2, HEIGHT//2 + 180, button_width, button_height)

# Character selection buttons
char_button_width = 150
char_button_height = 180
char_button_spacing = 20
total_char_width = len(characters) * char_button_width + (len(characters) - 1) * char_button_spacing
char_start_x = WIDTH//2 - total_char_width//2
char_buttons = []
for i in range(len(characters)):
    x = char_start_x + i * (char_button_width + char_button_spacing)
    char_buttons.append(pygame.Rect(x, HEIGHT//2 - 50, char_button_width, char_button_height))

# Back button for character select
back_button_rect = pygame.Rect(50, HEIGHT - 100, 120, 50)

# Worlds button for character select (to show world selection)
worlds_button_rect = pygame.Rect(WIDTH - 180, HEIGHT - 100, 140, 50)

# Upgrades button for character select
upgrades_button_rect = pygame.Rect(WIDTH//2 - 70, HEIGHT - 100, 140, 50)

# World selection buttons
world_button_width = 200
world_button_height = 150
city_world_button = pygame.Rect(WIDTH//2 - 250, HEIGHT//2 - 75, world_button_width, world_button_height)
village_world_button = pygame.Rect(WIDTH//2 + 50, HEIGHT//2 - 75, world_button_width, world_button_height)

# Give Up button during gameplay
give_up_button_rect = pygame.Rect(WIDTH - 150, HEIGHT - 60, 140, 50)

running = True
while running:
    screen.fill(WHITE)
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "menu":
                if play_button_rect.collidepoint(event.pos):
                    # Go to character select
                    game_state = "character_select"
                elif quit_button_rect.collidepoint(event.pos):
                    running = False
                elif instructions_button_rect.collidepoint(event.pos):
                    show_instructions = not show_instructions
            elif game_state == "character_select":
                # Check character button clicks
                for i, button in enumerate(char_buttons):
                    if button.collidepoint(event.pos):
                        char = characters[i]
                        if char["unlocked"]:
                            # Already unlocked, select and play
                            selected_character = i
                            reset_game()
                            game_state = "playing"
                        elif blobs_rescued >= char["cost"]:
                            # Can afford to unlock
                            blobs_rescued -= char["cost"]
                            char["unlocked"] = True
                            selected_character = i
                            reset_game()
                            game_state = "playing"
                        # else: not enough blobs, do nothing
                        break
                # Back button (top right)
                back_button_char_select = pygame.Rect(WIDTH - 150, 20, 120, 50)
                if back_button_char_select.collidepoint(event.pos):
                    game_state = "menu"
                # Worlds button
                if worlds_button_rect.collidepoint(event.pos):
                    game_state = "world_select"
                # Upgrades button
                if upgrades_button_rect.collidepoint(event.pos):
                    game_state = "upgrades"
            elif game_state == "upgrades":
                # Character ability upgrades
                for i, (button, char) in enumerate(zip(char_buttons, characters)):
                    if button.collidepoint(event.pos):
                        if char["unlocked"] and not char["upgraded"] and blobs_rescued >= char["upgrade_cost"] and char["upgrade_cost"] > 0:
                            # Purchase upgrade
                            blobs_rescued -= char["upgrade_cost"]
                            char["upgraded"] = True
                        break
                # Mini blob count upgrade (4 buttons for 4 upgrades) - moved to bottom
                mini_blob_button_y = 510
                for upgrade_num in range(4):
                    button_rect = pygame.Rect(50 + upgrade_num * 185, mini_blob_button_y, 170, 80)
                    if button_rect.collidepoint(event.pos):
                        if upgrade_num == mini_blob_upgrade_level and mini_blob_upgrade_level < 4:
                            cost = mini_blob_upgrade_costs[upgrade_num]
                            if blobs_rescued >= cost:
                                blobs_rescued -= cost
                                mini_blob_upgrade_level += 1
                        break
                # Back button (top right position for upgrades screen)
                back_button_upgrades = pygame.Rect(WIDTH - 150, 20, 120, 50)
                if back_button_upgrades.collidepoint(event.pos):
                    game_state = "character_select"
            elif game_state == "world_select":
                # City world button
                if city_world_button.collidepoint(event.pos):
                    current_world = "city"
                    reset_game()
                    game_state = "playing"
                # Village world button
                if village_world_button.collidepoint(event.pos) and village_unlocked:
                    current_world = "village"
                    reset_game()
                    game_state = "playing"
                # Back button
                if back_button_rect.collidepoint(event.pos):
                    game_state = "character_select"
            elif game_state == "playing":
                # Give Up button
                if give_up_button_rect.collidepoint(event.pos):
                    game_state = "character_select"
            if game_state == "comic_panel":
                # Next level
                game_state = "playing"
                level += 1

                # Track max level and unlock village after city level 12
                if current_world == "city" and level > city_max_level:
                    city_max_level = level
                    if city_max_level >= 13:  # Completed level 12, unlock village
                        village_unlocked = True

                # Reset blobs collected this level to 0 so character size goes back to 20
                blobs_collected_level = 0

                # Start at full health (based on blobs collected in this run)
                max_power = 100 + (blobs_collected_run // 10) * 10
                power = max_power

                buildings = create_level_buildings(level, current_world)
                mini_blobs = spawn_mini_blobs()

                # Spawn gas clouds for village
                if current_world == "village":
                    gas_clouds = spawn_gas_clouds(level)
                else:
                    gas_clouds = []

                # Reset gate for new level
                gate["open"] = False
                gate["timer"] = 0

                blob_x, blob_y = 100, 450
                blob_vel_x, blob_vel_y = 0, 0
                flying = False
                can_catch = False
                collision_cooldown = 0

            elif game_state == "level_failed":
                # Out of power - restart from level 1
                reset_game()
                game_state = "playing"
                
            elif can_catch and flying:
                # Catch blob mid-flight - INCREASED CATCH RADIUS
                mouse_x, mouse_y = event.pos
                dist = math.sqrt((mouse_x - blob_x)**2 + (mouse_y - blob_y)**2)
                if dist < blob_radius + 50:  # Much bigger catch zone
                    dragging = True
                    flying = False
                    can_catch = False
                    launch_x, launch_y = blob_x, blob_y
                    blob_vel_x, blob_vel_y = 0, 0
                    
            elif not flying and not dragging:
                # Initial launch
                mouse_x, mouse_y = event.pos
                dist = math.sqrt((mouse_x - blob_x)**2 + (mouse_y - blob_y)**2)
                if dist < blob_radius + 20:
                    dragging = True
                    launch_x, launch_y = blob_x, blob_y
                    
        elif event.type == pygame.MOUSEBUTTONUP and dragging:
            dragging = False
            flying = True
            can_catch = True
            blob_vel_x = (launch_x - blob_x) * 0.2
            blob_vel_y = (launch_y - blob_y) * 0.2

    if game_state == "menu":
        # Animate background blobs
        for blob in menu_blobs:
            blob["x"] += blob["vel_x"]
            blob["y"] += blob["vel_y"]

            # Bounce off walls
            if blob["x"] - blob["radius"] < 0 or blob["x"] + blob["radius"] > WIDTH:
                blob["vel_x"] *= -1
            if blob["y"] - blob["radius"] < 0 or blob["y"] + blob["radius"] > HEIGHT:
                blob["vel_y"] *= -1

            # Draw blob with character appearance
            draw_blob_with_cape(blob["x"], blob["y"], blob["radius"], blob["color"])
            pulse = abs(math.sin(pygame.time.get_ticks() / 300)) * 4
            pygame.draw.circle(screen, WHITE, (int(blob["x"]), int(blob["y"])), blob["radius"] + int(pulse), 2)

        # Draw semi-transparent background for title area
        title_bg = pygame.Surface((WIDTH - 100, 140))
        title_bg.set_alpha(200)
        title_bg.fill(WHITE)
        screen.blit(title_bg, (50, 50))

        # Title with character replacing the "O" in BLOB
        title_part1 = font.render("SUPER BL", True, BLACK)
        title_part2 = font.render("B", True, BLACK)

        # Calculate positions to center the whole title
        blob_char_size = 35  # Size of the blob character
        total_width = title_part1.get_width() + blob_char_size + title_part2.get_width()
        start_x = WIDTH//2 - total_width//2
        title_y = 70

        # Draw title parts
        screen.blit(title_part1, (start_x, title_y))
        # Draw Super Blob character in place of "O"
        blob_x = start_x + title_part1.get_width() + blob_char_size//2
        blob_y = title_y + font.get_height()//2
        draw_blob_with_cape(blob_x, blob_y, blob_char_size//2, BLUE)
        screen.blit(title_part2, (start_x + title_part1.get_width() + blob_char_size, title_y))

        credits = tiny_font.render("Created by Emma Wilkinson", True, BLUE)
        screen.blit(credits, (WIDTH//2 - credits.get_width()//2, 150))

        # PLAY button
        play_hover = play_button_rect.collidepoint(mouse_pos)
        play_color = YELLOW if play_hover else GREEN
        pygame.draw.rect(screen, play_color, play_button_rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, play_button_rect, 4, border_radius=10)
        play_text = small_font.render("PLAY", True, BLACK)
        screen.blit(play_text, (play_button_rect.centerx - play_text.get_width()//2,
                                 play_button_rect.centery - play_text.get_height()//2))

        # QUIT button
        pygame.draw.rect(screen, BRIGHT_RED, quit_button_rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, quit_button_rect, 4, border_radius=10)
        quit_text = small_font.render("QUIT", True, BLACK)
        screen.blit(quit_text, (quit_button_rect.centerx - quit_text.get_width()//2,
                                 quit_button_rect.centery - quit_text.get_height()//2))

        # INSTRUCTIONS button
        instructions_hover = instructions_button_rect.collidepoint(mouse_pos)
        instructions_color = YELLOW if instructions_hover else BRIGHT_BLUE
        pygame.draw.rect(screen, instructions_color, instructions_button_rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, instructions_button_rect, 4, border_radius=10)
        instructions_text = small_font.render("HOW TO PLAY", True, BLACK)
        screen.blit(instructions_text, (instructions_button_rect.centerx - instructions_text.get_width()//2,
                                 instructions_button_rect.centery - instructions_text.get_height()//2))

        # Instructions dropdown (only show if button clicked)
        if show_instructions:
            instructions = [
                "HOW TO PLAY:",
                "• Drag the blob to aim and release to launch",
                "• Collect gray mini-blobs to gain power",
                "• Destroy buildings - save power for the GOLD boss!",
                "• Click mid-flight to catch and re-launch"
            ]

            # Draw semi-transparent background for instructions
            inst_bg = pygame.Surface((WIDTH - 100, 140))
            inst_bg.set_alpha(220)
            inst_bg.fill(WHITE)
            screen.blit(inst_bg, (50, HEIGHT - 165))

            y_offset = HEIGHT - 155
            for i, line in enumerate(instructions):
                inst_text = tiny_font.render(line, True, BLACK)
                screen.blit(inst_text, (WIDTH//2 - inst_text.get_width()//2, y_offset + i * 25))

    elif game_state == "character_select":
        # Title
        title = font.render("SELECT CHARACTER", True, BLACK)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))

        # Show total blobs rescued (top left corner)
        blob_count_text = small_font.render(f"Blobs: {blobs_rescued}", True, PURPLE)
        screen.blit(blob_count_text, (20, 20))

        # Character buttons
        for i, (button, char) in enumerate(zip(char_buttons, characters)):
            # Check if locked
            is_locked = not char["unlocked"]
            can_afford = blobs_rescued >= char["cost"]

            # Button background
            button_hover = button.collidepoint(mouse_pos)
            if is_locked:
                if can_afford and button_hover:
                    pygame.draw.rect(screen, GREEN, button, border_radius=10)
                elif can_afford:
                    pygame.draw.rect(screen, (200, 200, 200), button, border_radius=10)
                else:
                    pygame.draw.rect(screen, (150, 150, 150), button, border_radius=10)
            else:
                if button_hover:
                    pygame.draw.rect(screen, YELLOW, button, border_radius=10)
                else:
                    pygame.draw.rect(screen, WHITE, button, border_radius=10)
            pygame.draw.rect(screen, BLACK, button, 4, border_radius=10)

            # Character name (at top)
            name_text = tiny_font.render(char["name"], True, BLACK)
            screen.blit(name_text, (button.centerx - name_text.get_width()//2, button.y + 10))

            # Character description (below name)
            desc_text = tiny_font.render(char["description"], True, BLACK)
            screen.blit(desc_text, (button.centerx - desc_text.get_width()//2, button.y + 30))

            # Lock status or stats (below description, above character)
            if is_locked:
                cost_color = GREEN if can_afford else RED
                cost_text = tiny_font.render(f"Cost: {char['cost']} blobs", True, cost_color)
                screen.blit(cost_text, (button.centerx - cost_text.get_width()//2, button.y + 50))
            else:
                drain_text = tiny_font.render(f"Drain: {char['power_drain']}", True, BLACK)
                screen.blit(drain_text, (button.centerx - drain_text.get_width()//2, button.y + 50))

            # Character preview blob with cape (moved down)
            blob_x_pos = button.centerx
            blob_y_pos = button.y + 115
            draw_blob_with_cape(blob_x_pos, blob_y_pos, 35, char["color"])

            # Additional info at bottom
            if is_locked and can_afford:
                unlock_text = tiny_font.render("Click to unlock!", True, GREEN)
                screen.blit(unlock_text, (button.centerx - unlock_text.get_width()//2, button.y + 165))

        # Back button (moved to top right)
        back_button_char_select = pygame.Rect(WIDTH - 150, 20, 120, 50)
        back_hover = back_button_char_select.collidepoint(mouse_pos)
        back_color = ORANGE if back_hover else RED
        pygame.draw.rect(screen, back_color, back_button_char_select, border_radius=10)
        pygame.draw.rect(screen, BLACK, back_button_char_select, 4, border_radius=10)
        back_text = small_font.render("BACK", True, BLACK)
        screen.blit(back_text, (back_button_char_select.centerx - back_text.get_width()//2,
                                back_button_char_select.centery - back_text.get_height()//2))

        # Worlds button
        worlds_hover = worlds_button_rect.collidepoint(mouse_pos)
        worlds_color = YELLOW if worlds_hover else BRIGHT_BLUE
        pygame.draw.rect(screen, worlds_color, worlds_button_rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, worlds_button_rect, 4, border_radius=10)
        worlds_text = tiny_font.render("WORLDS", True, BLACK)
        screen.blit(worlds_text, (worlds_button_rect.centerx - worlds_text.get_width()//2,
                                   worlds_button_rect.centery - worlds_text.get_height()//2))

        # Upgrades button
        upgrades_hover = upgrades_button_rect.collidepoint(mouse_pos)
        upgrades_color = YELLOW if upgrades_hover else GREEN
        pygame.draw.rect(screen, upgrades_color, upgrades_button_rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, upgrades_button_rect, 4, border_radius=10)
        upgrades_text = tiny_font.render("UPGRADES", True, BLACK)
        screen.blit(upgrades_text, (upgrades_button_rect.centerx - upgrades_text.get_width()//2,
                                     upgrades_button_rect.centery - upgrades_text.get_height()//2))

    elif game_state == "upgrades":
        # Upgrades screen
        title = font.render("UPGRADES", True, BLACK)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))

        # Show total blobs rescued (top left corner)
        blob_count_text = small_font.render(f"Blobs: {blobs_rescued}", True, PURPLE)
        screen.blit(blob_count_text, (20, 20))

        # Character ability upgrades
        subtitle = small_font.render("Character Abilities", True, BLACK)
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 80))

        for i, (button, char) in enumerate(zip(char_buttons, characters)):
            is_unlocked = char["unlocked"]
            is_upgraded = char["upgraded"]
            can_afford = blobs_rescued >= char["upgrade_cost"]
            has_upgrade = char["upgrade_cost"] > 0

            # Button background
            button_hover = button.collidepoint(mouse_pos)
            if not is_unlocked:
                pygame.draw.rect(screen, (100, 100, 100), button, border_radius=10)
            elif is_upgraded:
                pygame.draw.rect(screen, (100, 255, 100), button, border_radius=10)  # Green for upgraded
            elif has_upgrade and can_afford and button_hover:
                pygame.draw.rect(screen, YELLOW, button, border_radius=10)
            elif has_upgrade and can_afford:
                pygame.draw.rect(screen, (200, 255, 200), button, border_radius=10)
            else:
                pygame.draw.rect(screen, (180, 180, 180), button, border_radius=10)
            pygame.draw.rect(screen, BLACK, button, 4, border_radius=10)

            # Character preview
            blob_x_pos = button.centerx
            blob_y_pos = button.y + 60
            draw_blob_with_cape(blob_x_pos, blob_y_pos, 35, char["color"])

            # Upgraded star indicator
            if is_upgraded:
                star_text = small_font.render("★", True, GOLD)
                screen.blit(star_text, (button.centerx - star_text.get_width()//2, button.y + 15))

            # Character name
            name_text = tiny_font.render(char["name"], True, BLACK)
            screen.blit(name_text, (button.centerx - name_text.get_width()//2, button.y + 110))

            # Upgrade status
            if not is_unlocked:
                locked_text = tiny_font.render("LOCKED", True, RED)
                screen.blit(locked_text, (button.centerx - locked_text.get_width()//2, button.y + 135))
            elif is_upgraded:
                upgraded_text = tiny_font.render("UPGRADED!", True, GREEN)
                screen.blit(upgraded_text, (button.centerx - upgraded_text.get_width()//2, button.y + 135))
            elif has_upgrade:
                desc_text = tiny_font.render(char["upgrade_desc"], True, BLACK)
                screen.blit(desc_text, (button.centerx - desc_text.get_width()//2, button.y + 135))
                cost_color = GREEN if can_afford else RED
                cost_text = tiny_font.render(f"Cost: {char['upgrade_cost']}", True, cost_color)
                screen.blit(cost_text, (button.centerx - cost_text.get_width()//2, button.y + 155))
                if can_afford:
                    click_text = tiny_font.render("Click to buy!", True, GREEN)
                    screen.blit(click_text, (button.centerx - click_text.get_width()//2, button.y + 175))
            else:
                no_upgrade_text = tiny_font.render("No upgrade", True, BLACK)
                screen.blit(no_upgrade_text, (button.centerx - no_upgrade_text.get_width()//2, button.y + 135))

        # Mini blob count upgrades (moved to bottom)
        mini_subtitle = small_font.render("Mini Blob Count (6 base)", True, BLACK)
        screen.blit(mini_subtitle, (WIDTH//2 - mini_subtitle.get_width()//2, 470))

        mini_blob_button_y = 510
        for upgrade_num in range(4):
            button_rect = pygame.Rect(50 + upgrade_num * 185, mini_blob_button_y, 170, 80)
            is_purchased = upgrade_num < mini_blob_upgrade_level
            is_next = upgrade_num == mini_blob_upgrade_level
            cost = mini_blob_upgrade_costs[upgrade_num]
            can_afford = blobs_rescued >= cost

            # Button background
            button_hover = button_rect.collidepoint(mouse_pos)
            if is_purchased:
                pygame.draw.rect(screen, (100, 255, 100), button_rect, border_radius=10)  # Green
            elif is_next and can_afford and button_hover:
                pygame.draw.rect(screen, YELLOW, button_rect, border_radius=10)
            elif is_next and can_afford:
                pygame.draw.rect(screen, (200, 255, 200), button_rect, border_radius=10)
            elif is_next:
                pygame.draw.rect(screen, WHITE, button_rect, border_radius=10)
            else:
                pygame.draw.rect(screen, (150, 150, 150), button_rect, border_radius=10)
            pygame.draw.rect(screen, BLACK, button_rect, 4, border_radius=10)

            # Upgrade info
            upgrade_title = tiny_font.render(f"Upgrade {upgrade_num + 1}", True, BLACK)
            screen.blit(upgrade_title, (button_rect.centerx - upgrade_title.get_width()//2, button_rect.y + 10))

            new_count = 7 + upgrade_num
            count_text = tiny_font.render(f"+1 blob ({new_count} total)", True, BLACK)
            screen.blit(count_text, (button_rect.centerx - count_text.get_width()//2, button_rect.y + 30))

            if is_purchased:
                purchased_text = tiny_font.render("PURCHASED", True, GREEN)
                screen.blit(purchased_text, (button_rect.centerx - purchased_text.get_width()//2, button_rect.y + 50))
            elif is_next:
                cost_color = GREEN if can_afford else RED
                cost_text = tiny_font.render(f"Cost: {cost}", True, cost_color)
                screen.blit(cost_text, (button_rect.centerx - cost_text.get_width()//2, button_rect.y + 50))
            else:
                locked_text = tiny_font.render("LOCKED", True, (100, 100, 100))
                screen.blit(locked_text, (button_rect.centerx - locked_text.get_width()//2, button_rect.y + 50))

        # Back button (moved to top right to avoid blocking mini blob upgrades)
        back_button_upgrades = pygame.Rect(WIDTH - 150, 20, 120, 50)
        back_hover = back_button_upgrades.collidepoint(mouse_pos)
        back_color = ORANGE if back_hover else RED
        pygame.draw.rect(screen, back_color, back_button_upgrades, border_radius=10)
        pygame.draw.rect(screen, BLACK, back_button_upgrades, 4, border_radius=10)
        back_text = small_font.render("BACK", True, BLACK)
        screen.blit(back_text, (back_button_upgrades.centerx - back_text.get_width()//2,
                                back_button_upgrades.centery - back_text.get_height()//2))

    elif game_state == "world_select":
        # World selection screen
        title = font.render("SELECT WORLD", True, BLACK)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))

        # City world button
        city_hover = city_world_button.collidepoint(mouse_pos)
        city_color = YELLOW if city_hover else (200, 200, 200)
        pygame.draw.rect(screen, city_color, city_world_button, border_radius=10)
        pygame.draw.rect(screen, BLACK, city_world_button, 5, border_radius=10)
        city_title = small_font.render("CITY", True, BLACK)
        screen.blit(city_title, (city_world_button.centerx - city_title.get_width()//2, city_world_button.y + 20))
        city_desc = tiny_font.render("Skyscrapers & Buildings", True, BLACK)
        screen.blit(city_desc, (city_world_button.centerx - city_desc.get_width()//2, city_world_button.y + 60))
        city_max_text = tiny_font.render(f"Max Level: {city_max_level}", True, BLACK)
        screen.blit(city_max_text, (city_world_button.centerx - city_max_text.get_width()//2, city_world_button.y + 90))

        # Village world button
        village_hover = village_world_button.collidepoint(mouse_pos)
        if village_unlocked:
            village_color = YELLOW if village_hover else (150, 200, 150)
            pygame.draw.rect(screen, village_color, village_world_button, border_radius=10)
            pygame.draw.rect(screen, BLACK, village_world_button, 5, border_radius=10)
            village_title = small_font.render("VILLAGE", True, BLACK)
            screen.blit(village_title, (village_world_button.centerx - village_title.get_width()//2, village_world_button.y + 20))
            village_desc = tiny_font.render("Houses & Gas Clouds", True, BLACK)
            screen.blit(village_desc, (village_world_button.centerx - village_desc.get_width()//2, village_world_button.y + 60))
            unlocked_text = tiny_font.render("UNLOCKED!", True, GREEN)
            screen.blit(unlocked_text, (village_world_button.centerx - unlocked_text.get_width()//2, village_world_button.y + 90))
        else:
            pygame.draw.rect(screen, (100, 100, 100), village_world_button, border_radius=10)
            pygame.draw.rect(screen, BLACK, village_world_button, 5, border_radius=10)
            locked_icon = font.render("🔒", True, BLACK)
            screen.blit(locked_icon, (village_world_button.centerx - locked_icon.get_width()//2, village_world_button.y + 30))
            locked_text = tiny_font.render("Beat City Level 12", True, BLACK)
            screen.blit(locked_text, (village_world_button.centerx - locked_text.get_width()//2, village_world_button.y + 100))

        # Back button
        back_hover = back_button_rect.collidepoint(mouse_pos)
        back_color = ORANGE if back_hover else RED
        pygame.draw.rect(screen, back_color, back_button_rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, back_button_rect, 4, border_radius=10)
        back_text = small_font.render("BACK", True, BLACK)
        screen.blit(back_text, (back_button_rect.centerx - back_text.get_width()//2,
                                back_button_rect.centery - back_text.get_height()//2))

    elif game_state == "playing":
        # Draw background based on world
        if current_world == "village":
            draw_village_background()
        else:
            draw_city_background()

        # Update blob size based on blobs collected THIS level (resets each level)
        blob_radius = 20 + (blobs_collected_level // 5) * 4

        # Max power increases by 10 for every 10 blobs collected in current run
        max_power = 100 + (blobs_collected_run // 10) * 10

        # VILLAGE BONUS: Extra +10 max health for every 7 mini blobs collected in the level
        if current_world == "village":
            max_power += (blobs_collected_level // 7) * 10

        # Gate timer update (level 10+ in city only)
        if level >= 10 and current_world == "city":
            gate["timer"] += 1
            if gate["open"]:
                if gate["timer"] >= gate["open_duration"]:
                    gate["open"] = False
                    gate["timer"] = 0
            else:
                if gate["timer"] >= gate["close_duration"]:
                    gate["open"] = True
                    gate["timer"] = 0

        # Power drain
        if flying:
            power -= power_drain_rate
            power = max(0, power)
            
            # Check if power depleted
            if power <= 0:
                game_state = "level_failed"
        
        # Drag visual with trajectory preview
        if dragging:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            blob_x, blob_y = mouse_x, mouse_y
            pygame.draw.line(screen, RED, (launch_x, launch_y), (blob_x, blob_y), 3)
            
            # Draw arc preview
            preview_vel_x = (launch_x - blob_x) * 0.2
            preview_vel_y = (launch_y - blob_y) * 0.2
            px, py = launch_x, launch_y
            for i in range(30):
                preview_vel_y += gravity
                px += preview_vel_x
                py += preview_vel_y
                if i % 3 == 0 and py < HEIGHT:
                    pygame.draw.circle(screen, RED, (int(px), int(py)), 2)
        
        # Physics
        if flying:
            blob_vel_y += gravity
            blob_x += blob_vel_x
            blob_y += blob_vel_y

            # Magnetic attraction (Richard's ability - STRONGER PULL!)
            if has_magnetic_ability:
                for mini in mini_blobs:
                    if mini["alive"]:
                        dist = math.sqrt((blob_x - mini["x"])**2 + (blob_y - mini["y"])**2)
                        magnetic_range = 150  # Attraction range (same as before)
                        if dist < magnetic_range and dist > 0:
                            # Pull mini blobs toward player
                            pull_strength = 5.0  # Base strength
                            # Upgrade: Even stronger magnetic pull
                            if characters[selected_character]["upgraded"]:
                                pull_strength = 7.5  # Upgraded strength
                            dx = (blob_x - mini["x"]) / dist
                            dy = (blob_y - mini["y"]) / dist
                            mini["x"] += dx * pull_strength
                            mini["y"] += dy * pull_strength

            # Collect mini blobs - FIXED DISTANCE CHECK
            for mini in mini_blobs:
                if mini["alive"]:
                    dist = math.sqrt((blob_x - mini["x"])**2 + (blob_y - mini["y"])**2)
                    if dist < blob_radius + mini["r"] + 5:  # Added buffer
                        mini["alive"] = False
                        blobs_rescued += 1  # Currency for unlocking characters
                        blobs_collected_run += 1  # Counter for max power increase
                        blobs_collected_level += 1  # Counter for size increase this level
                        power = min(max_power, power + 15)  # Refill power
            
            # Collision cooldown
            if collision_cooldown > 0:
                collision_cooldown -= 1
            
            # Building collisions
            if collision_cooldown == 0:
                for building in buildings:
                    if building["alive"]:
                        # Rectangle collision detection
                        if (blob_x + blob_radius > building["x"] and 
                            blob_x - blob_radius < building["x"] + building["w"] and
                            blob_y + blob_radius > building["y"] and 
                            blob_y - blob_radius < building["y"] + building["h"]):
                            
                            collision_cooldown = 15  # Prevent rapid re-collision
                            
                            # Check if boss building
                            if building.get("is_boss"):
                                required = building.get("required_power", 50)
                                # Evil Mob upgrade: Smash bosses faster (30% less power needed)
                                if can_pierce_buildings and characters[selected_character]["upgraded"]:
                                    required = int(required * 0.7)  # 30% reduction
                                if power >= required:
                                    # SMASH THE BOSS!
                                    building["alive"] = False
                                    building["pieces"] = create_debris(building)
                                    game_state = "comic_panel"
                                else:
                                    # Bounce off - not enough power
                                    center_x = building["x"] + building["w"] / 2
                                    
                                    if blob_x < center_x:
                                        blob_vel_x = -abs(blob_vel_x) * bounce_damping
                                        blob_x = building["x"] - blob_radius - 2
                                    else:
                                        blob_vel_x = abs(blob_vel_x) * bounce_damping
                                        blob_x = building["x"] + building["w"] + blob_radius + 2
                            else:
                                # Regular building - DESTROY ON HIT
                                building["alive"] = False
                                building["pieces"] = create_debris(building)

                                # Pierce or bounce based on character ability
                                if not can_pierce_buildings:
                                    # Bounce after destruction
                                    center_x = building["x"] + building["w"] / 2

                                    if blob_x < center_x:
                                        blob_vel_x = -abs(blob_vel_x) * bounce_damping
                                    else:
                                        blob_vel_x = abs(blob_vel_x) * bounce_damping
                                # else: Red blob pierces through, no bounce!

                            if not can_pierce_buildings:
                                break  # Only break if not piercing
            
            # Bounce off edges
            if blob_x - blob_radius < 0:
                blob_vel_x = abs(blob_vel_x) * bounce_damping
                blob_x = blob_radius
            elif blob_x + blob_radius > WIDTH:
                blob_vel_x = -abs(blob_vel_x) * bounce_damping
                blob_x = WIDTH - blob_radius
            
            if blob_y - blob_radius < 0:
                blob_vel_y = abs(blob_vel_y) * bounce_damping
                blob_y = blob_radius

            # Gate collision (level 10+ in city only)
            if level >= 10 and current_world == "city" and collision_cooldown == 0:
                if not gate["open"]:
                    # Check collision with closed gate
                    if (blob_x + blob_radius > gate["x"] and
                        blob_x - blob_radius < gate["x"] + gate["width"] and
                        blob_y + blob_radius > gate["y"] and
                        blob_y - blob_radius < gate["y"] + gate["height"]):
                        # Bounce off closed gate
                        collision_cooldown = 15
                        if blob_x < gate["x"] + gate["width"] / 2:
                            blob_vel_x = -abs(blob_vel_x) * bounce_damping
                            blob_x = gate["x"] - blob_radius - 2
                        else:
                            blob_vel_x = abs(blob_vel_x) * bounce_damping
                            blob_x = gate["x"] + gate["width"] + blob_radius + 2

            # Hit ground - reset
            if blob_y > HEIGHT - blob_radius:
                blob_x, blob_y = 100, 450
                blob_vel_x, blob_vel_y = 0, 0
                flying = False
                can_catch = False
                collision_cooldown = 0
        
        # Update debris
        for building in buildings:
            for piece in building["pieces"]:
                piece["vel_y"] += gravity
                piece["x"] += piece["vel_x"]
                piece["y"] += piece["vel_y"]
                piece["rotation"] += piece["rot_speed"]
                
                if piece["y"] < HEIGHT + 50:
                    color = GOLD if building.get("is_boss") else (120, 120, 120)  # Gray for regular buildings
                    pygame.draw.rect(screen, color, (int(piece["x"]), int(piece["y"]), piece["w"], piece["h"]))
        
        # Draw buildings with new graphics
        for building in buildings:
            draw_building(building, current_world)
            # Draw power requirement for boss
            if building["alive"] and building.get("is_boss"):
                req_text = tiny_font.render(f"Need {building['required_power']} pwr", True, BLACK)
                req_bg = pygame.Surface((req_text.get_width() + 10, req_text.get_height() + 4))
                req_bg.set_alpha(200)
                req_bg.fill(WHITE)
                screen.blit(req_bg, (building["x"] - 5, building["y"] - 28))
                screen.blit(req_text, (building["x"], building["y"] - 26))

        # Update and draw gas clouds (village only)
        if current_world == "village":
            for cloud in gas_clouds:
                # Move gas cloud (always moving)
                cloud["x"] += cloud["vel_x"]
                cloud["y"] += cloud["vel_y"]

                # Bounce off walls
                if cloud["x"] - cloud["r"] < 0 or cloud["x"] + cloud["r"] > WIDTH:
                    cloud["vel_x"] *= -1
                if cloud["y"] - cloud["r"] < 0 or cloud["y"] + cloud["r"] > HEIGHT:
                    cloud["vel_y"] *= -1

                # Check collision with player (only when flying)
                if flying:
                    dist = math.sqrt((blob_x - cloud["x"])**2 + (blob_y - cloud["y"])**2)
                    if dist < blob_radius + cloud["r"]:
                        # Hit gas cloud - lose 20 power!
                        power = max(0, power - 20)

                # Draw gas cloud (darker light purple) - ALWAYS VISIBLE
                gas_surface = pygame.Surface((cloud["r"] * 2, cloud["r"] * 2), pygame.SRCALPHA)
                # Darker purple with higher alpha - easier to see
                pygame.draw.circle(gas_surface, (200, 180, 230, 80), (cloud["r"], cloud["r"]), cloud["r"])
                screen.blit(gas_surface, (int(cloud["x"] - cloud["r"]), int(cloud["y"] - cloud["r"])))
                # Darker outer edge - more visible
                pygame.draw.circle(screen, (180, 160, 210, 100), (int(cloud["x"]), int(cloud["y"])), cloud["r"], 2)

        # Draw gate (level 10+ in city only, not in village)
        if level >= 10 and current_world == "city":
            if gate["open"]:
                # Draw open gate - just the top and bottom bars
                top_height = 50
                bottom_y = gate["y"] + gate["height"] - 50
                pygame.draw.rect(screen, DARK_RED, (gate["x"], gate["y"], gate["width"], top_height))
                pygame.draw.rect(screen, DARK_RED, (gate["x"], bottom_y, gate["width"], 50))
                pygame.draw.rect(screen, BLACK, (gate["x"], gate["y"], gate["width"], top_height), 3)
                pygame.draw.rect(screen, BLACK, (gate["x"], bottom_y, gate["width"], 50), 3)
            else:
                # Draw closed gate - full bar
                pygame.draw.rect(screen, DARK_RED, (gate["x"], gate["y"], gate["width"], gate["height"]))
                pygame.draw.rect(screen, BLACK, (gate["x"], gate["y"], gate["width"], gate["height"]), 3)
                # Timer indicator
                progress = gate["timer"] / gate["close_duration"]
                indicator_height = int(gate["height"] * progress)
                pygame.draw.rect(screen, YELLOW, (gate["x"] + 5, gate["y"] + gate["height"] - indicator_height, gate["width"] - 10, indicator_height))

        # Draw mini blobs
        for mini in mini_blobs:
            if mini["alive"]:
                # Main body
                pygame.draw.circle(screen, PURPLE, (mini["x"], mini["y"]), mini["r"])
                pygame.draw.circle(screen, BLACK, (mini["x"], mini["y"]), mini["r"], 1)

                # Pulsing glow effect
                pulse = abs(math.sin(pygame.time.get_ticks() / 200)) * 3
                pygame.draw.circle(screen, WHITE, (mini["x"], mini["y"]), mini["r"] + int(pulse), 1)

                # Draw eyes with white circles and black pupils
                eye_size = max(2, int(mini["r"] * 0.4))
                pupil_size = max(1, int(mini["r"] * 0.25))
                eye_y = mini["y"] - mini["r"] * 0.25
                # Left eye
                pygame.draw.circle(screen, WHITE, (int(mini["x"] - mini["r"] * 0.4), int(eye_y)), eye_size)
                pygame.draw.circle(screen, BLACK, (int(mini["x"] - mini["r"] * 0.4), int(eye_y)), pupil_size)
                # Right eye
                pygame.draw.circle(screen, WHITE, (int(mini["x"] + mini["r"] * 0.4), int(eye_y)), eye_size)
                pygame.draw.circle(screen, BLACK, (int(mini["x"] + mini["r"] * 0.4), int(eye_y)), pupil_size)

                # Small happy smile
                smile_y = int(mini["y"] + mini["r"] * 0.2)
                pygame.draw.arc(screen, BLACK, (int(mini["x"] - mini["r"] * 0.3), smile_y - 3, int(mini["r"] * 0.6), 8), 3.14, 6.28, 2)
        
        # Draw main blob with cape
        draw_blob_with_cape(blob_x, blob_y, blob_radius, player_color)

        # Magnetic field indicator (Richard)
        if has_magnetic_ability and flying:
            magnetic_range = 150  # Same range, stronger pull
            pulse = abs(math.sin(pygame.time.get_ticks() / 300)) * 10
            pygame.draw.circle(screen, ORANGE, (int(blob_x), int(blob_y)), int(magnetic_range + pulse), 2)

        # Catch indicator - BIGGER VISUAL
        if can_catch and flying:
            pygame.draw.circle(screen, ORANGE, (int(blob_x), int(blob_y)), blob_radius + 50, 3)
        
        # Comic panel border
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, HEIGHT), 10)
        
        # UI - Power bar
        bar_width = 200
        bar_height = 20
        bar_x = WIDTH - bar_width - 20
        bar_y = 10
        
        pygame.draw.rect(screen, BLACK, (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4))
        pygame.draw.rect(screen, DARK_RED, (bar_x, bar_y, bar_width, bar_height))
        
        current_bar = int((power / max_power) * bar_width)
        bar_color = GREEN if power > 50 else ORANGE if power > 25 else RED
        pygame.draw.rect(screen, bar_color, (bar_x, bar_y, current_bar, bar_height))
        
        power_text = tiny_font.render(f"POWER: {int(power)}", True, WHITE)
        screen.blit(power_text, (bar_x + 5, bar_y + 2))
        
        # Level and stats
        level_text = small_font.render(f"Level {level}", True, BLACK)
        screen.blit(level_text, (10, 10))
        
        rescue_text = tiny_font.render(f"Rescued: {blobs_rescued} | Size: {blob_radius}", True, BLACK)
        screen.blit(rescue_text, (10, 50))

        # Give Up button
        give_up_hover = give_up_button_rect.collidepoint(mouse_pos)
        give_up_color = YELLOW if give_up_hover else BRIGHT_RED
        pygame.draw.rect(screen, give_up_color, give_up_button_rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, give_up_button_rect, 4, border_radius=10)
        give_up_text = tiny_font.render("GIVE UP", True, BLACK)
        screen.blit(give_up_text, (give_up_button_rect.centerx - give_up_text.get_width()//2,
                                   give_up_button_rect.centery - give_up_text.get_height()//2))

    elif game_state == "comic_panel":
        # Traditional comic book style with multiple panels - rotate designs
        screen.fill((240, 240, 240))  # Light gray background

        # Comic title at top
        title = font.render("SUPER BLOB", True, BLACK)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 20))

        comic_variant = level % 8  # Rotate through 8 different comic styles

        # Different comics for village vs city
        if current_world == "village":
            # VILLAGE COMICS - countryside themed
            if comic_variant == 0:
                # Village Comic 1: "The village needs help!" / "I'll protect the houses!"
                # Panel 1 - Mini blobs in front of village houses
                panel1_rect = pygame.Rect(30, 80, 350, 220)
                pygame.draw.rect(screen, (150, 220, 150), panel1_rect)  # Green background
                pygame.draw.rect(screen, BLACK, panel1_rect, 5)

                # Draw small village houses in background - cleaner design
                for i in range(2):
                    hx = panel1_rect.x + 60 + i * 130
                    hy = panel1_rect.y + 110
                    # House body with shading
                    pygame.draw.rect(screen, (160, 82, 45), (hx, hy, 60, 55))
                    pygame.draw.rect(screen, BLACK, (hx, hy, 60, 55), 3)
                    # Clean triangular roof
                    roof = [(hx - 6, hy), (hx + 30, hy - 25), (hx + 66, hy)]
                    pygame.draw.polygon(screen, (200, 50, 50), roof)
                    pygame.draw.polygon(screen, BLACK, roof, 3)
                    # Door
                    pygame.draw.rect(screen, (101, 67, 33), (hx + 20, hy + 25, 20, 30))
                    pygame.draw.rect(screen, BLACK, (hx + 20, hy + 25, 20, 30), 2)
                    # Window
                    pygame.draw.rect(screen, (255, 255, 200), (hx + 8, hy + 15, 15, 15))
                    pygame.draw.rect(screen, BLACK, (hx + 8, hy + 15, 15, 15), 2)

                # Mini blobs - cleaner with consistent style
                for i in range(2):
                    mini_x = panel1_rect.x + 110 + i * 90
                    mini_y = panel1_rect.y + 170
                    # Body with outline
                    pygame.draw.circle(screen, PURPLE, (mini_x, mini_y), 22)
                    pygame.draw.circle(screen, BLACK, (mini_x, mini_y), 22, 3)
                    # Eyes - larger and cleaner
                    eye_size = 6
                    pupil_size = 4
                    # Left eye
                    pygame.draw.circle(screen, WHITE, (mini_x - 9, mini_y - 5), eye_size)
                    pygame.draw.circle(screen, BLACK, (mini_x - 9, mini_y - 5), eye_size, 1)
                    pygame.draw.circle(screen, BLACK, (mini_x - 9, mini_y - 5), pupil_size)
                    # Right eye
                    pygame.draw.circle(screen, WHITE, (mini_x + 9, mini_y - 5), eye_size)
                    pygame.draw.circle(screen, BLACK, (mini_x + 9, mini_y - 5), eye_size, 1)
                    pygame.draw.circle(screen, BLACK, (mini_x + 9, mini_y - 5), pupil_size)

                # Cleaner speech bubble with rounded rect
                bubble1_rect = pygame.Rect(panel1_rect.x + 35, panel1_rect.y + 22, 280, 55)
                pygame.draw.ellipse(screen, WHITE, bubble1_rect)
                pygame.draw.ellipse(screen, BLACK, bubble1_rect, 4)
                help_text = small_font.render("The village needs help!", True, BLACK)
                screen.blit(help_text, (bubble1_rect.centerx - help_text.get_width()//2,
                                        bubble1_rect.centery - help_text.get_height()//2))

                # Panel 2 - Hero ready
                panel2_rect = pygame.Rect(420, 80, 350, 220)
                pygame.draw.rect(screen, (255, 235, 200), panel2_rect)
                pygame.draw.rect(screen, BLACK, panel2_rect, 5)
                draw_blob_with_cape(panel2_rect.centerx, panel2_rect.centery + 20, 40, player_color)

                bubble2_rect = pygame.Rect(panel2_rect.x + 50, panel2_rect.y + 20, 250, 70)
                pygame.draw.ellipse(screen, WHITE, bubble2_rect)
                pygame.draw.ellipse(screen, BLACK, bubble2_rect, 3)
                save_text1 = tiny_font.render("I'll protect", True, BLACK)
                save_text2 = tiny_font.render("the houses!", True, BLACK)
                screen.blit(save_text1, (bubble2_rect.centerx - save_text1.get_width()//2, bubble2_rect.centery - 15))
                screen.blit(save_text2, (bubble2_rect.centerx - save_text2.get_width()//2, bubble2_rect.centery + 10))

            elif comic_variant == 1:
                # Village Comic 2: "The gas cloud is dangerous!" / "I'll fly carefully!"
                # Panel 1 - Gas cloud warning
                panel1_rect = pygame.Rect(30, 80, 350, 220)
                pygame.draw.rect(screen, (180, 200, 180), panel1_rect)
                pygame.draw.rect(screen, BLACK, panel1_rect, 5)

                # Draw gas cloud
                gas_surface = pygame.Surface((80, 80), pygame.SRCALPHA)
                pygame.draw.circle(gas_surface, (200, 180, 230, 150), (40, 40), 40)
                screen.blit(gas_surface, (panel1_rect.centerx - 40, panel1_rect.centery - 20))
                pygame.draw.circle(screen, (180, 160, 210, 200), (panel1_rect.centerx, panel1_rect.centery), 40, 3)

                bubble1_rect = pygame.Rect(panel1_rect.x + 30, panel1_rect.y + 20, 290, 60)
                pygame.draw.ellipse(screen, WHITE, bubble1_rect)
                pygame.draw.ellipse(screen, BLACK, bubble1_rect, 3)
                warn_text1 = tiny_font.render("The gas cloud is", True, BLACK)
                warn_text2 = tiny_font.render("dangerous!", True, BLACK)
                screen.blit(warn_text1, (bubble1_rect.centerx - warn_text1.get_width()//2, bubble1_rect.centery - 15))
                screen.blit(warn_text2, (bubble1_rect.centerx - warn_text2.get_width()//2, bubble1_rect.centery + 10))

                # Panel 2 - Determined hero
                panel2_rect = pygame.Rect(420, 80, 350, 220)
                pygame.draw.rect(screen, (200, 255, 200), panel2_rect)
                pygame.draw.rect(screen, BLACK, panel2_rect, 5)
                draw_blob_with_cape(panel2_rect.centerx, panel2_rect.centery + 30, 45, player_color)

                bubble2_rect = pygame.Rect(panel2_rect.x + 50, panel2_rect.y + 20, 250, 60)
                pygame.draw.ellipse(screen, WHITE, bubble2_rect)
                pygame.draw.ellipse(screen, BLACK, bubble2_rect, 3)
                careful_text = small_font.render("I'll fly carefully!", True, BLACK)
                screen.blit(careful_text, (bubble2_rect.centerx - careful_text.get_width()//2,
                                          bubble2_rect.centery - careful_text.get_height()//2))

            elif comic_variant == 2:
                # Village Comic 3: "So many houses!" / "I can protect them all!"
                panel1_rect = pygame.Rect(30, 80, 350, 220)
                pygame.draw.rect(screen, (180, 220, 180), panel1_rect)
                pygame.draw.rect(screen, BLACK, panel1_rect, 5)

                # Draw multiple small houses - cleaner design
                for i in range(4):
                    hx = panel1_rect.x + 35 + i * 72
                    hy = panel1_rect.y + 125
                    # House body
                    pygame.draw.rect(screen, (160, 82, 45), (hx, hy, 48, 45))
                    pygame.draw.rect(screen, BLACK, (hx, hy, 48, 45), 3)
                    # Clean triangular roof
                    roof = [(hx - 4, hy), (hx + 24, hy - 18), (hx + 52, hy)]
                    pygame.draw.polygon(screen, (200, 50, 50), roof)
                    pygame.draw.polygon(screen, BLACK, roof, 3)
                    # Door
                    pygame.draw.rect(screen, (101, 67, 33), (hx + 16, hy + 20, 16, 25))
                    pygame.draw.rect(screen, BLACK, (hx + 16, hy + 20, 16, 25), 2)
                    # Window
                    pygame.draw.rect(screen, (255, 255, 200), (hx + 6, hy + 12, 12, 12))
                    pygame.draw.rect(screen, BLACK, (hx + 6, hy + 12, 12, 12), 2)

                bubble1_rect = pygame.Rect(panel1_rect.x + 40, panel1_rect.y + 20, 270, 50)
                pygame.draw.ellipse(screen, WHITE, bubble1_rect)
                pygame.draw.ellipse(screen, BLACK, bubble1_rect, 3)
                houses_text = tiny_font.render("So many houses!", True, BLACK)
                screen.blit(houses_text, (bubble1_rect.centerx - houses_text.get_width()//2, bubble1_rect.centery - houses_text.get_height()//2))

                # Panel 2
                panel2_rect = pygame.Rect(420, 80, 350, 220)
                pygame.draw.rect(screen, (255, 240, 200), panel2_rect)
                pygame.draw.rect(screen, BLACK, panel2_rect, 5)
                draw_blob_with_cape(panel2_rect.centerx, panel2_rect.centery + 30, 45, player_color)

                bubble2_rect = pygame.Rect(panel2_rect.x + 50, panel2_rect.y + 20, 250, 60)
                pygame.draw.ellipse(screen, WHITE, bubble2_rect)
                pygame.draw.ellipse(screen, BLACK, bubble2_rect, 3)
                protect_text1 = tiny_font.render("I can protect", True, BLACK)
                protect_text2 = tiny_font.render("them all!", True, BLACK)
                screen.blit(protect_text1, (bubble2_rect.centerx - protect_text1.get_width()//2, bubble2_rect.centery - 15))
                screen.blit(protect_text2, (bubble2_rect.centerx - protect_text2.get_width()//2, bubble2_rect.centery + 10))

            elif comic_variant == 3:
                # Village Comic 4: Mini blobs with countryside / "We believe in you!"
                panel1_rect = pygame.Rect(30, 80, 350, 220)
                pygame.draw.rect(screen, (200, 240, 200), panel1_rect)
                pygame.draw.rect(screen, BLACK, panel1_rect, 5)

                # Draw cleaner fence with horizontal bars
                for i in range(7):
                    fx = panel1_rect.x + 40 + i * 45
                    fy = panel1_rect.y + 155
                    # Vertical post
                    pygame.draw.rect(screen, (139, 69, 19), (fx, fy, 10, 50))
                    pygame.draw.rect(screen, BLACK, (fx, fy, 10, 50), 2)
                # Horizontal bars
                pygame.draw.rect(screen, (139, 69, 19), (panel1_rect.x + 40, panel1_rect.y + 170, 280, 8))
                pygame.draw.rect(screen, BLACK, (panel1_rect.x + 40, panel1_rect.y + 170, 280, 8), 2)
                pygame.draw.rect(screen, (139, 69, 19), (panel1_rect.x + 40, panel1_rect.y + 190, 280, 8))
                pygame.draw.rect(screen, BLACK, (panel1_rect.x + 40, panel1_rect.y + 190, 280, 8), 2)

                # Mini blobs in front of fence
                for i in range(2):
                    mini_x = panel1_rect.x + 120 + i * 80
                    mini_y = panel1_rect.y + 160
                    pygame.draw.circle(screen, PURPLE, (mini_x, mini_y), 20)
                    pygame.draw.circle(screen, BLACK, (mini_x, mini_y), 20, 2)
                    # Eyes
                    eye_size = 5
                    pupil_size = 3
                    pygame.draw.circle(screen, WHITE, (mini_x - 8, mini_y - 5), eye_size)
                    pygame.draw.circle(screen, BLACK, (mini_x - 8, mini_y - 5), pupil_size)
                    pygame.draw.circle(screen, WHITE, (mini_x + 8, mini_y - 5), eye_size)
                    pygame.draw.circle(screen, BLACK, (mini_x + 8, mini_y - 5), pupil_size)

                bubble1_rect = pygame.Rect(panel1_rect.x + 60, panel1_rect.y + 30, 230, 60)
                pygame.draw.ellipse(screen, WHITE, bubble1_rect)
                pygame.draw.ellipse(screen, BLACK, bubble1_rect, 3)
                believe_text = small_font.render("We believe in you!", True, BLACK)
                screen.blit(believe_text, (bubble1_rect.centerx - believe_text.get_width()//2, bubble1_rect.centery - believe_text.get_height()//2))

                # Panel 2
                panel2_rect = pygame.Rect(420, 80, 350, 220)
                pygame.draw.rect(screen, (255, 245, 220), panel2_rect)
                pygame.draw.rect(screen, BLACK, panel2_rect, 5)
                draw_blob_with_cape(panel2_rect.centerx, panel2_rect.centery + 30, 45, player_color)

                bubble2_rect = pygame.Rect(panel2_rect.x + 50, panel2_rect.y + 20, 250, 60)
                pygame.draw.ellipse(screen, WHITE, bubble2_rect)
                pygame.draw.ellipse(screen, BLACK, bubble2_rect, 3)
                thanks_text = small_font.render("Thanks!", True, BLACK)
                screen.blit(thanks_text, (bubble2_rect.centerx - thanks_text.get_width()//2, bubble2_rect.centery - thanks_text.get_height()//2))

            elif comic_variant == 4:
                # Village Comic 5: "You're doing great!" / "I won't give up!"
                panel1_rect = pygame.Rect(30, 80, 350, 220)
                pygame.draw.rect(screen, (220, 255, 220), panel1_rect)
                pygame.draw.rect(screen, BLACK, panel1_rect, 5)

                # Mini blob cheering
                mini_x = panel1_rect.centerx
                mini_y = panel1_rect.centery + 20
                pygame.draw.circle(screen, PURPLE, (mini_x, mini_y), 25)
                pygame.draw.circle(screen, BLACK, (mini_x, mini_y), 25, 2)
                # Eyes
                eye_size = 6
                pupil_size = 4
                pygame.draw.circle(screen, WHITE, (mini_x - 10, mini_y - 6), eye_size)
                pygame.draw.circle(screen, BLACK, (mini_x - 10, mini_y - 6), pupil_size)
                pygame.draw.circle(screen, WHITE, (mini_x + 10, mini_y - 6), eye_size)
                pygame.draw.circle(screen, BLACK, (mini_x + 10, mini_y - 6), pupil_size)

                bubble1_rect = pygame.Rect(panel1_rect.x + 60, panel1_rect.y + 30, 230, 60)
                pygame.draw.ellipse(screen, WHITE, bubble1_rect)
                pygame.draw.ellipse(screen, BLACK, bubble1_rect, 3)
                great_text = small_font.render("You're doing great!", True, BLACK)
                screen.blit(great_text, (bubble1_rect.centerx - great_text.get_width()//2, bubble1_rect.centery - great_text.get_height()//2))

                # Panel 2
                panel2_rect = pygame.Rect(420, 80, 350, 220)
                pygame.draw.rect(screen, (255, 240, 200), panel2_rect)
                pygame.draw.rect(screen, BLACK, panel2_rect, 5)
                draw_blob_with_cape(panel2_rect.centerx, panel2_rect.centery + 30, 45, player_color)

                bubble2_rect = pygame.Rect(panel2_rect.x + 50, panel2_rect.y + 20, 250, 60)
                pygame.draw.ellipse(screen, WHITE, bubble2_rect)
                pygame.draw.ellipse(screen, BLACK, bubble2_rect, 3)
                wont_text = small_font.render("I won't give up!", True, BLACK)
                screen.blit(wont_text, (bubble2_rect.centerx - wont_text.get_width()//2, bubble2_rect.centery - wont_text.get_height()//2))

            elif comic_variant == 5:
                # Village Comic 6: "Look at that boss house!" / "I can do this!"
                panel1_rect = pygame.Rect(30, 80, 350, 220)
                pygame.draw.rect(screen, (180, 200, 220), panel1_rect)
                pygame.draw.rect(screen, BLACK, panel1_rect, 5)

                # Big boss house - cleaner design
                hx = panel1_rect.centerx - 45
                hy = panel1_rect.y + 90
                # House body
                pygame.draw.rect(screen, (139, 69, 19), (hx, hy, 90, 110))
                pygame.draw.rect(screen, BLACK, (hx, hy, 90, 110), 4)
                # Big red roof with clean lines
                roof = [(hx - 12, hy), (hx + 45, hy - 45), (hx + 102, hy)]
                pygame.draw.polygon(screen, (180, 0, 0), roof)
                pygame.draw.polygon(screen, BLACK, roof, 4)
                # Door
                pygame.draw.rect(screen, (101, 67, 33), (hx + 30, hy + 60, 30, 50))
                pygame.draw.rect(screen, BLACK, (hx + 30, hy + 60, 30, 50), 3)
                # Windows
                for row in range(2):
                    for col in range(2):
                        wx = hx + 12 + col * 45
                        wy = hy + 20 + row * 35
                        pygame.draw.rect(screen, (255, 255, 200), (wx, wy, 20, 20))
                        pygame.draw.rect(screen, BLACK, (wx, wy, 20, 20), 2)

                bubble1_rect = pygame.Rect(panel1_rect.x + 40, panel1_rect.y + 20, 270, 50)
                pygame.draw.ellipse(screen, WHITE, bubble1_rect)
                pygame.draw.ellipse(screen, BLACK, bubble1_rect, 3)
                boss_text = tiny_font.render("Look at that boss house!", True, BLACK)
                screen.blit(boss_text, (bubble1_rect.centerx - boss_text.get_width()//2, bubble1_rect.centery - boss_text.get_height()//2))

                # Panel 2
                panel2_rect = pygame.Rect(420, 80, 350, 220)
                pygame.draw.rect(screen, (255, 250, 200), panel2_rect)
                pygame.draw.rect(screen, BLACK, panel2_rect, 5)
                draw_blob_with_cape(panel2_rect.centerx, panel2_rect.centery + 30, 45, player_color)

                bubble2_rect = pygame.Rect(panel2_rect.x + 50, panel2_rect.y + 20, 250, 60)
                pygame.draw.ellipse(screen, WHITE, bubble2_rect)
                pygame.draw.ellipse(screen, BLACK, bubble2_rect, 3)
                can_text = small_font.render("I can do this!", True, BLACK)
                screen.blit(can_text, (bubble2_rect.centerx - can_text.get_width()//2, bubble2_rect.centery - can_text.get_height()//2))

            elif comic_variant == 6:
                # Village Comic 7: "More blobs to save!" / "Let's go!"
                panel1_rect = pygame.Rect(30, 80, 350, 220)
                pygame.draw.rect(screen, (200, 255, 200), panel1_rect)
                pygame.draw.rect(screen, BLACK, panel1_rect, 5)

                # Multiple mini blobs scattered
                blob_positions = [(100, 130), (160, 150), (220, 140), (280, 135)]
                for bx, by in blob_positions:
                    mini_x = panel1_rect.x + bx
                    mini_y = panel1_rect.y + by
                    pygame.draw.circle(screen, PURPLE, (mini_x, mini_y), 15)
                    pygame.draw.circle(screen, BLACK, (mini_x, mini_y), 15, 2)
                    # Eyes
                    eye_size = 4
                    pupil_size = 2
                    pygame.draw.circle(screen, WHITE, (mini_x - 6, mini_y - 4), eye_size)
                    pygame.draw.circle(screen, BLACK, (mini_x - 6, mini_y - 4), pupil_size)
                    pygame.draw.circle(screen, WHITE, (mini_x + 6, mini_y - 4), eye_size)
                    pygame.draw.circle(screen, BLACK, (mini_x + 6, mini_y - 4), pupil_size)

                bubble1_rect = pygame.Rect(panel1_rect.x + 40, panel1_rect.y + 20, 270, 50)
                pygame.draw.ellipse(screen, WHITE, bubble1_rect)
                pygame.draw.ellipse(screen, BLACK, bubble1_rect, 3)
                more_text = tiny_font.render("More blobs to save!", True, BLACK)
                screen.blit(more_text, (bubble1_rect.centerx - more_text.get_width()//2, bubble1_rect.centery - more_text.get_height()//2))

                # Panel 2
                panel2_rect = pygame.Rect(420, 80, 350, 220)
                pygame.draw.rect(screen, (255, 255, 220), panel2_rect)
                pygame.draw.rect(screen, BLACK, panel2_rect, 5)
                draw_blob_with_cape(panel2_rect.centerx, panel2_rect.centery + 30, 45, player_color)

                bubble2_rect = pygame.Rect(panel2_rect.x + 50, panel2_rect.y + 20, 250, 60)
                pygame.draw.ellipse(screen, WHITE, bubble2_rect)
                pygame.draw.ellipse(screen, BLACK, bubble2_rect, 3)
                go_text = small_font.render("Let's go!", True, BLACK)
                screen.blit(go_text, (bubble2_rect.centerx - go_text.get_width()//2, bubble2_rect.centery - go_text.get_height()//2))

            elif comic_variant == 7:
                # Village Comic 8: "The countryside is beautiful!" / "And worth protecting!"
                panel1_rect = pygame.Rect(30, 80, 350, 220)
                pygame.draw.rect(screen, (160, 220, 160), panel1_rect)
                pygame.draw.rect(screen, BLACK, panel1_rect, 5)

                # Draw beautiful countryside - cleaner trees and flowers
                for i in range(3):
                    tx = panel1_rect.x + 70 + i * 100
                    ty = panel1_rect.y + 145
                    # Tree trunk
                    pygame.draw.rect(screen, (101, 67, 33), (tx, ty, 18, 45))
                    pygame.draw.rect(screen, BLACK, (tx, ty, 18, 45), 2)
                    # Tree foliage - layered circles for depth
                    pygame.draw.circle(screen, (34, 139, 34), (tx + 9, ty - 5), 28)
                    pygame.draw.circle(screen, (44, 149, 44), (tx + 9, ty - 5), 22)
                    pygame.draw.circle(screen, BLACK, (tx + 9, ty - 5), 28, 3)

                # Flowers with stems
                for i in range(5):
                    fx = panel1_rect.x + 55 + i * 60
                    fy = panel1_rect.y + 185
                    # Stem
                    pygame.draw.line(screen, (34, 139, 34), (fx, fy - 10), (fx, fy + 5), 3)
                    # Flower petals
                    pygame.draw.circle(screen, (255, 100, 150), (fx, fy - 10), 8)
                    pygame.draw.circle(screen, BLACK, (fx, fy - 10), 8, 2)
                    # Center
                    pygame.draw.circle(screen, (255, 200, 0), (fx, fy - 10), 3)

                bubble1_rect = pygame.Rect(panel1_rect.x + 30, panel1_rect.y + 20, 290, 60)
                pygame.draw.ellipse(screen, WHITE, bubble1_rect)
                pygame.draw.ellipse(screen, BLACK, bubble1_rect, 3)
                beautiful_text1 = tiny_font.render("The countryside is", True, BLACK)
                beautiful_text2 = tiny_font.render("beautiful!", True, BLACK)
                screen.blit(beautiful_text1, (bubble1_rect.centerx - beautiful_text1.get_width()//2, bubble1_rect.centery - 15))
                screen.blit(beautiful_text2, (bubble1_rect.centerx - beautiful_text2.get_width()//2, bubble1_rect.centery + 10))

                # Panel 2
                panel2_rect = pygame.Rect(420, 80, 350, 220)
                pygame.draw.rect(screen, (255, 240, 220), panel2_rect)
                pygame.draw.rect(screen, BLACK, panel2_rect, 5)
                draw_blob_with_cape(panel2_rect.centerx, panel2_rect.centery + 30, 45, player_color)

                bubble2_rect = pygame.Rect(panel2_rect.x + 50, panel2_rect.y + 20, 250, 60)
                pygame.draw.ellipse(screen, WHITE, bubble2_rect)
                pygame.draw.ellipse(screen, BLACK, bubble2_rect, 3)
                worth_text1 = tiny_font.render("And worth", True, BLACK)
                worth_text2 = tiny_font.render("protecting!", True, BLACK)
                screen.blit(worth_text1, (bubble2_rect.centerx - worth_text1.get_width()//2, bubble2_rect.centery - 15))
                screen.blit(worth_text2, (bubble2_rect.centerx - worth_text2.get_width()//2, bubble2_rect.centery + 10))

        elif comic_variant == 0:
            # Comic 1: Classic "Help us!" / "I've got to save these blobs!"
            # Panel 1 (Top Left) - Mini blobs crying for help
            panel1_rect = pygame.Rect(30, 80, 350, 220)
            pygame.draw.rect(screen, WHITE, panel1_rect)
            pygame.draw.rect(screen, BLACK, panel1_rect, 5)

            for i in range(3):
                mini_x = panel1_rect.x + 80 + i * 80
                mini_y = panel1_rect.y + 120
                pygame.draw.circle(screen, PURPLE, (mini_x, mini_y), 20)
                pygame.draw.circle(screen, BLACK, (mini_x, mini_y), 20, 2)
                # Eyes like in the game (bigger)
                eye_size = 5
                pupil_size = 3
                eye_y_offset = -5
                # Left eye
                pygame.draw.circle(screen, WHITE, (mini_x - 8, mini_y + eye_y_offset), eye_size)
                pygame.draw.circle(screen, BLACK, (mini_x - 8, mini_y + eye_y_offset), pupil_size)
                # Right eye
                pygame.draw.circle(screen, WHITE, (mini_x + 8, mini_y + eye_y_offset), eye_size)
                pygame.draw.circle(screen, BLACK, (mini_x + 8, mini_y + eye_y_offset), pupil_size)

            bubble1_rect = pygame.Rect(panel1_rect.x + 50, panel1_rect.y + 30, 250, 60)
            pygame.draw.ellipse(screen, WHITE, bubble1_rect)
            pygame.draw.ellipse(screen, BLACK, bubble1_rect, 3)
            tail_points = [(bubble1_rect.centerx - 20, bubble1_rect.bottom),
                          (bubble1_rect.centerx - 10, bubble1_rect.bottom + 15),
                          (bubble1_rect.centerx, bubble1_rect.bottom)]
            pygame.draw.polygon(screen, WHITE, tail_points)
            pygame.draw.polygon(screen, BLACK, tail_points, 3)
            help_text = small_font.render("HELP US!", True, BLACK)
            screen.blit(help_text, (bubble1_rect.centerx - help_text.get_width()//2,
                                    bubble1_rect.centery - help_text.get_height()//2))

            # Panel 2 (Top Right)
            panel2_rect = pygame.Rect(420, 80, 350, 220)
            pygame.draw.rect(screen, WHITE, panel2_rect)
            pygame.draw.rect(screen, BLACK, panel2_rect, 5)
            draw_blob_with_cape(panel2_rect.centerx, panel2_rect.centery + 20, 40, player_color)

            bubble2_rect = pygame.Rect(panel2_rect.x + 50, panel2_rect.y + 20, 250, 70)
            pygame.draw.ellipse(screen, WHITE, bubble2_rect)
            pygame.draw.ellipse(screen, BLACK, bubble2_rect, 3)
            tail2_points = [(bubble2_rect.centerx, bubble2_rect.bottom),
                           (bubble2_rect.centerx + 10, bubble2_rect.bottom + 20),
                           (bubble2_rect.centerx + 20, bubble2_rect.bottom)]
            pygame.draw.polygon(screen, WHITE, tail2_points)
            pygame.draw.polygon(screen, BLACK, tail2_points, 3)
            save_text1 = tiny_font.render("I've got to save", True, BLACK)
            save_text2 = tiny_font.render("these blobs!", True, BLACK)
            screen.blit(save_text1, (bubble2_rect.centerx - save_text1.get_width()//2, bubble2_rect.centery - 15))
            screen.blit(save_text2, (bubble2_rect.centerx - save_text2.get_width()//2, bubble2_rect.centery + 10))

        elif comic_variant == 1:
            # Comic 2: "There's so many buildings!" / "I can do this!"
            # Panel 1 - Buildings looming
            panel1_rect = pygame.Rect(30, 80, 350, 220)
            pygame.draw.rect(screen, (200, 220, 255), panel1_rect)
            pygame.draw.rect(screen, BLACK, panel1_rect, 5)

            # Draw threatening buildings with windows
            for i in range(3):
                bx = panel1_rect.x + 60 + i * 100
                by = panel1_rect.y + 60
                pygame.draw.rect(screen, (80, 80, 80), (bx, by, 50, 140))
                pygame.draw.rect(screen, BLACK, (bx, by, 50, 140), 2)
                # Add windows
                for row in range(5):
                    for col in range(2):
                        wx = bx + 8 + col * 20
                        wy = by + 15 + row * 25
                        pygame.draw.rect(screen, (255, 255, 150), (wx, wy, 12, 10))
                        pygame.draw.rect(screen, BLACK, (wx, wy, 12, 10), 1)

            bubble1_rect = pygame.Rect(panel1_rect.x + 40, panel1_rect.y + 20, 270, 50)
            pygame.draw.ellipse(screen, WHITE, bubble1_rect)
            pygame.draw.ellipse(screen, BLACK, bubble1_rect, 3)
            worry_text = tiny_font.render("There's so many buildings!", True, BLACK)
            screen.blit(worry_text, (bubble1_rect.centerx - worry_text.get_width()//2, bubble1_rect.centery - worry_text.get_height()//2))

            # Panel 2 - Super Blob determined
            panel2_rect = pygame.Rect(420, 80, 350, 220)
            pygame.draw.rect(screen, (255, 255, 200), panel2_rect)
            pygame.draw.rect(screen, BLACK, panel2_rect, 5)
            draw_blob_with_cape(panel2_rect.centerx, panel2_rect.centery + 30, 45, player_color)

            bubble2_rect = pygame.Rect(panel2_rect.x + 50, panel2_rect.y + 20, 250, 60)
            pygame.draw.ellipse(screen, WHITE, bubble2_rect)
            pygame.draw.ellipse(screen, BLACK, bubble2_rect, 3)
            tail2_points = [(bubble2_rect.centerx, bubble2_rect.bottom),
                           (bubble2_rect.centerx, bubble2_rect.bottom + 25),
                           (bubble2_rect.centerx + 15, bubble2_rect.bottom)]
            pygame.draw.polygon(screen, WHITE, tail2_points)
            pygame.draw.polygon(screen, BLACK, tail2_points, 3)
            confidence_text = small_font.render("I can do this!", True, BLACK)
            screen.blit(confidence_text, (bubble2_rect.centerx - confidence_text.get_width()//2, bubble2_rect.centery - confidence_text.get_height()//2))

        elif comic_variant == 2:
            # Comic 3: "The city needs me!" / "POW!"
            # Panel 1 - Super Blob flying
            panel1_rect = pygame.Rect(30, 80, 350, 220)
            pygame.draw.rect(screen, (135, 206, 250), panel1_rect)
            pygame.draw.rect(screen, BLACK, panel1_rect, 5)

            # Draw background buildings for city
            bg_buildings = [
                (panel1_rect.x + 20, panel1_rect.y + 170, 40, 100),
                (panel1_rect.x + 75, panel1_rect.y + 140, 35, 130),
                (panel1_rect.x + 300, panel1_rect.y + 160, 45, 110)
            ]
            for bx, by, bw, bh in bg_buildings:
                pygame.draw.rect(screen, (100, 100, 120), (bx, by, bw, bh))
                pygame.draw.rect(screen, BLACK, (bx, by, bw, bh), 2)
                # Windows
                for row in range(int(bh / 20)):
                    for col in range(2):
                        wx = bx + 5 + col * (bw - 15)
                        wy = by + 8 + row * 20
                        if wy + 8 < by + bh:
                            pygame.draw.rect(screen, (180, 180, 100), (wx, wy, 8, 8))

            # Draw motion lines
            for i in range(5):
                y_pos = panel1_rect.y + 40 + i * 30
                pygame.draw.line(screen, WHITE, (panel1_rect.x + 120, y_pos), (panel1_rect.x + 200, y_pos), 3)

            draw_blob_with_cape(panel1_rect.x + 250, panel1_rect.y + 130, 40, player_color)

            bubble1_rect = pygame.Rect(panel1_rect.x + 40, panel1_rect.y + 30, 250, 60)
            pygame.draw.ellipse(screen, WHITE, bubble1_rect)
            pygame.draw.ellipse(screen, BLACK, bubble1_rect, 3)
            tail_points = [(bubble1_rect.centerx + 80, bubble1_rect.bottom - 10),
                          (bubble1_rect.centerx + 110, bubble1_rect.bottom + 30),
                          (bubble1_rect.centerx + 90, bubble1_rect.bottom)]
            pygame.draw.polygon(screen, WHITE, tail_points)
            pygame.draw.polygon(screen, BLACK, tail_points, 3)
            city_text = small_font.render("The city needs me!", True, BLACK)
            screen.blit(city_text, (bubble1_rect.centerx - city_text.get_width()//2, bubble1_rect.centery - city_text.get_height()//2))

            # Panel 2 - Action impact
            panel2_rect = pygame.Rect(420, 80, 350, 220)
            pygame.draw.rect(screen, ORANGE, panel2_rect)
            pygame.draw.rect(screen, BLACK, panel2_rect, 5)

            # Draw impact starburst
            for i in range(8):
                angle = i * 45
                import math
                x_end = panel2_rect.centerx + math.cos(math.radians(angle)) * 100
                y_end = panel2_rect.centery + math.sin(math.radians(angle)) * 80
                pygame.draw.line(screen, YELLOW, (panel2_rect.centerx, panel2_rect.centery), (x_end, y_end), 5)

            pow_text = font.render("POW!", True, RED)
            screen.blit(pow_text, (panel2_rect.centerx - pow_text.get_width()//2, panel2_rect.centery - pow_text.get_height()//2))

        elif comic_variant == 3:
            # Comic 4: Mini blob "Thank you!" / Super Blob "All in a day's work!"
            # Panel 1 - Rescued mini blobs happy
            panel1_rect = pygame.Rect(30, 80, 350, 220)
            pygame.draw.rect(screen, (255, 240, 245), panel1_rect)
            pygame.draw.rect(screen, BLACK, panel1_rect, 5)

            for i in range(3):
                mini_x = panel1_rect.x + 80 + i * 80
                mini_y = panel1_rect.y + 130
                pygame.draw.circle(screen, PURPLE, (mini_x, mini_y), 20)
                pygame.draw.circle(screen, BLACK, (mini_x, mini_y), 20, 2)
                # Eyes like in the game (bigger)
                eye_size = 5
                pupil_size = 3
                eye_y_offset = -5
                # Left eye
                pygame.draw.circle(screen, WHITE, (mini_x - 8, mini_y + eye_y_offset), eye_size)
                pygame.draw.circle(screen, BLACK, (mini_x - 8, mini_y + eye_y_offset), pupil_size)
                # Right eye
                pygame.draw.circle(screen, WHITE, (mini_x + 8, mini_y + eye_y_offset), eye_size)
                pygame.draw.circle(screen, BLACK, (mini_x + 8, mini_y + eye_y_offset), pupil_size)

            bubble1_rect = pygame.Rect(panel1_rect.x + 50, panel1_rect.y + 25, 250, 65)
            pygame.draw.ellipse(screen, WHITE, bubble1_rect)
            pygame.draw.ellipse(screen, BLACK, bubble1_rect, 3)
            tail_points = [(bubble1_rect.centerx, bubble1_rect.bottom),
                          (bubble1_rect.centerx - 5, bubble1_rect.bottom + 20),
                          (bubble1_rect.centerx + 10, bubble1_rect.bottom)]
            pygame.draw.polygon(screen, WHITE, tail_points)
            pygame.draw.polygon(screen, BLACK, tail_points, 3)
            thank_text1 = tiny_font.render("Thank you,", True, BLACK)
            thank_text2 = tiny_font.render("Super Blob!", True, BLACK)
            screen.blit(thank_text1, (bubble1_rect.centerx - thank_text1.get_width()//2, bubble1_rect.centery - 15))
            screen.blit(thank_text2, (bubble1_rect.centerx - thank_text2.get_width()//2, bubble1_rect.centery + 10))

            # Panel 2 - Super Blob heroic pose
            panel2_rect = pygame.Rect(420, 80, 350, 220)
            pygame.draw.rect(screen, (255, 235, 200), panel2_rect)
            pygame.draw.rect(screen, BLACK, panel2_rect, 5)
            draw_blob_with_cape(panel2_rect.centerx, panel2_rect.centery + 30, 42, player_color)

            bubble2_rect = pygame.Rect(panel2_rect.x + 40, panel2_rect.y + 20, 270, 65)
            pygame.draw.ellipse(screen, WHITE, bubble2_rect)
            pygame.draw.ellipse(screen, BLACK, bubble2_rect, 3)
            tail2_points = [(bubble2_rect.centerx, bubble2_rect.bottom),
                           (bubble2_rect.centerx + 5, bubble2_rect.bottom + 20),
                           (bubble2_rect.centerx + 15, bubble2_rect.bottom)]
            pygame.draw.polygon(screen, WHITE, tail2_points)
            pygame.draw.polygon(screen, BLACK, tail2_points, 3)
            hero_text1 = tiny_font.render("All in a", True, BLACK)
            hero_text2 = tiny_font.render("day's work!", True, BLACK)
            screen.blit(hero_text1, (bubble2_rect.centerx - hero_text1.get_width()//2, bubble2_rect.centery - 15))
            screen.blit(hero_text2, (bubble2_rect.centerx - hero_text2.get_width()//2, bubble2_rect.centery + 10))

        elif comic_variant == 4:
            # Comic 5: Mini blobs cheering / Super Blob smiling
            # Panel 1 - Mini blobs cheering
            panel1_rect = pygame.Rect(30, 80, 350, 220)
            pygame.draw.rect(screen, (255, 250, 230), panel1_rect)
            pygame.draw.rect(screen, BLACK, panel1_rect, 5)

            # Draw happy mini blobs
            for i in range(3):
                mini_x = panel1_rect.x + 80 + i * 80
                mini_y = panel1_rect.y + 130
                pygame.draw.circle(screen, PURPLE, (mini_x, mini_y), 18)
                pygame.draw.circle(screen, BLACK, (mini_x, mini_y), 18, 2)
                # Eyes like in the game (bigger)
                eye_size = 5
                pupil_size = 3
                eye_y_offset = -4
                # Left eye
                pygame.draw.circle(screen, WHITE, (mini_x - 7, mini_y + eye_y_offset), eye_size)
                pygame.draw.circle(screen, BLACK, (mini_x - 7, mini_y + eye_y_offset), pupil_size)
                # Right eye
                pygame.draw.circle(screen, WHITE, (mini_x + 7, mini_y + eye_y_offset), eye_size)
                pygame.draw.circle(screen, BLACK, (mini_x + 7, mini_y + eye_y_offset), pupil_size)

            bubble1_rect = pygame.Rect(panel1_rect.x + 60, panel1_rect.y + 30, 230, 60)
            pygame.draw.ellipse(screen, WHITE, bubble1_rect)
            pygame.draw.ellipse(screen, BLACK, bubble1_rect, 3)
            tail_points = [(bubble1_rect.centerx, bubble1_rect.bottom),
                          (bubble1_rect.centerx - 5, bubble1_rect.bottom + 15),
                          (bubble1_rect.centerx + 10, bubble1_rect.bottom)]
            pygame.draw.polygon(screen, WHITE, tail_points)
            pygame.draw.polygon(screen, BLACK, tail_points, 3)
            cheer_text1 = tiny_font.render("You're doing", True, BLACK)
            cheer_text2 = tiny_font.render("great!", True, BLACK)
            screen.blit(cheer_text1, (bubble1_rect.centerx - cheer_text1.get_width()//2, bubble1_rect.centery - 15))
            screen.blit(cheer_text2, (bubble1_rect.centerx - cheer_text2.get_width()//2, bubble1_rect.centery + 10))

            # Panel 2 - Super Blob happy
            panel2_rect = pygame.Rect(420, 80, 350, 220)
            pygame.draw.rect(screen, (230, 255, 230), panel2_rect)
            pygame.draw.rect(screen, BLACK, panel2_rect, 5)
            draw_blob_with_cape(panel2_rect.centerx, panel2_rect.centery + 25, 45, player_color)

            bubble2_rect = pygame.Rect(panel2_rect.x + 60, panel2_rect.y + 25, 230, 60)
            pygame.draw.ellipse(screen, WHITE, bubble2_rect)
            pygame.draw.ellipse(screen, BLACK, bubble2_rect, 3)
            tail2_points = [(bubble2_rect.centerx, bubble2_rect.bottom),
                           (bubble2_rect.centerx + 5, bubble2_rect.bottom + 20),
                           (bubble2_rect.centerx + 15, bubble2_rect.bottom)]
            pygame.draw.polygon(screen, WHITE, tail2_points)
            pygame.draw.polygon(screen, BLACK, tail2_points, 3)
            happy_text1 = tiny_font.render("Thanks for", True, BLACK)
            happy_text2 = tiny_font.render("believing in me!", True, BLACK)
            screen.blit(happy_text1, (bubble2_rect.centerx - happy_text1.get_width()//2, bubble2_rect.centery - 15))
            screen.blit(happy_text2, (bubble2_rect.centerx - happy_text2.get_width()//2, bubble2_rect.centery + 10))

        elif comic_variant == 5:
            # Comic 6: "Look at that boss!" / "I can smash it!"
            # Panel 1 - Looking at golden boss building
            panel1_rect = pygame.Rect(30, 80, 350, 220)
            pygame.draw.rect(screen, (220, 240, 255), panel1_rect)
            pygame.draw.rect(screen, BLACK, panel1_rect, 5)

            # Draw golden boss building with details
            boss_x = panel1_rect.x + 240
            boss_y = panel1_rect.y + 80
            pygame.draw.rect(screen, GOLD, (boss_x, boss_y, 70, 120))
            # Gold accent sides for depth
            pygame.draw.rect(screen, (200, 170, 0), (boss_x, boss_y, 7, 120))
            pygame.draw.rect(screen, (200, 170, 0), (boss_x + 63, boss_y, 7, 120))
            pygame.draw.rect(screen, BLACK, (boss_x, boss_y, 70, 120), 3)
            # Windows on boss with borders
            for row in range(4):
                for col in range(2):
                    wx = boss_x + 12 + col * 28
                    wy = boss_y + 15 + row * 26
                    pygame.draw.rect(screen, (255, 255, 200), (wx, wy, 16, 14))
                    pygame.draw.rect(screen, BLACK, (wx, wy, 16, 14), 1)

            draw_blob_with_cape(panel1_rect.x + 100, panel1_rect.y + 150, 35, player_color)

            bubble1_rect = pygame.Rect(panel1_rect.x + 40, panel1_rect.y + 30, 240, 60)
            pygame.draw.ellipse(screen, WHITE, bubble1_rect)
            pygame.draw.ellipse(screen, BLACK, bubble1_rect, 3)
            tail_points = [(bubble1_rect.centerx + 20, bubble1_rect.bottom),
                          (bubble1_rect.centerx + 10, bubble1_rect.bottom + 30),
                          (bubble1_rect.centerx + 30, bubble1_rect.bottom)]
            pygame.draw.polygon(screen, WHITE, tail_points)
            pygame.draw.polygon(screen, BLACK, tail_points, 3)
            look_text1 = tiny_font.render("Look at that", True, BLACK)
            look_text2 = tiny_font.render("golden boss!", True, BLACK)
            screen.blit(look_text1, (bubble1_rect.centerx - look_text1.get_width()//2, bubble1_rect.centery - 15))
            screen.blit(look_text2, (bubble1_rect.centerx - look_text2.get_width()//2, bubble1_rect.centery + 10))

            # Panel 2 - Super Blob determined
            panel2_rect = pygame.Rect(420, 80, 350, 220)
            pygame.draw.rect(screen, (255, 240, 200), panel2_rect)
            pygame.draw.rect(screen, BLACK, panel2_rect, 5)
            draw_blob_with_cape(panel2_rect.centerx, panel2_rect.centery + 30, 50, player_color)

            bubble2_rect = pygame.Rect(panel2_rect.x + 70, panel2_rect.y + 25, 210, 60)
            pygame.draw.ellipse(screen, WHITE, bubble2_rect)
            pygame.draw.ellipse(screen, BLACK, bubble2_rect, 3)
            tail2_points = [(bubble2_rect.centerx, bubble2_rect.bottom),
                           (bubble2_rect.centerx - 10, bubble2_rect.bottom + 20),
                           (bubble2_rect.centerx + 5, bubble2_rect.bottom)]
            pygame.draw.polygon(screen, WHITE, tail2_points)
            pygame.draw.polygon(screen, BLACK, tail2_points, 3)
            smash_text1 = tiny_font.render("I can", True, BLACK)
            smash_text2 = tiny_font.render("smash it!", True, BLACK)
            screen.blit(smash_text1, (bubble2_rect.centerx - smash_text1.get_width()//2, bubble2_rect.centery - 15))
            screen.blit(smash_text2, (bubble2_rect.centerx - smash_text2.get_width()//2, bubble2_rect.centery + 10))

        elif comic_variant == 6:
            # Comic 7: "More blobs to save!" / "Let's go!"
            # Panel 1 - Mini blobs in danger
            panel1_rect = pygame.Rect(30, 80, 350, 220)
            pygame.draw.rect(screen, (255, 240, 240), panel1_rect)
            pygame.draw.rect(screen, BLACK, panel1_rect, 5)

            # Draw mini blobs looking worried
            for i in range(4):
                mini_x = panel1_rect.x + 60 + i * 70
                mini_y = panel1_rect.y + 140
                pygame.draw.circle(screen, PURPLE, (mini_x, mini_y), 16)
                pygame.draw.circle(screen, BLACK, (mini_x, mini_y), 16, 2)
                # Eyes like in the game (bigger)
                eye_size = 4
                pupil_size = 3
                eye_y_offset = -4
                # Left eye
                pygame.draw.circle(screen, WHITE, (mini_x - 6, mini_y + eye_y_offset), eye_size)
                pygame.draw.circle(screen, BLACK, (mini_x - 6, mini_y + eye_y_offset), pupil_size)
                # Right eye
                pygame.draw.circle(screen, WHITE, (mini_x + 6, mini_y + eye_y_offset), eye_size)
                pygame.draw.circle(screen, BLACK, (mini_x + 6, mini_y + eye_y_offset), pupil_size)

            bubble1_rect = pygame.Rect(panel1_rect.x + 50, panel1_rect.y + 30, 250, 65)
            pygame.draw.ellipse(screen, WHITE, bubble1_rect)
            pygame.draw.ellipse(screen, BLACK, bubble1_rect, 3)
            tail_points = [(bubble1_rect.centerx, bubble1_rect.bottom),
                          (bubble1_rect.centerx - 5, bubble1_rect.bottom + 20),
                          (bubble1_rect.centerx + 10, bubble1_rect.bottom)]
            pygame.draw.polygon(screen, WHITE, tail_points)
            pygame.draw.polygon(screen, BLACK, tail_points, 3)
            danger_text1 = tiny_font.render("More blobs", True, BLACK)
            danger_text2 = tiny_font.render("need saving!", True, BLACK)
            screen.blit(danger_text1, (bubble1_rect.centerx - danger_text1.get_width()//2, bubble1_rect.centery - 15))
            screen.blit(danger_text2, (bubble1_rect.centerx - danger_text2.get_width()//2, bubble1_rect.centery + 10))

            # Panel 2 - Super Blob ready!
            panel2_rect = pygame.Rect(420, 80, 350, 220)
            pygame.draw.rect(screen, (240, 255, 255), panel2_rect)
            pygame.draw.rect(screen, BLACK, panel2_rect, 5)
            draw_blob_with_cape(panel2_rect.centerx, panel2_rect.centery + 30, 48, player_color)

            bubble2_rect = pygame.Rect(panel2_rect.x + 80, panel2_rect.y + 25, 190, 60)
            pygame.draw.ellipse(screen, WHITE, bubble2_rect)
            pygame.draw.ellipse(screen, BLACK, bubble2_rect, 3)
            tail2_points = [(bubble2_rect.centerx, bubble2_rect.bottom),
                           (bubble2_rect.centerx, bubble2_rect.bottom + 20),
                           (bubble2_rect.centerx + 15, bubble2_rect.bottom)]
            pygame.draw.polygon(screen, WHITE, tail2_points)
            pygame.draw.polygon(screen, BLACK, tail2_points, 3)
            lets_text = small_font.render("Let's go!", True, BLACK)
            screen.blit(lets_text, (bubble2_rect.centerx - lets_text.get_width()//2, bubble2_rect.centery - lets_text.get_height()//2))

        else:  # comic_variant == 7
            # Comic 8: "Keep going!" / "We believe in you!"
            # Panel 1 - Super Blob flying with energy
            panel1_rect = pygame.Rect(30, 80, 350, 220)
            pygame.draw.rect(screen, (245, 245, 255), panel1_rect)
            pygame.draw.rect(screen, BLACK, panel1_rect, 5)

            # Draw motion lines
            for i in range(5):
                y_pos = panel1_rect.y + 50 + i * 30
                line_len = 100 + i * 10
                pygame.draw.line(screen, (220, 220, 220), (panel1_rect.x + 30, y_pos), (panel1_rect.x + 30 + line_len, y_pos), 3)

            draw_blob_with_cape(panel1_rect.x + 220, panel1_rect.y + 130, 42, player_color)

            bubble1_rect = pygame.Rect(panel1_rect.x + 40, panel1_rect.y + 30, 220, 55)
            pygame.draw.ellipse(screen, WHITE, bubble1_rect)
            pygame.draw.ellipse(screen, BLACK, bubble1_rect, 3)
            tail_points = [(bubble1_rect.centerx + 60, bubble1_rect.bottom - 5),
                          (bubble1_rect.centerx + 90, bubble1_rect.bottom + 25),
                          (bubble1_rect.centerx + 70, bubble1_rect.bottom + 5)]
            pygame.draw.polygon(screen, WHITE, tail_points)
            pygame.draw.polygon(screen, BLACK, tail_points, 3)
            keep_text = small_font.render("Keep going!", True, BLACK)
            screen.blit(keep_text, (bubble1_rect.centerx - keep_text.get_width()//2, bubble1_rect.centery - keep_text.get_height()//2))

            # Panel 2 - Mini blobs cheering
            panel2_rect = pygame.Rect(420, 80, 350, 220)
            pygame.draw.rect(screen, (255, 250, 245), panel2_rect)
            pygame.draw.rect(screen, BLACK, panel2_rect, 5)

            # Draw cheering mini blobs
            for i in range(3):
                mini_x = panel2_rect.x + 90 + i * 70
                mini_y = panel2_rect.y + 140
                pygame.draw.circle(screen, PURPLE, (mini_x, mini_y), 18)
                pygame.draw.circle(screen, BLACK, (mini_x, mini_y), 18, 2)
                # Eyes like in the game (bigger)
                eye_size = 5
                pupil_size = 3
                eye_y_offset = -4
                # Left eye
                pygame.draw.circle(screen, WHITE, (mini_x - 7, mini_y + eye_y_offset), eye_size)
                pygame.draw.circle(screen, BLACK, (mini_x - 7, mini_y + eye_y_offset), pupil_size)
                # Right eye
                pygame.draw.circle(screen, WHITE, (mini_x + 7, mini_y + eye_y_offset), eye_size)
                pygame.draw.circle(screen, BLACK, (mini_x + 7, mini_y + eye_y_offset), pupil_size)

            bubble2_rect = pygame.Rect(panel2_rect.x + 60, panel2_rect.y + 25, 230, 65)
            pygame.draw.ellipse(screen, WHITE, bubble2_rect)
            pygame.draw.ellipse(screen, BLACK, bubble2_rect, 3)
            tail2_points = [(bubble2_rect.centerx, bubble2_rect.bottom),
                           (bubble2_rect.centerx - 5, bubble2_rect.bottom + 20),
                           (bubble2_rect.centerx + 10, bubble2_rect.bottom)]
            pygame.draw.polygon(screen, WHITE, tail2_points)
            pygame.draw.polygon(screen, BLACK, tail2_points, 3)
            believe_text1 = tiny_font.render("We believe", True, BLACK)
            believe_text2 = tiny_font.render("in you!", True, BLACK)
            screen.blit(believe_text1, (bubble2_rect.centerx - believe_text1.get_width()//2, bubble2_rect.centery - 15))
            screen.blit(believe_text2, (bubble2_rect.centerx - believe_text2.get_width()//2, bubble2_rect.centery + 10))

        # Panel 3 (Bottom) - Stats panel (same for all variants)
        panel3_rect = pygame.Rect(30, 330, 740, 220)
        pygame.draw.rect(screen, YELLOW, panel3_rect)
        pygame.draw.rect(screen, BLACK, panel3_rect, 5)

        smash_text = font.render("SMASH!", True, RED)
        screen.blit(smash_text, (panel3_rect.centerx - smash_text.get_width()//2, panel3_rect.y + 30))

        level_complete = small_font.render(f"Level {level} Complete!", True, BLACK)
        rescued_text = tiny_font.render(f"Total Blobs Rescued: {blobs_rescued}", True, BLACK)
        continue_text = small_font.render("Click to continue...", True, BLACK)

        screen.blit(level_complete, (panel3_rect.centerx - level_complete.get_width()//2, panel3_rect.y + 100))
        screen.blit(rescued_text, (panel3_rect.centerx - rescued_text.get_width()//2, panel3_rect.y + 140))
        screen.blit(continue_text, (panel3_rect.centerx - continue_text.get_width()//2, panel3_rect.y + 180))
    
    elif game_state == "level_failed":
        # Failure screen - restart from level 1
        pygame.draw.rect(screen, RED, (50, 50, WIDTH-100, HEIGHT-100))
        pygame.draw.rect(screen, BLACK, (50, 50, WIDTH-100, HEIGHT-100), 15)

        title = font.render("OUT OF POWER!", True, BLACK)
        subtitle = small_font.render("Restarting from Level 1...", True, BLACK)
        retry = small_font.render("Click to continue...", True, BLACK)

        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 60))
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, HEIGHT//2))
        screen.blit(retry, (WIDTH//2 - retry.get_width()//2, HEIGHT//2 + 60))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()