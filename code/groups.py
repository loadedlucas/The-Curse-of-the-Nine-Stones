from settings import *

class AllSprites(pygame.sprite.Group):
    cameraPos = vector()
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.cameraPos.x = 0
        self.cameraPos.y = 0
        self.offset = vector()

    def draw(self, target_pos):
        self.offset.x = -(target_pos[0] - WINDOW_WIDTH / 2)
        self.offset.y = -(target_pos[1] - 50 - WINDOW_HIGHT / 2)
        playerOffset = vector(self.offset.x - self.cameraPos.x, self.offset.y - self.cameraPos.y)
        self.cameraPos += playerOffset * 0.1

        for sprite in self:
            offset_pos = sprite.rect.topleft + self.cameraPos
            self.display_surface.blit(sprite.image, offset_pos)