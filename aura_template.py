# aura_template.py
"""
Patrón TEMPLATE METHOD — Esqueleto algorítmico de los decoradores de aura.

Problema original:
  Los cuatro decoradores (Fire, Ice, Thunder, Nature) repetían en cada
  uno el mismo esqueleto lógico:
    1. ¿Expiró? → dejar de aplicar efecto
    2. Aplicar efecto de comportamiento (velocidad / escudo / etc.)
    3. Actualizar partículas / cristales / rayos
    4. Decrementar timer
    5. draw: dibujar entidad interna → efecto visual → barra de duración

  Este esqueleto estaba duplicado en los cuatro update() y draw(),
  lo que generaba código repetido y hacía difícil cambiar el flujo
  común sin editar las cuatro clases → violación de DRY + OCP.

Solución — Template Method:
  AuraTemplate define el algoritmo completo en update() y draw().
  Los "pasos variables" se delegan a métodos hook protegidos que
  las subclases sobreescriben sólo donde tienen lógica propia:

    update():
      ├── _apply_behavior_effect()   ← hook: velocidad, fuerza animación, etc.
      ├── _update_particles()        ← hook: mover partículas propias
      └── _on_expire()               ← hook: limpiar al expirar

    draw():
      ├── _draw_background_fx()      ← hook: partículas / fx detrás del dino
      ├── [dibuja entidad interna]   ← fijo (siempre en el medio)
      └── _draw_foreground_fx()      ← hook: aura, cristales, barra de duración

  Ahora agregar un nuevo decorador sólo requiere sobreescribir los
  hooks relevantes — el flujo común nunca se toca.
"""

from __future__ import annotations
import math
import pygame
from base_entity import EntityComponent
from setting import POWERUP_DURATION, PLAYER_SIZE, WHITE


class AuraTemplate(EntityComponent):
    """
    Decorator base + Template Method.

    Combina ambos patrones:
      • Como Decorator: envuelve a EntityComponent y delega métodos base.
      • Como Template Method: define el algoritmo de update/draw con
        ganchos (hooks) para que las subclases personalicen sólo su parte.

    Atributos de clase que las subclases DEBEN sobreescribir:
        NAME  (str)            — nombre legible del poder (para HUD)
        COLOR (tuple[int,...]) — color RGB del aura (para barra / efectos)
    """

    NAME  = "Base"
    COLOR = WHITE

    def __init__(self, entity: EntityComponent, duration: int = POWERUP_DURATION):
        self._entity  = entity
        self.duration = duration
        self.timer    = 0

    # ─── Propiedades de tiempo ────────────────────────────────
    @property
    def expired(self) -> bool:
        return self.timer >= self.duration

    @property
    def remaining(self) -> int:
        return max(0, self.duration - self.timer)

    @property
    def progress(self) -> float:
        return self.timer / self.duration if self.duration > 0 else 1.0

    # ─── Delegación al componente envuelto ───────────────────
    def get_speed(self) -> int:
        return self._entity.get_speed()

    def get_rect(self) -> pygame.Rect:
        return self._entity.get_rect()

    def is_invincible(self) -> bool:
        return self._entity.is_invincible()

    def get_attack_bonus(self) -> int:
        return self._entity.get_attack_bonus()

    def get_state(self) -> str:
        return self._entity.get_state()

    def set_animation(self, name: str):
        self._entity.set_animation(name)

    def force_animation(self, name: str):
        self._entity.force_animation(name)

    # ─── Template Method: update ─────────────────────────────
    def update(self):
        """
        Algoritmo fijo de actualización.
        Las subclases personalizan los hooks, no este método.
        """
        if not self.expired:
            self._apply_behavior_effect()   # hook: efectos de comportamiento
            self._entity.update()
            self._update_particles()        # hook: animación de partículas
            self.timer += 1
        else:
            self._entity.update()
            self._on_expire()               # hook: limpieza al expirar

    # ─── Template Method: draw ───────────────────────────────
    def draw(self, screen: pygame.Surface):
        """
        Algoritmo fijo de renderizado: fx-fondo → dino → fx-frente.
        Las subclases personalizan los hooks, no este método.
        """
        self._draw_background_fx(screen)    # hook: fx detrás del sprite
        self._entity.draw(screen)
        if not self.expired:
            self._draw_foreground_fx(screen)  # hook: aura + barra encima

    # ─────────────────────────────────────────────────────────
    #  HOOKS — sobreescribir en subclases (por defecto no hacen nada)
    # ─────────────────────────────────────────────────────────

    def _apply_behavior_effect(self):
        """Aplica el efecto de comportamiento del poder (velocidad, animación…)."""
        pass

    def _update_particles(self):
        """Actualiza el estado interno de partículas / elementos visuales."""
        pass

    def _on_expire(self):
        """Limpieza cuando el decorador expira (liberar animaciones, etc.)."""
        pass

    def _draw_background_fx(self, screen: pygame.Surface):
        """Dibuja efectos visuales DETRÁS del sprite del dinosaurio."""
        pass

    def _draw_foreground_fx(self, screen: pygame.Surface):
        """Dibuja efectos visuales ENCIMA del sprite (aura, cristales, barra)."""
        pass

    # ─────────────────────────────────────────────────────────
    #  Utilidades compartidas (reutilizables por todas las subclases)
    # ─────────────────────────────────────────────────────────

    def _draw_timer_bar(self, screen: pygame.Surface, color: tuple, offset_y: int = 0):
        """Barra de duración debajo del dinosaurio."""
        rect  = self.get_rect()
        bar_w = PLAYER_SIZE
        ratio = self.remaining / self.duration
        y_pos = rect.bottom + 6 + offset_y

        bg = pygame.Rect(rect.centerx - bar_w // 2, y_pos, bar_w, 5)
        pygame.draw.rect(screen, (30, 30, 40), bg, border_radius=3)

        fg = pygame.Rect(rect.centerx - bar_w // 2, y_pos,
                         int(bar_w * ratio), 5)
        pygame.draw.rect(screen, color, fg, border_radius=3)
        pygame.draw.rect(screen, (*color, 120), bg, 1, border_radius=3)

    def _get_base(self):
        """Navega hasta el Player base a través de la cadena de decoradores."""
        obj = self._entity
        while hasattr(obj, '_entity'):
            obj = obj._entity
        return obj

    def _get_bar_offset(self) -> int:
        """Calcula offset vertical para la barra según decoradores apilados."""
        count, obj = 0, self._entity
        while hasattr(obj, '_entity'):
            if isinstance(obj, AuraTemplate) and not obj.expired:
                count += 1
            obj = obj._entity
        return count * 10

    def _pulsing_aura(
        self,
        screen: pygame.Surface,
        color: tuple,
        base_radius: int,
        pulse_amplitude: int = 8,
        alpha_fill: int = 50,
        alpha_ring: int = 130,
    ):
        """
        Dibuja un aura circular pulsante sobre el dinosaurio.
        Utilidad reutilizable para Fire, Thunder, Nature y cualquier aura futura.
        """
        rect   = self.get_rect()
        pulse  = abs(math.sin(self.timer * 0.12)) * pulse_amplitude
        radius = base_radius + int(pulse)
        surf   = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*color, alpha_fill), (radius, radius), radius)
        pygame.draw.circle(surf, (*color, alpha_ring), (radius, radius), radius, 2)
        screen.blit(surf, (rect.centerx - radius, rect.centery - radius))
