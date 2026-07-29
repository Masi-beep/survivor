import pygame
from settings import *
from player import Player
from sprites import *
from pytmx.util_pygame import load_pygame
from groups import AllSprites

from random import randint, choice

class Game:
    def __init__(self):
        # setup
        pygame.init()
        pygame.display.set_caption("survive")
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.running = True
        self.clock = pygame.time.Clock()
                
        # grop
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        
        # gun timer
        self.can_shoot = True
        self.shoot_time = 0
        self.gun_cooldown = 100
        
        # enemy timer
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, 300)
        self.spawn_positions = []

        # load sounds
        self.impact_sound = pygame.mixer.Sound(join("..", "audio", "impact.ogg"))
        self.impact_sound.set_volume(0.2)
        self.shoot_sound = pygame.mixer.Sound(join("..", "audio", "shoot.wav"))
        self.shoot_sound.set_volume(0.05)
        self.music = pygame.mixer.Sound(join("..", "audio", "music.wav"))
        self.music.set_volume(0.1)
        self.music.play(-1)

        # load font
        self.font = pygame.font.Font(join("..", "images", "Oxanium-Bold.ttf"), 40)

        self.load_images()
        self.setup()


    def load_images(self):
        self.bullet_surf = pygame.image.load(join("..", "images", "gun", "bullet.png")).convert_alpha()
        
        folders = list(walk(join("..", "images", "enemies")))[0][1]
        self.enemy_frames = {}
        for folder in folders:
            for folder_path, _, file_names in walk(join("..", "images", "enemies", folder)):
                self.enemy_frames[folder] = []
                for file_name in sorted(file_names, key= lambda name: int(name.split(".")[0])):
                    full_path = join(folder_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.enemy_frames[folder].append(surf)

    def input(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            pos = self.gun.rect.center + self.gun.player_direction * 50
            Bullet(self.bullet_surf, pos, self.gun.player_direction, (self.all_sprites, self.bullet_sprites))
            self.shoot_sound.play()
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

    def gun_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.gun_cooldown:
                self.can_shoot = True
    
    def setup(self):
        map = load_pygame(join("..", "data", "maps", "world.tmx"))
        for x,y,image in map.get_layer_by_name("Ground").tiles():
            Sprite((x * TILE_SIZE , y * TILE_SIZE), image, self.all_sprites)

        for obj in map.get_layer_by_name("Collisions"):
            CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)),self.collision_sprites)

        for obj in map.get_layer_by_name("Objects"):
            CollisionSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))
        
        for obj in map.get_layer_by_name("Entities"):
            if obj.name == "Player":
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites)
                self.gun = Gun(self.player, self.all_sprites)
            else:
                self.spawn_positions.append((obj.x, obj.y))

    def bullet_collisions(self):
        if self.bullet_sprites:
            # collisions bullet with enemy
            for bullet in self.bullet_sprites:
                collided_sprite = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
                if collided_sprite:
                    for sprite in collided_sprite:
                        self.impact_sound.play()
                        sprite.destroy()
                    bullet.kill()
    
    def player_collision(self):
        # collisions enemy with player
        if pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask):
            self.player.take_damage(1)
            print(self.player.hp)
            if self.player.hp <= 0:
                self.running = False

    def display_health(self):
        health_str = f"{self.player.hp}|{self.player.max_hp}"
        text_surf = self.font.render(health_str, True, (240,240,240))
        text_rect = text_surf.get_frect(midbottom = (100, 100))
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, (240,240,240), text_rect.inflate(20, 15).move(0,-5), 8, 10)

    def run(self):
        while self.running:
            # dt
            dt = self.clock.tick() / 1000
            
            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == self.enemy_event:
                    Enemy(choice(self.spawn_positions), choice(list(self.enemy_frames.values())), (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites)

            # update
            self.gun_timer()
            self.input()
            self.bullet_collisions()
            self.player_collision()
            self.all_sprites.update(dt)

            # draw 
            self.display_surface.fill('grey')
            self.all_sprites.draw(self.player.rect.center)
            self.display_health()
            pygame.display.update()

        pygame.quit()

# game.run() will work as long as the file running it is '__main__'
if __name__ == '__main__':
    game = Game()
    game.run()
