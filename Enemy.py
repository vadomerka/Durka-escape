import os
import sys
import random
import pygame


cell_h = cell_w = 50
size = width, height = 1000, 800
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


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.count = 0
        self.pos = (500, 500)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        #self.pos =
        #self.rect.x, self.rect.y = player.rect.x, player.rect.y
        if self.count % 5 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
        self.count += 1


class Gun(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, img):
        super().__init__(all_sprites)
        self.image = pygame.transform.scale(img, (player_w, player_h // 2))
        self.rect = self.image.get_rect().move(
            cell_w * pos_x, cell_h * pos_y)
        self.equipped = False
        self.speed_x = 0
        self.speed_y = 0
        self.count = 0
        self.pos = (pos_x, pos_y)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.count += 1
        if self.count == 10:
            self.image = pygame.transform.scale(load_image('spoon.png'), (player_w, player_h // 2))
        if pygame.sprite.collide_mask(self, player):
            self.equipped = True
        if self.equipped:
            self.rect.y = player.rect.y
            self.rect.x = player.rect.x
        self.speed_y += gravity
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.x >= (width - player_w):
            self.speed_x = -self.speed_x
        elif self.rect.x <= 0:
            self.speed_x = -self.speed_x
        if self.rect.y >= (height - player_h // 2):
            self.rect.y = (height - player_h // 2)
        elif self.rect.y <= 0:
            self.rect.y = 0

    def shoot(self):
        clock = pygame.time.Clock()
        self.image = self.image = pygame.transform.scale(load_image('hit_spoon.png'), (player_w, player_h // 2))
        self.rect.y = player.rect.y - 10
        clock.tick(10000)
        self.count = 0


class Bullet(pygame.sprite.Sprite):
    def __init__(self, img):
        super().__init__(all_sprites)
        pass
        #self.image = pygame.transform.scale(img, (player_w, player_h))
        #self.rect = self.image.get_rect().move(
        #    cell_w * pos_x, cell_h * pos_y)
        #self.speed_x = 0
        #self.speed_y = 0
        #self.pos = (pos_x, pos_y)
        #self.mask = pygame.mask.from_surface(self.image)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, img):
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
            #terminate()
            #self.kill()
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
        if self.direction == 0 or 1:
            self.image = pygame.transform.flip(self.image, flip_y=False, flip_x=True)
            self.direction = 2


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode(size)
    screen.fill(pygame.Color("black"))
    clock = pygame.time.Clock()
    fps = 60
    player_img = load_image('mar.png')
    enemy_img = load_image('box.png')
    gun_img = load_image('spoon.png')
    bul_img = load_image('hit.png')
    all_sprites = pygame.sprite.Group()


    player = Player(5, 5, player_img, all_sprites)
    dragon = AnimatedSprite(load_image("dragon_sheet8x2.png"), 8, 2, 50, 50)
    gun = Gun(7, 8, gun_img)
    enemy = Enemy(7, 7, enemy_img)
    #bullet = Bullet(bul_img)

    running = True
    while running:
        screen.fill((0, 0, 0))
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            player.movement("y", "up")
        if keys[pygame.K_LEFT]:
            player.movement("x", "left")
            #player.direction = 1
            #player.flip()
        if keys[pygame.K_RIGHT]:
            #player.flip()
            #player.direction = 0
            player.movement("x", "right")
        if keys[pygame.K_DOWN]:
            player.movement("y", "down")
        if keys[pygame.K_SPACE]:
            #print(1)
            pass
        if not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):  # если юзер не двигается по х, тогда стоп
            player.movement("x", "stop")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                pass
            elif event.type == pygame.KEYUP and last_event[pygame.K_SPACE]:
                gun.shoot()
            elif event.type == pygame.K_SPACE:
                print(1)
            if random.random() > 0.5:
                enemy.movement("x", "right")
            else:
                enemy.movement("x", "left")
        last_event = keys
        all_sprites.draw(screen)
        all_sprites.update()
        clock.tick(fps)
        pygame.display.flip()

