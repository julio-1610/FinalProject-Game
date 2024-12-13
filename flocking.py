import pygame
import random
import time

# Inicializar Pygame
pygame.init()

# Dimensiones de la pantalla
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Geometry Dash con Flocking")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 50, 150)
RED = (255, 0, 0)  # Color para el fondo de la pregunta

# Recursos
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Preguntas culturales (Didáctico)
questions = [
    ("¿El Mirador de Yanahuara ofrece una vista panorámica de Arequipa?", True),
    ("¿El Mirador de Yanahuara está ubicado en el centro histórico de Arequipa?", False),
    ("""¿El Mirador de Yanahuara tiene 
una estructura de piedra blanca?""", True),
    ("¿El Mirador de Yanahuara fue construido en el siglo XIX?", True),
    ("¿Desde el Mirador de Yanahuara se puede ver el volcán Misti?", True),
    ("¿En el Mirador de Yanahuara se encuentra una gran estatua de Santa Catalina?", False),
    ("¿La zona del Mirador de Yanahuara está rodeada de jardines y áreas recreativas?", True)
]


current_question = None
question_time = random.randint(5, 15)  # Tiempo aleatorio para la próxima pregunta (en segundos)
last_question_time = time.time()

# Clase del jugador
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.topleft = (100, SCREEN_HEIGHT - 150)
        self.velocity = pygame.math.Vector2(0, 0)
        self.speed = 5  # Velocidad de movimiento

    def update(self):
        keys = pygame.key.get_pressed()

        # Mover el jugador con las teclas de dirección
        if keys[pygame.K_LEFT]:
            self.velocity.x = -self.speed
        elif keys[pygame.K_RIGHT]:
            self.velocity.x = self.speed
        else:
            self.velocity.x = 0

        if keys[pygame.K_UP]:
            self.velocity.y = -self.speed
        elif keys[pygame.K_DOWN]:
            self.velocity.y = self.speed
        else:
            self.velocity.y = 0

        # Actualizar la posición
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

        # Limitar el movimiento del jugador para que no se salga de la pantalla
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        elif self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    def check_collision(self, enemies):
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                return True
        return False


# Clase para enemigos con comportamiento de flocking
class FlockingEnemy(pygame.sprite.Sprite):
    def __init__(self, x, y, is_group=False):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = pygame.math.Vector2(random.uniform(-2, 2), random.uniform(-2, 2))
        self.acceleration = pygame.math.Vector2(0, 0)
        self.max_speed = 10
        self.perception_radius = 180
        self.is_group = is_group  # Indica si el enemigo se mueve en grupo o de forma individual

    def update(self, enemies, player_pos=None):
        self.acceleration = pygame.math.Vector2(0, 0)
        if self.is_group:
            self.align(enemies)
            self.cohesion(enemies)
            self.separation(enemies)
            if player_pos:
                self.chase(player_pos)
        else:
            # Movimiento de enemigos individuales
            self.velocity += self.acceleration
        self.velocity += self.acceleration
        if self.velocity.length() > self.max_speed:
            self.velocity.scale_to_length(self.max_speed)
        self.rect.center += self.velocity

        # Rebote en los límites de la pantalla
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.velocity.x *= -1
        if self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT:
            self.velocity.y *= -1

    def align(self, enemies):
        avg_velocity = pygame.math.Vector2(0, 0)
        total = 0
        for enemy in enemies:
            if enemy != self and pygame.math.Vector2(self.rect.center).distance_to(
                    pygame.math.Vector2(enemy.rect.center)) < self.perception_radius:
                avg_velocity += enemy.velocity
                total += 1
        if total > 0:
            avg_velocity /= total
            avg_velocity = avg_velocity.normalize() * self.max_speed
            steer = avg_velocity - self.velocity
            self.acceleration += steer

    def cohesion(self, enemies):
        center_mass = pygame.math.Vector2(0, 0)
        total = 0
        for enemy in enemies:
            if enemy != self and pygame.math.Vector2(self.rect.center).distance_to(
                    pygame.math.Vector2(enemy.rect.center)) < self.perception_radius:
                center_mass += pygame.math.Vector2(enemy.rect.center)
                total += 1
        if total > 0:
            center_mass /= total
            desired = center_mass - pygame.math.Vector2(self.rect.center)
            if desired.length() > 0:
                desired = desired.normalize() * self.max_speed
            steer = desired - self.velocity
            self.acceleration += steer

    def separation(self, enemies):
        avoid_force = pygame.math.Vector2(0, 0)
        total = 0
        for enemy in enemies:
            distance = pygame.math.Vector2(self.rect.center).distance_to(pygame.math.Vector2(enemy.rect.center))

            if enemy != self and distance < self.perception_radius / 2 and distance > 0:
                diff = pygame.math.Vector2(self.rect.center) - pygame.math.Vector2(enemy.rect.center)
                diff /= distance  # Esta división ahora es segura
                avoid_force += diff
                total += 1

        if total > 0:
            avoid_force /= total
            if avoid_force.length() > 0:
                avoid_force = avoid_force.normalize() * self.max_speed
            steer = avoid_force - self.velocity
            self.acceleration += steer

    def chase(self, player_pos):
        direction = pygame.math.Vector2(player_pos) - pygame.math.Vector2(self.rect.center)
        if direction.length() > 0:
            direction = direction.normalize() * self.max_speed
        steer = direction - self.velocity
        self.acceleration += steer


