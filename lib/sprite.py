import res
from OpenGL.GL import *
import level
from timing import timer

class Sprite:
  def __init__(self, imagename):
    self.img = res.getTexture(imagename)
    (self.x,  self.y)  = (0, 0)
    (self.vx, self.vy) = (0, 0)
    (self.h, self.w) = (1.0, 1.0)

    self.physics = 'standing'

    self.lev = level.getCurrent()

    self.state = 'normal'
    self.nextstate = -1
    
  def setstate(self, state, duration = -1):
    self.state = state
    self.nextstate = duration

  def move(self):
    self.vy += 5 * timer.curspd
    self.checkCollision(self.vx * timer.curspd, self.vy * timer.curspd)

    if self.nextstate != -1:
      self.nextstate -= timer.curspd
      if self.nextstate < 0:
        self.setstate('normal')

  def mark(self, x, y, w, h):
    glDisable(GL_TEXTURE_2D)
    glBegin(GL_LINES)
    glVertex2f(0 + x, y)
    glVertex2f(0 + x + w, y + h)
    glEnd()
    glEnable(GL_TEXTURE_2D)

  def markTile(self, x, y):
    glDisable(GL_TEXTURE_2D)
    glBegin(GL_QUADS)
    glVertex2f(x, y + 1)
    glVertex2d(x + 1, y + 1)
    glVertex2f(x + 1, y)
    glVertex2f(x, y)
    glEnd()
    glEnable(GL_TEXTURE_2D)

  def checkVerLine(self, x, y):
    tilx = int(x)
    tily = int(y)
    endy = int(y + self.h)
    
    #glColor4f(1.0, 0.0, 0.0, 0.25)

    #self.mark(x, y, 0, self.h)
    if tily != y - (1.0 - self.h):
      endy += 1

    for ty in range(tily, endy) or [tily]:
      #self.markTile(tilx, ty)
      if ty >= self.lev.h or tilx >= self.lev.w:
        return True
      if self.lev.collision[self.lev.level[ty][tilx]] == 1:
        return True

    return False

  def checkHorLine(self, x, y):
    tilx = int(x)
    tily = int(y)
    endx = int(x + self.w)
    #glColor4f(0.0, 1.0, 0.0, 0.25)
    #self.mark(x, y, self.w, 0)

    if tilx != x - (1.0 - self.w):
      endx += 1

    for tx in range(tilx, endx) or [tilx]:
      #self.markTile(tx, tily)
      if tily >= self.lev.h or tx >= self.lev.w:
        return True
      if self.lev.collision[self.lev.level[tily][tx]] == 1:
        return True
      elif self.lev.collision[self.lev.level[tily][tx]] in [4, 5] and self.vy > 0 and tily - self.y >= self.h:
        return True

    return False

  def checkCollision(self, vx, vy):
    if vx > 0:
      if self.checkVerLine(self.x + vx + self.w, self.y):
        self.x = int(self.x + vx) - self.w + 1
        self.vx = 0
      else:
        self.x += vx
    elif vx < 0:
      if self.checkVerLine(self.x + vx, self.y):
        self.x = int(self.x + vx) + 1
        self.vx = 0
      else:
        self.x += vx

    if vy > 0:
      if self.checkHorLine(self.x, self.y + vy + self.h):
        self.y = int(self.y + vy) - self.h + 1
        self.vy = 0
        self.physics = 'standing'
      else:
        self.y += vy
        self.physics = 'falling'
    elif vy < 0:
      if self.checkHorLine(self.x, self.y + vy):
        self.y = int(self.y + vy) + 1
        self.vy = self.vy * -0.25
        self.physics = 'falling'
      else:
        self.y += vy
        self.physics = 'falling'

  def draw(self, image = None, alpha = 1.0):
    if image:
      image.bind()
    else:
      self.img.bind()
    glColor4f(1.0, 1.0, 1.0, alpha)

    glPushMatrix()
    glTranslatef(self.x, self.y, 0)
    if self.vx < 0:
      glTranslatef(self.w, 0, 0)
      glScalef(-1, 1, 0)
    glScalef(self.w, self.h, 1)

    glBegin(GL_QUADS)
    
    glTexCoord2f(0, 1)
    glVertex2i(0, 1)

    glTexCoord2f(0, 0)
    glVertex2i(0, 0)

    glTexCoord2f(1, 0)
    glVertex2i(1, 0)

    glTexCoord2f(1, 1)
    glVertex2i(1, 1)

    glEnd()
    
    glPopMatrix()
