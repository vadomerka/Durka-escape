import os
import sys
import random
import pygame


cell_h = cell_w = 50
size = width, height = 1000, 1500
player_h = cell_h * 2
player_w = cell_w
gravity = 0.1
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
    # print(list(map(lambda x: list(x.ljust(max_width, '.')), level_map)))
    return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                wall = Wall('empty', x, y)
                walls.append(wall)
            if level[y][x] == '#':
                wall = Wall('wall', x, y)
                walls.append(wall)
            elif level[y][x] == '@':
                wall = Wall('empty', x, y)
                walls.append(wall)
                new_player = Player(x, y, player_img)
                level[y][x] = "."
        #print(level[y])
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


class Camera(Sprite):
    # зададим начальный сдвиг камеры
    def __init__(self):
        super().__init__(camera_group)
        self.dx = 250
        self.dy = 0
        self.count = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj, vx):
        if self.count % 10 == 0:
            obj.rect.x = obj.rect.x - vx
            print(level[3])

    # позиционировать камеру на объекте target
    def update(self, target):
        self.count += 1
        #print(self.count)
        #self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        #self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


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
        self.image = pygame.transform.scale(tile_images[img], (cell_w, cell_h))
        self.rect = self.image.get_rect().move(
            cell_w * pos_x, cell_h * pos_y)
        self.abs_pos = (self.rect.x, self.rect.y)
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = 0


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
        self.max_y = 0
        self.max_x = width - player_w
        self.min_x = 0

    def movement(self, line, direction="up"):
        if line == "x":
            if direction == "right":
                vx = 5
            elif direction == "left":
                vx = -5
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

    def update(self):
        self.collide()
        if self.rect.y == self.min_y:
            self.plat = True
            self.speed_y -= gravity
        else:
            self.plat = False
        self.speed_y += gravity
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.x >= self.max_x:
            self.rect.x = self.max_x
        elif self.rect.x <= self.min_x:
            self.rect.x = self.min_x

        if self.rect.y >= self.min_y:
            self.rect.y = self.min_y
        if self.rect.y <= self.max_y:
            self.rect.y = self.max_y

    def collide(self):
        global gravity
        if level[self.rect.y // cell_h + self.rect.h // cell_h][(self.rect.x + 5) // cell_w] == '#' or \
                level[self.rect.y // cell_h + self.rect.h // cell_h][(self.rect.x + cell_w - 5) // cell_w] == '#':
            self.min_y = (self.rect.y // cell_h) * cell_h
            self.plat = True
        else:
            self.min_y = height - player_h

        if level[self.rect.y // cell_h][(self.rect.x + 5) // cell_w] == '#' or \
                level[self.rect.y // cell_h][(self.rect.x + cell_w - 5) // cell_w] == '#':
            self.max_y = self.rect.y // cell_h * cell_h
            self.speed_y = 0
            self.rect.y = self.max_y + cell_h
        else:
            self.max_y = 0

        if level[self.rect.y // cell_w][self.rect.x // cell_w + self.rect.w // cell_w] == '#' or \
                level[self.rect.y // cell_w + 1][self.rect.x // cell_w + self.rect.w // cell_w] == '#':
            self.max_x = self.rect.x
            #print(self.rect.x // cell_w + self.rect.w // cell_w)
        else:
            self.max_x = width - player_w

        if level[self.rect.y // cell_h][self.rect.x // cell_w] == '#' or \
                level[self.rect.y // cell_h + 1][self.rect.x // cell_w] == '#':
            self.min_x = self.rect.x
            self.rect.x += 1
        else:
            self.min_x = 0

        if (self.rect.x // cell_w + self.rect.w // cell_w) + 3 == 20 and \
                self.speed_x > 0:
            for obj in all_sprites:
                camera.apply(obj, self.rect.w)
                self.max_x = self.rect.x

        if (self.rect.x // cell_w + self.rect.w // cell_w) - 3 == 0 and \
                self.speed_x < 0:
            for obj in all_sprites:
                camera.apply(obj, -self.rect.w)
                self.min_x = self.rect.x


if __name__ == '__main__':
    cell_h = cell_w = 50
    size = width, height = 1000, 800
    player_h = cell_h * 2
    player_w = cell_w
    gravity = 0.1
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
    camera_group = SpriteGroup()
    walls = []
    level_map = load_level('map.map')

    player, max_x, max_y, level = generate_level(level_map)
    gun = Gun(7, 8, gun_img)
    enemy = Enemy(7, 7, enemy_img)
    camera = Camera()

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
        camera_group.update(player)
        all_sprites.update()
        player_group.update()
        clock.tick(fps)
        pygame.display.flip()
