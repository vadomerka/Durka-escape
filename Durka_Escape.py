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
    filename = f"data/levels/stage {str(stage)}/{filename}/{1}"
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        l_m = [li.strip() for li in mapFile]

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
            elif lev[y][x] in enemies:
                background.append((Wall, "empty", x, y))
                front.append((Enemy, x, y, lev[y][x]))
            elif lev[y][x] == 'W':
                background.append((Wall, "empty", x, y))
                front.append((Gun, x, y, random.choice(weapons)))
                lev[y][x] = "."
            elif lev[y][x] == 'C':
                background.append((Wall, "empty", x, y))
                background.append((Chest, chests_images["closed"], x, y))
            elif lev[y][x] == "H":
                background.append((Wall, "empty", x, y))
                front.append((Heal, x, y, "пирожок"))
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
    if stage < max_stage:
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
    else:
        win_screen()


def draw_interface():
    global weapons_info
    for hp in range(0, player.health, 5):
        screen.blit(heart_image, (hp * 5, 0))
    screen.blit(pygame.transform.scale(invent_image, (cell_w * 3, cell_h * 3)),
                (width - cell_w * 3, cell_h))
    if player.first_weapon:
        screen.blit(pygame.transform.scale(weapons_info[player.first_weapon.type][0],
                                           (cell_w * 3, cell_h * 3)), (width - cell_w * 3, cell_h))
    if player.second_weapon:
        screen.blit(pygame.transform.scale(weapons_info[player.second_weapon.type][0],
                                           (cell_w, cell_h)), (width - cell_w * 3, cell_h * 3))


def menu():
    text = ["Начать игру"]

    fn = pygame.transform.scale(load_image('psix.jpg'), (screen.get_size()))
    screen.blit(fn, (0, 0))
    fnt = pygame.font.Font(None, 50)
    text_cord = 240
    for lin in text:
        string_render = fnt.render(lin, 1, pygame.Color('black'))
        int_rect = string_render.get_rect()
        text_cord += 10
        int_rect.top = text_cord
        int_rect.x = 600
        text_cord += int_rect.height
        screen.blit(string_render, int_rect)


def start_screen(storytelling=True):
    comics_count = 0 if storytelling else 4
    # menu()
    if comics_count < 3:
        comics_img = pygame.transform.scale(load_image(f'story_{str(comics_count)}.png'),
                                            (screen.get_size()))
        screen.blit(comics_img, (0, 0))
    else:
        menu()
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                terminate()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if comics_count < 3:
                    comics_count += 1
                    comics_img = pygame.transform.scale(load_image(f'story_{str(comics_count)}.png'),
                                                        (screen.get_size()))
                    screen.blit(comics_img, (0, 0))
                else:
                    menu()
                    if 810 > ev.pos[0] > 590 and 350 > ev.pos[1] > 240:
                        return
                if ev.pos[0] and ev.pos[1]:
                    pass

        pygame.display.flip()
        clock.tick(fps)


def new_game():
    global all_sprites, player_group, player, room_number, level_map, room_maps, level_sprites, \
        creature_group, doors_group, only_player_group, player_attacks, chests_group, stage, \
        walls, paused, running
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
    only_player_group = pygame.sprite.Group()
    only_player_group.add(player)
    paused = False
    start_screen(storytelling=False)
    running = True


def statistics(result):
    text = ["Главное меню",
            "",
            "",
            "Убийств: " + str(kills),
            "Смертей: " + str(died),
            "Уровень: " + str(stage),
            "Итог: " + result]

    fn = pygame.transform.scale(load_image('каневский(злится).jpg'), (screen.get_size()))
    screen.blit(fn, (0, 0))
    fnt = pygame.font.Font(None, 50)
    text_cord = 10
    for lin in text:
        string_render = fnt.render(lin, 1, pygame.Color('black'))
        int_rect = string_render.get_rect()
        text_cord += 10
        int_rect.top = text_cord
        int_rect.x = 10
        text_cord += int_rect.height
        screen.blit(string_render, int_rect)


