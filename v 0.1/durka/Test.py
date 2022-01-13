import os
import sys
import random
import pygame




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
                Wall('empty', x, y)
            if level[y][x] == '#':
                Wall('wall', x, y)
            if level[y][x] == '$':
                Wall('empty', x, y)
                AnimatedSprite(pygame.transform.scale(load_image('portal.png'), (cell_w * 4, cell_h * 2)), 4, 1, x, y)
            elif level[y][x] == '@':
                Wall('empty', x, y)
                new_player = Player(x, y, load_image('mar.png'))
                level[y][x] = "."
        print(level[y])
    return new_player, x, y, level


def regenerate_level():
    global player, max_x, max_y, level, levels, all_sprites, player_group, count
    all_sprites = SpriteGroup()
    player_group = SpriteGroup()
    player, max_x, max_y, level = generate_level(levels[count])


def start_screen():
    intro_text = ["Начать игру", "",
                  "",
                  "Новая игра"]

    fon = pygame.transform.scale(load_image('Каневский_показывает.jpg'), (screen.get_size()))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 50)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if 210 > event.pos[0] > 0 and 100 > event.pos[1] > 50:
                    return
                if event.pos[0] and event.pos[1]:
                    pass
                print(event.pos)

        pygame.display.flip()
        clock.tick(fps)


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


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x * cell_w, y * (cell_h - 5))
        self.mask = pygame.mask.from_surface(self.image)
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
        if pygame.sprite.collide_mask(self, player):
            regenerate_level()
        if self.count % 5 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            self.mask = pygame.mask.from_surface(self.image)
        self.count += 1


class Gun(Sprite):
    def __init__(self, pos_x, pos_y, img):
        super().__init__(gun_group)
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
        self.image = pygame.transform.scale(img, (cell_w, cell_h))
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


class Player(Sprite):
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
            self.speed_y -= gravity
        else:
            self.plat = False
        self.speed_y += gravity
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.x >= self.max_x:
            self.rect.x = self.max_x
        if self.rect.x <= self.min_x:
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
        else:
            self.max_x = width - player_w

        if level[self.rect.y // cell_h][self.rect.x // cell_w] == '#' or \
                level[self.rect.y // cell_h + 1][self.rect.x // cell_w] == '#':
            self.min_x = self.rect.x
            self.rect.x += 1
        else:
            self.min_x = 0


if __name__ == '__main__':
    count = 1
    cell_h = cell_w = 50
    size = width, height = 1000, 800
    player_h = cell_h * 2
    player_w = cell_w
    gravity = 0.1

    pygame.init()
    screen = pygame.display.set_mode(size)
    screen.fill(pygame.Color("black"))
    clock = pygame.time.Clock()
    fps = 60

    enemy_img = load_image('box.png')
    gun_img = load_image('spoon.png')
    tile_images = {
        'wall': load_image('box.png'),
        'empty': load_image('grass.png'),
        'portal': load_image('portal.png')
    }

    all_sprites = SpriteGroup()
    player_group = SpriteGroup()
    gun_group = SpriteGroup()
    levels = [load_level('level 1'), load_level('level 2'), load_level('level 2')]

    player, max_x, max_y, level = generate_level(levels[0])
    gun = Gun(7, 8, gun_img)
    enemy = Enemy(7, 7, enemy_img)
    start_screen()
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
        gun_group.draw(screen)
        all_sprites.update()
        player_group.update()
        gun_group.update()
        clock.tick(fps)
        pygame.display.flip()
