# main.py
"""
Punto de entrada del juego.

Aquí se puede elegir la estrategia de spawn y la estrategia de movimiento
sin tocar ninguna otra clase — esto es la composición en acción.

Ejemplos:
    Game()                                          → defaults (Keyboard + Linear)
    Game(spawn_strategy=WaveSpawnStrategy())        → modo oleadas
    Player(..., movement_strategy=DashMovementStrategy())  → modo dash
"""

from game import Game
from spawn_strategy import LinearSpawnStrategy  # o WaveSpawnStrategy

if __name__ == "__main__":
    Game(spawn_strategy=LinearSpawnStrategy()).run()
