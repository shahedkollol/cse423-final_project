from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from math import radians, cos, sin, atan2, degrees

# Camera variables
camera_pos = (0, 500, 500)
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
    global player_x, player_y, player_z, player_rotate_z

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

    # Player
    glPushMatrix()
    glTranslatef(player_x, player_y, player_z + player_size/2.0)
    glRotatef(player_rotate_z, 0, 0, 1)
    glColor3f(0.4, 0.7, 0.2)
    glScalef(player_size, player_size, player_size)
    glutSolidCube(1)
    glPopMatrix()

def keyboardListener(key, x, y):
    global player_x, player_y, player_rotate_z, player_speed, score, life, game_over

    if isinstance(key, bytes):
        k = key.decode('utf-8').lower()
    else:
        k = str(key).lower()

    if game_over:
        if k == 'r':
            player_x = 0.0
            player_y = 0.0
            player_rotate_z = 0.0
            score = 0
            life = 3
            game_over = False
            print("Game restarted")
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
        player_x = 0.0
        player_y = 0.0
        player_rotate_z = 0.0
        score = 0
        life = 3
        game_over = False

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

    draw_text(10, 770, f"Score: {score}")
    draw_text(10, 740, f"Life: {life}")
    draw_text(10, 710, f"Pos: ({int(player_x)}, {int(player_y)})  Angle: {int(player_rotate_z)}")
    draw_text(10, 680, "Controls: W/A/S/D move, Arrow keys rotate/move camera, R reset")

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

    glutMainLoop()

if __name__ == "__main__":
    main()
