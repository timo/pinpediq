from OpenGL.GL import *

def quad():
    glBegin(GL_QUADS)
    
    glTexCoord2f(0, 1)
    glVertex2i(0, 1)

    glTexCoord2f(0, 0)
    glVertex2i(0, 0)

    glTexCoord2f(1, 0)
    glVertex2i(1, 0)

    glTexCoord2f(1, 1)
    glVertex2i(1, 1)

    glEnd()
