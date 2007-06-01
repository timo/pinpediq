from timing import timer
from OpenGL.GL import *
from math import sin, cos, sqrt
from sprite import *
import random

def frange(start, end, step):
  w = end - start
  for i in xrange(int(w / step)):
    yield start + i * step

class RectDamage:
  def __init__(self, x, y, w, h, vx, vy, lifetime, damage = 10):
    self.x = x
    self.y = y
    self.w = w
    self.h = h
    self.vx = vx
    self.vy = vy
    self.lifetime = lifetime
    self.damage = damage

  def move(self):
    self.x += self.vx * timer.curspd
    self.y += self.vy * timer.curspd
    if self.lifetime != -1:
      self.lifetime -= timer.curspd
      if self.lifetime < 0:
        self.lifetime = 0

  def check(self, other):
    if (self.x <= other.x <= self.x + self.w or\
        self.x <= other.x + other.w <= self.x + self.w) and\
       (self.y <= other.y <= self.y + self.h or\
        self.y <= other.y + other.h <= self.y + self.h):
      return True

  def draw(self):
    glPushMatrix()

    glDisable(GL_TEXTURE_2D)

    glTranslatef(self.x, self.y, 0)
    glColor4f(1.0, 0.0, 1.0, 0.25)

    glBegin(GL_QUADS)

    glVertex2f(0, self.w)
    glVertex2f(0, 0)
    glVertex2f(self.h, 0)
    glVertex2f(self.h, self.w)

    glEnd()

    glPopMatrix()

  def hit(self, other):
    if other.state == NORMAL and self.damage > 0:
      dvx = other.x + other.w / 2. - (self.x + self.w / 2.)
      dvy = other.y + other.h / 2. - (self.y + self.h / 2.)
      len = sqrt(dvx ** 2 + dvy ** 2)
      dvx /= len
      dvy /= len
      other.vx = dvx * self.damage / 5 + random.random() - 0.5
      other.vy = dvy * self.damage / 5 - 2 + random.random() - 0.5

      other.health -= self.damage
      if random.random() < 0.1:
        other.setstate(FROZEN, 5)
        other.vy -= 2
      else:
        other.setstate(OUCH, 1)

class ArcDamage(RectDamage):
  def __init__(self, x, y, vx, vy, ra, sa, ea, lifetime, damage = 10):
    self.x = x
    self.y = y
    self.vx = vx
    self.vy = vy
    self.w = 0
    self.h = 0
    self.rad = ra
    self.sa = sa
    self.ea = ea
    self.lifetime = lifetime
    self.maxlifetime = lifetime
    self.damage = damage

  def draw(self):
    glPushMatrix()

    glTranslatef(self.x, self.y, 0)
    glColor4f(1.0, 0.0, 1.0, 0.1)
    glDisable(GL_TEXTURE_2D)

    glBegin(GL_TRIANGLE_FAN)

    glVertex2f(0, 0)
    for ang in frange(self.sa, self.ea, 0.1):
      px = cos(ang) * self.rad
      py = sin(ang) * self.rad
      glVertex2f(px, py)
  
    glEnd()

    glColor4f(1.0, 0.0, 0.0, 0.75)

    glBegin(GL_TRIANGLES)
    glVertex2f(0, 0)
    an = self.sa + (self.ea - self.sa) * self.lifetime / self.maxlifetime
    for ang in [an - 0.2, an + 0.2]:
      px = cos(ang) * self.rad
      py = sin(ang) * self.rad
      glVertex2f(px, py)
    glEnd()

    glPopMatrix()

  def check(self, other):
    # is the arc center inside the AABB?
    if other.x <= self.x <= other.x + other.w and\
       other.y <= self.y <= other.y + other.h:
      return True
    # check a few points on the arc
    for ang in frange(self.sa, self.ea, (self.ea - self.sa) / 8.):
      px = self.x + cos(ang) * self.rad
      py = self.y + sin(ang) * self.rad
      if other.x <= px <= other.x + other.w and\
         other.y <= py <= other.y + other.h:
        return True
