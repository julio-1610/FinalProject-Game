import pygame
import random
from flocking import main  # Asegúrate de importar lo necesario desde flocking.py

# Inicializar Pygame
pygame.init()

# Definir el tamaño de la pantalla
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Aventura en Arequipa")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (50, 50, 150)
# Fuentes
font = pygame.font.Font(None, 36)
fontTitle = pygame.font.Font(None, 72)

# Función para cargar y redimensionar imágenes
def load_image(path, size=None, grayscale=False):
    try:
        image = pygame.image.load(path).convert_alpha()
        if size:
            image = pygame.transform.scale(image, size)
        if grayscale:
            image = image.copy()
            arr = pygame.surfarray.pixels3d(image)
            avg = (arr[:, :, 0] + arr[:, :, 1] + arr[:, :, 2]) // 3
            arr[:, :, :] = avg[:, :, None]
            del arr
        return image
    except pygame.error as e:
        print(f"Error al cargar la imagen {path}: {e}")
        return None

# Cargar imágenes
player_image = load_image('assets/player.png', (80, 80))
npc_image = load_image('assets/npc.png', (40, 40))
plaza_image = load_image('assets/plaza.png', (150, 150))
monasterio_image = load_image('assets/monasterio.png', (150, 150))
monasterio_image_gray = load_image('assets/monasterio.png', (150, 150), grayscale=True)  # Monasterio en blanco y negro
mirador_image = load_image('assets/mirador.png', (150, 150))
mirador_image_gray = load_image('assets/mirador.png', (150, 150), grayscale=True)
background_image = load_image('assets/arequipa_mp_real.PNG', (SCREEN_WIDTH, SCREEN_HEIGHT))
menu_image = load_image('assets/menu.jpg', (SCREEN_WIDTH, SCREEN_HEIGHT))
monasterio_bg_image = load_image('assets/escenario_stc.jpg', (SCREEN_WIDTH, SCREEN_HEIGHT))

# Cargar imágenes de objetos en un tamaño más grande
objeto1_image = load_image('assets/objeto1.jpg', (70, 70))
objeto2_image = load_image('assets/objeto2.jpg', (70, 70))
objeto3_image = load_image('assets/objeto3.jpg', (70, 70))
objeto4_image = load_image('assets/objeto4.jpg', (70, 70))

# Cargar sonido de recolección de objetos
pickup_sound = pygame.mixer.Sound('assets/point.wav')

# Bandera para controlar si el Monasterio ha sido completado
monasterio_completado = False
mirador_completado = False

# Clase para el jugador
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.topright = (SCREEN_WIDTH - 10, 10)
        self.speed = 3

    def reset_position(self):
        self.rect.topright = (SCREEN_WIDTH - 10, 10)

    def update(self, pressed_keys):
        if pressed_keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if pressed_keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if pressed_keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if pressed_keys[pygame.K_DOWN]:
            self.rect.y += self.speed

