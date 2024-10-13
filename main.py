import pygame
import random

# Inicializar Pygame
pygame.init()

# Definir el tamaño de la pantalla
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Aventura en Arequipa")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Fuentes
font = pygame.font.Font(None, 36)
fontTitle = pygame.font.Font(None, 72)

# Función para cargar y redimensionar imágenes
def load_image(path, size=None):
    try:
        image = pygame.image.load(path).convert_alpha()
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except pygame.error as e:
        print(f"Error al cargar la imagen {path}: {e}")
        return None

# Definir los tamaños deseados para las imágenes
PLAYER_SIZE = (80, 80)
NPC_SIZE = (40, 40)
POINT_SIZE = (150, 150)
BG_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

# Cargar imágenes
player_image = load_image('assets/player.png', PLAYER_SIZE)
npc_image = load_image('assets/npc.png', NPC_SIZE)
plaza_image = load_image('assets/plaza.png', POINT_SIZE)
monasterio_image = load_image('assets/monasterio.png', POINT_SIZE)
mirador_image = load_image('assets/mirador.png', POINT_SIZE)
background_image = load_image('assets/arequipa_bg.jpg', BG_SIZE)
menu_image = load_image('assets/menu.jpg', BG_SIZE)

# Verificar si las imágenes se cargaron correctamente
if not player_image or not npc_image or not plaza_image or not background_image or not monasterio_image or not mirador_image:
    print("Error al cargar las imágenes, verifica las rutas.")
    pygame.quit()
    exit()

# Clase para el jugador
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.center = (400, 300)
        self.speed = 3

    def update(self, pressed_keys):
        if pressed_keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if pressed_keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if pressed_keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if pressed_keys[pygame.K_DOWN]:
            self.rect.y += self.speed

# Clase para NPCs
class NPC(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = npc_image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(0, SCREEN_HEIGHT - self.rect.height)
        self.speed = random.randint(1, 3)
        self.direction = pygame.math.Vector2(random.choice([-1, 1]), random.choice([-1, 1]))

    def update(self):
        if random.random() < 0.01:
            self.direction = pygame.math.Vector2(random.choice([-1, 1]), random.choice([-1, 1]))
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.direction.x *= -1
        if self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT:
            self.direction.y *= -1

# Clase para los puntos de interés
class PointOfInterest(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

# Función para mostrar el menú
def show_menu():
    screen.blit(menu_image, (0, 0))  # Dibujar el fondo en el menú
    title = fontTitle.render("Aventura en Arequipa", True, WHITE)  # Título en blanco
    screen.blit(title, (150, 150))

    # Definir botones
    start_button = pygame.Rect(250, 250, 300, 50)  # Botón de iniciar
    quit_button = pygame.Rect(250, 320, 300, 50)   # Botón de salir

    # Dibujar botones
    pygame.draw.rect(screen, GREEN, start_button)  # Botón de iniciar
    pygame.draw.rect(screen, RED, quit_button)      # Botón de salir

    start_text = font.render("Iniciar Juego", True, WHITE)
    quit_text = font.render("Salir", True, WHITE)
    screen.blit(start_text, (start_button.x + 70, start_button.y + 10))
    screen.blit(quit_text, (quit_button.x + 120, quit_button.y + 10))

    pygame.display.flip()

    in_menu = True
    while in_menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    in_menu = False
                elif event.key == pygame.K_2:
                    pygame.quit()
                    exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    in_menu = False
                elif quit_button.collidepoint(event.pos):
                    pygame.quit()
                    exit()

# Función de puzzle
def puzzle(location):
    screen.fill(BLACK)  # Cambia el color del fondo durante el puzzle
    puzzle_text = font.render(f"Resuelve el puzzle de {location}", True, WHITE)
    screen.blit(puzzle_text, (150, 250))
    pygame.display.flip()
    pygame.time.delay(3000)

# Inicializar grupos de sprites
all_sprites = pygame.sprite.Group()
npcs = pygame.sprite.Group()
points_of_interest = pygame.sprite.Group()

# Crear jugador y NPCs
player = Player()
all_sprites.add(player)
for _ in range(5):
    npc = NPC()
    all_sprites.add(npc)
    npcs.add(npc)

# Crear puntos de interés
plaza = PointOfInterest(700, 500, plaza_image)
monasterio = PointOfInterest(400, 150, monasterio_image)
mirador = PointOfInterest(100, 400, mirador_image)

# Agregar puntos de interés a los grupos
all_sprites.add(plaza, monasterio, mirador)
points_of_interest.add(plaza, monasterio, mirador)

# Ciclo del menú
show_menu()

# Ciclo principal del juego
running = True
clock = pygame.time.Clock()

while running:
    clock.tick(60)
    screen.blit(background_image, (0, 0))  # Dibujar el fondo

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    player.update(keys)
    npcs.update()

    all_sprites.draw(screen)

    # Verificar si el jugador ha llegado a un punto de interés
    collided_point = pygame.sprite.spritecollideany(player, points_of_interest)
    if collided_point:
        puzzle_location = "la Plaza de Armas" if collided_point == plaza else "el Monasterio" if collided_point == monasterio else "el Mirador"
        puzzle(puzzle_location)

    pygame.display.flip()

pygame.quit()