# Crear grupos de sprites
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

# Crear enemigos con flocking
for _ in range(5):  # Enemigos individuales
    enemy = FlockingEnemy(random.randint(200, SCREEN_WIDTH - 50), random.randint(50, SCREEN_HEIGHT - 150),
                          is_group=False)
    all_sprites.add(enemy)
    enemies.add(enemy)

for _ in range(5):  # Enemigos en grupo
    enemy = FlockingEnemy(random.randint(200, SCREEN_WIDTH - 50), random.randint(50, SCREEN_HEIGHT - 150),
                          is_group=True)
    all_sprites.add(enemy)
    enemies.add(enemy)


# Función para hacer una pregunta
def ask_question():
    global current_question, last_question_time
    if time.time() - last_question_time >= question_time:
        current_question = random.choice(questions)
        last_question_time = time.time()
        return True
    return False


# Bucle principal
def main():
    global current_question
    running = True
    answering = False  # Indica si el jugador está respondiendo
    player_answer = None  # Respuesta del jugador (Verdadero/Falso)
    game_lost = False  # Para saber si el jugador perdió

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                game_lost = True
            if event.type == pygame.KEYDOWN:
                if answering:
                    if event.key == pygame.K_v:  # Verdadero
                        player_answer = True
                    elif event.key == pygame.K_f:  # Falso
                        player_answer = False

        # Si es hora de hacer una pregunta
        if ask_question() and not answering:
            answering = True
            question_text = font.render(f"{current_question[0]}", True, WHITE)
            true_text = font.render("V = Verdadero", True, WHITE)
            false_text = font.render("F = Falso", True, WHITE)

            # Cambiar fondo de la pregunta
            screen.fill(RED)  # Fondo rojo para la pantalla de la pregunta
            screen.blit(question_text, (20, SCREEN_HEIGHT // 2 - 50))
            screen.blit(true_text, (20, SCREEN_HEIGHT // 2))
            screen.blit(false_text, (20, SCREEN_HEIGHT // 2 + 40))
            pygame.display.flip()

        # Esperar la respuesta
        if player_answer is not None:
            if player_answer == current_question[1]:  # Respuesta correcta
                answering = False
                player_answer = None
            else:  # Respuesta incorrecta, termina el juego
                # Mostrar mensaje de respuesta incorrecta

                screen.fill(BLACK)
                incorrect_answer_text = font.render("¡Respuesta incorrecta!", True, WHITE)
                screen.blit(incorrect_answer_text,
                            (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50))  # Mensaje de error

                # Esperar unos segundos para mostrar el mensaje
                pygame.display.flip()
                pygame.time.wait(2000)  # Espera 2 segundos para que el jugador vea el mensaje

                # Luego de mostrar el mensaje, mostrar "¡Perdiste!" y terminar el juego
                screen.fill(BLACK)
                game_over_text = font.render("¡Perdiste!", True, WHITE)
                screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
                pygame.display.flip()
                pygame.time.wait(2000)  # Espera 2 segundos antes de cerrar

                game_lost = True
                running = False

        # Detectar colisión entre el jugador y los enemigos
        if player.check_collision(enemies):
            screen.fill(BLACK)
            game_over_text = font.render("¡Te atraparon! Fin del juego", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))
            pygame.display.flip()
            pygame.time.wait(3000)
            running = False

        # Actualizar y mover sprites solo si no estamos respondiendo
        if not answering:
            player.update()
            for enemy in enemies:
                enemy.update(enemies, player.rect.center)

        # Dibujar
        if not answering:  # Solo dibujar los sprites cuando no estamos mostrando la pregunta
            screen.fill(BLACK)
            all_sprites.draw(screen)

        pygame.display.flip()

        clock.tick(60)

    return not game_lost


if __name__ == "__main__":
    main()
