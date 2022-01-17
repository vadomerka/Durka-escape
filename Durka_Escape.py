import os
import sys
import random
import pygame


cell_h = cell_w = 50
size = width, height = 1000, 800
player_h = cell_h * 2
player_w = cell_w
gravity = 0.1
creature_group = pygame.sprite.Group()
doors_group = pygame.sprite.Group()
only_player_group = pygame.sprite.Group()
player_attacks = pygame.sprite.Group()
chests_group = pygame.sprite.Group()


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
    filename = f"data/levels/stage {str(stage)}/{filename}"
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        l_m = [line.strip() for line in mapFile]

    max_width = max(map(len, l_m))
    # print(list(map(lambda x: list(x.ljust(max_width, '.')), level_map)))
    return list(map(lambda x: list(x.ljust(max_width, '.')), l_m))


def generate_level(lev, filename):
    global player, level_sprites, room_maps
    new_player, x, y = None, None, None
    numbers = "1234567890"
    background, front = [], []
    for y in range(len(lev)):
        # print(lev[y])
        for x in range(len(lev[y])):
            if lev[y][x] == '.':
                background.append((Wall, "empty", x, y))
            elif lev[y][x] == '#':
                background.append((Wall, "wall", x, y))
            elif lev[y][x] == '@':
                background.append((Wall, "empty", x, y))
                new_player = x, y
                lev[y][x] = "."
            elif lev[y][x] == 'X':
                background.append((Wall, "empty", x, y))
                front.append((Enemy, x, y, enemy_img))
            elif lev[y][x] == 'W':
                background.append((Wall, "empty", x, y))
                front.append((Gun, x, y, random.choice(weapons)))
                lev[y][x] = "."
            elif lev[y][x] == 'C':
                background.append((Wall, "empty", x, y))
                background.append((Chest, chests_images["closed"], x, y))
            elif lev[y][x] == "F":
                background.append((Wall, "empty", x, y))
                front.append((Exit, (x, y), (cell_w * 2, cell_h * 2), lev[y][x]))
            elif lev[y][x] in numbers:
                front.append((Door, (x, y), (cell_w, cell_h * 2), lev[y][x]))
    room_maps[int(filename[-1])] = lev
    for i in range(len(background)):
        clas, x, y, img = background[i]
        background[i] = clas(x, y, img)
    for i in range(len(front)):
        clas, x, y, img = front[i]
        front[i] = clas(x, y, img)
        if clas == Door and room_maps[int(img)] == 0:
            generate_level(load_level("room " + img), "room " + img)

    if new_player is not None:
        if player:
            player.rect.x, player.rect.y = new_player[0] * cell_w, new_player[1] * cell_h
            player.speed_y = -1
        else:
            player = Player(new_player[0], new_player[1], player_img)
    # room_maps[int(filename[-1])] = lev
    level_sprites[int(filename[-1])] = (background, front)
    # print(level_sprites)


def next_level():
    global all_sprites, player_group, player, room_number, level_map, room_maps, level_sprites, \
        creature_group, doors_group, only_player_group, player_attacks, chests_group, stage
    stage += 1
    all_sprites = SpriteGroup()
    player_group = SpriteGroup()
    creature_group = pygame.sprite.Group()
    doors_group = pygame.sprite.Group()
    only_player_group = pygame.sprite.Group()
    player_attacks = pygame.sprite.Group()
    chests_group = pygame.sprite.Group()
    room_number = 0
    level_map = load_level('room 0')
    room_maps = [0] * 9
    level_sprites = [0] * 9
    generate_level(level_map, 'room 0')
    only_player_group.add(player)


def draw_interface():
    global weapon_images
    for hp in range(0, player.health, 5):
        screen.blit(heart_image, (hp * 5, 0))
    screen.blit(pygame.transform.scale(invent_image, (cell_w * 3, cell_h * 3)), (width - cell_w * 3, cell_h))
    if first_weapon:
        screen.blit(pygame.transform.scale(weapon_images[first_weapon][0],
                                           (cell_w * 3, cell_h * 3)), (width - cell_w * 3, cell_h))
    if second_weapon:
        screen.blit(pygame.transform.scale(weapon_images[second_weapon][0],
                                           (cell_w, cell_h)), (width - cell_w * 3, cell_h * 3))


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

    def get_event(self, ev):
        for sprite in self:
            sprite.get_event(ev)


