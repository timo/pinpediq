from sprite import Sprite
from timing import timer
import random
import res

NORMAL    = 1
OUCH      = 2
FROZEN    = 3
TWISTING  = 4
DROWNING  = 5
BURNING   = 6
PARALYSED = 7
DEAD      = 8

class enemy(Sprite):
  def __init__(self, enemyname):
    Sprite.__init__(self, enemyname)
    self.health = 100
    self.state = NORMAL
    self.nextstate = -1
    self.ice = False

  def draw(self, image = None):
    Sprite.draw(self, image)
    if self.state == FROZEN and not self.ice:
      self.ice = True
      self.draw(res.getTexture("iceblock"))
      self.ice = False

  def move(self):
    if self.state == FROZEN:
      if self.vy < -0.1:
        self.vx *= 0.99
        self.vy *= 0.999
      else:
        self.vy = -5 * timer.curspd
        self.vx = 0
    elif self.state == TWISTING:
      self.vx = random.random()
    elif self.state == PARALYSED:
      self.vx *= 0.9
    Sprite.move(self)
    if self.nextstate != -1:
      self.nextstate -= timer.curspd
      if self.nextstate < 0:
        if self.state in [NORMAL, OUCH, TWISTING, DROWNING, BURNING, PARALYSED]:
          if self.health < 0:
            self.state = DEAD
          else:
            self.state = NORMAL
          self.nextstate = -1
        elif self.state == FROZEN:
          self.health = -1
          self.state = OUCH
          self.nextstate = 0.5
          self.vy = random.random() * -4
          self.vx = random.random() * 4 - 2
