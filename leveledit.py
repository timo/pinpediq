#!/usr/bin/python
from lib import level, font, main, timing, tinygui, scroll
import pygame
from pygame.locals import *
from OpenGL.GL import *

class Cursor:
  """A graphical, pulsing Cursor

  This class has no real use and has to be repositioned by the main loop of the
  program as necessary"""

  def __init__(self, x=0, y=0):
    self.x = x
    self.y = y

  def draw(self):
    """draw the Cursor to the screen.

    Matrix operations are kept, disables TEXTURE_2D"""
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
  """The Commandline for the Level Editor.

  Commands offered by it are:
  
  save
      saves the level to the current level name

  info
      displays width and heigth in a popup box

  w = x; h = x
      resizes the level, cutting parts off or adding tiles as necessary
  """

  def __init__(self, parent):
    """initialise the Commandline.

    takes an instance of `LevelArea` as its parent"""
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
  """A TextInput to display and change the Name of the currently loaded Level.

  if the name is changed and return is hit, a new level will be created.
  """

  def __init__(self, parent):
    """Initialises the LevelNameArea.

    takes a LevelArea as its parent.
    """

    self.lvlarea = parent
    tinygui.TextInputArea.__init__(self,
        self.lvlarea.lvl.levelname, # initial text
        pygame.Rect(0, 0, 0, 0))
    self.setPosition()

  def setPosition(self):
    self.rect = pygame.Rect(0, 0, self.lvlarea.lvl.w * 32, 32)
      
  def inputDone(self):
    """Tries to load the Level. If it fails, a dummy level is created."""
    try:
      self.lvlarea.updateLevel(level.load(self.text, None))
      tinygui.popup("level %s loaded" % (self.text))
    except IOError:
      self.lvlarea.updateLevel(level.load(None, None))
      self.lvlarea.lvl.levelname = self.text
      tinygui.popup("new level %s" % (self.text))

class TileSetNameArea(tinygui.TextInputArea):
  """An Input Field to display or change the name of the currently loaded Tileset."""

  def __init__(self, parent):
    """initialises the TileSetNameArea.

    takes a TileSetArea as its parent
    """
    self.tsa = parent
    tinygui.TextInputArea.__init__(self,
        self.tsa.lvlarea.lvl.tileset.name,
        pygame.Rect(0, 0, 0, 0))
    self.setPosition()

  def setPosition(self):
    self.rect = pygame.Rect(self.tsa.lvlarea.rect.w + 32, self.tsa.rect.y - 32, self.tsa.rect.w, 32)

  def inputDone(self):
    """Tries to load the tileset. If it fails, it displays an error"""
    try:
      self.tsa.lvlarea.lvl.tileset = level.Tileset(self.text)
      tinygui.popup("tileset %s loaded" % (self.text))
    except (IOError, pygame.error):
      tinygui.popup("tileset %s does not exist" % (self.text))

class TileSetArea(tinygui.Area):
  """This Area displays the TileSet of the current level.

  The user can select a tile from the Tileset which he wants to use for drawing
  """
  def __init__(self, parent):
    self.lvlarea = parent
    self.setPosition()
    self.tsna = TileSetNameArea(self)
    self.children = [self.tsna]
    self.tilesel = 0
    self.cursor = Cursor()

  def handleEvent(self, ev):
    """Handles mousebutton events to select a tileset or key events for scrolling."""

    if ev.type == MOUSEBUTTONDOWN and ev.button == 1:
      mpx = (ev.pos[0] - self.rect.x) / 32
      mpy = (ev.pos[1] - self.rect.y) / 32

      if 0 <= mpx < self.lvlarea.lvl.tileset.ttw and 0 <= mpy < self.lvlarea.lvl.tileset.tth:
        mpx += self.lvlarea.lvl.tileset.scroller.x
        mpy += self.lvlarea.lvl.tileset.scroller.y
        self.tilesel = mpx + mpy * self.lvlarea.lvl.tileset.ttw
        self.cursor.x = mpx
        self.cursor.y = mpy

    elif ev.type == KEYDOWN:
      md = {K_UP:    ( 0, -6),
            K_DOWN:  ( 0,  6),
            K_LEFT:  (-6,  0),
            K_RIGHT: ( 6,  0),
           }
      if ev.key == K_g:
        self.displayGrid = not self.displayGrid
      elif ev.key in md:
        self.lvlarea.lvl.tileset.scroller.rScroll(*md[ev.key])

  def setPosition(self):
    self.rect = pygame.Rect(32, 32, self.lvlarea.rect.w, self.lvlarea.rect.h * 32)
    self.rect.left = self.lvlarea.rect.w + 64
    try:
      self.tsna.setPosition()
    except:
      pass

  def draw(self):
    glPushMatrix()
    glTranslatef(self.rect.x / 32, self.rect.y / 32, 0)
    self.lvlarea.lvl.tileset.draw()
    self.lvlarea.lvl.tileset.showBorder()
    self.lvlarea.lvl.tileset.showGrid()
    self.lvlarea.lvl.tileset.scroller.scroll()
    self.cursor.draw()
    glPopMatrix()

    for ch in self.children:
      ch.draw()

