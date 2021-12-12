import pygame
from copy import deepcopy


class Board:
    # создание поля
    def __init__(self, width, height, left=15, top=15, cell_color=(255, 255, 255)):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        # значения по умолчанию
        self.left = left
        self.top = top
        self.cell_size = 30
        self.color = cell_color

    # настройка внешнего вида
    def set_view(self, left=15, top=15, cell_size=30):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, sc):
        for row in range(self.height):
            for col in range(self.width):
                left, top = self.left + col * self.cell_size, self.top + row * self.cell_size
                if self.board[row][col]:
                    w = 0
                else:
                    w = 1
                pygame.draw.rect(sc, self.color, (left, top, self.cell_size, self.cell_size), width=w)

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell:
            self.on_click(cell)

    def get_cell(self, mouse_pos):
        x, y = (mouse_pos[0] - self.left), (mouse_pos[1] - self.left)
        if x <= 0 or y <= 0:
            return None
        if x >= self.cell_size * self.width or y >= self.cell_size * self.height:
            return None
        if x % self.cell_size == 0 or x % self.cell_size == 0:
            return None
        return (mouse_pos[1] - self.top) // self.cell_size, (mouse_pos[0] - self.left) // self.cell_size

    def on_click(self, c_cords):
        print(c_cords)

    def checked(self, c):
        return 0 <= c[0] < self.width and 0 <= c[1] < self.height

    def neighbours(self, col, row):
        raw_cords = [(col - 1, row - 1), (col, row - 1), (col + 1, row - 1),
                     (col - 1, row), (col + 1, row),
                     (col - 1, row + 1), (col, row + 1), (col + 1, row + 1)]
        cords = list(map(lambda x: self.board[x[1]][x[0]], filter(lambda x: self.checked(x), raw_cords)))
        return sum(cords)


class Life(Board):
    def __init__(self, width, height, left=15, top=15, cell_color=(255, 255, 255)):
        super().__init__(width, height, left=left, top=top, cell_color=cell_color)

    def render(self, sc):
        for row in range(self.height):
            for col in range(self.width):
                left, top = self.left + col * self.cell_size, self.top + row * self.cell_size
                if self.board[row][col]:
                    w = 0
                else:
                    w = 1
                pygame.draw.rect(sc, self.color, (left, top, self.cell_size, self.cell_size), width=w)
                if self.board[row][col]:
                    pygame.draw.rect(sc, pygame.Color("white"), (left, top, self.cell_size, self.cell_size), width=0)
                # elif self.neighbours(col, row) == 1:
                #     pygame.draw.rect(sc, pygame.Color("green"), (left, top, self.cell_size, self.cell_size), width=0)
                # elif self.neighbours(col, row) == 2:
                #     pygame.draw.rect(sc, pygame.Color("blue"), (left, top, self.cell_size, self.cell_size), width=0)
                # elif self.neighbours(col, row) == 3:
                #     pygame.draw.rect(sc, pygame.Color("red"), (left, top, self.cell_size, self.cell_size), width=0)

    def on_click(self, c_cords):
        self.board[c_cords[0]][c_cords[1]] = 0 if self.board[c_cords[0]][c_cords[1]] else 1

    def next_move(self):
        new_board = deepcopy(self.board)
        for row in range(self.height):
            for col in range(self.width):
                n = self.neighbours(col, row)
                if self.board[row][col] == 1:
                    if n < 2 or n > 3:
                        new_board[row][col] = 0
                    else:
                        new_board[row][col] = 1
                else:
                    if n == 3:
                        new_board[row][col] = 1
        self.board = deepcopy(new_board)

    def checked(self, c):
        return 0 <= c[0] < self.width and 0 <= c[1] < self.height

    def neighbours(self, col, row):
        raw_cords = [(col - 1, row - 1), (col, row - 1), (col + 1, row - 1),
                     (col - 1, row), (col + 1, row),
                     (col - 1, row + 1), (col, row + 1), (col + 1, row + 1)]
        cords = list(map(lambda x: self.board[x[1]][x[0]], filter(lambda x: self.checked(x), raw_cords)))
        return sum(cords)


if __name__ == '__main__':
    pygame.init()
    size = width, height = 1000, 1000
    screen = pygame.display.set_mode(size)
    screen.fill(pygame.Color("black"))
    clock = pygame.time.Clock()
    fps = 60
    board = Life(50, 50)
    board.set_view(0, 0, 20)
    running = True
    evolving = False
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                board.get_click(event.pos)
            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 3) or \
                    (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                evolving = not evolving
            if event.type == pygame.MOUSEWHEEL:
                fps += event.y
                if fps <= 0:
                    fps = 1
                if fps > 60:
                    fps = 60
        if evolving:
            board.next_move()
        screen.fill((0, 0, 0))
        board.render(screen)
        clock.tick(fps)
        pygame.display.flip()
    pygame.quit()
