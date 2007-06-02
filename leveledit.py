#!/usr/bin/python
from lib import level, font, main, timing
import pygame
from pygame.locals import *
from OpenGL.GL import *

class Cursor:
  def __init__(self):
    self.x = 0
    self.y = 0

  def draw(self):
    glDisable(GL_TEXTURE_2D)
    glPushMatrix()
    glTranslatef(self.x + 0.5, self.y + 0.5, 0)
    sc = timing.timer.pulse(2, 0.4, 0.6)
    glScalef(sc, sc, 1)

    glBegin(GL_LINE_LOOP)
    glVertex2f(-1, -1)
    glVertex2f( 1, -1)
    glVertex2f( 1,  1)
    glVertex2f(-1,  1)
    glEnd()

    glPopMatrix()

main.init()

lvl = level.Level()
lvlname = "no level loaded"
lvltext = font.Text(lvlname)

lvlcur = Cursor()

running = True

timing.timer.startTiming()

while running:
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
  glLoadIdentity()
  
  lvl.draw()
  lvl.showBorder()
  lvl.showGrid()

  lvlcur.draw()

  glPushMatrix()
  glScalef(32 ** -1, 32 ** -1, 1)
  lvltext.draw()
  glPopMatrix()

  pygame.display.flip()
