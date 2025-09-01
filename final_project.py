from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
from OpenGL.GLU import *
from math import radians, cos, sin, atan2, degrees
import random
import time

# Camera variables
fovY = 120
GRID_LENGTH = 600
rand_var = 423

# Game state
player_x = 0.0
player_y = 0.0
player_z = 0.0
player_rotate_z = 0.0
player_speed = 20.0
player_size = 50.0

score = 0
life = 4
game_over = False
game_won = False

# Display settings
dark_mode = False

# Camera controls
cam_theta = 45.0
cam_radius = 800.0
cam_height = 500.0
camera_pos = (0, 500, 500)  

# Treasures
NUM_TREASURES = 5
treasures = []  # list of dictionaries: {'x': , 'y': , 'size': , 'pulse_dir': 1}
TREASURE_BASE_SIZE = player_size * 0.5
TREASURE_PULSE_SPEED = 0.01
LEVEL = 1

# Enemy globals
enemies = []  # list of dicts: {'x': , 'y': , 'size': , 'speed': , 'type': , 'projectile': {...}}
ENEMY_SIZE = player_size * 0.6
ENEMY_BASE_SPEED = 5.0

# Boss globals
boss = None  # dict: {'x': , 'y': , 'size': , 'speed': , 'health': , 'shoot_timer': }
BOSS_SIZE = player_size * 1.0  # Reduced from 2.5 to 2.0
BOSS_SPEED = .4
BOSS_HEALTH = 10
BOSS_SHOOT_COOLDOWN = 60  # frames between shots

# Power-up globals
power_ups = []  # list of dicts: {'x': , 'y': , 'size': , 'type': 'health'|'immortal', 'active': True}
power_up_size = player_size * 0.5
power_up_types = ['health', 'immortal']
power_up_chance = 0.5

# Immortality state
immortal = False
immortal_timer = 0.0
immortal_duration = 50  # seconds

# Projectiles
projectiles = []  # list of dicts: {'x': , 'y': , 'vx': , 'vy': , 'size': , 'active': True, 'source': , 'damage': }
projectile_size = player_size * 0.2
projectile_speed = 15.0

# Timer
level_timer = 120  # seconds per level
timer_start = None

# Traps
traps = []  # list of dicts: {'x': , 'y': , 'size': }
TRAP_SIZE = player_size * 0.8

LEVEL_ENEMY_CONFIG = {
    1: {'num_enemies': 0, 'speed': 0.1, 'projectile_enemies': 0, 'projectile_speed': 0.0},  # Only boss in level 1
    2: {'num_enemies': 1, 'speed': 0.1, 'projectile_enemies': 1, 'projectile_speed': 0.3},
    3: {'num_enemies': 2, 'speed': 0.2, 'projectile_enemies': 2, 'projectile_speed': 0.4},
    4: {'num_enemies': 3, 'speed': 0.5, 'projectile_enemies': 3, 'projectile_speed': 0.6},
    5: {'num_enemies': 4, 'speed': 0.7, 'projectile_enemies': 4, 'projectile_speed': 0.7},
}

# Initial values for restart
INITIAL_PLAYER_X = 0.0
INITIAL_PLAYER_Y = 0.0
INITIAL_PLAYER_Z = 0.0
INITIAL_PLAYER_ROTATE_Z = 0.0
INITIAL_SCORE = 0
INITIAL_LIFE = 3
INITIAL_CAM_THETA = 45.0
INITIAL_CAM_RADIUS = 800.0
INITIAL_CAM_HEIGHT = 500.0
INITIAL_CAMERA_POS = (0, 500, 500)
INITIAL_LEVEL = 1

