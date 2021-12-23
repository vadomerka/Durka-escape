import os
import sys
import random
import pygame


cell_h = cell_w = 50


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)

    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, img):
        super().__init__(all_sprites)
        self.image = load_image(img)
        self.rect = self.image.get_rect().move(
            cell_w * pos_x + 25, cell_h * pos_y + 25)

    def update(self):
        pass


if __name__ == '__main__':
    pygame.init()
    size = width, height = 1000, 1000
    screen = pygame.display.set_mode(size)
    screen.fill(pygame.Color("black"))
    clock = pygame.time.Clock()
    fps = 60

    all_sprites = pygame.sprite.Group()

    player = Player(0, 0, "sad_cat.jpg")

    running = True
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        all_sprites.draw(screen)
        all_sprites.update()
        clock.tick(fps)
        pygame.display.flip()
    pygame.quit()