# Clase para NPCs con movimiento "wandering" en el primer nivel
class WanderingNPC(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = npc_image
        self.rect = self.image.get_rect()
        self.reset_position()

    def reset_position(self):
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

# Clase para el NPC del segundo nivel que sigue waypoints
class WaypointNPC(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = npc_image
        self.rect = self.image.get_rect()
        self.rect.topleft = (500, 100)
        self.speed = 5  # Mayor velocidad en el segundo nivel
        self.waypoints = []
        self.current_waypoint = 0

    def set_waypoints(self, waypoints):
        self.waypoints = waypoints

    def update(self):
        if not self.waypoints:
            return
        target_x, target_y = self.waypoints[self.current_waypoint]
        npc_direction = pygame.math.Vector2(target_x - self.rect.x, target_y - self.rect.y)
        if npc_direction.length() != 0:
            npc_direction = npc_direction.normalize()
        self.rect.x += npc_direction.x * self.speed
        self.rect.y += npc_direction.y * self.speed
        if self.rect.collidepoint(target_x, target_y):
            self.current_waypoint = (self.current_waypoint + 1) % len(self.waypoints)

# Clase para los puntos de interés
class PointOfInterest(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

# Función para mostrar el menú
def show_menu():
    screen.blit(menu_image, (0, 0))
    title = fontTitle.render("Aventura en Arequipa", True, WHITE)
    screen.blit(title, (150, 150))

    start_button = pygame.Rect(250, 250, 300, 50)
    quit_button = pygame.Rect(250, 320, 300, 50)

    pygame.draw.rect(screen, GREEN, start_button)
    pygame.draw.rect(screen, RED, quit_button)

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
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    in_menu = False
                    reset_game()
                elif quit_button.collidepoint(event.pos):
                    pygame.quit()
                    exit()

# Función para mostrar la pantalla de Game Over
def game_over():
    screen.fill(BLACK)
    game_over_text = fontTitle.render("Game Over", True, RED)
    screen.blit(game_over_text, (250, 200))

    restart_button = pygame.Rect(250, 300, 300, 50)
    pygame.draw.rect(screen, GREEN, restart_button)
    restart_text = font.render("Volver al Inicio", True, WHITE)
    screen.blit(restart_text, (restart_button.x + 60, restart_button.y + 10))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.collidepoint(event.pos):
                    show_menu()
                    waiting = False

# Función de puzzle
def puzzle(location):
    screen.fill(BLACK)
    puzzle_text = font.render(f"Resuelve el puzzle de {location}", True, WHITE)
    screen.blit(puzzle_text, (150, 250))
    pygame.display.flip()
    pygame.time.delay(3000)

# Función de segundo nivel
def level_two():
    global monasterio_completado  # Modificar la variable global para indicar que el nivel fue completado
    start_time = pygame.time.get_ticks()
    remaining_time = 15
    objects_remaining = 4

    player.rect.topleft = (50, 500)

    # Crear NPC de waypoints y establecer sus puntos
    waypoint_npc = WaypointNPC()
    waypoint_npc.set_waypoints([(600, 50), (200, 100), (300, 200), (100, 400)])

    # Crear objetos más grandes en las posiciones deseadas
    objeto1 = PointOfInterest(100, 400, objeto1_image)
    objeto2 = PointOfInterest(300, 200, objeto2_image)
    objeto3 = PointOfInterest(200, 100, objeto3_image)
    objeto4 = PointOfInterest(600, 50, objeto4_image)

    objects = pygame.sprite.Group()
    objects.add(objeto1, objeto2, objeto3, objeto4)

    running = True
    while running:
        screen.blit(monasterio_bg_image, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        keys = pygame.key.get_pressed()
        player.update(keys)
        waypoint_npc.update()  # Actualizar el movimiento del NPC de waypoints

        # Verificar colisión con el NPC
        if pygame.sprite.collide_rect(player, waypoint_npc):
            game_over()
            return  # Salir de level_two y volver al menú principal en caso de Game Over

        # Verificar colisión con objetos
        collected_object = pygame.sprite.spritecollideany(player, objects)
        if collected_object:
            collected_object.kill()
            pickup_sound.play()
            objects_remaining -= 1

        elapsed_time = (pygame.time.get_ticks() - start_time) / 1000
        remaining_time = max(0, 15 - int(elapsed_time))

        # Comprobar si el jugador ha ganado o si el tiempo ha terminado
        if objects_remaining == 0:
            monasterio_completado = True  # Marcar el monasterio como completado
            return  # Volver al primer nivel si se completan todos los objetos
        elif remaining_time == 0:
            game_over()
            return  # Mostrar Game Over si el tiempo se acaba

        objects.draw(screen)
        screen.blit(player.image, player.rect)
        screen.blit(waypoint_npc.image, waypoint_npc.rect)

        time_text = font.render(f"Contador: {remaining_time} segundos", True, GREEN)
        objects_text = font.render(f"Objetos Restantes: {objects_remaining}", True, GREEN)
        screen.blit(time_text, (SCREEN_WIDTH - 200, 20))
        screen.blit(objects_text, (20, 20))

        pygame.display.flip()
        clock.tick(60)




# Inicializar el resto del juego (jugador, NPCs, etc.)
all_sprites = pygame.sprite.Group()
npcs = pygame.sprite.Group()
points_of_interest = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

# Crear 5 NPCs para el primer nivel
for _ in range(5):
    npc = WanderingNPC()
    all_sprites.add(npc)
    npcs.add(npc)

mirador = PointOfInterest(100, 100, mirador_image)
monasterio = PointOfInterest(400, 300, monasterio_image if not monasterio_completado else monasterio_image_gray)
plaza = PointOfInterest(700, 500, plaza_image)

all_sprites.add(mirador, plaza)
points_of_interest.add(mirador, plaza)

# Añadir el Monasterio si no está completado
if not monasterio_completado:
    all_sprites.add(monasterio)
    points_of_interest.add(monasterio)
# Añadir el Monasterio si no está completado

if not mirador_completado:
    all_sprites.add(mirador)
    points_of_interest.add(mirador)

def reset_game():
    player.reset_position()
    for npc in npcs:
        npc.reset_position()

show_menu()

running = True
clock = pygame.time.Clock()

while running:
    clock.tick(60)
    screen.blit(background_image, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    player.update(keys)
    npcs.update()

    all_sprites.draw(screen)

    # Actualizar monasterio en blanco y negro si está completado
    if monasterio_completado:
        screen.blit(monasterio_image_gray, (monasterio.rect.x, monasterio.rect.y))
    if mirador_completado:
        screen.blit(mirador_image_gray, (mirador.rect.x, mirador.rect.y))

    collided_point = pygame.sprite.spritecollideany(player, points_of_interest)
    if collided_point:
        if collided_point == mirador and not mirador_completado:
            minijuego_completado = main()  # Ejecuta el minijuego
            if minijuego_completado:
                mirador_completado = True  # Marca el mirador como completado
            else:
                # El jugador perdió, actualiza la lógica (mirador en gris)
                mirador_completado = False  # O lo que necesites para manejar el estado
        elif collided_point == monasterio and not monasterio_completado:
            level_two()  # Iniciar el segundo nivel solo si no está completado
        else:
            puzzle_location = "la Plaza de Armas"


    if pygame.sprite.spritecollideany(player, npcs):
        game_over()

    pygame.display.flip()

pygame.quit()
