import res, scroll
from OpenGL.GL import *
import random
# Collisions:
# 0:  none
# 1:  full
# 2:  /
# 3:  \

class Tileset:
  def __init__(self, tilesetname = "__dummy__"):
    self.name = tilesetname
    self.img = res.getTexture(self.name)
    self.w = self.img.w
    self.h = self.img.h

    if self.name != "__dummy__":
      cf = open("data/tilemaps/%s.pqt" % self.name, "r")
      self.ttw, self.tth = [int(a) for a in cf.readline().strip().split(",")]
      self.collision = []
      for l in cf.readlines():
        self.collision.extend([int(lp) for lp in l.split(" ") if lp])
    else:
      self.ttw, self.tth = 4, 4
      self.collisions = [0] * 16

  def bind(self):
    self.img.bind()

class TilesetView(Tileset):
  def __init__(self, name, scroller = None):
    Tileset.__init__(self, name)
    self.scroller = scroller or scroll.ScrollView(10, 10)
    self.scroller.changeArea(self.ttw, self.tth)
    self.scroller.scrollTo(0, 0)
  
  def quad(self, col, row):
    # this describes the position of the upper left corner
    w = 1.0 / self.ttw
    x = col * w
    h = 1.0 / self.tth
    y = row * h
    zx = 1 / (2.0 * self.w)
    zy = 1 / (2.0 * self.h)

    glBegin(GL_QUADS)
    
    glTexCoord2f(x + zx, y + zy)
    glVertex2i(0, 0)

    glTexCoord2f(x + zx, y + h - zy)
    glVertex2i(0, 1)

    glTexCoord2f(x + w - zx , y + h - zx)
    glVertex2i(1, 1)

    glTexCoord2f(x + w - zy, y + zy)
    glVertex2i(1, 0)

    glEnd()

  def draw(self):
    glEnable(GL_TEXTURE_2D)
    self.bind()
    glPushMatrix()
    sx, sy, sw, sh = self.scroller.levelScroll()
    self.scroller.scroll()
    glColor4f(1.0, 1.0, 1.0, 1.0)
    for tx in range(sx, sx + sw):
      for ty in range(sy, sy + sh):
        glPushMatrix()
        glTranslatef(tx, ty, 0)
        self.quad(tx, ty)
        glPopMatrix()

    glPopMatrix()

  def showBorder(self):
    glColor4f(1, 1, 1, 1)
    glDisable(GL_TEXTURE_2D)

    glBegin(GL_LINE_LOOP)
    glVertex2f(0, 0)
    glVertex2f(0, self.scroller.h)
    glVertex2f(self.scroller.w, self.scroller.h)
    glVertex2f(self.scroller.w, 0)
    glEnd()

  def showGrid(self):
    glColor4f(1, 1, 1, 1)
    glDisable(GL_TEXTURE_2D)
    
    glBegin(GL_LINES)
    for x in range(self.scroller.w):
      glVertex2f(x, 0)
      glVertex2f(x, self.scroller.h)
    for y in range(self.scroller.h):
      glVertex2f(0, y)
      glVertex2f(self.scroller.w, y)
    glEnd()

class DummyTileset(Tileset):
  def __init__(self):
    self.collision = []
    self.img = res.getTexture("__dummy__")
    self.name = "__dummy__"
    self.ttw = 4
    self.tth = 4

class DummyTilesetView(TilesetView):
  def __init__(self):
    TilesetView.__init__("__dummy__", scroll.ScrollView(4, 4))

