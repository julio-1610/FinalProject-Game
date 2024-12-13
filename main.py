import pygame
import random
import cv2 as cv
import numpy as np
import os
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
plaza_completado = False
# Fuentes
font = pygame.font.Font(None, 36)
fontTitle = pygame.font.Font(pygame.font.match_font("Comic Sans MS"), 72)
fontTitle.set_bold(True)

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
background_image = load_image('assets/mapa_sin etiqueta.png', (SCREEN_WIDTH, SCREEN_HEIGHT))
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
        # Movimiento con las teclas de flecha
        if pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_a]:  # Flecha izquierda o 'A'
            self.rect.x -= self.speed
        if pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_d]:  # Flecha derecha o 'D'
            self.rect.x += self.speed
        if pressed_keys[pygame.K_UP] or pressed_keys[pygame.K_w]:  # Flecha arriba o 'W'
            self.rect.y -= self.speed
        if pressed_keys[pygame.K_DOWN] or pressed_keys[pygame.K_s]:  # Flecha abajo o 'S'
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
def plaza_ra():
    # Ruta de las imágenes
    image_folder = "assets/"
    images = [
        "pa_1.jpg",
        "pa_2.jpg",
        "pa_3.jpg",
        "pa_4.jpg"
    ]

    # Cargar imágenes
    loaded_images = [cv.imread(os.path.join(image_folder, img)) for img in images]
    if any(img is None for img in loaded_images):
        print("Error: No se pudieron cargar todas las imágenes. Verifica las rutas.")
        return False  # Retornar nivel no completado

    # Configuración de la cámara
    cap = cv.VideoCapture(0)
    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara.")
        return False

    current_image_index = 0
    cooldown_active = False

    def detect_white_sheet(frame):
        """Detecta si hay una hoja en blanco en el marco."""
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        _, thresh = cv.threshold(gray, 200, 255, cv.THRESH_BINARY)
        contours, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            epsilon = 0.02 * cv.arcLength(cnt, True)
            approx = cv.approxPolyDP(cnt, epsilon, True)
            area = cv.contourArea(cnt)
            if len(approx) == 4 and area > 5000:  # Detecta un área grande con 4 lados
                return approx
        return None

    def detect_hand(frame):
        """Detecta si hay una mano en el marco usando el rango de color de piel."""
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        mask = cv.inRange(hsv, lower_skin, upper_skin)
        mask = cv.erode(mask, None, iterations=2)
        mask = cv.dilate(mask, None, iterations=2)
        contours, _ = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            area = cv.contourArea(cnt)
            if area > 3000:  # Detectar áreas significativas de una mano
                return True
        return False

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: No se pudo capturar el cuadro de la cámara.")
            break

        # Detectar hoja blanca
        sheet_corners = detect_white_sheet(frame)
        if sheet_corners is not None:
            sheet_corners = np.array(sorted(sheet_corners[:, 0], key=lambda x: (x[1], x[0])), dtype=np.float32)
            if len(sheet_corners) == 4:
                src_points = np.array([[0, 0], [0, loaded_images[0].shape[0]],
                                       [loaded_images[0].shape[1], loaded_images[0].shape[0]],
                                       [loaded_images[0].shape[1], 0]], dtype=np.float32)
                dst_points = sheet_corners.reshape(4, 2).astype(np.float32)
                H, status = cv.findHomography(src_points, dst_points)
                if H is not None:
                    warped_image = cv.warpPerspective(loaded_images[current_image_index], H,
                                                      (frame.shape[1], frame.shape[0]))
                    mask = np.zeros_like(frame, dtype=np.uint8)
                    cv.fillConvexPoly(mask, dst_points.astype(int), (255, 255, 255))
                    inverse_mask = cv.bitwise_not(mask)
                    frame = cv.bitwise_and(frame, inverse_mask)
                    frame = cv.add(frame, warped_image)

        # Detectar mano para cambiar de imagen
        elif detect_hand(frame):
            if not cooldown_active:  # Solo cambiar si no está en enfriamiento
                cooldown_active = True
                current_image_index = (current_image_index + 1) % len(loaded_images)
        else:
            cooldown_active = False

        # Agregar instrucciones en el marco
        if sheet_corners is None:  # Si no se detecta una hoja
            cv.putText(frame, "Use una hoja en blanco", (20, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2,
                       cv.LINE_AA)
        else:  # Si ya se detectó una hoja
            cv.putText(frame, "Arrastre su mano para pasar de imagen", (20, 50), cv.FONT_HERSHEY_SIMPLEX, 1,
                       (0, 255, 0), 2, cv.LINE_AA)

        # Mostrar el marco actualizado
        cv.imshow("AR Plaza", frame)

        # Detectar la tecla 'Esc' para salir de la cámara sin cerrar el juego
        if cv.waitKey(1) & 0xFF == 27:  # 27 es el código ASCII de 'Esc'
            cap.release()
            cv.destroyAllWindows()
            return True  # Indicar que el nivel terminó correctamente

# Función para mostrar el menú
def show_menu():
    screen.blit(menu_image, (0, 0))

    # Título
    title = fontTitle.render("Aventura en Arequipa", True, (34, 139, 34))
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 120))
    rounded_rect = pygame.Rect(title_rect.left - 10, title_rect.top - 10, title_rect.width + 20,
                               title_rect.height + 20)  # Ajusta el tamaño según necesites
    border_radius = 10

    # Dibujar el rectángulo redondeado con transparencia
    pygame.draw.rect(screen, WHITE, rounded_rect, border_radius=border_radius)

    # Dibujar el texto
    screen.blit(title, title_rect)

    # Definir botones
    start_button = pygame.Rect(250, 250, 300, 60)
    quit_button = pygame.Rect(250, 350, 300, 60)

    # Dibujar botones con bordes redondeados
    pygame.draw.rect(screen, (34, 139, 34), start_button, border_radius=15)  # Verde oscuro
    pygame.draw.rect(screen, (178, 34, 34), quit_button, border_radius=15)   # Rojo oscuro

    # Agregar borde a los botones
    pygame.draw.rect(screen, WHITE, start_button, width=3, border_radius=15)
    pygame.draw.rect(screen, WHITE, quit_button, width=3, border_radius=15)

    # Texto de los botones
    start_text = font.render("Iniciar Juego", True, WHITE)
    quit_text = font.render("Salir", True, WHITE)
    start_text_rect = start_text.get_rect(center=start_button.center)
    quit_text_rect = quit_text.get_rect(center=quit_button.center)

    # Dibujar texto
    screen.blit(start_text, start_text_rect)
    screen.blit(quit_text, quit_text_rect)

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

    # Título de Game Over
    game_over_text = fontTitle.render("Game Over", True, RED)
    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
    screen.blit(game_over_text, game_over_rect)

    # Definir botón de reinicio
    restart_button = pygame.Rect(250, 300, 300, 60)

    # Dibujar botón con bordes redondeados
    pygame.draw.rect(screen, (34, 139, 34), restart_button, border_radius=15)  # Verde oscuro

    # Agregar borde al botón
    pygame.draw.rect(screen, WHITE, restart_button, width=3, border_radius=15)

    # Texto del botón
    restart_text = font.render("Volver al Inicio", True, WHITE)
    restart_text_rect = restart_text.get_rect(center=restart_button.center)

    # Dibujar texto
    screen.blit(restart_text, restart_text_rect)

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
    game_over()

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

    # Crear objetos en las posiciones deseadas
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

    collided_point = pygame.sprite.spritecollideany(player, points_of_interest)
    if collided_point:
        if collided_point == plaza and not plaza_completado:
            plaza_completado = plaza_ra()  # Ejecutar nivel de Plaza
            if plaza_completado:  # Si completó el nivel
                plaza.image = load_image('assets/plaza_negro.png', (150, 150))  # Cambiar imagen a negro
                points_of_interest.remove(plaza)  # Eliminar Plaza de puntos activos
            continue  # Regresar al mapa

        elif collided_point == mirador:
            puzzle("el Mirador")

        elif collided_point == monasterio and not monasterio_completado:
            level_two()


    if pygame.sprite.spritecollideany(player, npcs):
        game_over()

    pygame.display.flip()

pygame.quit()
