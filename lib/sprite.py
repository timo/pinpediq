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
      if self.lev.tileset.collision[self.lev.level[ty][tilx]] == 1:
        return True

    return False

  def pointCollides(self, x, y, vx, vy):
    col = self.tileset.collision[self.level[y][x]]
    rx = x % 1
    ry = y % 1
    if col == 0:   # air
      return False

    elif col == 1: # wall
      return True

    elif col == 2 or (col == 6 and vy > 0): # / slope with solid part at bottom
      return rx >= 1 - ry
    elif col == 3 or (col == 7 and vy > 0): # \ slope
      return rx >= ry

    elif col == 4: # / slope with solid at top
      return rx <= 1 - ry
    elif col == 5: # \ slope
      return rx <= ry

    elif col in [8, 9]: # platforms that only blocks from above
      return vy > 0

    elif col == 10 or (col == 26 and vy >= 0): # shallow slope / left half bottom-solid or fall-block
      return ry <= 1 - 0.5 * rx
    elif col == 11 or (col == 27 and vy >= 0): # shallow slope / right half bottom-solid or fall-block
      return ry <= 0.5 - 0.5 * rx

    elif col == 12 or (col == 28 and vy >= 0): # shallow slope \ left half
      return ry >= 0.5 * rx
    elif col == 13 or (col == 29 and vy >= 0): # shallow slope \ right half
      return ry >= 0.5 + 0.5 * rx

    elif col == 14 or (col == 30 and vy >= 0): # steep slope / lower half
      return ry >= 1 - 2 * rx
    elif col == 15 or (col == 31 and vy >= 0): # steep slope / upper half
      return ry >= 2 - 2 * rx

    elif col == 16 or (col == 32 and vy >= 0): # steep slope \ lower
      return ry >= -1 + 2 * rx
    elif col == 17 or (col == 33 and vy >= 0): # steep slope \ upper
      return ry >= 2 * rx
    
    elif col == 18:  #  shallow slope / left half top-solid
      return ry >= 1 - 0.5 * rx
    elif col == 19:  #  shallow slope / right half
      return ry >= 0.5 - 0.5 * rx

    elif col == 20:  #  shallow slope \ l
      return ry <= 0.5 * rx
    elif col == 21:  #  shallow slope \ r
      return ry <= 0.5 + 0.5 * rx

    elif col == 22:  #  steep / l
      return ry <= 1 - 2 * rx
    elif col == 23:  #  steep / u
      return ry <= 2 - 2 * rx

    elif col == 24:  #  steep \ l
      return ry <= -1 + 2 * rx
    elif col == 25:  #  steep \ u
      return ry <= 2 * rx

    elif col == 34:  # left half
      return rx <= 0.5
    elif col == 35:  # right halg
      return rx >= 0.5
    elif col == 36:  # upper half
      return ry <= 0.5
    elif col == 37:  # lower half
      return ry >= 0.5

    else:
      return True

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
      if self.lev.tileset.collision[self.lev.level[tily][tx]] == 1:
        return True
      elif self.lev.tileset.collision[self.lev.level[tily][tx]] in [8, 9] and self.vy > 0 and tily - self.y >= self.h:
        return True

    return False

  def checkCollision(self, vx, vy):
    hit = [False] * 4 # left, right, top, bottom
    if vx > 0:
      if self.checkVerLine(self.x + vx + self.w, self.y):
        self.x = int(self.x + vx) - self.w + 1
        #self.vx = 0
        hit[1] = True
      else:
        self.x += vx
    elif vx < 0:
      if self.checkVerLine(self.x + vx, self.y):
        self.x = int(self.x + vx) + 1
        #self.vx = 0
        hit[0] = True
      else:
        self.x += vx

    if vy > 0:
      if self.checkHorLine(self.x, self.y + vy + self.h):
        self.y = int(self.y + vy) - self.h + 1
        self.vy = 0
        self.physics = 'standing'
        hit[3] = True
      else:
        self.y += vy
        self.physics = 'falling'
    elif vy < 0:
      if self.checkHorLine(self.x, self.y + vy):
        self.y = int(self.y + vy) + 1
        self.vy = self.vy * -0.25
        self.physics = 'falling'
        hit[2] = True
      else:
        self.y += vy
        self.physics = 'falling'

    if hit[0]:
      self.hitLeft()
    elif hit[1]:
      self.hitRight()
    if hit[2]:
      self.hitTop()
    elif hit[3]:
      self.hitBottom()

  def hitLeft(self):   pass
  def hitRight(self):  pass
  def hitTop(self):    pass
  def hitBottom(self): pass

  def draw(self, image = None, alpha = 1.0):
    if image:
      image.bind()
    else:
      self.img.bind()

    if self.state == "ouch" and timer.blink(0.1):
      glColor4f(1.0, 1.0, 1.0, alpha / 2)
    else:
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