class Level:
  def __init__(self, levelname = None, scroller = None, tilesetclass=Tileset):
    if levelname:
      self.load(levelname, tilesetclass)
    else:
      (self.w, self.h) = (4, 4)
      self.level = [[0, 1, 2, 3],
                    [3, 2, 1, 0],
                    [0, 1, 2, 3],
                    [3, 2, 1, 0]]
      
      self.tileset = DummyTileset()

    self.setScroller(scroller or scroll.ScrollView(self.w, self.h))

  def setScroller(self, scroller):
    self.scroller = scroller
    self.scroller.changeArea(self.w, self.h)
    self.scroller.scrollTo(0, 0)

  def load(self, levelname, tilesetclass = Tileset):
    self.levelname = levelname

    lf = open("data/levels/%s.pql" % levelname, "r")
    
    self.tilesetname = lf.readline().strip()
    (self.w, self.h) = [int(a) for a in lf.readline().strip().split(",")]

    self.level = []
    for row in range(self.h):
      self.level.append([int(a) for a in lf.readline().strip().split()])

    lf.close()

    self.tileset = tilesetclass(self.tilesetname)

  def save(self):
    lf = open("data/levels/%s.pql" % self.levelname, "w")

    lf.write(self.tileset.name + "\n")
    lf.write("%s, %s" % (self.w, self.h) + "\n")

    for row in self.level:
      lf.write(" ".join(str(a) for a in row) + "\n")

    lf.close()

  def quad(self, col, row, numx, numy):
    # this describes the position of the upper left corner
    w = 1.0 / numx
    x = col * w
    h = 1.0 / numy
    y = row * h
    zx = 1 / (2.0 * self.tileset.w)
    zy = 1 / (2.0 * self.tileset.h)

    glBegin(GL_QUADS)
    
    glTexCoord2f(x + zx, y + zy)
    glVertex2i(0, 0)

    glTexCoord2f(x + zx, y + h - zy)
    glVertex2i(0, 1)

    glTexCoord2f(x + w - zx , y + h - zx)
    glVertex2i(1, 1)

    glTexCoord2f(x + w - zy, y + zy)
    glVertex2i(1, 0)

    glEnd()

  def draw(self):
    if self.scroller:
      sx, sy, sw, sh = self.scroller.levelScroll()
    else:
      sx, sy, sw, sh = 0, 0, self.w, self.h

    self.tileset.bind()
    glEnable(GL_TEXTURE_2D)
    glColor4f(1.0, 1.0, 1.0, 1.0)
    for x in range(  sx, sx + sw):
      for y in range(sy, sy + sh):
        glPushMatrix()
        glTranslatef(x, y, 0)
        self.quad(self.level[y][x] % self.tileset.ttw, self.level[y][x] / self.tileset.ttw, self.tileset.ttw, self.tileset.tth)
        glPopMatrix()

  def showBorder(self):
    glColor4f(1, 1, 1, 1)
    glDisable(GL_TEXTURE_2D)

    glBegin(GL_LINE_LOOP)
    glVertex2f(0, 0)
    glVertex2f(0, self.scroller.h)
    glVertex2f(self.scroller.w, self.scroller.h)
    glVertex2f(self.scroller.w, 0)
    glEnd()

  def showGrid(self):
    glColor4f(1, 1, 1, 1)
    glDisable(GL_TEXTURE_2D)
    
    glBegin(GL_LINES)
    for x in range(self.scroller.w):
      glVertex2f(x, 0)
      glVertex2f(x, self.scroller.h)
    for y in range(self.scroller.h):
      glVertex2f(0, y)
      glVertex2f(self.scroller.w, y)
    glEnd()

  def showCollision(self):
    glColor4f(0.0, 1.0, 1.0, 0.25)
    glDisable(GL_TEXTURE_2D)
    for x in range(0, self.w):
      for y in range(0, self.h):
        glPushMatrix()
        glTranslatef(x, y, 0)
        v = self.collision[self.level[y][x]]
        if v == 1:
          glBegin(GL_QUADS)
          glVertex2i(0, 0)
          glVertex2i(1, 0)
          glVertex2i(1, 1)
          glVertex2i(0, 1)
          glEnd()
        elif v == 2 or v == 3:
          glBegin(GL_TRIANGLES)
          glVertex2i(0, 0)
          glVertex2i(1, 0)
          if v == 2:
            glVertex2f(1, 1)
          else:
            glVertex2f(0, 1)
          glEnd()
        elif v == 4 or v == 5:
          glBegin(GL_QUADS)
          glVertex2f(0, 0.8)
          glVertex2i(0, 1)
          glVertex2i(1, 1)
          glVertex2f(1, 0.8)
          glEnd()

          glBegin(GL_TRIANGLE_STRIP)
          glVertex2f(0.5, 1.1)
          glVertex2f(0.25, 0.9)
          glVertex2f(.75, 0.9)
          if v == 4:
            glVertex2f(0.5, 0.7)
          glEnd()
        glPopMatrix()
    glEnable(GL_TEXTURE_2D)

__level__ = None
def load(levelname, scroller = None, tilesetclass = Tileset):
  global __level__
  __level__ = Level(levelname, scroller, tilesetclass)
  return __level__

def getCurrent():
  global __level__
  return __level__
