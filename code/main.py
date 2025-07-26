from settings import *
from level import Level
from pytmx import load_pygame
from os.path import join

from support import *

class Game:
	def __init__(self):
		pygame.init()
		self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HIGHT), vsync = True)
		pygame.display.set_caption("The Curse of the Nine Stones")
		self.clock = pygame.time.Clock()
		self.import_assets()

		self.tmx_maps = {0: load_pygame(join("..", "data", "levels", "0.tmx"))}
		self.current_level = Level(self.tmx_maps[0], self.level_frames)

	def import_assets(self):
		self.level_frames = {
			"spikes": import_folder("..", "graphics", "traps", "spikes"),
			"player": import_sub_folders("..", "graphics", "player"),
			"spider": import_sub_folders("..", "graphics", "enemies", "spider"),
			"items": import_sub_folders("..", "graphics", "items"),
			"disappear": import_folder("..", "graphics", "particles", "disappear"),
		}

	def run(self):
		while True:
			dt = self.clock.tick(FPS) / 1000 # Convert milliseconds to seconds
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()

			self.current_level.run(dt)

			pygame.display.update()

if __name__ == "__main__":
	game = Game()
	game.run()