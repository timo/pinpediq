import res
from OpenGL.GL import *
import random
from physics import *
# Collisions:
# 0:  none
# 1:  full
# 2:  /
# 3:  \

class Level:
  def __init__(self, levelname):
    self.levelname = levelname

    lf = open("data/levels/%s.pql" % levelname, "r")
    
    tilemapname = lf.readline().strip()
    self.size = [int(a) for a in lf.readline().strip().split(",")]

    self.level = []
    for row in range(self.size[1]):
      self.level.append([int(a) for a in lf.readline().strip().split()])

    self.tilemap = res.getTexture(tilemapname)
    
    cf = open("data/tilemaps/%s.pqt" % tilemapname, "r")
    self.ttc = int(cf.readline().strip())
    self.collision = []
    for l in cf.readlines():
      self.collision.append(int(l))

  def draw(self):
    def quad(self, col, row, numx, numy):
      # this describes the position of the upper left corner
      w = 1.0 / numx
      x = col * w
      h = 1.0 / numy
      y = row * h
      zx = 1 / (2.0 * self.tilemap.w)
      zy = 1 / (2.0 * self.tilemap.h)
      #zx = 0
      #zy = 0

      glBegin(GL_QUADS)
      
      glTexCoord2f(x + zx, y + zy)
      glVertex2i(0, 1)

      glTexCoord2f(x + zx, y + h - zy)
      glVertex2i(0, 0)

      glTexCoord2f(x + w - zx , y + h - zx)
      glVertex2i(1, 0)

      glTexCoord2f(x + w - zy, y + zy)
      glVertex2i(1, 1)

      glEnd()

    self.tilemap.bind()

    glColor4f(1.0, 1.0, 1.0, 1.0)
    for x in range(0, self.size[0]):
      for y in range(0, self.size[1]):
        glPushMatrix()
        glTranslatef(x, -y, 0)
        quad(self, self.level[y][x] % self.ttc,self.level[y][x] / self.ttc, self.ttc, self.ttc)
        glPopMatrix()

  def showCollision(self):
    glColor4f(0.0, 1.0, 1.0, 0.25)
    glDisable(GL_TEXTURE_2D)
    for x in range(0, self.size[0]):
      for y in range(0, self.size[1]):
        glPushMatrix()
        glTranslatef(x, -y, 0)
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
def load(levelname):
  global __level__
  __level__ = Level(levelname)
  return __level__

def getCurrent():
  global __level__
  return __level__
