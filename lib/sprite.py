import res
from OpenGL.GL import *
import level
from timing import timer

class Tilecollider:
  def __init__(self, m, c, solidtype):
    """m and c define a linear function of the form:

    f(x) = m * x + c

    solidtype is -1, if the part above the line is blocking
    and 1, if the part below it is blocking.
    if it's a jump-through tile, it's 0"""
    self.m = m
    self.c = c
    self.st = solidtype

  def collide(self, x, y, mx, my):
    rx = x % 1
    ry = y % 1

    if (self.st == 0 and my >= 0) or self.st == 1:
      return rx >= self.m * rx + self.c
    else:
      return rx <= self.m * rx + self.c

  def putOutside(self, x, y, mx, my):
    if self.st != 0:
        y += self.st * 1    
    else: # still needs some magic
        y += 1
    return [x, y, mx, my]

tiletypes = [\
  Tilecollider(0,  0, -1),  # air, never block
  Tilecollider(0,  0,  1),   # wall, always block

  Tilecollider(-1, 1,  1),   # slope /
  Tilecollider(1,  0,  1),   # slope \
  
  Tilecollider(-1, 1, -1),   # /
  Tilecollider(1,  0, -1),   # \

  Tilecollider(-1, 1,  0),   # /
  Tilecollider(1,  0,  0),   # \

  Tilecollider(0, 0, 0),
  Tilecollider(0, 0, 0),

  Tilecollider(-0.5, 1,   1),
  Tilecollider(-0.5, 0.5, 1),
  Tilecollider( 0.5, 0,   1),
  Tilecollider( 0.5, 0.5, 1),

  Tilecollider(-2,  1, 1),
  Tilecollider(-2,  2, 1), # 15
  Tilecollider( 2, -1, 1),
  Tilecollider( 2,  0, 1),

  Tilecollider(-0.5, 1,   -1),
  Tilecollider(-0.5, 0.5, -1),
  Tilecollider( 0.5, 0  , -1),
  Tilecollider( 0.5, 0.5, -1),

  Tilecollider(-2, 1, -1),
  Tilecollider(-2, 2, -1),
  Tilecollider(2, -1, -1),
  Tilecollider(2, 0,  -1),

  Tilecollider(-0.5, 1,   0),
  Tilecollider(-0.5, 0.5, 0),
  Tilecollider( 0.5, 0  , 0),
  Tilecollider( 0.5, 0.5, 0),

  Tilecollider(-2, 1, 0),
  Tilecollider(-2, 2, 0),
  Tilecollider(2, -1, 0),
  Tilecollider(2, 0,  0),

  Tilecollider(-5000, 2500.5, -1),
  Tilecollider(-5000, 2500.5, 1),
  Tilecollider(0, 0.5, -1),
  Tilecollider(0, 0.5, 1),
]

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
    hit = self.checkCollision(self.vx * timer.curspd, self.vy * timer.curspd)

    if hit:
      pass
    else:
      self.x = self.vx * timer.curspd
      self.y = self.vy * timer.curspd

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

  def checkCollision(self, vx, vy):
    
    x = self.x
    y = self.y
    col = self.lev.tileset.collision[self.lev.level[int(x)][int(y)]]
    if tiletypes[col].collide(x, y, vx, vy):
      newpos = tiletypes[col].putOutside(x, y, vx, vy)
      self.x = x
      self.y = y
      self.vx = vx
      self.vy = vy
      return True
    else:
      return False

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
