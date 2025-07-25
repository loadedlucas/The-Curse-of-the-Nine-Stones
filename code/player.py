from settings import *
from mytimer import Timer
from os.path import join

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites, semi_collision_sprites, frames):
        # general setup
        super().__init__(groups)

        # image
        self.frames, self.frame_index = frames, 0
        self.state, self.facing_right, self.sneak, self.attacking, self.attack_state = "idle", True, False, False, 0
        self.image = self.frames[self.state][self.frame_index]

        # rects
        self.rect = self.image.get_frect(topleft = pos)
        self.hitbox_rect = self.rect.inflate(-288, -256)
        self.old_rect = self.hitbox_rect.copy()

        # movement
        self.direction = vector()
        self.speed = 400
        self.gravity = 4800
        self.jump = False
        self.jump_height = 2000

        # collision
        self.collision_sprites = collision_sprites
        self.semi_collision_sprites = semi_collision_sprites
        self.on_surface = {"floor": False, "platform": False, "left": False, "right": False}

        # timer
        self.timers = {
            "wall_jump": Timer(400),
            "wall_slide_block": Timer(300),
            "platform_skip": Timer(100)
        }

    def input(self):
        keys = pygame.key.get_pressed()
        events = pygame.event.get()
        input_vector = vector(0,0)

        if not self.timers["wall_jump"].active:
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                input_vector.x += 1
                self.facing_right = True
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                input_vector.x -= 1
                self.facing_right = False
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.timers["platform_skip"].activate()
                self.sneak = True
            if keys[pygame.K_LSHIFT]:
                self.run = True
            if keys[pygame.K_x]:
                self.attack()
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.attack()
            
            self.direction.x = input_vector.normalize().x if input_vector else input_vector.x

        if keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]:
            self.jump = True

    def attack(self):
        if not self.attacking:
            self.attack_state += 1
            self.attacking = True
            self.frame_index = 0

            if self.attack_state > 3:
                self.attack_state = 1

    def move(self, dt):
        # horizontal
        if not self.attacking:
            if self.sneak:
                self.hitbox_rect.x += self.direction.x * self.speed / 2 * dt
            elif self.run and any((self.on_surface["floor"], self.on_surface["platform"])):
                self.hitbox_rect.x += self.direction.x * self.speed * 1.5 * dt
            else:
                self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collisioin("horizontal")

        # vertical
        if not self.on_surface["floor"] and any((self.on_surface["left"], self.on_surface["right"])) and not self.timers["wall_slide_block"].active and not self.sneak: # wall slide
            self.direction.y = 0
            self.hitbox_rect.y += self.gravity / 10 * dt
        else: # apply gravity
            self.direction.y += self.gravity / 2 * dt
            self.hitbox_rect.y += self.direction.y * dt
            self.direction.y += self.gravity / 2 * dt

        if self.jump:
            self.jump = False
            if self.on_surface["floor"] or self.on_surface["platform"]: # jump
                self.direction.y = -self.jump_height
                self.timers["wall_slide_block"].activate()
                self.hitbox_rect.bottom -= 1
            elif any((self.on_surface["left"], self.on_surface["right"])) and not self.timers["wall_slide_block"].active and not self.sneak: # wall jump
                self.timers["wall_jump"].activate()
                self.direction.y = -self.jump_height
                self.direction.x = 1 if self.on_surface["left"] else -1

        self.collisioin("vertical")
        self.semi_collisioin()
        self.rect.center = self.hitbox_rect.center

    def check_contact(self):
        floor_rect = pygame.Rect(self.hitbox_rect.bottomleft, (self.hitbox_rect.width, 2))
        right_rect = pygame.Rect(self.hitbox_rect.topright + vector(0, self.hitbox_rect.height / 4), (2, self.hitbox_rect.height / 2))
        left_rect = pygame.Rect(self.hitbox_rect.topleft + vector(-2, self.hitbox_rect.height / 4), (2, self.hitbox_rect.height / 2))
        collide_rects = [sprite.rect for sprite in self.collision_sprites]
        semi_collide_rects = [sprite.rect for sprite in self.semi_collision_sprites]

        # collisions
        self.on_surface["floor"] = True if floor_rect.collidelist(collide_rects) >= 0 else False
        for sprite in semi_collide_rects: # seperate check for platforms to avoid preemtive jumping
            if floor_rect.bottom >= sprite.top and floor_rect.top <= sprite.top and floor_rect.colliderect(sprite) and self.direction.y >= 0:
                self.on_surface["platform"] = True
                break
            else:
                self.on_surface["platform"] = False

        self.on_surface["right"] = True if right_rect.collidelist(collide_rects) >= 0 else False
        self.on_surface["left"] = True if left_rect.collidelist(collide_rects) >= 0 else False

    def collisioin(self, axis):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if axis == "horizontal":
                    #left
                    if self.hitbox_rect.left <= sprite.rect.right and int(self.old_rect.left) >= int(sprite.rect.right):
                        self.hitbox_rect.left = sprite.rect.right
                    #right
                    if self.hitbox_rect.right >= sprite.rect.left and int(self.old_rect.right) <= int(sprite.rect.left):
                        self.hitbox_rect.right = sprite.rect.left
                        
                else: # vertical
                    # top
                    if self.hitbox_rect.top <= sprite.rect.bottom and int(self.old_rect.top) >= int(sprite.rect.bottom):
                        self.hitbox_rect.top = sprite.rect.bottom
                    # bottom
                    if self.hitbox_rect.bottom >= sprite.rect.top and int(self.old_rect.bottom) <= int(sprite.rect.top):
                        self.hitbox_rect.bottom = sprite.rect.top
                    self.direction.y = 0

    def semi_collisioin(self):
        if not self.timers["platform_skip"].active:
            for sprite in self.semi_collision_sprites:
                if sprite.rect.colliderect(self.hitbox_rect):
                    if self.hitbox_rect.bottom >= sprite.rect.top and int(self.old_rect.bottom) <= int(sprite.rect.top):
                            self.hitbox_rect.bottom = sprite.rect.top
                            if self.direction.y > 0:
                                self.direction.y = 0

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt
        if self.attacking and self.frame_index >= len(self.frames[self.state]):
            self.state = "idle"
            self.attacking = False
        self.image = self.frames[self.state][int(self.frame_index % len(self.frames[self.state]))]
        self.image = self.image if self.facing_right else pygame.transform.flip(self.image, True, False)

    def get_state(self):
        if self.attacking and self.attack_state == 1:
            self.state = "attack-1"
        elif self.attacking and self.attack_state == 2:
            self.state = "attack-2"
        elif self.attacking and self.attack_state == 3:
            self.state = "attack-3"
        elif self.sneak and self.direction.x != 0:
            self.state = "sneak"
        elif any((self.on_surface["floor"], self.on_surface["platform"])):
            self.state = "idle" if self.direction.x == 0 else "walk" if not self.run else "run"
        elif any((self.on_surface["left"], self.on_surface["right"])) and not self.timers["wall_slide_block"].active:
                self.state = "wall_slide"
        else:
            self.state = "jump" if self.direction.y < 0 else "fall"

    def update(self, dt):
        self.sneak, self.run = False, False
        self.old_rect = self.hitbox_rect.copy()
        self.update_timers()

        self.input()
        self.move(dt)
        self.check_contact()

        self.get_state()
        self.animate(dt)