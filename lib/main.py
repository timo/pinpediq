#!/usr/bin/python
import random
from timing import timer

import pygame
from pygame.locals import *
from OpenGL.GL import *


import level
import sprite
from time import sleep
from physics import *

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
  glOrtho(0, width / 32, 0, height / 32, -10, 10)
  glMatrixMode(GL_MODELVIEW)
  glLoadIdentity()

def rungame():
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

  lvl = level.load("krasi")

  plr = sprite.Sprite("player")
  plr.x = 1
  plr.y = 1
  plr.vy = -0.5

  while running:
    timer.startFrame()
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False


    if pygame.key.get_pressed()[K_UP]:
      if plr.physics == STANDING:
        plr.vy = -5.0
    elif plr.physics == FALLING and plr.vy < 0:
      plr.vy *= 1.0 - timer.curspd

    if pygame.key.get_pressed()[K_LEFT]:
      plr.vx = max(-3, plr.vx - 5 * timer.curspd)
    elif pygame.key.get_pressed()[K_RIGHT]:
      plr.vx = min(3, plr.vx + 5 * timer.curspd)
    else:
      if plr.vx != 0:
        plr.vx *= 0.99

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    glTranslatef(0,10,0)

    plr.move()

    # do stuff
    lvl.draw()
    plr.draw()
    glTranslatef(10, 0, 0)
    lvl.showCollision()

    pygame.display.flip()
    timer.endFrame()

  # exit pygame
  pygame.quit()
