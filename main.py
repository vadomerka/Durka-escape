import os
import sys
import random
import pygame


cell_h = cell_w = 50
gravity = 0.16


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
        self.image = pygame.transform.scale(load_image(img), (300, 100))
        self.rect = self.image.get_rect().move(
            cell_w * pos_x + 25, cell_h * pos_y + 25)
        self.speed_x = 0
        self.speed_y = 0

    def redirect(self, line, direction):
        vx = 0
        vy = 0
        if line == "x":
            if direction:
                vx = 5
            else:
                vx = -5
            self.speed_x += vx
        else:
            if direction:
                vy = 0
            else:
                vy = -5
            self.speed_y = vy

    def update(self):
        self.speed_y += gravity
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.x >= 1000:
            self.rect.x = 0
        elif self.rect.x <= 0:
            self.rect.x = 1000
        if self.rect.y >= 1000:
            self.rect.y = 0
        elif self.rect.y <= 0:
            self.rect.y = 1000


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
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            player.redirect("y", False)
        if keys[pygame.K_LEFT]:
            player.redirect("x", False)
        if keys[pygame.K_RIGHT]:
            player.redirect("x", True)
        if keys[pygame.K_DOWN]:
            player.redirect("y", True)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                pass
        all_sprites.draw(screen)
        all_sprites.update()
        clock.tick(fps)
        pygame.display.flip()
    pygame.quit()
