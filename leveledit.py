#!/usr/bin/python
from lib import level, font, main, timing, tinygui
import pygame
from pygame.locals import *
from OpenGL.GL import *

class Cursor:
  def __init__(self, x=0, y=0):
    self.x = x
    self.y = y

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

class CommandInputArea(tinygui.TextInputArea):
  def __init__(self, parent):
    tinygui.TextInputArea.__init__(self,
        "",
        pygame.Rect(0, 768 - 32, 1024, 32),
        "cmd: ")

    self.lvlarea = parent
    self.background = True

  def inputDone(self):
    if self.text == "save":
      try:
        self.lvlarea.lvl.save()
        tinygui.popup("level saved as '%s'" % self.lvlarea.lvl.levelname)
      except Exception, e:
        tinygui.popup("exception caught while saving: %s" % str(e))

    elif self.text == "info":
      tinygui.popup("level is %s * %s big." % (self.lvlarea.lvl.w, self.lvlarea.lvl.h))

    elif self.text[:4] == "w = ":
      try:
        w = int(self.text[4:])
      except:
        tinygui.popup("error in input.")
        return
      if w <= 0:
        tinygui.popup("invalid value.")
      elif w == self.lvlarea.lvl.w:
        tinygui.popup("level width unchanged.")
      elif w < self.lvlarea.lvl.w:
        for row in self.lvlarea.lvl.level:
          del row[w:]
      elif w > self.lvlarea.lvl.w:
        for row in self.lvlarea.lvl.level:
          row.extend([0] * (w - self.lvlarea.lvl.w))

      self.lvlarea.lvl.w = w
      self.lvlarea.updateLevel()

    elif self.text[:4] == "h = ":
      try:
        h = int(self.text[4:])
      except:
        tinygui.popup("error in input.")
        return
      if h <= 0:
        tinygui.popup("invalid value.")
      elif h == self.lvlarea.lvl.h:
        tinygui.popup("level height unchanged.")
      elif h < self.lvlarea.lvl.h:
        del self.lvlarea.lvl.level[h:]
      elif h > self.lvlarea.lvl.h:
        for i in range(self.lvlarea.lvl.h, h):
          self.lvlarea.lvl.level.append([0] * self.lvlarea.lvl.w)

      self.lvlarea.lvl.h = h
      self.lvlarea.updateLevel()

class LevelNameArea(tinygui.TextInputArea):
  def __init__(self, parent):
    self.lvlarea = parent
    tinygui.TextInputArea.__init__(self,
        self.lvlarea.lvl.levelname, # initial text
        pygame.Rect(0, 0, 0, 0))
    self.setPosition()

  def setPosition(self):
    self.rect = pygame.Rect(0, 0, self.lvlarea.lvl.w * 32, 32)
      
  def inputDone(self):
    try:
      self.lvlarea.updateLevel(level.load(self.text))
      tinygui.popup("level %s loaded" % (self.text))
    except IOError:
      self.lvlarea.updateLevel(level.load(None))
      tinygui.popup("new level %s" % (self.text))

class TileSetNameArea(tinygui.TextInputArea):
  def __init__(self, parent):
    self.tsa = parent
    tinygui.TextInputArea.__init__(self,
        self.tsa.lvlarea.lvl.tilemapname,
        pygame.Rect(0, 0, 0, 0))
    self.setPosition()
    print self.rect

  def setPosition(self):
    self.rect = pygame.Rect(self.tsa.lvlarea.lvl.w * 32 + 32, self.tsa.rect.y - 32, self.tsa.rect.w, 32)
    print self.rect

  def inputDone(self):
    try:
      self.tsa.lvlarea.lvl.loadTileset(self.text)
      tinygui.popup("tileset %s loaded" % (self.text))
    except (IOError, pygame.error):
      tinygui.popup("tileset %s does not exist" % (self.text))

class TileSetArea(tinygui.Area):
  def __init__(self, parent):
    self.lvlarea = parent
    self.setPosition()
    self.tsna = TileSetNameArea(self)
    self.children = [self.tsna]
    self.tilesel = 0
    self.cursor = Cursor()

  def handleEvent(self, ev):
    if ev.type == MOUSEBUTTONDOWN:
      mpx = (ev.pos[0] - self.rect.x) / 32
      mpy = (ev.pos[1] - self.rect.y) / 32

      if 0 <= mpx < self.lvlarea.lvl.ttc and 0 <= mpy < self.lvlarea.lvl.ttc:
        self.tilesel = mpx + mpy * self.lvlarea.lvl.ttc
        self.cursor.x = mpx
        self.cursor.y = mpy

  def setPosition(self):
    self.rect = pygame.Rect(32, 32, self.lvlarea.lvl.ttc * 32, self.lvlarea.lvl.ttc * 32)
    self.rect.left = self.lvlarea.lvl.w * 32 + 64
    try:
      self.tsna.setPosition()
    except:
      pass

  def draw(self):
    glPushMatrix()
    glTranslatef(self.rect.x / 32, self.rect.y / 32, 0)
    self.lvlarea.lvl.drawTileset()
    self.lvlarea.lvl.showTilesetBorder()
    self.lvlarea.lvl.showTilesetGrid()
    self.cursor.draw()
    glPopMatrix()

    for ch in self.children:
      ch.draw()

class LevelArea(tinygui.Area):
  def __init__(self, levelname):
    self.lvl = level.load(levelname)
    self.rect = pygame.Rect(0, 0, self.lvl.w * 32, self.lvl.h * 32 + 32)
    self.lna = LevelNameArea(self)
    self.tsa = TileSetArea(self)
    self.cmd = CommandInputArea(self)
    self.children = [self.lna, self.tsa, self.cmd]
    self.displayGrid = True
    self.cursor = Cursor()

  def updateLevel(self, newlevel = None):
    if newlevel:
      self.lvl = newlevel
    self.rect = pygame.Rect(0, 0, self.lvl.w * 32 + 32, self.lvl.h * 32 + 32)
    self.lna.setPosition()
    self.tsa.setPosition()
    self.tsa.tsna.setText(self.lvl.tilemapname)
    (self.cursor.x, self.cursor.y) = (0, 0)

  def handleEvent(self, ev):
    if ev.type == MOUSEBUTTONDOWN:
      tpx = (ev.pos[0] - self.rect.x - 32) / 32
      tpy = (ev.pos[1] - self.rect.y - 32) / 32

      if 0 <= tpx < self.lvl.w and 0 <= tpy < self.lvl.h:
        self.lvl.level[tpy][tpx] = self.tsa.tilesel
        self.cursor.x = tpx
        self.cursor.y = tpy
    elif ev.type == KEYDOWN:
      if ev.key == K_g:
        self.displayGrid = not self.displayGrid

  def draw(self):
    glPushMatrix()
    glTranslatef(1 + self.rect.x / 32, 1 + self.rect.y / 32, 0)

    self.lvl.draw()
    self.lvl.showBorder()
    if self.displayGrid:
      self.lvl.showGrid()

    self.cursor.draw()

    glPopMatrix()

    for ch in self.children:
      ch.draw()

main.init()
tinygui.areas.append(LevelArea("krasi"))

running = True
timing.timer.startTiming()

while running:
  for ev in pygame.event.get():
    tinygui.handleEvent(ev)

    if ev.type == QUIT:
      running = False

  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
  glLoadIdentity()
  tinygui.draw()
  pygame.display.flip()