def restart_game():
    # Reset all game variables
    global player_x, player_y, player_z, player_rotate_z
    global score, life, game_over, game_won
    global cam_theta, cam_radius, cam_height, camera_pos
    global treasures, LEVEL, enemies, power_ups, immortal, immortal_timer, projectiles, timer_start, traps, boss

    # Reset player position and rotation
    player_x = INITIAL_PLAYER_X
    player_y = INITIAL_PLAYER_Y
    player_z = INITIAL_PLAYER_Z
    player_rotate_z = INITIAL_PLAYER_ROTATE_Z

    # Reset game state
    score = INITIAL_SCORE
    life = INITIAL_LIFE
    game_over = False
    game_won = False
    LEVEL = INITIAL_LEVEL
    immortal = False
    immortal_timer = 0.0
    projectiles = []
    traps = []
    boss = None
    timer_start = time.time()

    # Reset camera 
    cam_theta = INITIAL_CAM_THETA
    cam_radius = INITIAL_CAM_RADIUS
    cam_height = INITIAL_CAM_HEIGHT
    camera_pos = INITIAL_CAMERA_POS  

    # Reinitialize treasures, enemies, power-ups, traps
    init_treasures()
    init_enemies()
    init_power_ups()
    init_traps()
    init_boss()


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    gluOrtho2D(0, 1000, 0, 800)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_floor():
    tile_size = 100        
    num_tiles = (GRID_LENGTH * 2) // tile_size  
    half_size = GRID_LENGTH

    for i in range(-half_size, half_size, tile_size):
        for j in range(-half_size, half_size, tile_size):
            # Check if this tile is a trap
            is_trap = False
            for trap in traps:
                trap_tile_x = int(trap['x'] // tile_size) * tile_size
                trap_tile_y = int(trap['y'] // tile_size) * tile_size
                if abs(i - trap_tile_x) < tile_size and abs(j - trap_tile_y) < tile_size:
                    is_trap = True
                    break
            
            if is_trap:
                glColor3f(1.0, 0.0, 0.0)  # Red color for trap tiles
            elif ((i // tile_size) + (j // tile_size)) % 2 == 0:
                if dark_mode:
                    glColor3f(0.2, 0.2, 0.2)  # Dark gray for dark mode
                else:
                    glColor3f(0.8, 0.8, 0.8)  # Light gray for normal mode
            else:
                if dark_mode:
                    glColor3f(0.1, 0.1, 0.1)  # Very dark gray for dark mode
                else:
                    glColor3f(0.3, 0.3, 0.3)  # Dark gray for normal mode

            glBegin(GL_QUADS)
            glVertex3f(i, j, 0)
            glVertex3f(i + tile_size, j, 0)
            glVertex3f(i + tile_size, j + tile_size, 0)
            glVertex3f(i, j + tile_size, 0)
            glEnd()

# --------------------------------------------
def draw_shapes():
    wall_height = 80.0
    wall_thickness = 10.0

    glColor3f(0.0, 0.0, 0.6)
    glPushMatrix()
    glTranslatef(-GRID_LENGTH, 0, wall_height/2)
    glScalef(wall_thickness, GRID_LENGTH*2, wall_height)
    glutSolidCube(1)
    glPopMatrix()

    glColor3f(0.0, 0.0, 0.6)
    glPushMatrix()
    glTranslatef(GRID_LENGTH, 0, wall_height/2)
    glScalef(wall_thickness, GRID_LENGTH*2, wall_height)
    glutSolidCube(1)
    glPopMatrix()

    glColor3f(0.0, 0.0, 0.6)
    glPushMatrix()
    glTranslatef(0, -GRID_LENGTH, wall_height/2)
    glScalef(GRID_LENGTH*2, wall_thickness, wall_height)
    glutSolidCube(1)
    glPopMatrix()

    glColor3f(0.0, 0.0, 0.6)
    glPushMatrix()
    glTranslatef(0, GRID_LENGTH, wall_height/2)
    glScalef(GRID_LENGTH*2, wall_thickness, wall_height)
    glutSolidCube(1)
    glPopMatrix()

# --------------------------------------------
def draw_player():
    global player_x, player_y, player_z, player_rotate_z, player_size
    glPushMatrix()
    glTranslatef(player_x, player_y, player_z)  
    glRotatef(player_rotate_z, 0, 0, 1)

    # Head
    glColor3f(0.9, 0.8, 0.6)
    glPushMatrix()
    glTranslatef(0, 0, player_size * 0.9)  
    glutSolidSphere(player_size * 0.4, 30, 30)  

    # Eyes
    glColor3f(0, 0, 0)
    eye_offset = player_size * 0.15
    eye_z = player_size * 0.05
    eye_depth = player_size * 0.35

    glPushMatrix()
    glTranslatef(-eye_offset, eye_depth, eye_z)
    glutSolidSphere(player_size * 0.07, 10, 10)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(eye_offset, eye_depth, eye_z)
    glutSolidSphere(player_size * 0.07, 10, 10)
    glPopMatrix()
    glPopMatrix()

    # Body
    glColor3f(0.4, 0.7, 0.9)
    glPushMatrix()
    glTranslatef(0, 0, player_size * 0.4)  
    glutSolidSphere(player_size * 0.5, 30, 30)  
    glPopMatrix()

    # Legs
    glColor3f(0.3, 0.3, 0.3)
    glPushMatrix()
    glTranslatef(-player_size * 0.2, 0, 0)  
    glutSolidSphere(player_size * 0.25, 20, 20)  
    glPopMatrix()

    glPushMatrix()
    glTranslatef(player_size * 0.2, 0, 0)  
    glutSolidSphere(player_size * 0.25, 20, 20)  
    glPopMatrix()
    glPopMatrix()

# --------------------------------------------
def draw_boss():
    global boss
    if boss is None:
        return
    
    # Boss body - large intimidating cube
    glColor3f(0.5, 0.0, 0.5)  # Dark purple
    glPushMatrix()
    glTranslatef(boss['x'], boss['y'], boss['size']/2)
    glutSolidCube(boss['size'])
    glPopMatrix()
    
    # Boss head - large black sphere on top
    glColor3f(0.0, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(boss['x'], boss['y'], boss['size'] * 1.2)
    glutSolidSphere(boss['size'] * 0.6, 30, 30)
    glPopMatrix()
    
    # Boss eyes - glowing red
    glColor3f(1.0, 0.0, 0.0)
    eye_offset = boss['size'] * 0.2
    eye_z = boss['size'] * 1.2
    eye_depth = boss['size'] * 0.5
    
    glPushMatrix()
    glTranslatef(boss['x'] - eye_offset, boss['y'] + eye_depth, eye_z)
    glutSolidSphere(boss['size'] * 0.08, 10, 10)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(boss['x'] + eye_offset, boss['y'] + eye_depth, eye_z)
    glutSolidSphere(boss['size'] * 0.08, 10, 10)
    glPopMatrix()
    
    # Boss health indicator (small cubes above head)
    glColor3f(1.0, 0.0, 0.0)
    for i in range(boss['health']):
        glPushMatrix()
        glTranslatef(boss['x'] + (i - boss['health']/2) * 10, boss['y'], boss['size'] * 1.8)
        glutSolidCube(8)
        glPopMatrix()

# --------------------------------------------
def init_treasures():
    global treasures
    treasures = []
    for _ in range(NUM_TREASURES):
        tx = random.uniform(-GRID_LENGTH + TREASURE_BASE_SIZE, GRID_LENGTH - TREASURE_BASE_SIZE)
        ty = random.uniform(-GRID_LENGTH + TREASURE_BASE_SIZE, GRID_LENGTH - TREASURE_BASE_SIZE)
        treasures.append({'x': tx, 'y': ty, 'size': TREASURE_BASE_SIZE, 'pulse_dir': 1})

# --------------------------------------------
def init_enemies():
    global enemies, LEVEL
    enemies = []
    config = LEVEL_ENEMY_CONFIG.get(LEVEL, {'num_enemies': 0, 'speed': ENEMY_BASE_SPEED, 'projectile_enemies': 0, 'projectile_speed': projectile_speed})
    # Normal enemies
    for _ in range(config['num_enemies']):
        ex = random.uniform(-GRID_LENGTH + ENEMY_SIZE, GRID_LENGTH - ENEMY_SIZE)
        ey = random.uniform(-GRID_LENGTH + ENEMY_SIZE, GRID_LENGTH - ENEMY_SIZE)
        enemies.append({'x': ex, 'y': ey, 'size': ENEMY_SIZE, 'speed': config['speed'], 'type': 'normal', 'projectile': None})
    # Block tower (projectile) enemies
    for _ in range(config['projectile_enemies']):
        ex = random.uniform(-GRID_LENGTH + ENEMY_SIZE, GRID_LENGTH - ENEMY_SIZE)
        ey = random.uniform(-GRID_LENGTH + ENEMY_SIZE, GRID_LENGTH - ENEMY_SIZE)
        enemies.append({'x': ex, 'y': ey, 'size': ENEMY_SIZE, 'speed': config['speed'], 'type': 'block_tower', 'projectile': None})

def init_power_ups():
    global power_ups, LEVEL
    power_ups = []
    # 50% chance to spawn a power-up per level
    if random.random() < power_up_chance:
        px = random.uniform(-GRID_LENGTH + power_up_size, GRID_LENGTH - power_up_size)
        py = random.uniform(-GRID_LENGTH + power_up_size, GRID_LENGTH - power_up_size)
        ptype = random.choice(power_up_types)
        power_ups.append({'x': px, 'y': py, 'size': power_up_size, 'type': ptype, 'active': True})

def init_traps():
    global traps, LEVEL
    traps = []
    if LEVEL == 2:
        # Add 1 trap in level 2
        tx = random.uniform(-GRID_LENGTH + TRAP_SIZE, GRID_LENGTH - TRAP_SIZE)
        ty = random.uniform(-GRID_LENGTH + TRAP_SIZE, GRID_LENGTH - TRAP_SIZE)
        traps.append({'x': tx, 'y': ty, 'size': TRAP_SIZE})
    elif LEVEL == 3:
        # Add 2 traps in level 3
        for _ in range(2):
            tx = random.uniform(-GRID_LENGTH + TRAP_SIZE, GRID_LENGTH - TRAP_SIZE)
            ty = random.uniform(-GRID_LENGTH + TRAP_SIZE, GRID_LENGTH - TRAP_SIZE)
            traps.append({'x': tx, 'y': ty, 'size': TRAP_SIZE})
    elif LEVEL == 4:
        # Add 3 traps in level 4
        for _ in range(3):
            tx = random.uniform(-GRID_LENGTH + TRAP_SIZE, GRID_LENGTH - TRAP_SIZE)
            ty = random.uniform(-GRID_LENGTH + TRAP_SIZE, GRID_LENGTH - TRAP_SIZE)
            traps.append({'x': tx, 'y': ty, 'size': TRAP_SIZE})
    elif LEVEL == 5:
        # Add 4 traps in level 5
        for _ in range(4):
            tx = random.uniform(-GRID_LENGTH + TRAP_SIZE, GRID_LENGTH - TRAP_SIZE)
            ty = random.uniform(-GRID_LENGTH + TRAP_SIZE, GRID_LENGTH - TRAP_SIZE)
            traps.append({'x': tx, 'y': ty, 'size': TRAP_SIZE})

def init_boss():
    global boss, LEVEL, player_x, player_y
    boss = None
    if LEVEL == 5:  # Boss only appears in level 1
        # Keep trying to find a position at least 10 radius away from player
        min_distance = 10 * BOSS_SIZE  # At least 10 times the boss radius away
        attempts = 0
        max_attempts = 100  # Prevent infinite loop
        
        while attempts < max_attempts:
            bx = random.uniform(-GRID_LENGTH + BOSS_SIZE, GRID_LENGTH - BOSS_SIZE)
            by = random.uniform(-GRID_LENGTH + BOSS_SIZE, GRID_LENGTH - BOSS_SIZE)
            
            # Check distance from player
            dx = bx - player_x
            dy = by - player_y
            distance = (dx**2 + dy**2)**0.5
            
            if distance >= min_distance:
                boss = {'x': bx, 'y': by, 'size': BOSS_SIZE, 'speed': BOSS_SPEED, 'health': BOSS_HEALTH, 'shoot_timer': 0}
                break
            
            attempts += 1
        
        # If we couldn't find a good spot after max_attempts, place it at a fixed safe location
        if boss is None:
            # Place boss at a corner, far from the center where player starts
            bx = GRID_LENGTH - BOSS_SIZE * 2
            by = GRID_LENGTH - BOSS_SIZE * 2
            boss = {'x': bx, 'y': by, 'size': BOSS_SIZE, 'speed': BOSS_SPEED, 'health': BOSS_HEALTH, 'shoot_timer': 0}

# --------------------------------------------
def draw_treasures():
    global treasures
    for t in treasures:
        t['size'] += TREASURE_PULSE_SPEED * t['pulse_dir']
        if t['size'] > TREASURE_BASE_SIZE * 1.2:
            t['pulse_dir'] = -1
        elif t['size'] < TREASURE_BASE_SIZE * 0.8:
            t['pulse_dir'] = 1

        glColor3f(1.0, 1.0, 0.0)
        glPushMatrix()
        glTranslatef(t['x'], t['y'], t['size'] / 2)
        # Spinning treasures
        glRotatef(time.time() * 100 % 360, 0, 0, 1)
        glutSolidCube(t['size'])
        glPopMatrix()

# --------------------------------------------
def draw_enemies():
    global enemies
    for e in enemies:
        if e['type'] == 'normal':
            # Draw body
            glColor3f(1.0, 0.0, 0.0)
            glPushMatrix()
            glTranslatef(e['x'], e['y'], e['size']/2)
            glutSolidCube(e['size'])
            glPopMatrix()
            
            # Draw head (bigger and black)
            glColor3f(0.0, 0.0, 0.0)
            glPushMatrix()
            glTranslatef(e['x'], e['y'], e['size'] * 1.2)
            glutSolidSphere(e['size'] * 0.5, 20, 20)
            glPopMatrix()
            
        elif e['type'] == 'block_tower':
            # Draw body
            glColor3f(0.7, 0.3, 0.9)
            glPushMatrix()
            glTranslatef(e['x'], e['y'], e['size']/2)
            # Draw block tower as a tall cuboid
            glScalef(1, 1, 2)
            glutSolidCube(e['size']/1.5)
            glPopMatrix()
            
            # Draw head (bigger and black)
            glColor3f(0.0, 0.0, 0.0)
            glPushMatrix()
            glTranslatef(e['x'], e['y'], e['size'] * 1.3)
            glutSolidSphere(e['size'] * 0.4, 15, 15)
            glPopMatrix()

# --------------------------------------------
def draw_power_ups():
    global power_ups
    for p in power_ups:
        if not p['active']:
            continue
        if p['type'] == 'health':
            glColor3f(0.0, 1.0, 1.0)
        elif p['type'] == 'immortal':
            glColor3f(0.8, 0.5, 0.5)
        else:
            glColor3f(0.0, 0.7, 1.0)
        glPushMatrix()
        glTranslatef(p['x'], p['y'], p['size']/2)
        glutSolidSphere(p['size']/2, 20, 20)
        glPopMatrix()

# --------------------------------------------
def draw_projectiles():
    global projectiles
    glColor3f(1.0, 0.0, 0.0)
    for pr in projectiles:
        if not pr['active']:
            continue
        # Boss projectiles are larger and different color
        if pr.get('source') == 'boss':
            glColor3f(0.8, 0.0, 0.8)  # Purple for boss projectiles
        else:
            glColor3f(1.0, 0.0, 0.0)  # Red for enemy projectiles
        glPushMatrix()
        glTranslatef(pr['x'], pr['y'], pr['size']/2)
        glutSolidSphere(pr['size']/2, 10, 10)
        glPopMatrix()

# --------------------------------------------
def draw_traps():
    global traps
    for trap in traps:
        # Draw trap marker above the tile
        glColor3f(1.0, 0.0, 0.0)
        glPushMatrix()
        glTranslatef(trap['x'], trap['y'], 5.0)
        glutSolidCube(trap['size'] * 0.3)
        glPopMatrix()

# --------------------------------------------
def move_enemies():
    global enemies, player_x, player_y, projectiles, LEVEL
    config = LEVEL_ENEMY_CONFIG.get(LEVEL, {'projectile_speed': projectile_speed})
    for e in enemies:
        dx = player_x - e['x']
        dy = player_y - e['y']
        dist = (dx**2 + dy**2)**0.5
        if e['type'] == 'normal':
            if dist > 5.0: 
                normalized_dx = dx / dist
                normalized_dy = dy / dist
                e['x'] += e['speed'] * normalized_dx
                e['y'] += e['speed'] * normalized_dy
        elif e['type'] == 'block_tower':
            has_active = False
            for pr in projectiles:
                if pr.get('source') == id(e) and pr['active']:
                    has_active = True
                    break
            if not has_active and random.random() < 0.02:
                if dist > 10.0:
                    pr_dx = dx / dist
                    pr_dy = dy / dist
                    projectiles.append({'x': e['x'], 'y': e['y'], 'vx': pr_dx * config['projectile_speed'], 'vy': pr_dy * config['projectile_speed'], 'size': projectile_size, 'active': True, 'source': id(e), 'damage': 1})

def move_boss():
    global boss, player_x, player_y, projectiles
    if boss is None:
        return
    
    dx = player_x - boss['x']
    dy = player_y - boss['y']
    dist = (dx**2 + dy**2)**0.5
    
    # Boss moves slowly towards player
    if dist > 50.0:
        normalized_dx = dx / dist
        normalized_dy = dy / dist
        boss['x'] += boss['speed'] * normalized_dx
        boss['y'] += boss['speed'] * normalized_dy
    
    # Boss shooting - reduced projectile speed
    boss['shoot_timer'] -= 1
    if boss['shoot_timer'] <= 0:
        boss['shoot_timer'] = BOSS_SHOOT_COOLDOWN
        if dist > 10.0:
            pr_dx = dx / dist
            pr_dy = dy / dist
            # Boss shoots larger, more damaging projectiles with reduced speed
            projectiles.append({
                'x': boss['x'], 
                'y': boss['y'], 
                'vx': pr_dx * 1.2,  # Further reduced from 4.0 to 2.5
                'vy': pr_dy * 1.2, 
                'size': projectile_size * 1.3, 
                'active': True, 
                'source': 'boss',
                'damage': 2
            })

def move_projectiles():
    global projectiles
    for pr in projectiles:
        if not pr['active']:
            continue
        pr['x'] += pr['vx']
        pr['y'] += pr['vy']
        if abs(pr['x']) > GRID_LENGTH or abs(pr['y']) > GRID_LENGTH:
            pr['active'] = False

def check_enemy_collision():
    global enemies, player_x, player_y, life, game_over, immortal
    player_radius = player_size * 0.5
    for e in enemies[:]:  # iterate over a copy so we can remove enemies
        dx = player_x - e['x']
        dy = player_y - e['y']
        distance = (dx**2 + dy**2)**0.5
        if distance < (player_radius + e['size']/2):
            if not immortal:
                life -= 1
            enemies.remove(e)  # remove the enemy after collision
            if life <= 0:
                life = 0
                game_over = True
                return


def check_projectile_collision():
    global projectiles, player_x, player_y, life, game_over, immortal
    player_radius = player_size * 0.5
    for pr in projectiles:
        if not pr['active']:
            continue
        dx = player_x - pr['x']
        dy = player_y - pr['y']
        distance = (dx**2 + dy**2)**0.5
        if distance < (player_radius + pr['size']/2):
            if not immortal:
                damage = pr.get('damage', 1)
                life -= damage
            pr['active'] = False
            if life <= 0:
                life = 0
                game_over = True
                return

def check_boss_collision():
    global boss, player_x, player_y, life, game_over, immortal
    if boss is None:
        return
    
    player_radius = player_size * 0.5
    dx = player_x - boss['x']
    dy = player_y - boss['y']
    distance = (dx**2 + dy**2)**0.5
    if distance < (player_radius + boss['size']/2):
        if not immortal:
            life -= 2  # Boss touch reduces life by 2
        if life <= 0:
            life = 0
            game_over = True
            return

def check_treasure_collision():
    global treasures, player_x, player_y, score, LEVEL, timer_start, projectiles, boss, game_won
    player_radius = player_size * 0.5
    for t in treasures[:]:
        dx = player_x - t['x']
        dy = player_y - t['y']
        distance = (dx**2 + dy**2)**0.5
        if distance < (player_radius + t['size']/2):
            treasures.remove(t)
            score += 1
            
            # Check if boss is defeated (boss collision reduces its health)
            if boss is not None:
                boss['health'] -= 1
                if boss['health'] <= 0:
                    boss = None  # Boss is defeated
    
    # Check level up or game win
    if len(treasures) == 0:
        if LEVEL == 5:
            # Game won!
            game_won = True
            game_over = True
        elif LEVEL < 5:
            LEVEL += 1
            init_treasures()
            init_enemies()
            init_power_ups()
            init_traps()
            init_boss()
            projectiles = []
            timer_start = time.time()

def check_power_up_collision():
    global power_ups, player_x, player_y, life, immortal, immortal_timer
    player_radius = player_size * 0.5
    for p in power_ups:
        if not p['active']:
            continue
        dx = player_x - p['x']
        dy = player_y - p['y']
        distance = (dx**2 + dy**2)**0.5
        if distance < (player_radius + p['size']/2):
            if p['type'] == 'health':
                life += 1
            else:
                immortal = True
                immortal_timer = immortal_duration
            p['active'] = False

def check_trap_collision():
    global traps, player_x, player_y, game_over, immortal, life
    player_radius = player_size * 0.5
    for trap in traps:
        dx = player_x - trap['x']
        dy = player_y - trap['y']
        distance = (dx**2 + dy**2)**0.5
        if distance < (player_radius + trap['size']/2):
            # Instantly set life to 0 and trigger game over
            life = 0
            game_over = True
            return

def keyboardListener(key, x, y):
    global player_x, player_y, player_rotate_z, player_speed, score, life, game_over, immortal, immortal_timer, dark_mode

    if isinstance(key, bytes):
        k = key.decode('utf-8').lower()
    else:
        k = str(key).lower()

    if game_over:
        if k == 'r':
            restart_game()
        return

    if k == 'w':
        angle_rad = radians(player_rotate_z + 90)
        nx = player_x + player_speed * cos(angle_rad)
        ny = player_y + player_speed * sin(angle_rad)
        player_x = max(-GRID_LENGTH + player_size/2, min(GRID_LENGTH - player_size/2, nx))
        player_y = max(-GRID_LENGTH + player_size/2, min(GRID_LENGTH - player_size/2, ny))
    elif k == 's':
        angle_rad = radians(player_rotate_z + 90)
        nx = player_x - player_speed * cos(angle_rad)
        ny = player_y - player_speed * sin(angle_rad)
        player_x = max(-GRID_LENGTH + player_size/2, min(GRID_LENGTH - player_size/2, nx))
        player_y = max(-GRID_LENGTH + player_size/2, min(GRID_LENGTH - player_size/2, ny))
    elif k == 'a':
        player_rotate_z += 10.0
        player_rotate_z %= 360.0
    elif k == 'd':
        player_rotate_z -= 10.0
        player_rotate_z %= 360.0
    elif k == 'p':
        # Toggle immortal mode
        immortal = not immortal
        if immortal:
            immortal_timer = 10000
        else:
            immortal_timer = 0.0
    elif k == 'c':
        # Toggle dark mode
        dark_mode = not dark_mode
        if dark_mode:
            glClearColor(0.05, 0.05, 0.1, 1.0)  # Dark background
        else:
            glClearColor(0.1, 0.2, 0.4, 1.0)  # Normal background
    elif k == 'r':
        restart_game()

def specialKeyListener(key, x, y):
    global camera_pos, cam_theta, cam_height, cam_radius
    
    if key == GLUT_KEY_UP:
        cam_height = min(cam_height + 20, 1200)
    elif key == GLUT_KEY_DOWN:
        cam_height = max(cam_height - 20, 120)
    elif key == GLUT_KEY_LEFT:
        cam_theta += 5.0
    elif key == GLUT_KEY_RIGHT:
        cam_theta -= 5.0

    cam_x = cam_radius * cos(radians(cam_theta))
    cam_y = cam_radius * sin(radians(cam_theta))
    cam_z = cam_height
    camera_pos = (cam_x, cam_y, cam_z)


def mouseListener(button, state, x, y):
    pass


def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    x, y, z = camera_pos
    gluLookAt(x, y, z, 0, 0, 0, 0, 0, 1)


def idle():
    global immortal, immortal_timer, game_over, timer_start, level_timer
    if immortal:
        immortal_timer -= 0.02
        if immortal_timer <= 0:
            immortal = False
            immortal_timer = 0.0
    if timer_start and not game_over:
        elapsed = time.time() - timer_start
        if elapsed > level_timer:
            game_over = True
    glutPostRedisplay()


def showScreen():
    global life, game_over, game_won, immortal, timer_start, level_timer
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    setupCamera()
    draw_floor()
    draw_shapes()
    draw_player()
    draw_treasures()
    draw_enemies()
    draw_boss()  # Draw the boss
    draw_power_ups()
    draw_projectiles()
    draw_traps()

    move_enemies()
    move_boss()
    move_projectiles()
    check_treasure_collision()
    check_enemy_collision()
    check_boss_collision()
    check_projectile_collision()
    check_power_up_collision()
    check_trap_collision()

    if game_won:
        draw_text(350, 400, "YOU WON! Press R to restart")
    elif life <= 0 or (timer_start and (time.time() - timer_start) > level_timer):
        game_over = True
        draw_text(400, 400, "GAME OVER! Press R to restart")

    draw_text(10, 770, f"Score: {score}")
    draw_text(10, 750, f"Level: {LEVEL}")
    draw_text(10, 720, f"Life: {life}")
    if immortal:
        draw_text(10, 700, f"IMMORTAL: {int(immortal_timer)}s")
    # Timer display
    if timer_start:
        remaining = max(0, int(level_timer - (time.time() - timer_start)))
        draw_text(10, 680, f"Time Left: {remaining}s")
    
    # Controls display
    draw_text(10, 50, "Controls: WASD=Move, Arrows=Camera, P=Immortal, C=Dark Mode, R=Restart")

    glutSwapBuffers()

def main():
    global timer_start
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"Final Project")

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.2, 0.4, 1.0)

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    init_treasures()
    init_enemies()
    init_power_ups()
    init_traps()
    init_boss()
    timer_start = time.time()

    glutMainLoop()

if __name__ == "__main__":
    main()
