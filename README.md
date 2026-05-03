# diferencias-patrones-strategy-y-template-method
Integrantes:
```
- Miguel Ángel Hernández Medina
- Juan Pablo Diaz Ricaurte
- Nicolás Martínez Pineda
```
# Rol
Actúa como un Arquitecto de Software Senior experto en Python y patrones de diseño.

# Contexto
Tengo el siguiente juego creado en python, en el que se ha importado la librería de Pygame, allí se ha implementado el patrón de diseño "Decorator"

# Tarea
1. Analiza el código anterior e identifica áreas de mejora.
2. Refactoriza el código aplicando los siguientes patrones de diseño: [Strategy y Template Method].
3. Asegúrate de seguir los principios SOLID

# Salida
1. Haz una explicación de la manera en como se implementaron dichos patrones y como esta implementación hace mas escalable y mantenible el código
2. Código refactorizado y modulado listo para ser ejecutado

# Respuesta de la IA
1. Análisis del código original — Áreas de mejora
```El código original implementaba correctamente el patrón Decorator, pero tenía tres problemas principales:
a) Lógica de movimiento mezclada con la entidad (Player.update)
Todo el control de teclado, física, límites de pantalla y selección de animación vivían en un único método. Añadir otro modo de control (táctil, IA, dash) requería modificar Player directamente → violación de OCP.
b) Algoritmo repetido en los cuatro decoradores
FireDecorator, IceDecorator, ThunderDecorator y NatureDecorator repetían el mismo esqueleto en sus update() y draw(): verificar expiración → aplicar efecto → actualizar partículas → dibujar capas. Cualquier cambio al flujo común exigía editar los cuatro → violación de DRY.
c) Lógica de dificultad incrustada en Game
maybe_spawn_enemy() mezclaba el intervalo de spawn, el cálculo de dificultad y la creación del enemigo. Cambiar la curva de dificultad implicaba tocar Game → violación de OCP.
```
2. Patrones aplicados
```Patrón Strategy — dos implementaciones
MovementStrategy (movement_strategy.py)
Player ya no sabe cómo se mueve: recibe una estrategia por inyección en el construc``` tor (principio DIP).
MovementStrategy (ABC)
  ├── KeyboardMovementStrategy   ← comportamiento original
  └── DashMovementStrategy       ← extensión nueva (dash con SPACE)
Player.update() ahora hace simplemente:
pythondx, dy, facing = self._movement.compute_move(self.rect, self.speed)
anim = self._movement.select_animation(dx, dy, self.speed)
Para agregar movimiento con IA, táctil o cualquier otro modo: crear una subclase, pasarla al constructor. Player, Game y ningún decorador se tocan.
EnemySpawnStrategy (spawn_strategy.py)
Game.maybe_spawn_enemy() pasó de ~6 líneas con lógica propia a una sola llamada:
pythoncount = self._spawn_strategy.tick(self.score)
EnemySpawnStrategy (ABC)
  ├── LinearSpawnStrategy   ← dificultad lineal (original)
  └── WaveSpawnStrategy     ← oleadas de enemigos (nueva; tecla S la activa en vivo)

Patrón Template Method — AuraTemplate
AuraTemplate (aura_template.py) reemplaza a AuraDecorator y define el algoritmo fijo de update() y draw() con hooks que las subclases sobreescriben:
update():                         draw():
  ├── _apply_behavior_effect()      ├── _draw_background_fx()   ← partículas detrás
  ├── entity.update()               ├── entity.draw()            ← orden fijo
  ├── _update_particles()           └── _draw_foreground_fx()   ← aura encima
  └── _on_expire()
Cada decorador concreto sobreescribe sólo los hooks que necesita:
ClaseHooks que implementaFireDecorator_apply_behavior_effect, _update_particles, _on_expire, _draw_background_fx, _draw_foreground_fxIceDecorator_update_particles, _draw_background_fx, _draw_foreground_fxThunderDecorator_apply_behavior_effect, _update_particles, _on_expire, draw (override para parpadeo)NatureDecorator_update_particles, _draw_background_fx, _draw_foreground_fx
Además se extrajeron dos utilidades compartidas a AuraTemplate que antes se repetían: _draw_timer_bar() y el nuevo _pulsing_aura(), que FireDecorator y NatureDecorator reutilizan sin duplicar código.
```
3. Cómo esto mejora escalabilidad y mantenibilidad
```Principio SOLID aplicado por pieza:

SRP: cada archivo tiene una sola razón para cambiar. movement_strategy.py cambia sólo si cambia cómo se mueve el jugador; spawn_strategy.py cambia sólo si cambia la curva de dificultad;
OCP: agregar un nuevo tipo de movimiento o una nueva curva de dificultad no toca ninguna clase existente, solo se agrega una nueva subclase.
LSP: todas las estrategias y todos los decoradores son intercambiables con sus interfaces.
DIP: Player y Game dependen de las abstracciones (MovementStrategy, EnemySpawnStrategy), no de implementaciones concretas.
```
