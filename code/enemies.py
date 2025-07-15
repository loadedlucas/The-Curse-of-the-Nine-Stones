from settings import *
from random import choice

class Spider(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, collision_sprites):
        super().__init__(groups)
        self.frames, self.frame_index = frames, 0
        self.state = "run"
        self.image = self.frames[self.state][self.frame_index]
        self.rect = self.image.get_frect(topleft = pos)
        self.hitbox_rect = self.rect.inflate(-160, 0)

        self.direction = choice((-1, 1))
        self.collision_rects = [sprite.rect for sprite in collision_sprites]
        self.speed = 600

    def update(self, dt):
        self.rect.center = self.hitbox_rect.center
        # animate
        self.frame_index += ANIMATION_SPEED * dt
        self.image = self.frames[self.state][int(self.frame_index % len(self.frames[self.state]))]
        if self.direction < 0:
            self.image = pygame.transform.flip(self.image, True, False)

        # move
        self.hitbox_rect.x += self.direction * self.speed * dt

        # reverse direction if cliff
        floor_rect_right = pygame.FRect(self.hitbox_rect.bottomright, (20, 20))
        floor_rect_left = pygame.FRect(self.hitbox_rect.bottomleft, (-20, 20))

        if floor_rect_right.collidelist(self.collision_rects) < 0 and self.direction > 0 or floor_rect_left.collidelist(self.collision_rects) < 0 and self.direction < 0:
            self.direction *= -1

        # reverse direction if wall
        rect_right = pygame.FRect(self.hitbox_rect.topright, (20, self.hitbox_rect.height))
        rect_left = pygame.FRect(self.hitbox_rect.topleft, (-20, self.hitbox_rect.height))

        if rect_right.collidelist(self.collision_rects) >= 0 and self.direction > 0 or rect_left.collidelist(self.collision_rects) >= 0 and self.direction < 0:
            self.direction *= -1