def win_screen():
    global player, player_group, jumps, kills, shoots, level_sprites, level, all_sprites, walls,\
        stage, room_number, room_maps, only_player_group
    comics_count = 0
    if comics_count < 2:
        comics_img = pygame.transform.scale(load_image(f'ending_{str(comics_count)}.png'),
                                            (screen.get_size()))
        screen.blit(comics_img, (0, 0))
    else:
        statistics("победа")

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                terminate()
            elif comics_count < 2 and ev.type == pygame.KEYDOWN:
                comics_count += 1
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                if comics_count < 1:
                    comics_count += 1
                    comics_img = pygame.transform.scale(load_image(f'ending_{str(comics_count)}.png'),
                                                        (screen.get_size()))
                    screen.blit(comics_img, (0, 0))
                else:
                    statistics("победа")
                    if 0 <= ev.pos[0] <= 270 and 0 <= ev.pos[1] <= 60:
                        new_game()
                        return
                # print(event.pos)

        pygame.display.flip()
        clock.tick(fps)


def death_screen():
    global player, player_group, jumps, kills, shoots, level_sprites, level, all_sprites, walls, \
        stage, room_number, room_maps, only_player_group
    statistics("вы погибли")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if 0 <= event.pos[0] <= 270 and 0 <= event.pos[1] <= 60:
                    new_game()
                    return
                # print(event.pos)

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
            weapon = 'empty'
            # while weapon == first_weapon or weapon == second_weapon:
            weapon = random.choice(weapons)
            level_sprites[room_number][1].append(
                Gun(self.rect.x // cell_w, (self.rect.y - self.rect.h) // cell_h, weapon))
            self.rect.y -= size_of_cap
        self.image = chests_images["open"]
        self.opened = True


class Heal(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, type):
        # global player_group
        super().__init__(player_group)
        self.type = type
        self.heal = heals_info[self.type]["heal"]
        self.image = pygame.transform.scale(heals_info[self.type]["img"], (cell_w, cell_h))
        self.rect = self.image.get_rect().move(
            cell_w * pos_x, cell_h * pos_y)
        self.move_speed = 2
        self.speed_x = 0
        self.speed_y = -self.move_speed

        self.mask = pygame.mask.from_surface(self.image)
        self.near_player = False
        self.plat = False
        self.min_y = height - self.rect.h
        self.max_y = 0
        self.max_x = width - self.rect.w
        self.min_x = 0

    def update(self):
        self.collide()
        if self.rect.y == self.min_y:
            self.plat = True
            self.speed_y -= gravity
        else:
            self.plat = False
        if self.plat:
            self.speed_y = 0
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

        if pygame.sprite.collide_mask(self, player):
            self.draw_stats()
            self.near_player = True
        else:
            self.near_player = False

    def draw_stats(self):
        text = ["Wanna grab a " + self.type + "?",
                "             +hp " + str(self.heal)]
        fn = pygame.transform.scale(self.image, (width * 0.8, height * 0.8))
        screen.blit(fn, (width * 0.1, height * 0.1))
        fnt = pygame.font.Font(None, 30)
        text_cord = 50
        for lin in text:
            string_render = fnt.render(lin, 1, pygame.Color('white'))
            int_rect = string_render.get_rect()
            text_cord += 10
            int_rect.top = text_cord
            int_rect.x = 10
            text_cord += int_rect.height
            screen.blit(string_render, int_rect)

    def use(self):
        player.health += player.max_health * self.heal // 100
        if player.health > player.max_health:
            player.health = player.max_health
        if self in level_sprites[room_number][1]:
            level_sprites[room_number][1].remove(self)

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


class Gun(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, type):
        # global player_group
        super().__init__(player_group)
        self.type = type
        self.damage = weapons_info[self.type][1]
        self.attack_speed = weapons_info[self.type][2]
        self.image = pygame.transform.scale(weapons_info[self.type][0], (cell_w, cell_h))
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
        self.range = weapons_info[type][3]

        self.equipped = False

    def update(self):
        self.damage = weapons_info[self.type][1]
        if self.equipped:
            # self.rect.x = width - cell_w * 2.5
            # self.rect.y = cell_h * 1.5
            # self.image = pygame.transform.scale(self.image, (cell_w * 2, cell_h * 2))
            if self.shoot_cooldown > 0:
                self.shoot_cooldown -= (1 / fps)
            else:
                self.shoot_cooldown = 0
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
        if player.first_weapon:
            intro_text = ["Wanna grab a " + self.type + "?",
                          "             old stats: damage " + str(
                              player.first_weapon.damage) + ", speed " + str(player.stats[1]),
                          "             new stats: damage " + str(self.damage) + ", speed " + str(
                              self.attack_speed)]
        else:
            intro_text = ["Wanna grab a " + self.type + "?",
                          "             old stats: damage " + str(0) + ", speed " + str(
                              player.stats[1]),
                          "             new stats: damage " + str(self.damage) + ", speed " + str(
                              self.attack_speed)]
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
        # global level_sprites, room_number

        if player.first_weapon:
            if player.first_weapon.type == self.type:
                # weapons_info[self.type][1] += 5
                player.first_weapon.damage += weapons_info[self.type][1]

        if not player.second_weapon or player.second_weapon.type != self.type:
            if player.first_weapon and player.first_weapon.type != self.type:
                player.first_weapon.equipped = False
                level_sprites[room_number][1].append(player.first_weapon)
                old_weapon = level_sprites[room_number][1][-1]
                old_weapon.image = pygame.transform.scale(weapons_info[old_weapon.type][0],
                                                          (cell_w, cell_h))
                old_weapon.rect = old_weapon.image.get_rect().move(
                    cell_w * old_weapon.pos_x, cell_h * old_weapon.pos_y)
                old_weapon.speed_x = random.randint(-old_weapon.move_speed, old_weapon.move_speed)
                old_weapon.speed_y = -old_weapon.move_speed
            player.first_weapon = self
            if self in level_sprites[room_number][1]:
                level_sprites[room_number][1].remove(self)
            self.equipped = True

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
        global shoots
        shoots += 1
        if weapons_info[self.type][3] == 'melee':
            if self.equipped and self.shoot_cooldown == 0:
                pos_x = player.rect.x - player.rect.w if player.direction < 0 \
                    else player.rect.x + player.rect.w
                pos_y = player.rect.y
                self.bullet = Bullet_A(bul_img, row_sheet=5, col_sheet=1, pos_x=pos_x, pos_y=pos_y,
                                       damage=self.damage,
                                       speed_x=(0 * player.direction), speed_y=0, gravitated=False,
                                       timer=0.1)
                self.shoot_cooldown = 1

        elif weapons_info[self.type][3] == 'long-range':
            if self.equipped and self.shoot_cooldown == 0:
                pos_x = player.rect.x if player.direction < 0 \
                    else player.rect.x + player.rect.w
                pos_y = player.rect.y
                self.bullet = Bullet(drop_img, pos_x, pos_y, damage=self.damage,
                                     speed_x=(5 * player.direction), speed_y=0, gravitated=False,
                                     timer=1)
                self.shoot_cooldown = 0.3

        elif weapons_info[self.type][3] == 'on suppression':
            if self.equipped and self.shoot_cooldown == 0:
                pos_x = player.rect.x if player.direction < 0 \
                    else player.rect.x + player.rect.w
                pos_y = player.rect.y
                self.bullet = Bullet(fire_img, pos_x, pos_y, damage=self.damage,
                                     speed_x=(5 * player.direction), speed_y=-1.5, gravitated=True,
                                     timer=1)
                self.shoot_cooldown = 0.1


class Bullet(Sprite):
    def __init__(self, img, pos_x, pos_y, damage, speed_x, speed_y, gravitated, timer):
        super().__init__(player_attacks)
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
        self.mask = pygame.mask.from_surface(self.image)

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
            self.speed_y += gravity
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


class Bullet_A(AnimatedSprite):
    def __init__(self, img, row_sheet=1, col_sheet=1, pos_x=0, pos_y=0, damage=1, speed_x=0,
                 speed_y=0, gravitated=False, timer=1):
        super().__init__(img, row_sheet, col_sheet, pos_x, pos_y, player_attacks)
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
        global jumps
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
        global kills, died
        super().kill()
        if self.__class__ == Player:
            died += 1
            death_screen()
        else:
            kills += 1
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


class Enemy(Creature):
    def __init__(self, pos_x, pos_y, name):
        super().__init__(pos_x, pos_y, enemy_images[name][0], cell_w, cell_h * 2,
                         enemy_images[name][1] * (stage + 1), enemy_images[name][2])
        self.time = 0
        self.frames_count = 1

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
        hp_size = 5
        start_of_bar = self.rect.centerx - (length_of_health_bar // 2)
        for y in range(0, round(self.health // 100)):
            for x in range(0, 100, hp_val):
                screen.blit(pygame.transform.scale(heart_image, (hp_size, hp_size)),
                            (start_of_bar + x, self.rect.y - hp_size * (2 + y)))
        for x in range(0, round(self.health % 100), 5):
            screen.blit(pygame.transform.scale(heart_image, (hp_size, hp_size)),
                        (start_of_bar + x, self.rect.y - hp_size * 2))

    def AI(self, free_r=False, free_l=False, stop=False):
        if free_l:
            direction = 1
        elif free_r:
            direction = 2
        elif stop:
            direction = 0
        else:
            direction = random.randint(0, 2)
        if direction == 1:
            self.movement("x", "left")
        elif direction == 2:
            self.movement("x", "right")
        else:
            self.movement("x", "stop")

    def update(self):
        super().update()
        if self.time % (fps // self.frames_count) == 0:
            self.AI()
        self.time = (self.time + 1) % fps
        self.draw_hp()
        if pygame.sprite.collide_mask(self, player):
            player.health -= self.damage
        for obj in player_attacks:
            if pygame.sprite.collide_mask(self, obj):
                self.health -= obj.damage
                obj.kill()

    def collide(self):
        super().collide()
        row1 = self.rect.y // cell_h
        col1 = self.rect.x // cell_w
        col2 = self.rect.x // cell_w
        row2 = self.rect.y // cell_h + self.rect.h // cell_h
        if 0 <= row1 < len(level) and 0 <= col1 < len(level[-1]) and \
                0 <= row2 < len(level) and 0 <= col2 < len(level[-1]) and \
                level[row2][col2 + 1] == '.' and \
                level[row2][col2 - 1] == '.':
            self.AI(False, False, True)
        elif 0 <= row1 < len(level) and 0 <= col1 < len(level[-1]) and \
                0 <= row2 < len(level) and 0 <= col2 < len(level[-1]) and \
                level[row2][col2 + 1] == '.':
            self.AI(False, True)
        elif 0 <= row1 < len(level) and 0 <= col1 < len(level[-1]) and \
                0 <= row2 < len(level) and 0 <= col2 < len(level[-1]) and \
                level[row2][col2] == '.':
            self.AI(True, False)


class Player(Creature):
    def __init__(self, pos_x, pos_y, img):
        super().__init__(pos_x, pos_y, img, cell_w, cell_h * 2, damage=0, speed=5)
        self.first_weapon = None
        self.second_weapon = None
        self.stats = [0, 0]

    def update(self):
        super().update()
        if self.first_weapon:
            self.first_weapon.damage = weapons_info[self.first_weapon.type][1]
            self.first_weapon.update()
            self.first_weapon.pos_x = self.rect.x // cell_w
            self.first_weapon.pos_y = self.rect.y // cell_h
        if self.second_weapon:
            self.second_weapon.update()
            self.second_weapon.pos_x = self.rect.x // cell_w
            self.second_weapon.pos_y = self.rect.y // cell_h

    def left_attack(self):
        if self.first_weapon:
            self.first_weapon.shoot()

    def right_attack(self):
        if self.second_weapon:
            self.second_weapon.shoot()


if __name__ == '__main__':
    jumps = 0
    died = 0
    shoots = 0
    kills = 0
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
    player_img = load_image('player.png')
    enemy_img = load_image('worker1.png')
    bul_img = load_image('hit_sheet.png')
    drop_img = load_image('drop.png', -1)
    fire_img = load_image('fire.png', -1)
    melee_img = load_image("hit.png")
    heart_image = load_image("small_heart.png")
    first_weapon = 'empty'
    second_weapon = 'empty'
    invent_image = load_image('рамка.png')
    tile_images = {
        'wall': load_image('box.png'),
        'empty': load_image('grey wall.jpg')
    }
    weapons_info = {
        'empty': [load_image('empty.png'), 0, 1, 'melee'],
        'spoon': [load_image('spoon.png'), 3, 1, 'melee'],
        'syringe': [load_image('syringe.png'), 10, 1, 'long-range'],
        'broken extinguisher': [load_image('fire_extinguisher.png'), 3, 1, 'on suppression']
    }
    heals_info = {
        "пирожок": {
            "img": load_image("pie.png"),
            "heal": 30
        }
    }
    chests_images = {
        "closed": load_image('closed_chest.png'),
        "open": load_image('opened_chest.png')
    }
    weapons = ['spoon', 'syringe', 'broken extinguisher']
    doors_images = {
        0: load_image("green_door.png"),
        1: load_image("door_1.png"),
        2: load_image("door_2.png"),
        3: load_image("door_3.png"),
        4: load_image("door_4.png"),
        "F": load_image("exit_door.png"),
    }
    enemy_images = {
        'X': [load_image('worker1.png'), 100, 1],
        'S': [load_image('security.png'), 150, 3]
    }
    enemies = ['X', 'S']
    max_stage = 1

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
    paused = False
    start_screen()
    running = True
    while running:
        screen.fill((0, 0, 0))
        if not paused:
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
            if mouse_pressed[
                0]:  # нужно будет заменить ноль на константу из pygame (девая кнопка мыши)
                player.left_attack()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e and not paused:
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
                            equipable_entities[-1].kill()
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
                        chest_group = pygame.sprite.Group(
                            list(filter(lambda obj: isinstance(obj, Chest) and not obj.opened,
                                        level_sprites[room_number][0])))
                        near_chests = list(filter(
                            lambda obj: pygame.sprite.collide_mask(player, obj), list(chest_group)))
                        if near_chests:
                            near_chests[-1].open()

                    if pygame.sprite.spritecollideany(player, player_group):
                        heals_group = pygame.sprite.Group(
                            list(filter(lambda obj: isinstance(obj, Heal),
                                        level_sprites[room_number][1])))
                        near_heals = list(filter(
                            lambda obj: pygame.sprite.collide_mask(player, obj), list(heals_group)))
                        if near_heals:
                            near_heals[-1].use()
                # замена оружия на второстепенное
                if event.key == pygame.K_q and not paused:
                    player.first_weapon, player.second_weapon = player.second_weapon, player.first_weapon
                # пауза
                if event.key == pygame.K_ESCAPE:
                    if not paused:
                        paused = True
                    else:
                        paused = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if paused:
                    if 370 > event.pos[0] > 50 and 100 > event.pos[1] > 50:
                        paused = False
                    elif 160 > event.pos[0] > 40 and 180 > event.pos[1] > 140:
                        new_game()

        if not paused:
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
        else:
            intro_text = ["Продолжить игру", "", "Меню"]
            fon = pygame.transform.scale(load_image('paused.jpg'), (screen.get_size()))
            screen.blit(fon, (0, 0))
            font = pygame.font.Font(None, 50)
            text_coord = 50
            for line in intro_text:
                string_rendered = font.render(line, 1, pygame.Color('black'))
                intro_rect = string_rendered.get_rect()
                text_coord += 10
                intro_rect.top = text_coord
                intro_rect.x = 50
                text_coord += intro_rect.height
                screen.blit(string_rendered, intro_rect)
        clock.tick(fps)
        pygame.display.flip()
