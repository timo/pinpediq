from OpenGL.GL import *

class ScrollView:
  def __init__(self, w, h):
    self.w, self.areaw = w, w
    self.h, self.areah = h, h
    self.scrollTo(0, 0)

  def changeArea(self, naw, nah):
    self.areaw = naw
    self.areah = nah
    self.w = min(self.w, self.areaw)
    self.h = min(self.h, self.areah)
    self.x = min(self.areaw - self.w, self.x)
    self.y = min(self.areah - self.h, self.y)

  def scrollTo(self, x, y):
    self.x = min(self.areaw - self.w, max(x, 0))
    self.y = min(self.areah - self.h, max(y, 0))

  def rScroll(self, rx, ry):
    self.scrollTo(self.x + rx, self.y + ry)

  def scroll(self):
    glTranslatef(-self.x, -self.y, 0)

  def levelScroll(self):
    return (int(x) for x in (self.x, self.y, self.w, self.h))
  
  def centerOn(self, x, y, speed = 1):
    self.rScroll(speed * (x - self.x - self.w * 0.5), speed * (y - self.y - self.h * 0.5))

  def __repr__(self):
    return "ScrollView: viewing part (%s, %s, %s, %s) of area (0, 0, %s, %s)" % (self.x, self.y, self.w, self.h, self.areaw, self.areah)
