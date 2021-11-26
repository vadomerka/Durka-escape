import pygame


def draw_cycle(sc, pos):
    color = pygame.Color("white")
    pygame.draw.circle(sc, color, pos, 10)


if __name__ == '__main__':
    pygame.init()
    size = width, height = 200, 200
    screen = pygame.display.set_mode(size)
    screen.fill(pygame.Color("black"))
    count = 0
    clock = pygame.time.Clock()
    fps = 60
    mouse_pos = None
    move = False
    running = True
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            # при закрытии окна
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.WINDOWHIDDEN:
                count += 1
                # print(count)
        font = pygame.font.Font(None, 100)
        text = font.render(str(count), True, (255, 0, 0))
        screen.blit(text, (85, 60))
        clock.tick(fps)
        pygame.display.flip()
    pygame.quit()
