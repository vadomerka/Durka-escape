import pygame


def draw_cycle(sc, pos):
    color = pygame.Color("white")
    pygame.draw.circle(sc, color, pos, 10)


if __name__ == '__main__':
    pygame.init()
    size = width, height = 300, 300
    screen = pygame.display.set_mode(size)
    screen.fill(pygame.Color("black"))
    repos = 0, 0
    dif = 0, 0
    pygame.draw.rect(screen, pygame.Color("green"), (*repos, 100, 100), width=0)
    clock = pygame.time.Clock()
    fps = 60
    mouse_pos = None
    move = False
    running = True
    while running:
        # screen.fill((0, 0, 0))
        for event in pygame.event.get():
            # при закрытии окна
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if repos[0] <= event.pos[0] <= repos[0] + 100 and \
                        repos[1] <= event.pos[1] <= repos[1] + 100:
                    mouse_pos = event.pos
                    dif = mouse_pos[0] - repos[0], mouse_pos[1] - repos[1]
            if event.type == pygame.MOUSEBUTTONUP:
                mouse_pos = None
            if event.type == pygame.MOUSEMOTION:
                if mouse_pos:
                    screen.fill(pygame.Color("black"))
                    mouse_pos = event.pos
                    repos = mouse_pos[0] - dif[0], mouse_pos[1] - dif[1]
                    pygame.draw.rect(screen, pygame.Color("green"), (*repos, 100, 100), width=0)

        clock.tick(fps)
        pygame.display.flip()
    pygame.quit()
