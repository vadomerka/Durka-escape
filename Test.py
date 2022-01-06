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
    filename = "data/levels/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))
    print(list(map(lambda x: list(x.ljust(max_width, '.')), level_map)))
    return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                wall = Wall('empty', x, y * 2)
                walls.append(wall)
            if level[y][x] == '#':
                wall = Wall('wall', x, y * 2)
                walls.append(wall)
            elif level[y][x] == '@':
                wall = Wall('empty', x, y * 2)
                walls.append(wall)
                new_player = Player(x, y * 2, player_img)
                level[y][x] = "."
        print(level[y])
    #print(walls)
    return new_player, x, y, level


class SpriteGroup(pygame.sprite.Group):

    def __init__(self):
        super().__init__()

    def get_event(self, event):
        for sprite in self:
            sprite.get_event(event)


class Sprite(pygame.sprite.Sprite):

    def __init__(self, group):
        super().__init__(group)
        self.rect = None

    def get_event(self, event):
        pass


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


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


class MiniMap(Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(mini_map)
        self.image = pygame.transform.scale(load_image('creature.png'), (player_w * 2, player_h))
        self.rect = self.image.get_rect().move(
            cell_w * pos_x, cell_h * pos_y)


class Gun(Sprite):
    def __init__(self, pos_x, pos_y, img):
        super().__init__(player_group)
        self.image = pygame.transform.scale(img, (player_w, player_h // 2))
        self.rect = self.image.get_rect().move(
            cell_w * pos_x, cell_h * pos_y)
        self.equipped = False
        self.speed_x = 0
        self.speed_y = 0
        self.count = 0
        self.pos = (pos_x, pos_y)
        self.mask = pygame.mask.from_surface(self.image)
        self.anim_on = False

    def update(self):
        self.count += 1
        if self.count == 10:
            self.image = pygame.transform.scale(load_image('spoon.png'), (player_w, player_h // 2))
            self.anim_on = False
        if pygame.sprite.collide_mask(self, player):
            self.equipped = True
        if self.equipped and not self.anim_on:
            self.speed_y = player.speed_y
            self.rect.y = player.rect.y
            self.rect.x = player.rect.x - 20
        elif self.equipped and self.anim_on:
            self.rect.x = player.rect.x - 30
            self.rect.y = player.rect.y + 30

    def shoot(self):
        self.image = pygame.transform.scale(load_image('hit_spoon.png'), (player_w, player_h // 2))
        self.anim_on = True
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


class Enemy(Sprite):
    def __init__(self, pos_x, pos_y, img):
        super().__init__(player_group)
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
            else:
                vx = -2
            self.speed_x = vx
        if line == "stop":
            pass

    def update(self):
        if pygame.sprite.collide_mask(self, player):
            self.speed_x = 0
            #terminate()
            self.kill()
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


class Wall(Sprite):
    def __init__(self, img, pos_x, pos_y):
        super().__init__(all_sprites)
        self.name = img
        img = tile_images[img]
        self.image = pygame.transform.scale(img, (player_w, player_h))
        self.rect = self.image.get_rect().move(
            cell_w * pos_x, cell_h * pos_y)
        self.speed_x = 0
        self.speed_y = 0
        self.pos = (pos_x, pos_y)
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = 0

    def update(self):
        if pygame.sprite.collide_mask(self, player):
            pass
            #if player.rect.y > self.rect.y - 100:
            #    player.rect.y = self.rect.y - 100
            #    player.speed_y = 0
            #    player.plat = True
            #else:
            #    player.plat = False
            #if player.rect.y <= self.rect.y - 100 and player.rect.x == self.rect.x:
            #    player.speed_x = 0
        #else:
        #    player.plat = False

            #terminate()
            #self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, img):
        super().__init__(player_group)
        self.image = pygame.transform.scale(img, (player_w, player_h))
        self.rect = self.image.get_rect().move(
            cell_w * pos_x, cell_h * pos_y)
        self.speed_x = 0
        self.speed_y = 0
        self.pos = (pos_x, pos_y)
        self.mask = pygame.mask.from_surface(self.image)
        self.plat = False
        self.min_y = height - player_h
        self.max_x = width - player_w
        self.min_x = 0

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
                if self.rect.y == self.min_y or self.plat:
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
        self.collide()
        if self.rect.y == self.min_y:
            self.plat = True
        else:
            self.plat = False
        self.speed_y += gravity
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y * 2
        if self.rect.x >= self.max_x:
            self.rect.x = self.max_x
        elif self.rect.x <= self.min_x:
            self.rect.x = self.min_x
        #if self.plat:
        #    self.rect.y = self.rect.y
        if self.rect.y >= self.min_y:
            self.rect.y = self.min_y
        if self.rect.y <= self.max_y:
            self.rect.y = self.max_y

    def collide(self):
        global gravity
        #print(player.rect.y // 100 + 1, round(player.rect.x * 2 / 100 + 1), level[player.rect.y // 100 + 1][round(player.rect.x * 2 / 100 + 1)])
        if level[self.rect.y // 100 + 1][round(self.rect.x * 2 / 100)] == '#':
            self.min_y = self.rect.y
            gravity = 0
        else:
            self.min_y = height - player_h
            gravity = 0.16

        if level[self.rect.y // 100][round(self.rect.x * 2 / 100)] == '#':
            self.max_y = (self.rect.y + 100) // 100 * 100
            print('Yes')
            print(self.max_y)
        else:
            self.max_y = 0

        if level[player.rect.y // 100][round((player.rect.x + 30) / 50)] == '#':
            self.max_x = self.rect.x
        else:
            self.max_x = width - player_w

        if level[self.rect.y // 100][round((self.rect.x - 30) / 50)] == '#':
            self.min_x = self.rect.x
            #print(self.min_x)
        else:
            self.min_x = 0


if __name__ == '__main__':
    cell_h = cell_w = 50
    size = width, height = 1000, 800
    player_h = cell_h * 2
    player_w = cell_w
    gravity = 0.16
    horizontal_borders = pygame.sprite.Group()
    vertical_borders = pygame.sprite.Group()

    pygame.init()
    screen = pygame.display.set_mode(size)
    screen.fill(pygame.Color("black"))
    clock = pygame.time.Clock()
    fps = 60
    player_img = load_image('mar.png')
    enemy_img = load_image('box.png')
    gun_img = load_image('spoon.png')
    bul_img = load_image('hit.png')
    wall_img = load_image('box.png')
    tile_images = {
        'wall': load_image('box.png'),
        'empty': load_image('grass.png')
    }

    all_sprites = SpriteGroup()
    player_group = SpriteGroup()
    mini_map = SpriteGroup()

    #level_map = load_level('level 1.txt')
    walls = []
    level_map = load_level('map.map')

    player, max_x, max_y, level = generate_level(level_map)
    print(level)
    #player = Player(5, 5, player_img)
    #dragon = AnimatedSprite(load_image("dragon_sheet8x2.png"), 8, 2, 50, 50)
    gun = Gun(7, 8, gun_img)
    enemy = Enemy(7, 7, enemy_img)
    min_map = MiniMap(18, 0)
    #bullet = Bullet(bul_img)

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
        if keys[pygame.K_SPACE]:
            print(player.rect.y // 100 + 1, round(player.rect.x * 2 / 100 + 1))
        if not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):  # если юзер не двигается по х, тогда стоп
            player.movement("x", "stop")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                pass
            elif event.type == pygame.KEYUP and last_event[pygame.K_SPACE] and gun.equipped:
                gun.shoot()
            elif event.type == pygame.K_SPACE:
                print(1)
            if random.random() > 0.5:
                enemy.movement("x", "right")
            else:
                enemy.movement("x", "left")
        last_event = keys
        all_sprites.draw(screen)
        player_group.draw(screen)
        mini_map.draw(screen)
        all_sprites.update()
        player_group.update()
        mini_map.update()
        clock.tick(fps)
        pygame.display.flip()
