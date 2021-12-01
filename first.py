import pygame


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
        self.turn = 1

    # настройка внешнего вида
    def set_view(self, left=15, top=15, cell_size=30):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, sc):
        for row in range(self.height):
            for col in range(self.width):
                left, top = self.left + col * self.cell_size, self.top + row * self.cell_size
                pygame.draw.rect(sc, self.color, (left, top, self.cell_size, self.cell_size), width=1)
                if self.board[row][col] == 1:
                    center_l = left + self.cell_size // 2
                    center_r = top + self.cell_size // 2
                    pygame.draw.circle(sc, pygame.Color("red"),
                                       (center_l, center_r), (self.cell_size // 2 - 2), width=2)
                elif self.board[row][col] == 2:
                    pygame.draw.line(sc, pygame.Color("blue"),
                                     (left + 2, top + 2), (left + self.cell_size - 2, top + self.cell_size - 2), width=2)
                    pygame.draw.line(sc, pygame.Color("blue"),
                                     (left + 2, top + self.cell_size - 2), (left + self.cell_size - 2, top + 2), width=2)

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
        ri, ci = c_cords
        print(c_cords)
        if self.board[ri][ci] == 0:
            self.board[ri][ci] = self.turn
            self.turn = 2 if self.turn == 1 else 1

if __name__ == '__main__':
    pygame.init()
    size = width, height = 500, 500
    screen = pygame.display.set_mode(size)
    screen.fill(pygame.Color("black"))
    clock = pygame.time.Clock()
    fps = 60
    board = Board(5, 7)
    board.set_view(50, 50, 30)
    running = True
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                board.get_click(event.pos)
        screen.fill((0, 0, 0))
        board.render(screen)
        clock.tick(fps)
        pygame.display.flip()
    pygame.quit()