class Sprite(pygame.sprite.Sprite):

    def __init__(self, group):
        super().__init__(group)
        self.rect = None

    def get_event(self, ev):
        pass


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, pos_x, pos_y, group):
        super().__init__(group)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(pos_x, pos_y)
        self.reversed = False
        self.time = 0
        self.frames_count = 30

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        # time нужен, чтобы в fps было меньше смены кадров (а иначе не запасешься sheet'ов)
        if self.time % (fps // self.frames_count) == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            if self.reversed:
                self.image = pygame.transform.flip(self.image, True, False)
        self.time = (self.time + 1) % fps


class Door(pygame.sprite.Sprite):
    def __init__(self, pos, door_size, num):
        self.room_num = int(num)
        pos_x, pos_y = pos
        size_x, size_y = door_size
        img = doors_images[self.room_num]
        self.image = pygame.transform.scale(img, (size_x, size_y))
        self.rect = self.image.get_rect().move(
            cell_w * pos_x, cell_h * pos_y)
        super().__init__(all_sprites, doors_group)
        self.near_player = False

    def update(self):
        self.near_player = pygame.sprite.collide_mask(self, player)

    def enter(self):
        global room_number, player
        room_number = self.room_num
        player.rect.x = self.rect.x
        # десять - чтобы меньше проходил в текстуры
        player.rect.y = self.rect.y - 10


class Exit(pygame.sprite.Sprite):
    def __init__(self, pos, door_size, num):
        super().__init__(doors_group)
        pos_x, pos_y = pos
        size_x, size_y = door_size
        img = doors_images["F"]
        self.image = pygame.transform.scale(img, (size_x, size_y))
        self.rect = self.image.get_rect().move(
            cell_w * pos_x, cell_h * pos_y)
        self.near_player = False

    def update(self):
        self.near_player = pygame.sprite.collide_mask(self, player)

    def enter(self):
        next_level()


class Chest(pygame.sprite.Sprite):
    def __init__(self, img, pos_x, pos_y):
        self.image = pygame.transform.scale(img, (cell_w, cell_h))
        self.rect = self.image.get_rect().move(
            cell_w * pos_x, cell_h * pos_y)
        super().__init__(all_sprites, chests_group)
        self.near_player = False
        self.opened = False

    def update(self):
        self.near_player = pygame.sprite.collide_mask(self, player)

    def open(self):
        size_of_cap = 29
        if not self.opened:
            level_sprites[room_number][1].append(
            Gun(self.rect.x // cell_w, (self.rect.y - self.rect.h) // cell_h, random.choice(weapons)))
            self.rect.y -= size_of_cap
        self.image = chests_images["open"]
        self.opened = True


class Gun(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, type):
        global player_group
        super().__init__(player_group)
        self.type = type
        self.damage = weapon_images[self.type][1]
        self.attack_speed = weapon_images[self.type][2]
        self.image = pygame.transform.scale(weapon_images[self.type][0], (cell_w, cell_h))
        self.rect = self.image.get_rect().move(
            cell_w * pos_x, cell_h * pos_y)
        self.shoot_cooldown = 0
        self.bullet = None
        self.move_speed = 2
        self.speed_x = random.randint(-self.move_speed, self.move_speed)
        self.speed_y = -self.move_speed
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.mask = pygame.mask.from_surface(self.image)
        self.plat = False
        self.near_player = False
        self.min_y = height - self.rect.h
        self.max_y = 0
        self.max_x = width - self.rect.w
        self.min_x = 0

        self.equipped = False

    def update(self):
        # print(self.rect.x)
        if self.equipped:
            self.rect.x = width - cell_w * 2.5
            self.rect.y = cell_h * 1.5
            self.image = pygame.transform.scale(self.image, (cell_w * 2, cell_h * 2))
            if self.shoot_cooldown > 0:
                self.shoot_cooldown -= (1 / fps)
            else:
                self.shoot_cooldown = 0
            # print(self.min_x, self.max_y)
        else:
            self.collide()
            if self.rect.y == self.min_y:
                self.plat = True
                self.speed_y -= gravity
            else:
                self.plat = False
            if self.plat:
                self.speed_x = 0
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

        # if self.bullet:
        #     self.bullet.update()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= (1 / fps)
        else:
            self.shoot_cooldown = 0
        if pygame.sprite.collide_mask(self, player) and not self.equipped:
            self.draw_stats()
            # self.equip()
            self.near_player = True
        else:
            self.near_player = False

    def draw_stats(self):
        intro_text = ["Wanna grab a " + self.type + " ?",
                      "             old stats: damage, " + str(player.stats[0]) + " speed, " + str(player.stats[1]),
                      "             new stats: damage, " + str(self.damage) + " speed, " + str(self.attack_speed)]

        fon = pygame.transform.scale(self.image, (width * 0.8, height * 0.8))
        screen.blit(fon, (width * 0.1, height * 0.1))
        font = pygame.font.Font(None, 30)
        text_coord = 50
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('white'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)

    def equip(self):
        global level_sprites, room_number
        player.weapon = self
        if self in level_sprites[room_number][1]:
            level_sprites[room_number][1].remove(self)
        self.equipped = True
        player.stats = [self.damage, self.attack_speed]

    def collide(self):
        row1 = self.rect.y // cell_h + self.rect.h // cell_h
        row2 = self.rect.y // cell_h + self.rect.h // cell_h
        col1 = (self.rect.x + self.move_speed) // cell_w
        col2 = (self.rect.x + cell_w - self.move_speed) // cell_w
        if 0 <= row1 < len(level) and 0 <= col1 < len(level[-1]) and \
                0 <= row2 < len(level) and 0 <= col2 < len(level[-1]) and \
                (level[row1][col1] == '#' or level[row2][col2] == '#'):
            self.min_y = (self.rect.y // cell_h) * cell_h
        else:
            self.min_y = height - self.rect.height
        row1 = self.rect.y // cell_h
        col1 = (self.rect.x + self.move_speed) // cell_w
        row2 = self.rect.y // cell_h
        col2 = (self.rect.x + cell_w - self.move_speed) // cell_w
        if 0 <= row1 < len(level) and 0 <= col1 < len(level[-1]) and \
                0 <= row2 < len(level) and 0 <= col2 < len(level[-1]) and \
                (level[row1][col1] == '#' or level[row2][col2] == '#'):
            self.max_y = self.rect.y // cell_h * cell_h
            self.speed_y = 0
            self.rect.y = self.max_y + cell_h
        else:
            self.max_y = 0
        row1 = self.rect.y // cell_w
        col1 = self.rect.x // cell_w + self.rect.w // cell_w
        row2 = self.rect.y // cell_w + 1
        col2 = self.rect.x // cell_w + self.rect.w // cell_w
        if 0 <= row1 < len(level) and 0 <= col1 < len(level[-1]) and \
                0 <= row2 < len(level) and 0 <= col2 < len(level[-1]) and \
                (level[row1][col1] == '#' or level[row2][col2] == '#'):
            self.max_x = self.rect.x
        else:
            self.max_x = width - player_w
        row1 = self.rect.y // cell_h
        col1 = self.rect.x // cell_w
        row2 = self.rect.y // cell_h + 1
        col2 = self.rect.x // cell_w
        if 0 <= row1 < len(level) and 0 <= col1 < len(level[-1]) and \
                0 <= row2 < len(level) and 0 <= col2 < len(level[-1]) and \
                (level[row1][col1] == '#' or level[row2][col2] == '#'):
            self.min_x = self.rect.x
            self.rect.x += 1
        else:
            self.min_x = 0

    def shoot(self):
        if self.equipped and self.shoot_cooldown == 0 and first_weapon != 'empty':
            pos_x = player.rect.x - player.rect.w if player.direction < 0 \
                else player.rect.x + player.rect.w
            pos_y = player.rect.y
            self.bullet = Bullet(bul_img, pos_x, pos_y, damage=player.damage,
                                 speed_x=(0 * player.direction), speed_y=0, gravitated=False,
                                 timer=0.1)
            self.shoot_cooldown = 1


class Bullet(AnimatedSprite):
    def __init__(self, img, pos_x, pos_y, damage, speed_x, speed_y, gravitated, timer):
        super().__init__(img, 5, 1, pos_x, pos_y, player_attacks)
        self.image = pygame.transform.scale(img, (cell_w, cell_h))
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        level_sprites[room_number][1].append(self)
        self.rect.x = pos_x
        self.rect.y = pos_y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.timer = timer
        self.damage = damage
        self.direction = -1
        if self.speed_x == 0:
            self.rotate(player.direction)
        self.gravitated = gravitated

    def kill(self):
        super().kill()
        if self in level_sprites[room_number][1]:
            level_sprites[room_number][1].remove(self)

    def update(self):
        super().update()
        if self.timer > 0:
            self.timer -= 1 / fps
        else:
            self.kill()

        if self.speed_x > 0:
            new_dir = 1
        elif self.speed_x < 0:
            new_dir = -1
        else:
            new_dir = 0
        self.rotate(new_dir)
        if self.gravitated:
            self.speed_y -= gravity
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

    def rotate(self, new_dir):
        if new_dir and new_dir != self.direction:
            flip_x = True
            flip_y = False
            self.direction = new_dir
            self.image = pygame.transform.flip(self.image, flip_x, flip_y)
        if self.direction == 1:
            self.reversed = True
        elif self.direction == -1:
            self.reversed = False


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

    def update(self):
        if pygame.sprite.collide_mask(self, player):
            pass


class Creature(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, img, size_x, size_y, health=100, damage=1, speed=2):
        super().__init__(all_sprites, creature_group)
        self.image = pygame.transform.scale(img, (size_x, size_y))
        self.rect = self.image.get_rect().move(
            cell_w * pos_x, cell_h * pos_y)
        self.speed_x = 0
        self.speed_y = 0
        self.max_health = health
        self.health = health
        self.damage = damage
        self.move_speed = speed
        self.direction = -1
        self.pos = (pos_x, pos_y)
        self.mask = pygame.mask.from_surface(self.image)
        self.plat = False
        self.min_y = height - self.rect.height
        self.max_y = 0
        self.max_x = width - self.rect.width
        self.min_x = 0

    def movement(self, line, direction="up"):
        if line == "x":
            if direction == "right":
                vx = self.move_speed
            elif direction == "left":
                vx = -self.move_speed
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
                    vy = -self.move_speed
                else:
                    vy = self.speed_y
            else:
                vy = 0
                print("wrong direction", line)
            self.speed_y = vy
        if line == "stop":
            pass

    def kill(self):
        super().kill()
        if self in level_sprites[room_number][1]:
            level_sprites[room_number][1].remove(self)

    def update(self):
        # умирание
        if self.health <= 0:
            self.kill()

        # коллайд со стенами
        self.collide()
        # елси на платформе
        if self.rect.y == self.min_y:
            self.plat = True
            self.speed_y -= gravity
        else:
            self.plat = False

        self.speed_y += gravity
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.speed_x > 0:
            new_dir = 1
        elif self.speed_x < 0:
            new_dir = -1
        else:
            new_dir = 0
        self.rotate(new_dir)
        # функция стен (!ее нельзя переносить относительно других штук в этой функции!)
        if self.rect.x >= self.max_x:
            self.rect.x = self.max_x
        if self.rect.x <= self.min_x:
            self.rect.x = self.min_x

        if self.rect.y >= self.min_y:
            self.rect.y = self.min_y
        if self.rect.y <= self.max_y:
            self.rect.y = self.max_y

    def rotate(self, new_dir):
        if new_dir and new_dir != self.direction:
            flip_x = True
            flip_y = False
            self.direction = new_dir
            self.image = pygame.transform.flip(self.image, flip_x, flip_y)

    def collide(self):
        row1 = self.rect.y // cell_h + self.rect.h // cell_h
        row2 = self.rect.y // cell_h + self.rect.h // cell_h
        col1 = (self.rect.x + self.move_speed) // cell_w
        col2 = (self.rect.x + cell_w - self.move_speed) // cell_w
        if 0 <= row1 < len(level) and 0 <= col1 < len(level[-1]) and \
                0 <= row2 < len(level) and 0 <= col2 < len(level[-1]) and \
                level[row1][col1] == '#' or \
                level[row2][col2] == '#':
            self.min_y = (self.rect.y // cell_h) * cell_h
        else:
            self.min_y = height - self.rect.height
        row1 = self.rect.y // cell_h
        col1 = (self.rect.x + self.move_speed) // cell_w
        row2 = self.rect.y // cell_h
        col2 = (self.rect.x + cell_w - self.move_speed) // cell_w
        if 0 <= row1 < len(level) and 0 <= col1 < len(level[-1]) and \
                0 <= row2 < len(level) and 0 <= col2 < len(level[-1]) and \
                level[row1][col1] == '#' or \
                level[row2][col2] == '#':
            self.max_y = self.rect.y // cell_h * cell_h
            self.speed_y = 0
            self.rect.y = self.max_y + cell_h
        else:
            self.max_y = 0
        row1 = self.rect.y // cell_w
        col1 = self.rect.x // cell_w + self.rect.w // cell_w
        row2 = self.rect.y // cell_w + 1
        col2 = self.rect.x // cell_w + self.rect.w // cell_w
        if 0 <= row1 < len(level) and 0 <= col1 < len(level[-1]) and \
                0 <= row2 < len(level) and 0 <= col2 < len(level[-1]) and \
                level[row1][col1] == '#' or \
                level[row2][col2] == '#':
            self.max_x = self.rect.x
        else:
            self.max_x = width - player_w
        row1 = self.rect.y // cell_h
        col1 = self.rect.x // cell_w
        row2 = self.rect.y // cell_h + 1
        col2 = self.rect.x // cell_w
        if 0 <= row1 < len(level) and 0 <= col1 < len(level[-1]) and \
                0 <= row2 < len(level) and 0 <= col2 < len(level[-1]) and \
                level[row1][col1] == '#' or \
                level[row2][col2] == '#':
            self.min_x = self.rect.x
            self.rect.x += 1
        else:
            self.min_x = 0


class Enemy(Creature):
    def __init__(self, pos_x, pos_y, img):
        super().__init__(pos_x, pos_y, img, cell_w, cell_h * 2)

    def movement(self, line, direction="up"):
        if line == "x":
            vx = 0
            if direction == "right":
                vx = self.move_speed
            elif direction == "left":
                vx = -self.move_speed
            elif direction == "stop":
                vx = 0
            self.speed_x = vx

    def draw_hp(self):
        length_of_health_bar = cell_w * 2
        hp_val = 5
        hp_size = (length_of_health_bar / self.max_health) * hp_val
        start_of_bar = self.rect.centerx - (length_of_health_bar // 2)
        for hp in range(0, round(self.health), hp_val):
            screen.blit(pygame.transform.scale(heart_image, (hp_size, hp_size)),
                        (start_of_bar + hp, self.rect.y - hp_size * 2))

    def AI(self):
        direction = random.randint(0, 3)
        if direction <= 1:
            self.movement("x", "left")
        elif direction <= 2:
            self.movement("x", "stop")
        else:
            self.movement("x", "right")

    def update(self):
        super().update()
        # self.AI()
        self.draw_hp()
        if pygame.sprite.collide_mask(self, player):
            player.health -= self.damage
        # print(player_attacks)
        for obj in player_attacks:
            if pygame.sprite.collide_mask(self, obj):
                self.health -= obj.damage
                # print(self.health)


class Player(Creature):
    def __init__(self, pos_x, pos_y, img):
        super().__init__(pos_x, pos_y, img, cell_w, cell_h * 2, damage=0, speed=5)
        self.weapon = None
        self.stats = [0, 0]

    def update(self):
        super().update()
        if self.weapon:
            self.damage, self.move_speed = weapon_images[first_weapon][1], weapon_images[first_weapon][2] * self.move_speed
            self.weapon.update()
            self.weapon.pos_x = self.rect.x
            self.weapon.pos_y = self.rect.y

    def attack(self):
        if self.weapon:
            self.weapon.shoot()


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
    player_img = load_image('sad_cat.jpg')
    enemy_img = load_image('box.png')
    bul_img = load_image('hit_sheet.png')
    wall_img = load_image('box.png')
    heart_image = load_image("small_heart.png")
    first_weapon = 'empty'
    second_weapon = 'empty'
    invent_image = load_image('рамка.png')
    tile_images = {
        'wall': load_image('box.png'),
        'empty': load_image('grass.png')
    }
    weapon_images = {
        'empty': [load_image('empty.png'), 0, 1],
        'spoon': [load_image('spoon.png'), 1, 1],
        'syringe': [load_image('syringe.png'), 5, 1]
    }
    chests_images = {
        "closed": load_image('closed_chest.png'),
        "open": load_image('opened_chest.png')
    }
    weapons = ['spoon', 'syringe']
    doors_images = {
        0: load_image("green_door.png"),
        1: load_image("door_1.png"),
        2: load_image("door_2.png"),
        3: load_image("door_3.png"),
        "F": load_image("exit_door.png"),
    }

    stage = 0

    all_sprites = SpriteGroup()
    player_group = SpriteGroup()
    walls = []
    player = None
    room_number = 0
    level_map = load_level('room 0')
    room_maps = [0] * 9
    level_sprites = [0] * 9
    generate_level(level_map, 'room 0')
    only_player_group.add(player)

    running = True
    while running:
        screen.fill((0, 0, 0))
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            player.movement("y", "up")
        if keys[pygame.K_a]:
            player.movement("x", "left")
        if keys[pygame.K_d]:
            player.movement("x", "right")
        if keys[pygame.K_s]:
            player.movement("y", "down")
        if not (keys[pygame.K_a] or keys[pygame.K_d]):  # если юзер не двигается по х, тогда стоп
            player.movement("x", "stop")

        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed[0]:  # нужно будет заменить ноль на константу из pygame (девая кнопка мыши)
            player.attack()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    # "Е" рядом с пистолетом
                    # берем все пистолеты в комнате
                    gun_group = pygame.sprite.Group(list(filter(lambda obj: isinstance(obj, Gun),
                                                                level_sprites[room_number][1])))
                    if pygame.sprite.spritecollideany(player, gun_group):
                        # оставляем только те, с которыми коллайдится игрок
                        equipable_entities = list(filter(
                            lambda obj: pygame.sprite.collide_mask(player, obj), list(gun_group)))
                        if equipable_entities:
                            equipable_entities[-1].equip()
                            if first_weapon == 'empty':
                                first_weapon = equipable_entities[-1].type
                                print(first_weapon)
                            elif first_weapon and second_weapon == 'empty' and first_weapon != equipable_entities[-1].type:
                                second_weapon = equipable_entities[-1].type
                                print(second_weapon)
                    # "Е" рядом с дверью
                    if pygame.sprite.spritecollideany(player, doors_group):
                        door_group = pygame.sprite.Group(
                            list(filter(lambda obj: isinstance(obj, Door) or isinstance(obj, Exit),
                                        level_sprites[room_number][1])))
                        near_doors = list(filter(
                            lambda obj: pygame.sprite.collide_mask(player, obj), list(door_group)))
                        if near_doors:
                            near_doors[-1].enter()
                    # "Е" рядом с сундуком
                    if pygame.sprite.spritecollideany(player, chests_group):
                        door_group = pygame.sprite.Group(
                            list(filter(lambda obj: isinstance(obj, Chest),
                                        level_sprites[room_number][1])))
                        near_chests = list(filter(
                            lambda obj: pygame.sprite.collide_mask(player, obj), list(chests_group)))
                        if near_chests:
                            near_chests[-1].open()
                # замена оружия на второстепенное
                if event.key == pygame.K_q:
                        first_weapon, second_weapon = second_weapon, first_weapon

        level = room_maps[room_number]
        # print(level_sprites[room_number])
        all_sprites = pygame.sprite.Group(level_sprites[room_number][0])
        all_sprites.update()
        all_sprites.draw(screen)
        all_sprites = pygame.sprite.Group(level_sprites[room_number][1])
        all_sprites.update()
        all_sprites.draw(screen)
        only_player_group.update()
        only_player_group.draw(screen)

        draw_interface()
        clock.tick(fps)
        pygame.display.flip()
