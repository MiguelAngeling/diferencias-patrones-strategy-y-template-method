# player.py
"""
Jugador concreto (ConcreteComponent) del patrón Decorator.

Cambios respecto al original:
  • Recibe una MovementStrategy por inyección (principio DIP).
  • update() delega el cálculo de movimiento y la selección de animación
    a la estrategia en lugar de tenerlos hard-coded.
  • El resto (carga de sprites, animación, draw, reset) permanece igual
    para no romper la cadena de decoradores.

Por defecto usa KeyboardMovementStrategy (comportamiento original).
Para cambiar el control basta pasar otra estrategia al constructor —
Player nunca sabe qué estrategia usa internamente.
"""

import os
import pygame
from base_entity         import EntityComponent
from movement_strategy   import MovementStrategy, KeyboardMovementStrategy
from setting import (
    PLAYER_SIZE, PLAYER_SPEED, PLAYER_COLOR, WHITE,
    SCREEN_WIDTH, SCREEN_HEIGHT,
    DINO_SCALE, DINO_ANIM_SPEED, DINO_SPRITES_DIR, DINO_ANIMS,
)


class Player(EntityComponent):
    """Dinosaurio animado — ConcreteComponent del patrón Decorator."""

    def __init__(
        self,
        x: int,
        y: int,
        movement_strategy: MovementStrategy | None = None,
    ):
        self.speed = PLAYER_SPEED
        self.size  = PLAYER_SIZE

        # Estrategia de movimiento (Strategy pattern — DIP)
        self._movement: MovementStrategy = (
            movement_strategy or KeyboardMovementStrategy()
        )

        # Cargar sprites
        self.animations: dict[str, list[pygame.Surface]] = {}
        self._load_sprites()

        # Estado de animación
        self.current_anim  = "Idle"
        self.frame_index   = 0
        self.anim_counter  = 0
        self.facing_right  = True
        self._forced_anim  = None

        self.image = self.animations["Idle"][0]
        self.rect  = self.image.get_rect(center=(x, y))

    # ─────────────────────────────────────────────────────────
    #  Inyección de estrategia en caliente
    # ─────────────────────────────────────────────────────────
    def set_movement_strategy(self, strategy: MovementStrategy):
        """Permite cambiar la estrategia de movimiento en tiempo de ejecución."""
        self._movement = strategy

    # ─────────────────────────────────────────────────────────
    #  Carga de sprites
    # ─────────────────────────────────────────────────────────
    def _load_sprites(self):
        base_dir = os.path.join(os.path.dirname(__file__), DINO_SPRITES_DIR)
        for anim_name, frame_count in DINO_ANIMS.items():
            frames = []
            for i in range(1, frame_count + 1):
                path = os.path.join(base_dir, f"{anim_name} ({i}).png")
                try:
                    surf = pygame.image.load(path).convert_alpha()
                    surf = pygame.transform.smoothscale(surf, DINO_SCALE)
                    frames.append(surf)
                except (FileNotFoundError, pygame.error):
                    fallback = pygame.Surface(DINO_SCALE, pygame.SRCALPHA)
                    pygame.draw.rect(fallback, PLAYER_COLOR,
                                     (0, 0, *DINO_SCALE), border_radius=8)
                    pygame.draw.circle(fallback, WHITE,
                                       (DINO_SCALE[0] // 2, DINO_SCALE[1] // 3), 4)
                    frames.append(fallback)
            self.animations[anim_name] = frames

        if not self.animations.get("Idle"):
            fb = pygame.Surface(DINO_SCALE, pygame.SRCALPHA)
            pygame.draw.rect(fb, PLAYER_COLOR, (0, 0, *DINO_SCALE), border_radius=8)
            self.animations["Idle"] = [fb]

    # ─────────────────────────────────────────────────────────
    #  Control de animación
    # ─────────────────────────────────────────────────────────
    def set_animation(self, name: str):
        if self._forced_anim:
            return
        if name in self.animations and name != self.current_anim:
            self.current_anim = name
            self.frame_index  = 0
            self.anim_counter = 0

    def force_animation(self, name: str):
        if name in self.animations:
            self._forced_anim = name
            if self.current_anim != name:
                self.current_anim = name
                self.frame_index  = 0
                self.anim_counter = 0

    def release_animation(self):
        self._forced_anim = None

    def get_state(self) -> str:
        return self.current_anim.lower()

    # ─────────────────────────────────────────────────────────
    #  EntityComponent interface
    # ─────────────────────────────────────────────────────────
    def get_speed(self) -> int:
        return self.speed

    def is_invincible(self) -> bool:
        return False

    def get_attack_bonus(self) -> int:
        return 0

    def get_rect(self) -> pygame.Rect:
        return self.rect

    # ─────────────────────────────────────────────────────────
    #  Update — delega movimiento a la Strategy
    # ─────────────────────────────────────────────────────────
    def update(self):
        # La estrategia calcula dx, dy y la dirección del sprite
        dx, dy, facing = self._movement.compute_move(self.rect, self.speed)

        # Aplicar desplazamiento (limitado a pantalla — la strategy ya lo controla,
        # pero clamp por seguridad)
        self.rect.x = max(0, min(SCREEN_WIDTH  - self.size, self.rect.x + dx))
        self.rect.y = max(0, min(SCREEN_HEIGHT - self.size, self.rect.y + dy))

        if facing is not None:
            self.facing_right = facing

        # Seleccionar animación según movimiento (si no está forzada)
        if not self._forced_anim:
            anim = self._movement.select_animation(dx, dy, self.speed)
            self.set_animation(anim)

        # Avanzar frame de animación
        self.anim_counter += 1
        if self.anim_counter >= DINO_ANIM_SPEED:
            self.anim_counter = 0
            frames = self.animations.get(self.current_anim, self.animations["Idle"])
            self.frame_index = (self.frame_index + 1) % len(frames)

        frames = self.animations.get(self.current_anim, self.animations["Idle"])
        self.image = frames[self.frame_index % len(frames)]

    # ─────────────────────────────────────────────────────────
    #  Draw
    # ─────────────────────────────────────────────────────────
    def draw(self, screen):
        img = self.image
        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)
        screen.blit(img, self.rect)

    # ─────────────────────────────────────────────────────────
    #  Animación de muerte
    # ─────────────────────────────────────────────────────────
    def play_death_frame(self, frame: int) -> pygame.Surface:
        dead_frames = self.animations.get("Dead", self.animations["Idle"])
        idx = min(frame, len(dead_frames) - 1)
        img = dead_frames[idx]
        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)
        return img

    # ─────────────────────────────────────────────────────────
    #  Reset
    # ─────────────────────────────────────────────────────────
    def reset_position(self, x: int, y: int):
        self.rect.center = (x, y)

    def reset_speed(self):
        self.speed = PLAYER_SPEED

    def reset_animation(self):
        self.current_anim = "Idle"
        self.frame_index  = 0
        self.anim_counter = 0
        self._forced_anim = None

    def reset(self, x: int, y: int):
        self.reset_position(x, y)
        self.reset_speed()
        self.reset_animation()
