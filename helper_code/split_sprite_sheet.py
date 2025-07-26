from PIL import Image
def slice_sheet(filename, tile_width, tile_height):
    n = 0
    img = Image.open(filename)
    for y in range(0, img.height, tile_height):
        for x in range(0, img.width, tile_width):
            box = (x, y, x + tile_width, y + tile_height)
            tile = img.crop(box)
            tile.save(f"{n}.png")
            n += 1
slice_sheet("disappear.png", 128, 128)