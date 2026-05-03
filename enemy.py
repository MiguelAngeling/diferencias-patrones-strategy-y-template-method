# enemy.py
"""
Enemigos que caen desde la parte superior de la pantalla.

Son obstáculos que el dinosaurio debe evitar.
Con decoradores activos:
  - Thunder (invencible) → destruye al enemigo y gana puntos
  - Ice (escudo) → absorbe el golpe sin perder vida
  - Sin protección → pierde 1 vida
"""

import pygame
import random
import math
from setting import (
    ENEMY_SIZE, ENEMY_COLOR, SCREEN_WIDTH, SCREEN_HEIGHT,
    ENEMY_SPEED_MIN, ENEMY_SPEED_MAX,
)


class Enemy(pygame.sprite.Sprite):
    """Asteroide / roca prehistórica que cae del cielo."""

    def __init__(self, speed_bonus: int = 0):
        super().__init__()
        self.size = ENEMY_SIZE

        # Crear imagen — roca irregular con textura
        self.image = pygame.Surface((self.size + 4, self.size + 4), pygame.SRCALPHA)
        self._draw_rock()

        self.rect   = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.size)
        self.rect.y = random.randint(-150, -self.size)
        self.speed  = random.randint(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX) + speed_bonus

        # Rotación visual
        self.angle     = random.uniform(0, 360)
        self.rot_speed = random.uniform(-3, 3)
        self._original = self.image.copy()

    def _draw_rock(self):
        """Dibuja una roca con aspecto prehistórico."""
        cx, cy = self.size // 2 + 2, self.size // 2 + 2
        r = self.size // 2

        # Silueta irregular (polígono)
        points = []
        num_points = 8
        for i in range(num_points):
            angle = math.radians(i * (360 / num_points))
            variation = random.uniform(0.7, 1.0)
            px = cx + int(math.cos(angle) * r * variation)
            py = cy + int(math.sin(angle) * r * variation)
            points.append((px, py))

        # Roca base
        base_color = (
            ENEMY_COLOR[0] - random.randint(0, 40),
            ENEMY_COLOR[1] + random.randint(0, 30),
            ENEMY_COLOR[2] + random.randint(0, 20),
        )
        pygame.draw.polygon(self.image, base_color, points)
        # Borde más oscuro
        darker = tuple(max(0, c - 50) for c in base_color)
        pygame.draw.polygon(self.image, darker, points, 2)

        # Grietas / textura
        for _ in range(2):
            x1 = cx + random.randint(-r // 2, r // 2)
            y1 = cy + random.randint(-r // 2, r // 2)
            x2 = x1 + random.randint(-8, 8)
            y2 = y1 + random.randint(-8, 8)
            pygame.draw.line(self.image, darker, (x1, y1), (x2, y2), 1)

    def update(self):
        self.rect.y += self.speed

        # Rotación visual
        self.angle += self.rot_speed
        self.image = pygame.transform.rotate(self._original, self.angle)
        old_center = self.rect.center
        self.rect  = self.image.get_rect(center=old_center)

        # Reaparecer arriba si sale de la pantalla
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.y = random.randint(-150, -self.size)
            self.rect.x = random.randint(0, SCREEN_WIDTH - self.size)
            self.speed  = random.randint(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)