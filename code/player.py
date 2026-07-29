from settings import *


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        self.load_images()
        self.state, self.frame_index = "down", 0
        self.image = pygame.image.load(join("..", "images", "player", "down", "0.png")).convert_alpha()
        self.rect = self.image.get_frect(center= pos)
        self.hitbox_rect = self.rect.inflate(-60,-90)

        # health
        self.hp = 10
        self.max_hp = self.hp
        
        self.can_take_damage = True
        self.flash_duration = 100
        self.damage_cooldown = 1000
        self.damage_time = 0

        # movement
        self.direction = pygame.math.Vector2()
        self.speed = 500
        self.collision_sprites = collision_sprites

    def load_images(self):
        self.frames = {"left": [], "right": [], "up": [], "down": []}

        for state in self.frames.keys():
            for folder_path, sub_folders, file_names in walk(join("..", "images", "player", state)):
                if file_names:
                    for file_name in sorted(file_names, key= lambda name: int(name.split(".")[0])):
                        full_path = join(folder_path, file_name)
                        surf = pygame.image.load(full_path).convert_alpha()
                        self.frames[state].append(surf)

    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])
        self.direction = self.direction.normalize() if self.direction else self.direction

    def move(self, dt):
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')
        self.rect.center = self.hitbox_rect.center # this need to happen other wise the only thing moving is the hitbox.

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0: self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0: self.hitbox_rect.left = sprite.rect.right
                elif direction == 'vertical':
                    if self.direction.y > 0: self.hitbox_rect.bottom = sprite.rect.top
                    if self.direction.y < 0: self.hitbox_rect.top = sprite.rect.bottom

    def take_damage(self, ammount):
        if not self.can_take_damage:
            return

        self.hp -= ammount

        self.can_take_damage = False
        self.damage_time = pygame.time.get_ticks()

    def damage_timer(self):
        if not self.can_take_damage:
            elapsed = pygame.time.get_ticks() - self.damage_time

            if elapsed >= self.damage_cooldown:
                self.can_take_damage = True

    def flicker(self):
        elapsed = pygame.time.get_ticks() - self.damage_time

        if elapsed < self.flash_duration:
            white = pygame.mask.from_surface(self.image).to_surface()
            white.set_colorkey((0,0,0))
            self.image = white

        else:
            if int(pygame.time.get_ticks() / 100) % 2:
                self.image.set_alpha(80)
            else:
                self.image.set_alpha(255)

    def animate(self, dt):
        # get state
        if self.direction.x != 0:
            self.state = "right" if self.direction.x > 0 else "left"
        if self.direction.y != 0:
            self.state = "down" if self.direction.y > 0 else "up"

        # animate state
        self.frame_index = self.frame_index + 6 * dt if self.direction else 0
        frame = self.frames[self.state][int(self.frame_index) % len(self.frames[self.state])]
        self.image = frame.copy()

        if not self.can_take_damage:
            self.flicker()

    def update(self, dt):
        self.input()
        self.move(dt)
        self.animate(dt)
        self.damage_timer()

