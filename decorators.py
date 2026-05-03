# decorators.py
"""
Decoradores de aura — Patrón Decorator + Template Method.

Cada clase concreta hereda de AuraTemplate y sobreescribe SÓLO
los hooks que necesita.  El flujo común (timer, orden de draw,
delegación a la entidad interna) vive en AuraTemplate y nunca
se repite aquí.

Jerarquía:
  EntityComponent          ← interfaz (base_entity.py)
    └── AuraTemplate       ← Template Method + Decorator base (aura_template.py)
          ├── FireDecorator
          ├── IceDecorator
          ├── ThunderDecorator
          └── NatureDecorator
"""

from __future__ import annotations
import math
import random
import pygame
from aura_template import AuraTemplate
from base_entity  import EntityComponent
from setting import (
    POWERUP_DURATION, PLAYER_SIZE, PLAYER_SPEED,
    SCREEN_WIDTH, SCREEN_HEIGHT,
    AURA_FIRE, AURA_ICE, AURA_THUNDER, AURA_HEAL,
)


# ════════════════════════════════════════════════════════════════
#  🔥 FUEGO
# ════════════════════════════════════════════════════════════════
class FireDecorator(AuraTemplate):
    """
    Efecto: +3 velocidad, +2 ataque.
    Visual: partículas de fuego + aura naranja pulsante.
    Hook de animación: fuerza «Run» mientras está activo.
    """

    NAME  = "Fuego +Vel"
    COLOR = AURA_FIRE
    BOOST = 3

    def __init__(self, entity: EntityComponent, duration: int = POWERUP_DURATION):
        super().__init__(entity, duration)
        self._particles: list[list] = []   # [x, y, age, vx, vy]

    # ── Delegación con override de stats ─────────────────────
    def get_speed(self) -> int:
        base = self._entity.get_speed()
        return base + (self.BOOST if not self.expired else 0)

    def get_attack_bonus(self) -> int:
        bonus = 2 if not self.expired else 0
        return self._entity.get_attack_bonus() + bonus

    # ── Hooks ─────────────────────────────────────────────────
    def _apply_behavior_effect(self):
        """Inyecta velocidad al núcleo y fuerza animación Run."""
        base = self._get_base()
        base.speed += self.BOOST
        # Forzar Run para que la lógica de animación del Player lo detecte
        base.force_animation("Run")
        # Nota: el decrement de base.speed lo hace update() del Player internamente
        # al recalcular; aquí lo revertimos justo antes de que Player.update() lea:
        # La estrategia de movimiento del Player usa self.speed al momento de update,
        # así que inyectamos y revertimos después:
        base.speed -= self.BOOST  # revertir; get_speed() ya devuelve el valor correcto

    def _update_particles(self):
        """Genera y envejece partículas de fuego."""
        r = self.get_rect()
        for _ in range(2):
            px = r.centerx + random.randint(-12, 12)
            py = r.bottom + random.randint(-8, 4)
            vx = random.uniform(-0.8, 0.8)
            vy = random.uniform(-2.5, -0.5)
            self._particles.append([px, py, 0, vx, vy])

        new_particles = []
        for p in self._particles:
            p[0] += p[3]
            p[1] += p[4]
            p[4] -= 0.05
            p[2] += 1
            if p[2] < 20:
                new_particles.append(p)
        self._particles = new_particles

    def _on_expire(self):
        """Libera la animación forzada al expirar."""
        self._get_base().release_animation()

    def _draw_background_fx(self, screen: pygame.Surface):
        """Partículas de fuego detrás del dino."""
        for x, y, age, *_ in self._particles:
            alpha  = max(0, 220 - age * 11)
            radius = max(1, 8 - age // 3)
            r = min(255, AURA_FIRE[0] + age * 2)
            g = max(0, AURA_FIRE[1] - age * 5)
            b = max(0, AURA_FIRE[2] - age)
            surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (r, g, b, alpha), (radius, radius), radius)
            screen.blit(surf, (int(x) - radius, int(y) - radius))

    def _draw_foreground_fx(self, screen: pygame.Surface):
        """Aura naranja pulsante + barra de duración."""
        self._pulsing_aura(
            screen, AURA_FIRE,
            base_radius=PLAYER_SIZE // 2 + 10,
            alpha_fill=50, alpha_ring=130,
        )
        self._draw_timer_bar(screen, AURA_FIRE, self._get_bar_offset())


