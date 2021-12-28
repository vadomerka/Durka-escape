import os
import sys
import random
import pygame


cell_h = cell_w = 50
size = width, height = 1000, 1000
player_h = cell_h * 2
player_w = cell_w
gravity = 0.16
horizontal_borders = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()


def terminate():
    pygame.quit()
    sys.exit()


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


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


class Level:
    pass


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, img, all_sprites):
        super().__init__(all_sprites)
        self.image = pygame.transform.scale(img, (player_w, player_h))
        self.rect = self.image.get_rect().move(
            cell_w * pos_x, cell_h * pos_y)
        self.speed_x = 0
        self.speed_y = 0
        self.pos = (pos_x, pos_y)
        self.mask = pygame.mask.from_surface(self.image)

    def movement(self, line, direction="up"):
        if line == "x":
            if direction == "right":
                vx = 2
            elif direction == "left":
                vx = -2
            elif direction == "stop":
                vx = 0
            else:
                vx = 0
                print("wrong direction", line)
            self.speed_x = vx
        if line == "y":
            if direction == "down":
                vy = 0
            elif direction == "up":
                if self.rect.y == (height - player_h):
                    vy = -5
                else:
                    vy = self.speed_y
            else:
                vy = 0
                print("wrong direction", line)
            self.speed_y = vy
        if line == "stop":
            pass

    def update(self):
        if pygame.sprite.collide_mask(self, player):
            self.speed_x = 0
            terminate()
        self.speed_y += gravity
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.x >= (width - player_w):
            self.speed_x = -self.speed_x
        elif self.rect.x <= 0:
            self.speed_x = -self.speed_x
        if self.rect.y >= (height - player_h):
            self.rect.y = (height - player_h)
        elif self.rect.y <= 0:
            self.rect.y = 0


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, img, all_sprites):
        super().__init__(all_sprites)
        self.image = pygame.transform.scale(img, (player_w, player_h))
        self.rect = self.image.get_rect().move(
            cell_w * pos_x, cell_h * pos_y)
        self.speed_x = 0
        self.speed_y = 0
        self.pos = (pos_x, pos_y)
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = 0

    def movement(self, line, direction="up"):
        if line == "x":
            if direction == "right":
                vx = 5
                self.direction = 1
            elif direction == "left":
                vx = -5
                self.direction = 0
            elif direction == "stop":
                vx = 0
            else:
                vx = 0
                print("wrong direction", line)
            self.speed_x = vx
        if line == "y":
            if direction == "down":
                vy = 0
            elif direction == "up":
                if self.rect.y == (height - player_h):
                    vy = -5
                else:
                    vy = self.speed_y
            else:
                vy = 0
                print("wrong direction", line)
            self.speed_y = vy
        if line == "stop":
            pass

    def update(self):
        self.speed_y += gravity
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.x >= (width - player_w):
            self.rect.x = (width - player_w)
        elif self.rect.x <= 0:
            self.rect.x = 0
        if self.rect.y >= (height - player_h):
            self.rect.y = (height - player_h)
        elif self.rect.y <= 0:
            self.rect.y = 0

    def flip(self):
        if self.direction == 1:
            self.image = pygame.transform.flip(self.image, flip_y=False, flip_x=True)
            self.direction = 0


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode(size)
    screen.fill(pygame.Color("black"))
    clock = pygame.time.Clock()
    fps = 60
    img = load_image('mar.png')
    img1 = load_image('box.png')
    all_sprites = pygame.sprite.Group()

    player = Player(5, 5, img, all_sprites)
    enemy = Enemy(7, 7, img1, all_sprites)
    running = True
    while running:
        screen.fill((0, 0, 0))
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            player.movement("y", "up")
        if keys[pygame.K_LEFT]:
            player.movement("x", "left")
        if keys[pygame.K_RIGHT]:
            player.movement("x", "right")
        if keys[pygame.K_DOWN]:
            player.movement("y", "down")
        if not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):  # если юзер не двигается по х, тогда стоп
            player.movement("x", "stop")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                pass
            elif event.type == pygame.K_RIGHT:
                player.flip()
            if random.random() > 0.5:
                enemy.movement("x", "right")
            else:
                enemy.movement("x", "left")
        all_sprites.draw(screen)
        all_sprites.update()
        clock.tick(fps)
        pygame.display.flip()