class LevelArea(tinygui.Area):
  """The Level area is responsible for almost all stuff that happens.

  It creates a `LevelNameArea`, a `TileSetArea` and a `CommandInputArea` as
  its children and houses the Level class.
  """

  def __init__(self, levelname):
    self.scroller = scroll.ScrollView(15, 30)
    self.lvl = level.load(levelname, self.scroller)
    self.rect = pygame.Rect(0, 0, self.scroller.w * 32, self.scroller.h * 32 + 32)
    self.lna = LevelNameArea(self)
    self.tsa = TileSetArea(self)
    self.cmd = CommandInputArea(self)
    self.children = [self.lna, self.tsa, self.cmd]
    self.displayGrid = True
    self.cursor = Cursor()
    self.mbdown = False

  def updateLevel(self, newlevel = None):
    """Updates the level, replacing it with a new one if necessary.

    This function also adjusts the scroller and the positions of Areas that
    it holds, such as the `TileSetArea` which will move left or right depending
    on the size of the level.
    """

    if newlevel:
      self.lvl = newlevel
    self.lvl.setScroller(self.scroller)
    self.scroller.h = min(self.lvl.h, 21)
    self.scroller.w = min(self.lvl.w, 18)
    self.rect = pygame.Rect(0, 0, self.scroller.w * 32 + 32, self.scroller.h * 32 + 32)
    self.lna.setPosition()
    self.tsa.setPosition()
    self.tsa.tsna.setText(self.lvl.tileset.name)
    self.cursor.x, self.cursor.y = 0, 0

  def handleEvent(self, ev):
    if (ev.type == MOUSEBUTTONDOWN and ev.button == 1) or \
       (ev.type == MOUSEMOTION and self.mbdown):
      tpx = (ev.pos[0] - self.rect.x - 32) / 32
      tpy = (ev.pos[1] - self.rect.y - 32) / 32

      self.mbdown = True

      if 0 <= tpx < self.scroller.areaw and 0 <= tpy < self.scroller.areah:
        tpx += self.scroller.x
        tpy += self.scroller.y
        if 0 <= tpx < self.lvl.w and 0 <= tpy < self.lvl.h:
          self.lvl.level[tpy][tpx] = self.tsa.tilesel
          self.cursor.x = tpx
          self.cursor.y = tpy
    elif ev.type == MOUSEBUTTONUP:
      self.mbdown = False
    elif ev.type == KEYDOWN:
      md = {K_UP:    ( 0, -6),
            K_DOWN:  ( 0,  6),
            K_LEFT:  (-6,  0),
            K_RIGHT: ( 6,  0),
           }
      if ev.key == K_g:
        self.displayGrid = not self.displayGrid
      elif ev.key in md:
        self.scroller.rScroll(*md[ev.key])

  def draw(self):
    glPushMatrix()
    glTranslatef(1 + self.rect.x / 32, 1 + self.rect.y / 32, 0)

    glPushMatrix()
    self.scroller.scroll()
    self.lvl.draw()
    self.cursor.draw()
    glPopMatrix()

    self.lvl.showBorder()
    if self.displayGrid:
      self.lvl.showGrid()

    glPopMatrix()

    for ch in self.children:
      ch.draw()

if __name__ == "__main__":
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
