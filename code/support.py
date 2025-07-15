from settings import * 
from os import walk
from os.path import join, dirname, abspath

def import_image(*path, alpha = True, format = 'png'):
	full_path = join(*path) + f'.{format}'
	return pygame.image.load(full_path).convert_alpha() if alpha else pygame.image.load(full_path).convert()

def import_folder(*path): # had issues with .DS_Store files on macos and image path 
	frames = []
	base_path = dirname(abspath(__file__)) # fix for path issue
	folder_path = join(base_path, *path)

	for folder_path, subfolders, image_names in walk(folder_path):
		for image_name in sorted(image_names):
			if not image_name.endswith(".png"): # fix for .DS_Store issue
				continue
			full_path = join(folder_path, image_name)
			frames.append(pygame.image.load(full_path).convert_alpha())
	return frames 

def import_folder_dict(*path):
	frame_dict = {}
	for folder_path, _, image_names in walk(join(*path)):
		for image_name in image_names:
			full_path = join(folder_path, image_name)
			surface = pygame.image.load(full_path).convert_alpha()
			frame_dict[image_name.split('.')[0]] = surface
	return frame_dict

def import_sub_folders(*path):
	frame_dict = {}
	base_path = dirname(abspath(__file__)) # fix for path issue
	folder_path = join(base_path, *path)
	for _, sub_folders, __ in walk(folder_path): 
		if sub_folders:
			for sub_folder in sub_folders:
				frame_dict[sub_folder] = import_folder(*path, sub_folder)
	return frame_dict