# base_entity.py
"""
Interfaz base (Component) del patrón Decorator.
Sin cambios respecto al original — es la raíz de la jerarquía.
"""

import pygame


class EntityComponent:
    """Interfaz base del patrón Decorator — Component."""

    def update(self):
        raise NotImplementedError

    def draw(self, screen):
        raise NotImplementedError

    def get_rect(self) -> pygame.Rect:
        raise NotImplementedError

    def get_speed(self) -> int:
        raise NotImplementedError

    def is_invincible(self) -> bool:
        raise NotImplementedError

    def get_state(self) -> str:
        return "idle"

    def set_animation(self, name: str):
        pass

    def force_animation(self, name: str):
        pass

    def get_attack_bonus(self) -> int:
        return 0