# ════════════════════════════════════════════════════════════════
#  ❄️  HIELO
# ════════════════════════════════════════════════════════════════
class IceDecorator(AuraTemplate):
    """
    Efecto: absorbe 1 golpe mortal.
    Visual: cristales de diamante orbitando + aura cyan.
    """

    NAME  = "Hielo +Escudo"
    COLOR = AURA_ICE

    def __init__(self, entity: EntityComponent, duration: int = POWERUP_DURATION):
        super().__init__(entity, duration)
        self.shield_hp   = 1
        self.flash_timer = 0

    def absorb_hit(self) -> bool:
        """Absorbe un golpe. Retorna True si fue absorbido."""
        if self.shield_hp > 0 and not self.expired:
            self.shield_hp   -= 1
            self.flash_timer  = 15
            self.timer        = self.duration  # agota el decorador
            return True
        return False

    # ── Hooks ─────────────────────────────────────────────────
    def _update_particles(self):
        if self.flash_timer > 0:
            self.flash_timer -= 1

    def _draw_background_fx(self, screen: pygame.Surface):
        """Flash blanco al absorber el golpe."""
        if self.flash_timer > 0:
            rect  = self.get_rect()
            alpha = int(200 * (self.flash_timer / 15))
            flash = pygame.Surface(
                (rect.width + 20, rect.height + 20), pygame.SRCALPHA
            )
            flash.fill((255, 255, 255, alpha))
            screen.blit(flash, (rect.x - 10, rect.y - 10))

    def _draw_foreground_fx(self, screen: pygame.Surface):
        """Cristales orbitando + aura helada + barra."""
        if self.shield_hp <= 0:
            return

        rect   = self.get_rect()
        radius = PLAYER_SIZE // 2 + 18

        # Cristales de diamante
        for i in range(6):
            angle = math.radians(i * 60 + self.timer * 1.5)
            sx = rect.centerx + int(math.cos(angle) * radius)
            sy = rect.centery + int(math.sin(angle) * radius)

            cs = 7
            crystal = pygame.Surface((cs * 2, cs * 2), pygame.SRCALPHA)
            points  = [(cs, 0), (cs * 2, cs), (cs, cs * 2), (0, cs)]
            pygame.draw.polygon(crystal, (*AURA_ICE, 220), points)
            pygame.draw.polygon(crystal, (200, 240, 255, 160), points, 1)
            rot = pygame.transform.rotate(crystal, math.degrees(angle) * 0.5)
            screen.blit(rot, (sx - rot.get_width() // 2, sy - rot.get_height() // 2))

        # Aura helada
        aura_r = radius + 6
        surf   = pygame.Surface((aura_r * 2, aura_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*AURA_ICE, 30), (aura_r, aura_r), aura_r)
        pygame.draw.circle(surf, (*AURA_ICE, 100), (aura_r, aura_r), aura_r, 2)
        screen.blit(surf, (rect.centerx - aura_r, rect.centery - aura_r))

        self._draw_timer_bar(screen, AURA_ICE, self._get_bar_offset())


# ════════════════════════════════════════════════════════════════
#  ⚡ RAYO
# ════════════════════════════════════════════════════════════════
class ThunderDecorator(AuraTemplate):
    """
    Efecto: invencibilidad total (destruye enemigos al contacto).
    Visual: rayos eléctricos zigzag + parpadeo del sprite.
    Hook de animación: fuerza «Jump» (el dino flota).
    """

    NAME  = "Rayo +Inven"
    COLOR = AURA_THUNDER

    def __init__(self, entity: EntityComponent, duration: int = POWERUP_DURATION):
        super().__init__(entity, duration)
        self._bolts: list[list[tuple]] = []

    def is_invincible(self) -> bool:
        return not self.expired or self._entity.is_invincible()

    # ── Hooks ─────────────────────────────────────────────────
    def _apply_behavior_effect(self):
        self._get_base().force_animation("Jump")

    def _update_particles(self):
        """Regenera rayos zigzag cada 3 frames."""
        if self.timer % 3 == 0:
            self._bolts = []
            rect = self.get_rect()
            for _ in range(4):
                angle  = random.uniform(0, math.pi * 2)
                length = PLAYER_SIZE // 2 + random.randint(15, 35)
                x1, y1 = rect.centerx, rect.centery
                pts    = [(x1, y1)]
                segs   = random.randint(3, 5)
                for s in range(1, segs + 1):
                    t  = s / segs
                    bx = x1 + int(math.cos(angle) * length * t) + random.randint(-6, 6)
                    by = y1 + int(math.sin(angle) * length * t) + random.randint(-6, 6)
                    pts.append((bx, by))
                self._bolts.append(pts)

    def _on_expire(self):
        self._get_base().release_animation()

    def _draw_background_fx(self, screen: pygame.Surface):
        """Oculta el dino en frames alternos (parpadeo eléctrico)."""
        # La forma más limpia: no dibujar la entidad interna esta vez.
        # Pero draw() ya la dibuja; anulamos aquí el renderizado del dino
        # sobreescribiendo draw() con lógica de parpadeo en _draw_foreground_fx.
        pass

    def draw(self, screen: pygame.Surface):
        """Override completo para controlar el parpadeo del sprite."""
        self._draw_background_fx(screen)

        show = self.expired or (self.timer // 4) % 3 != 0
        if show:
            self._entity.draw(screen)

        if not self.expired:
            self._draw_foreground_fx(screen)

    def _draw_foreground_fx(self, screen: pygame.Surface):
        """Aura eléctrica + rayos zigzag + chispas + barra."""
        rect = self.get_rect()

        # Aura central
        pulse  = abs(math.sin(self.timer * 0.15)) * 6
        aura_r = PLAYER_SIZE // 2 + 12 + int(pulse)
        surf   = pygame.Surface((aura_r * 2, aura_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*AURA_THUNDER, 40), (aura_r, aura_r), aura_r)
        screen.blit(surf, (rect.centerx - aura_r, rect.centery - aura_r))

        # Rayos
        for bolt in self._bolts:
            if len(bolt) >= 2:
                alpha     = 180 + int(math.sin(self.timer * 0.3) * 75)
                bolt_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                pygame.draw.lines(bolt_surf, (*AURA_THUNDER, alpha), False, bolt, 2)
                pygame.draw.lines(bolt_surf, (255, 255, 200, alpha // 2), False, bolt, 4)
                screen.blit(bolt_surf, (0, 0))

        # Chispas orbitando
        for i in range(3):
            angle = math.radians(self.timer * 8 + i * 120)
            sr    = PLAYER_SIZE // 2 + 20
            sx    = rect.centerx + int(math.cos(angle) * sr)
            sy    = rect.centery + int(math.sin(angle) * sr)
            spark = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(spark, (*AURA_THUNDER, 200), (3, 3), 3)
            screen.blit(spark, (sx - 3, sy - 3))

        self._draw_timer_bar(screen, AURA_THUNDER, self._get_bar_offset())


# ════════════════════════════════════════════════════════════════
#  🌿 NATURALEZA
# ════════════════════════════════════════════════════════════════
class NatureDecorator(AuraTemplate):
    """
    Efecto: regenera 1 vida cada REGEN_INTERVAL frames.
    Visual: hojas orbitando + pulso verde + esporas.
    """

    NAME           = "Natura +Regen"
    COLOR          = AURA_HEAL
    REGEN_INTERVAL = 90

    def __init__(self, entity: EntityComponent, duration: int = POWERUP_DURATION):
        super().__init__(entity, duration)
        self.regen_tick = 0
        self.healed     = 0
        self.heal_flash = 0

    # ── Hooks ─────────────────────────────────────────────────
    def _update_particles(self):
        """Lógica de regeneración + flash de curación."""
        self.regen_tick += 1
        if self.regen_tick >= self.REGEN_INTERVAL:
            self.healed    += 1
            self.regen_tick = 0
            self.heal_flash = 20

        if self.heal_flash > 0:
            self.heal_flash -= 1

    def _draw_background_fx(self, screen: pygame.Surface):
        """Flash verde al regenerar vida."""
        if self.heal_flash > 0:
            rect  = self.get_rect()
            alpha = int(100 * (self.heal_flash / 20))
            flash = pygame.Surface(
                (rect.width + 16, rect.height + 16), pygame.SRCALPHA
            )
            flash.fill((*AURA_HEAL, alpha))
            screen.blit(flash, (rect.x - 8, rect.y - 8))

    def _draw_foreground_fx(self, screen: pygame.Surface):
        """Hojas orbitando + pulso natural + esporas + barra."""
        rect = self.get_rect()

        # Hojas
        for i in range(5):
            angle   = math.radians(i * 72 + self.timer * 2)
            orbit_r = PLAYER_SIZE // 2 + 20
            lx = rect.centerx + int(math.cos(angle) * orbit_r)
            ly = rect.centery + int(math.sin(angle) * orbit_r)

            lw, lh = 16, 8
            leaf   = pygame.Surface((lw, lh), pygame.SRCALPHA)
            pygame.draw.ellipse(leaf, (*AURA_HEAL, 220), (0, 0, lw, lh))
            pygame.draw.line(leaf, (40, 180, 60, 180), (2, lh // 2), (lw - 2, lh // 2), 1)
            rotated = pygame.transform.rotate(leaf, math.degrees(angle))
            screen.blit(rotated, (
                lx - rotated.get_width() // 2,
                ly - rotated.get_height() // 2,
            ))

        # Pulso natural (reutiliza la utilidad de AuraTemplate)
        self._pulsing_aura(
            screen, AURA_HEAL,
            base_radius=PLAYER_SIZE // 2 + 8,
            pulse_amplitude=6,
            alpha_fill=35, alpha_ring=80,
        )

        # Esporas flotantes
        for i in range(3):
            sa = math.radians(self.timer * 1.5 + i * 120)
            sr = PLAYER_SIZE // 2 + 10 + int(math.sin(self.timer * 0.1 + i) * 8)
            sx = rect.centerx + int(math.cos(sa) * sr)
            sy = rect.centery + int(math.sin(sa) * sr)
            sp = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(sp, (*AURA_HEAL, 160), (2, 2), 2)
            screen.blit(sp, (sx - 2, sy - 2))

        self._draw_timer_bar(screen, AURA_HEAL, self._get_bar_offset())
