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

lvl = level.Level("krasi")
lvlname = "krasi"
lvltext = font.Text(lvlname)
tiletext = font.Text(lvl.tilemapname)

tilemapx = lvl.w + 2
tilemapy = 1

lvlcur = Cursor()
tilecur = Cursor()

levelgrid = True

running = True

timing.timer.startTiming()

while running:
  for ev in pygame.event.get():
    if ev.type == QUIT:
      running = False

    if ev.type == KEYDOWN:
      if ev.key == K_UP:
        lvlcur.y -= 1
      elif ev.key == K_DOWN:
        lvlcur.y += 1
      elif ev.key == K_LEFT:
        lvlcur.x -= 1
      elif ev.key == K_RIGHT:
        lvlcur.x += 1

      elif ev.key == K_a:
        try:
          lvl.level[lvlcur.y][lvlcur.x] += 1
        except:
          pass
      elif ev.key == K_s:
        try:
          lvl.level[lvlcur.y][lvlcur.x] -= 1
        except:
          pass
      elif ev.key == K_g:
        levelgrid = not levelgrid
    elif ev.type == MOUSEBUTTONDOWN:
      # is mouse in level area?
      if 32 <= ev.pos[0] <= 32 + 32 * lvl.w and\
         32 <= ev.pos[1] <= 32 + 32 * lvl.h:
        lvlcur.x = ev.pos[0] / 32 - 1
        lvlcur.y = ev.pos[1] / 32 - 1

        if ev.button == 1:
          try: lvl.level[lvlcur.y][lvlcur.x] = tilecur.x + tilecur.y * lvl.ttc
          except: pass
        
      elif tilemapx * 32 + 32 <= ev.pos[0] <= tilemapx * 32 + 32 + 32 * lvl.ttc and\
           tilemapy * 32 + 32 <= ev.pos[1] <= tilemapy * 32 + 32 + 32 * lvl.ttc:
        tilecur.x = ev.pos[0] / 32 - tilemapx - 1
        tilecur.y = ev.pos[1] / 32 - tilemapy - 1

  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
  glLoadIdentity()
  
  # level
  glPushMatrix()
  glTranslatef(1, 1, 0)
  lvl.draw()
  lvl.showBorder()
  if levelgrid:
    lvl.showGrid()
  lvlcur.draw()
  glPopMatrix()
  
  # level caption
  glPushMatrix()
  glScalef(32 ** -1, 32 ** -1, 1)
  lvltext.draw()
  glPopMatrix()

  glPushMatrix()
  glTranslatef(tilemapx, tilemapy, 0)

  # tileset
  glPushMatrix()
  glTranslatef(1, 1, 0)
  lvl.drawTileset()
  lvl.showTilesetBorder()
  lvl.showTilesetGrid()
  tilecur.draw()
  glPopMatrix()
  
  # tileset caption
  glPushMatrix()
  glScalef(32 ** -1, 32 ** -1, 1)
  tiletext.draw()
  glPopMatrix()

  glPopMatrix()

  pygame.display.flip()
