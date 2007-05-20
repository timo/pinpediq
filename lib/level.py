import res
from OpenGL.GL import *
import random
# Collisions:
# 0:  none
# 1:  full
# 2:  /
# 3:  \

class Level:
  def __init__(self, levelname):
    self.levelname = levelname

    lf = open("data/levels/%s.pql" % levelname)
    
    tilemapname = lf.readline().strip()
    self.size = [int(a) for a in lf.readline().strip().split(",")]

    self.level = []
    for row in range(self.size[1]):
      self.level.append([int(a) for a in lf.readline().strip().split()])

    self.tilemap = res.getTexture(tilemapname)

  def draw(self):
    def quad(col, row, numx, numy):
      # this describes the position of the upper left corner
      w = 1.0 / numx
      x = col * w
      h = 1.0 / numy
      y = row * h
      glBegin(GL_QUADS)
      
      glTexCoord2f(x, y)
      glVertex2f(0, 1)

      glTexCoord2f(x, y + h)
      glVertex2f(0, 0)

      glTexCoord2f(x + w, y + h)
      glVertex2f(1, 0)

      glTexCoord2f(x + w, y)
      glVertex2f(1, 1)

      glEnd()

    self.tilemap.bind()

    for x in range(0, self.size[0]):
      for y in range(0, self.size[1]):
        glPushMatrix()
        glTranslatef(x, -y, 0)
        quad(self.level[y][x] % 4,self.level[y][x] / 4, 4, 4) # TODO: lol
        glPopMatrix()
