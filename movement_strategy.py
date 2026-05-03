# movement_strategy.py
"""
Patrón STRATEGY — Estrategias de movimiento del dinosaurio.

Problema original:
  La lógica de movimiento estaba embebida directamente en Player.update(),
  mezclando lectura de input, física, límites de pantalla y selección de
  animación en un único método monolítico. Añadir un nuevo modo de movimiento
  (p.ej. movimiento con inercia, auto-pilot, movimiento táctil) requería
  modificar Player directamente → violación de OCP.

Solución — Strategy:
  MovementStrategy define el contrato (interfaz).
  Cada estrategia concreta encapsula UNA forma de mover al jugador.
  Player recibe la estrategia por inyección y la delega sin saber qué hace.

Estrategias incluidas:
  - KeyboardMovementStrategy  → control por teclado (original)
  - DashMovementStrategy      → movimiento con dash (velocidad extra temporal)

Para agregar un nuevo tipo de movimiento basta crear una nueva subclase
sin tocar Player ni Game — principio OCP garantizado.
"""

from __future__ import annotations
import pygame
from abc import ABC, abstractmethod
from setting import SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_SPEED


class MovementStrategy(ABC):
    """
    Interfaz Strategy para el movimiento del jugador.
    Contrato: recibe el rect actual y la velocidad, devuelve (dx, dy, facing_right).
    """

    @abstractmethod
    def compute_move(
        self,
        rect: pygame.Rect,
        speed: int,
    ) -> tuple[int, int, bool | None]:
        """
        Calcula el desplazamiento para este frame.

        Returns:
            (dx, dy, facing_right)
            facing_right=None  → no cambiar la dirección actual del sprite.
        """
        ...

    @abstractmethod
    def select_animation(self, dx: int, dy: int, speed: int) -> str:
        """
        Devuelve el nombre de la animación que corresponde al movimiento.
        El Player la usará sólo si no hay una animación forzada por un decorador.
        """
        ...


# ─────────────────────────────────────────────────────────────
#  Estrategia concreta 1 — Teclado estándar (original)
# ─────────────────────────────────────────────────────────────
class KeyboardMovementStrategy(MovementStrategy):
    """
    Mueve al jugador con las teclas de dirección, respetando los límites
    de pantalla.  Es la estrategia por defecto (comportamiento original).
    """

    def compute_move(
        self,
        rect: pygame.Rect,
        speed: int,
    ) -> tuple[int, int, bool | None]:
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        facing: bool | None = None

        if keys[pygame.K_LEFT] and rect.left > 0:
            dx = -speed
            facing = False
        if keys[pygame.K_RIGHT] and rect.right < SCREEN_WIDTH:
            dx = speed
            facing = True
        if keys[pygame.K_UP] and rect.top > 0:
            dy = -speed
        if keys[pygame.K_DOWN] and rect.bottom < SCREEN_HEIGHT:
            dy = speed

        return dx, dy, facing

    def select_animation(self, dx: int, dy: int, speed: int) -> str:
        moving = dx != 0 or dy != 0
        if not moving:
            return "Idle"
        # Run si tiene boost de velocidad, Walk en caso contrario
        return "Run" if speed > PLAYER_SPEED else "Walk"


# ─────────────────────────────────────────────────────────────
#  Estrategia concreta 2 — Teclado con Dash (extensión NUEVA)
# ─────────────────────────────────────────────────────────────
class DashMovementStrategy(MovementStrategy):
    """
    Igual que KeyboardMovementStrategy pero con un dash al pulsar SPACE.
    Demuestra cómo extender el comportamiento sin modificar Player.

    El dash multiplica la velocidad durante DASH_FRAMES frames y entra
    en cooldown durante COOLDOWN_FRAMES frames.
    """

    DASH_FRAMES     = 10
    DASH_MULTIPLIER = 3
    COOLDOWN_FRAMES = 45

    def __init__(self):
        self._dash_timer     = 0
        self._cooldown_timer = 0
        self._prev_space     = False   # evita repetición de keydown

    def compute_move(
        self,
        rect: pygame.Rect,
        speed: int,
    ) -> tuple[int, int, bool | None]:
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        facing: bool | None = None

        # — Activar dash —
        space_now = keys[pygame.K_SPACE]
        if space_now and not self._prev_space and self._cooldown_timer == 0:
            self._dash_timer = self.DASH_FRAMES
        self._prev_space = space_now

        # — Calcular multiplicador —
        if self._dash_timer > 0:
            effective_speed = speed * self.DASH_MULTIPLIER
            self._dash_timer -= 1
            if self._dash_timer == 0:
                self._cooldown_timer = self.COOLDOWN_FRAMES
        else:
            effective_speed = speed
            if self._cooldown_timer > 0:
                self._cooldown_timer -= 1

        if keys[pygame.K_LEFT] and rect.left > 0:
            dx = -effective_speed
            facing = False
        if keys[pygame.K_RIGHT] and rect.right < SCREEN_WIDTH:
            dx = effective_speed
            facing = True
        if keys[pygame.K_UP] and rect.top > 0:
            dy = -effective_speed
        if keys[pygame.K_DOWN] and rect.bottom < SCREEN_HEIGHT:
            dy = effective_speed

        return dx, dy, facing

    def select_animation(self, dx: int, dy: int, speed: int) -> str:
        moving = dx != 0 or dy != 0
        if not moving:
            return "Idle"
        return "Run" if self._dash_timer > 0 else (
            "Run" if speed > PLAYER_SPEED else "Walk"
        )
