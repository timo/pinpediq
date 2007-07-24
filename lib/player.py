from sprite import Sprite
import res

class Player(Sprite):
  def __init__(self):
    self.img = res.getTexture("player")
    self.x, self.y = 0, 0
    self.vx, self.vy = 0, 0
    self.w, self.h = 1.0, 0.9
    self.health = 100

  #def draw(self):
    # TODO: draw sword/active weapon
