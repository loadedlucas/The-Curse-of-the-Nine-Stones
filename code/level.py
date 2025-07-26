from settings import *
from sprites import Sprite, AnimatedSprite, Item, ParticleEffectSprite
from player import Player
from groups import AllSprites
from enemies import Spider

class Level:
    def __init__(self, tmx_map, level_frames):
        self.display_surface = pygame.display.get_surface()

        # groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.semi_collision_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        self.spider_sprites = pygame.sprite.Group()
        self.item_sprites = pygame.sprite.Group()

        self.setup(tmx_map, level_frames)

        # frames
        self.disappear_frames = level_frames["disappear"]

    def setup(self, tmx_map, level_frames):
        # trees
        for obj in tmx_map.get_layer_by_name("Trees"):
            Sprite((obj.x, obj.y), obj.image, self.all_sprites)

        # tiles
        for layer in ["Background", "Terrain", "Platforms"]:
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                groups = [self.all_sprites]
                if layer == "Terrain": groups.append(self.collision_sprites)
                if layer == "Platforms": groups.append(self.semi_collision_sprites)

                Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, groups)

        # items
        for obj in tmx_map.get_layer_by_name("Items"):
            Item(obj.name, (obj.x, obj.y), level_frames["items"][obj.name], (self.all_sprites, self.item_sprites))

        # player
        for obj in tmx_map.get_layer_by_name("Objects"):
            if obj.name == "player":
                self.player = Player(
                    pos = (obj.x, obj.y),
                    groups = self.all_sprites,
                    collision_sprites = self.collision_sprites,
                    semi_collision_sprites = self.semi_collision_sprites,
                    frames = level_frames["player"])

        # foreground entities
        for layer in ["Enemies", "Traps"]:
            for obj in tmx_map.get_layer_by_name(layer):
                if obj.name == "spider":
                    Spider((obj.x, obj.y), level_frames["spider"], (self.all_sprites, self.damage_sprites, self.spider_sprites), self.collision_sprites)
                else:
                    # frames
                    frames = level_frames[obj.name]

                    # groups
                    groups = [self.all_sprites]

                    AnimatedSprite((obj.x, obj.y), frames, groups)

    def item_collision(self):
        item_sprites = pygame.sprite.spritecollide(self.player, self.item_sprites, True)
        if item_sprites:
            ParticleEffectSprite((item_sprites[0].rect.center), self.disappear_frames, self.all_sprites)

    def run(self, dt):
        self.display_surface.fill("black")

        self.all_sprites.update(dt)
        self.item_collision()
        self.all_sprites.draw(self.player.hitbox_rect.center, dt)