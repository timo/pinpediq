import res
from OpenGL.GL import *
import level
from physics import *
from timing import timer

class Sprite:
  def __init__(self, imagename):
    self.img = res.getTexture(imagename)
    self.physics = FALLING
    (self.x,  self.y)  = (0, 0)
    (self.vx, self.vy) = (0, 0)
    (self.h, self.w) = (1.0, 1.0)

    self.lev = level.getCurrent()
    
  def move(self):
    self.vy += 5 * timer.curspd
    self.checkCollision(self.vx * timer.curspd, self.vy * timer.curspd)

  def mark(self, x, y, w, h):
    glDisable(GL_TEXTURE_2D)
    glColor4f(1.0, 0.0, 0.0, 0.25)
    glBegin(GL_LINES)
    glVertex2f(10 + x, -y)
    glVertex2f(10 + x + w, -y - h)
    glEnd()
    glEnable(GL_TEXTURE_2D)

  def markTile(self, x, y):
    glDisable(GL_TEXTURE_2D)
    glColor4f(1.0, 0.0, 0.0, 0.25)
    glBegin(GL_QUADS)
    glVertex2f(10 + x, -y)
    glVertex2d(10 + x + 1, -y)
    glVertex2f(10 + x + 1, -y - 1)
    glVertex2f(10 + x, -y -1)
    glEnd()
    glEnable(GL_TEXTURE_2D)

  def checkVerLine(self, x, y):
    tilx = int(x)
    tily = int(y)
    endy = int(y + self.h)

    self.mark(x, y, 0, self.h)
    if tily != y:
      endy += 1

    for ty in range(tily, endy):
      self.markTile(tilx, ty)
      if self.lev.collision[self.lev.level[ty][tilx]] == 1:
        return True

    return False

  def checkHorLine(self, x, y):
    tilx = int(x)
    tily = int(y)
    endx = int(x + self.w)
    self.mark(x, y, self.w, 0)

    if tilx != x:
      endx += 1

    for tx in range(tilx, endx):
      self.markTile(tx, tily)
      if self.lev.collision[self.lev.level[tily][tx]] == 1 or (self.lev.collision[self.lev.level[tily][tx]] in [4, 5] and self.vy > 0):
        return True

    return False

  def checkCollision(self, vx, vy):
    # horizontal movement
    #newx = self.x
    #newy = self.y
    if vy > 0:
      if self.checkHorLine(self.x, self.y + vy + self.h):
        self.y = int(self.y + vy) + (1.0 - self.h)
        self.vy = 0
        self.physics = STANDING
      else:
        self.y += vy
        self.physics = FALLING
    elif vy < 0:
      if self.checkHorLine(self.x, self.y + vy):
        self.y = int(self.y + vy) + self.h
        self.vy = self.vy * -0.25
      else:
        self.y += vy
        self.physics = FALLING

    if vx > 0:
      if self.checkVerLine(self.x + vx + self.w, self.y):
        self.x = int(self.x + vx) - (1.0 - self.w)
        self.vx = 0
      else:
        self.x += vx
    elif vx < 0:
      if self.checkVerLine(self.x + vx, self.y):
        self.x = int(self.x + vx) + 1
        self.vx = 0
      else:
        self.x += vx

    #self.x = newx
    #self.y = newy

  def draw(self):
    self.img.bind()
    glColor4f(1.0, 1.0, 1.0, 1.0)

    glPushMatrix()
    glTranslatef(self.x + 0.5 * (1.0 - self.w), -self.y - 0.5 * (1.0 - self.h), 0)

    glBegin(GL_QUADS)
    
    glTexCoord2f(0, 0)
    glVertex2i(0, 1)

    glTexCoord2f(0, 1)
    glVertex2i(0, 0)

    glTexCoord2f(1, 1)
    glVertex2i(1, 0)

    glTexCoord2f(1, 0)
    glVertex2i(1, 1)

    glEnd()
    
    glPopMatrix()
