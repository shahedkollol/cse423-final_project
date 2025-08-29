from OpenGL.GL import *
from OpenGL.GLUT import *
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
life = 3
game_over = False

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
    """Reset all game states to their initial values"""
    global player_x, player_y, player_z, player_rotate_z
    global score, life, game_over
    global cam_theta, cam_radius, cam_height, camera_pos
    global treasures, LEVEL
    
    # Reset player position and rotation
    player_x = INITIAL_PLAYER_X
    player_y = INITIAL_PLAYER_Y
    player_z = INITIAL_PLAYER_Z
    player_rotate_z = INITIAL_PLAYER_ROTATE_Z
    
    # Reset game state
    score = INITIAL_SCORE
    life = INITIAL_LIFE
    game_over = False
    LEVEL = INITIAL_LEVEL
    
    # Reset camera 
    cam_theta = INITIAL_CAM_THETA
    cam_radius = INITIAL_CAM_RADIUS
    cam_height = INITIAL_CAM_HEIGHT
    camera_pos = INITIAL_CAMERA_POS  
    
    # Reinitialize treasures
    init_treasures()
    


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

def draw_shapes():

    # Grid floor
    grid_size = 13
    cell_length = (GRID_LENGTH * 2) / grid_size
    glBegin(GL_QUADS)
    for i in range(grid_size):
        for j in range(grid_size):
            x0 = -GRID_LENGTH + i * cell_length
            x1 = x0 + cell_length
            y0 = -GRID_LENGTH + j * cell_length
            y1 = y0 + cell_length
            if (i + j) % 2 == 0:
                glColor3f(0.85, 0.85, 0.85)
            else:
                glColor3f(0.45, 0.55, 0.95)
            glVertex3f(x0, y0, 0)
            glVertex3f(x1, y0, 0)
            glVertex3f(x1, y1, 0)
            glVertex3f(x0, y1, 0)
    glEnd()

    # Boundary walls
    wall_height = 80.0
    wall_thickness = 10.0

    glColor3f(0, 0, 0.6)
    glPushMatrix()
    glTranslatef(-GRID_LENGTH, 0, wall_height/2)
    glScalef(wall_thickness, GRID_LENGTH*2, wall_height)
    glutSolidCube(1)
    glPopMatrix()

    glColor3f(0, 0.6, 0.6)
    glPushMatrix()
    glTranslatef(GRID_LENGTH, 0, wall_height/2)
    glScalef(wall_thickness, GRID_LENGTH*2, wall_height)
    glutSolidCube(1)
    glPopMatrix()

    glColor3f(0, 0.6, 0.2)
    glPushMatrix()
    glTranslatef(0, -GRID_LENGTH, wall_height/2)
    glScalef(GRID_LENGTH*2, wall_thickness, wall_height)
    glutSolidCube(1)
    glPopMatrix()

    glColor3f(0.9, 0.9, 0.9)
    glPushMatrix()
    glTranslatef(0, GRID_LENGTH, wall_height/2)
    glScalef(GRID_LENGTH*2, wall_thickness, wall_height)
    glutSolidCube(1)
    glPopMatrix()

def draw_player():
    global player_x, player_y, player_z, player_rotate_z, player_size
    # Player (spherical with body)
    glPushMatrix()
    glTranslatef(player_x, player_y, player_z)  
    glRotatef(player_rotate_z, 0, 0, 1)

        # Head
    glColor3f(0.9, 0.8, 0.6)  # skin tone
    glPushMatrix()
    glTranslatef(0, 0, player_size * 0.9)  
    glutSolidSphere(player_size * 0.4, 30, 30)  

    # Eyes (black spheres slightly in front of head, on +Y side = "front")
    glColor3f(0, 0, 0)
    eye_offset = player_size * 0.15
    eye_z = player_size * 0.05
    eye_depth = player_size * 0.35   # push eyes outward so they sit on surface

    # Left eye
    glPushMatrix()
    glTranslatef(-eye_offset, eye_depth, eye_z)
    glutSolidSphere(player_size * 0.07, 10, 10)
    glPopMatrix()

    # Right eye
    glPushMatrix()
    glTranslatef(eye_offset, eye_depth, eye_z)
    glutSolidSphere(player_size * 0.07, 10, 10)
    glPopMatrix()

    glPopMatrix()  # end head


    # Body
    glColor3f(0.4, 0.7, 0.9)  # shirt/body
    glPushMatrix()
    glTranslatef(0, 0, player_size * 0.4)  
    glutSolidSphere(player_size * 0.5, 30, 30)  
    glPopMatrix()

    # Legs
    glColor3f(0.3, 0.3, 0.3)  # pants
    glPushMatrix()
    glTranslatef(-player_size * 0.2, 0, 0)  
    glutSolidSphere(player_size * 0.25, 20, 20)  
    glPopMatrix()

    glPushMatrix()
    glTranslatef(player_size * 0.2, 0, 0)  
    glutSolidSphere(player_size * 0.25, 20, 20)  
    glPopMatrix()

    glPopMatrix()

def init_treasures():
    global treasures
    treasures = []
    for _ in range(NUM_TREASURES):
        tx = random.uniform(-GRID_LENGTH + TREASURE_BASE_SIZE, GRID_LENGTH - TREASURE_BASE_SIZE)
        ty = random.uniform(-GRID_LENGTH + TREASURE_BASE_SIZE, GRID_LENGTH - TREASURE_BASE_SIZE)
        treasures.append({'x': tx, 'y': ty, 'size': TREASURE_BASE_SIZE, 'pulse_dir': 1})

def draw_treasures():
    global treasures
    for t in treasures:
        # Pulsing effect
        t['size'] += TREASURE_PULSE_SPEED * t['pulse_dir']
        if t['size'] > TREASURE_BASE_SIZE * 1.2:
            t['pulse_dir'] = -1
        elif t['size'] < TREASURE_BASE_SIZE * 0.8:
            t['pulse_dir'] = 1

        glColor3f(1.0, 1.0, 0.0)  # yellow
        glPushMatrix()
        glTranslatef(t['x'], t['y'], t['size'] / 2)  # place on floor
        glutSolidCube(t['size'])
        glPopMatrix()

def check_treasure_collision():
    global treasures, player_x, player_y, score
    player_radius = player_size * 0.5
    for t in treasures[:]:  # iterate copy so we can remove
        dx = player_x - t['x']
        dy = player_y - t['y']
        distance = (dx**2 + dy**2)**0.5
        if distance < (player_radius + t['size']/2):
            treasures.remove(t)
            score += 1

    

def keyboardListener(key, x, y):
    global player_x, player_y, player_rotate_z, player_speed, score, life, game_over

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
    glutPostRedisplay()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    setupCamera()
    draw_shapes()
    draw_player()
    draw_treasures()
    check_treasure_collision()

    draw_text(10, 770, f"Score: {score}")
    draw_text(10, 750, f"Level: {LEVEL}")
    draw_text(10, 720, f"Life: {life}")


    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"Final Project")

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.15, 0.15, 0.2, 1.0)

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    init_treasures()


    glutMainLoop()

if __name__ == "__main__":
    main()
