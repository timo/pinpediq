#!/usr/bin/python
import random
from timing import timer

from math import pi

import pygame
from pygame.locals import *
from OpenGL.GL import *

import level
import sprite
import enemy
import font
from time import sleep
from physics import *

import damageArea

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
  glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
  glEnable(GL_LINE_SMOOTH)
  glEnable(GL_TEXTURE_2D)

  # yay! play the game!
  running = True
  timer.startTiming()

  lvl = level.load("krasi")

  plr = sprite.Sprite("player")
  plr.x = 2
  plr.y = -4
  plr.w = 0.75
  plr.h = 0.75
  plr.health = 100

  possiblepositions = [(1, 1), (1.5, 1), (2.5, 1), (3, 1), (3.5, 1), (4, 1), (4.5, 1),
                       (1, 8)]
  enemies = []
  pain = []
  ppain = []

  for i in range(5):
    ne = enemy.enemy("enemy")
    (ne.x, ne.y) = random.choice(possiblepositions)
    #possiblepositions.remove((ne.x, ne.y))
    (ne.w, ne.h) = (0.6, 0.6)
    ne.vx = 0.5
    enemies.append(ne)
    ppain.append(damageArea.RectDamage(ne.x, ne.y, ne.w, ne.h, ne.vx, ne.vy, -1, 10))
    ne.damager = ppain[-1] 

  timer.gameSpeed = 1

  lasthithp = 0


  sentence = ""
  sentencestrength = 1
  mode = 0

  textthing = font.Text("")

  while running:
    timer.startFrame()
    for event in pygame.event.get():
      if event.type == QUIT:
        running = False

      if mode == 1:
        if event.type == KEYDOWN:
          if K_a <= event.key <= K_z:
            if event.key == K_h:
              sentence += "'"
            else:
              sentence += chr(ord('a') + event.key - K_a)
            textthing.renderText(sentence + "_")
            textthing.rgba = (1, 1, 1, 1)
          elif event.key == K_SPACE:
            sentence += " "
            textthing.renderText(sentence + "_")
            textthing.rgba = (1, 1, 1, 1)
          elif event.key == K_BACKSPACE:
            sentence = sentence[:-1]
            textthing.renderText(sentence + "_")
            textthing.rgba = (1, 1, 1, 1)
            if len(sentence) == 0:
              mode = 0
              textthing.renderText(sentence)
          elif event.key == K_RETURN:
            mode = 0
            sentencestrength = 1
            textthing.renderText(sentence)
      else:
        if event.type == KEYDOWN:
          if event.key == K_s:
            mode = 1
            sentence = ""
            textthing.renderText(sentence + "_")
            textthing.rgba = (1, 1, 1, 1)
          if event.key == K_SPACE:
            if plr.vx > 0:
              x  = plr.x + plr.w
              sa = pi / -2
              ea = pi / 2
            else:
              x  = plr.x
              sa = pi / 2
              ea = pi / 2 * 3
            if plr.physics == STANDING:
              plr.vy -= 2
            np = damageArea.ArcDamage(x, plr.y - plr.h / 2.0, plr.vx, plr.vy, 0.75, sa, ea, 0.25, 10 + len(sentence) * sentencestrength * 3)
            pain.append(np)
            sentencestrength *= 0.75
            textthing.rgba = (1, 1, 1, sentencestrength)

    if mode == 0:
      if pygame.key.get_pressed()[K_UP]:
        if plr.physics == STANDING:
          plr.vy = -6.0
      elif plr.physics == FALLING and plr.vy < 0:
        plr.vy *= 1.0 - timer.curspd

      if pygame.key.get_pressed()[K_LEFT]:
        plr.vx = max(-3, plr.vx - 5 * timer.curspd)
      elif pygame.key.get_pressed()[K_RIGHT]:
        plr.vx = min(3, plr.vx + 5 * timer.curspd)
      else:
        if plr.vx != 0:
          plr.vx *= 0.9

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()


    glTranslatef(0,lvl.size[1],0)

    plr.move()
    for p in ppain:
      p.move()
      if p.lifetime == 0:
        ppain.remove(p)
      if p.check(plr):
        p.hit(plr)
    for p in pain:
      p.move()
      if p.lifetime == 0:
        pain.remove(p)
    for en in enemies:
      en.move()
      for p in pain:
        if p.check(en):
          p.hit(en)
          lasthithp = en.health
      if en.state == enemy.DEAD:
        enemies.remove(en)

    # do stuff
    lvl.draw()
    plr.draw()
    for en in enemies:
      en.draw()
    for p in pain:
      p.draw()

    glPushMatrix()

    glLoadIdentity()

    glTranslatef(5, 5, 0)
    glScalef(1./32, 1./32, 1)
    textthing.draw()

    glPopMatrix()

    # enemy HP
    glDisable(GL_TEXTURE_2D)
    glColor4f(1.0, 1.0, 1.0, 1.0)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(2, 0)
    glVertex2f(2, 0.2)
    glVertex2f(0, 0.2)

    glColor4f(1.0, 0.0, 0.0, 1.0)
    glVertex2f(0.05, 0.05)
    glVertex2f(0.05 + lasthithp / 100.0 * 1.9, 0.05)
    glVertex2f(0.05 + lasthithp / 100.0 * 1.9, 0.15)
    glVertex2f(0, 0.15)
    glEnd()
    
    # player HP
    glColor4f(1.0, 1.0, 1.0, 1.0)
    glBegin(GL_QUADS)
    glVertex2f(2, 0)
    glVertex2f(4, 0)
    glVertex2f(4, 0.2)
    glVertex2f(2, 0.2)

    glColor4f(1.0, 0.0, 0.0, 1.0)
    glVertex2f(2.05, 0.05)
    glVertex2f(2.05 + plr.health / 100.0 * 1.9, 0.05)
    glVertex2f(2.05 + plr.health / 100.0 * 1.9, 0.15)
    glVertex2f(2, 0.15)
    glEnd()

    pygame.display.flip()
    timer.endFrame()

  # exit pygame
  pygame.quit()
