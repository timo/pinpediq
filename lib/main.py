#!/usr/bin/python
import random
from timing import timer

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

from level import Level

# don't initialise sound stuff plzkthxbai
pygame.mixer = None

screen = None
screensize = (1024, 786)

def setres((width, height)):
  """res = tuple
sets the resolution and sets up the projection matrix"""
  if height==0:
    height=1
  glViewport(0, 0, width, height)
  glMatrixMode(GL_PROJECTION)
  glLoadIdentity()
  gluPerspective(45, 1.0*width/height, 1, 10)
  glMatrixMode(GL_MODELVIEW)
  glLoadIdentity()

if  __name__ == "__main__":
  # initialize everything
  pygame.init()
  screen = pygame.display.set_mode(screensize, OPENGL|DOUBLEBUF)
  setres(screensize)

  # some OpenGL magic!
  glEnable(GL_BLEND)
  glBlendFunc(GL_SRC_ALPHA, GL_ONE)
  glEnable(GL_LINE_SMOOTH)
  glEnable(GL_TEXTURE_2D)

  # yay! play the game!
  running = True
  timer.startTiming()

  lvl = Level("krasi")

  while running:
    timer.startFrame()
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    glTranslatef(-5,3,-10)

    # do stuff
    lvl.draw()

    pygame.display.flip()
    timer.endFrame()

  # exit pygame
  pygame.quit()
