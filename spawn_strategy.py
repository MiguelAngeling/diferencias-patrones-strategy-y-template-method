# spawn_strategy.py
"""
Patrón STRATEGY — Estrategias de spawn de enemigos.

Problema original:
  maybe_spawn_enemy() en Game mezclaba la decisión de cuándo spawnear,
  cuántos spawnear y con qué dificultad dentro del mismo método.
  Cambiar la curva de dificultad implicaba modificar Game directamente.

Solución — Strategy:
  EnemySpawnStrategy define el contrato.
  Cada estrategia concreta decide cuándo y cuántos enemigos generar.
  Game sólo llama a strategy.tick(score) y recibe una lista de Enemies.

Estrategias incluidas:
  - LinearSpawnStrategy    → dificultad lineal (original)
  - WaveSpawnStrategy      → oleadas de enemigos (extensión nueva)
"""

from __future__ import annotations
import random
from abc import ABC, abstractmethod
from setting import (
    ENEMY_SPAWN_MIN, ENEMY_SPAWN_BASE,
)


class EnemySpawnStrategy(ABC):
    """Interfaz Strategy para la generación de enemigos."""

    @abstractmethod
    def tick(self, score: int) -> int:
        """
        Llamado cada frame con el puntaje actual.
        Retorna el número de enemigos a generar este frame (0 ó más).
        También calcula el speed_bonus que llevarán.
        """
        ...

    @property
    @abstractmethod
    def speed_bonus(self) -> int:
        """Bono de velocidad que se aplica al enemigo recién generado."""
        ...


# ─────────────────────────────────────────────────────────────
#  Estrategia concreta 1 — Lineal (original)
# ─────────────────────────────────────────────────────────────
class LinearSpawnStrategy(EnemySpawnStrategy):
    """
    La dificultad aumenta de forma lineal con el puntaje.
    Comportamiento idéntico al original: el intervalo entre spawns
    se reduce conforme sube el score.
    """

    def __init__(self):
        self._timer = 0
        self._bonus = 0

    @property
    def speed_bonus(self) -> int:
        return self._bonus

    def tick(self, score: int) -> int:
        self._timer += 1
        interval = max(ENEMY_SPAWN_MIN, ENEMY_SPAWN_BASE - score // 200)
        self._bonus = score // 3000

        if self._timer >= interval:
            self._timer = 0
            return 1
        return 0


# ─────────────────────────────────────────────────────────────
#  Estrategia concreta 2 — Oleadas (extensión NUEVA)
# ─────────────────────────────────────────────────────────────
class WaveSpawnStrategy(EnemySpawnStrategy):
    """
    Genera enemigos en oleadas: un periodo de calma seguido de una
    ráfaga de varios enemigos al mismo tiempo.
    Demuestra cómo cambiar la curva de dificultad sin tocar Game.
    """

    CALM_FRAMES  = 180   # 3 s de calma
    WAVE_SIZE    = 4     # enemigos por oleada

    def __init__(self):
        self._timer    = 0
        self._in_wave  = False
        self._wave_rem = 0
        self._bonus    = 0

    @property
    def speed_bonus(self) -> int:
        return self._bonus

    def tick(self, score: int) -> int:
        self._timer += 1
        self._bonus  = score // 2000

        if not self._in_wave:
            if self._timer >= self.CALM_FRAMES:
                self._in_wave  = True
                self._wave_rem = self.WAVE_SIZE
                self._timer    = 0
            return 0

        # Durante la oleada: spawnea 1 por frame hasta agotar la ola
        if self._wave_rem > 0:
            self._wave_rem -= 1
            if self._wave_rem == 0:
                self._in_wave = False
            return 1
        return 0
