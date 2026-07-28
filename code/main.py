import pygame
from settings import *
from player import Player

class Game:
    def __init__(self):
        # setup
        pygame.init()
        pygame.display.set_caption("survive")
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.running = True
        self.clock = pygame.time.Clock()

        # groups
        self.all_sprites = pygame.sprite.Group()
        
        # sprites
        self.player = Player((400, 300), self.all_sprites)

    def run(self):
        while self.running:
            # dt
            dt = self.clock.tick() / 1000
            
            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # update 
            self.all_sprites.update(dt)

            # draw 
            self.display_surface.fill('grey')
            self.all_sprites.draw(self.display_surface)
            pygame.display.update()

        pygame.quit()

# game.run() will work as long as the file running it is '__main__'
if __name__ == '__main__':
    game = Game()
    game.run()
