from sprite import Sprite
from timing import timer
import random

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

  def move(self):
    if self.state == FROZEN:
      self.vx = 0
      self.vy = 0
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
          self.health = 0
          self.state = OUCH
          print "ouch!"
          self.nextstate = 0.5
