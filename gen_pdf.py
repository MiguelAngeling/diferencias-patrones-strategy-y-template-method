"""
Genera el PDF de documentación de la refactorización:
Patrón Strategy + Template Method sobre el juego Dino Aura.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether,
)
from reportlab.platypus.flowables import Flowable
from reportlab.lib.colors import HexColor

# ── Paleta de colores ─────────────────────────────────────────
C_DARK    = HexColor("#0F0C1E")   # fondo oscuro (título)
C_ACCENT  = HexColor("#7C5CBF")   # violeta principal
C_FIRE    = HexColor("#FF6414")   # naranja fuego
C_ICE     = HexColor("#64DCFF")   # cyan hielo
C_THUNDER = HexColor("#FFF028")   # amarillo rayo
C_NATURE  = HexColor("#3CDC50")   # verde naturaleza
C_CODE_BG = HexColor("#1E1B2E")   # fondo de bloques de código
C_CODE_FG = HexColor("#E8E0FF")   # texto en código
C_MUTED   = HexColor("#888888")
C_HEADING = HexColor("#2D1B5A")
C_RULE    = HexColor("#5A3FA0")
C_LIGHT   = HexColor("#F5F3FF")
C_WHITE   = colors.white
C_BLACK   = colors.black

W, H = A4

# ── Flowable: bloque de código ─────────────────────────────────
class CodeBlock(Flowable):
    """Caja con fondo oscuro que muestra código monoespaciado."""

    def __init__(self, lines: list[str], width=None):
        super().__init__()
        self._lines = lines
        self._w     = width or (W - 4 * cm)
        self._font  = "Courier"
        self._fs    = 8
        self._pad   = 10
        self._lh    = 12
        self.width  = self._w
        self.height = len(lines) * self._lh + self._pad * 2

    def draw(self):
        c = self.canv
        # Fondo
        c.setFillColor(C_CODE_BG)
        c.roundRect(0, 0, self._w, self.height, 6, fill=1, stroke=0)
        # Borde sutil
        c.setStrokeColor(C_ACCENT)
        c.setLineWidth(0.5)
        c.roundRect(0, 0, self._w, self.height, 6, fill=0, stroke=1)
        # Texto
        c.setFillColor(C_CODE_FG)
        c.setFont(self._font, self._fs)
        y = self.height - self._pad - self._fs
        for line in self._lines:
            c.drawString(self._pad, y, line)
            y -= self._lh

# ── Flowable: badge de color ────────────────────────────────────
class Badge(Flowable):
    """Pastilla de color con texto."""

    def __init__(self, text: str, bg: HexColor, fg=None, width=None):
        super().__init__()
        self._text = text
        self._bg   = bg
        self._fg   = fg or C_WHITE
        self.width  = width or 120
        self.height = 18

    def draw(self):
        c = self.canv
        c.setFillColor(self._bg)
        c.roundRect(0, 0, self.width, self.height, 4, fill=1, stroke=0)
        c.setFillColor(self._fg)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(self.width / 2, 4, self._text)


# ── Estilos ────────────────────────────────────────────────────
def build_styles():
    base = getSampleStyleSheet()

    styles = {
        "cover_title": ParagraphStyle(
            "cover_title", fontSize=32, textColor=C_WHITE,
            fontName="Helvetica-Bold", alignment=TA_CENTER,
            leading=38, spaceAfter=6,
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub", fontSize=13, textColor=HexColor("#C8B8FF"),
            fontName="Helvetica", alignment=TA_CENTER, leading=18,
        ),
        "cover_meta": ParagraphStyle(
            "cover_meta", fontSize=9, textColor=HexColor("#8878AA"),
            fontName="Helvetica", alignment=TA_CENTER,
        ),
        "h1": ParagraphStyle(
            "h1", fontSize=18, textColor=C_HEADING,
            fontName="Helvetica-Bold", spaceBefore=18, spaceAfter=6,
            leading=22,
        ),
        "h2": ParagraphStyle(
            "h2", fontSize=13, textColor=C_ACCENT,
            fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=4,
            leading=17,
        ),
        "h3": ParagraphStyle(
            "h3", fontSize=11, textColor=C_HEADING,
            fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=3,
            leading=14,
        ),
        "body": ParagraphStyle(
            "body", fontSize=10, textColor=HexColor("#1A1030"),
            fontName="Helvetica", leading=15, spaceAfter=6,
            alignment=TA_JUSTIFY,
        ),
        "bullet": ParagraphStyle(
            "bullet", fontSize=10, textColor=HexColor("#1A1030"),
            fontName="Helvetica", leading=14, spaceAfter=3,
            leftIndent=16, firstLineIndent=-10,
        ),
        "caption": ParagraphStyle(
            "caption", fontSize=8, textColor=C_MUTED,
            fontName="Helvetica-Oblique", alignment=TA_CENTER,
            spaceAfter=8,
        ),
        "callout": ParagraphStyle(
            "callout", fontSize=10, textColor=HexColor("#2D1B5A"),
            fontName="Helvetica", leading=14, leftIndent=12,
            rightIndent=12,
        ),
    }
    return styles


# ── Helpers ────────────────────────────────────────────────────
def rule(story, color=C_RULE, thickness=0.8):
    story.append(HRFlowable(width="100%", thickness=thickness,
                            color=color, spaceAfter=6, spaceBefore=2))

def callout(story, text, bg=C_LIGHT, border=C_ACCENT, styles=None):
    """Caja destacada tipo 'nota'."""
    data = [[Paragraph(text, styles["callout"])]]
    t = Table(data, colWidths=[W - 4 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), bg),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",(0, 0), (-1, -1), 10),
        ("TOPPADDING",  (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",(0,0), (-1, -1), 8),
        ("LINEBEFORETRUE",(0,0),(-1,-1), 3, border),
        ("ROUNDEDCORNERS", [4]),
    ]))
    story.append(t)
    story.append(Spacer(1, 6))


# ══════════════════════════════════════════════════════════════
#  CONTENIDO
# ══════════════════════════════════════════════════════════════
def build_story(styles):
    story = []
    S = styles

    # ── PORTADA ───────────────────────────────────────────────
    # Rectángulo de fondo oscuro simulado con tabla
    cover_data = [[
        Paragraph("DINO AURA", S["cover_title"]),
    ]]
    cover_bg = Table(cover_data, colWidths=[W - 4 * cm])
    cover_bg.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,-1), C_DARK),
        ("TOPPADDING",   (0,0),(-1,-1), 40),
        ("BOTTOMPADDING",(0,0),(-1,-1), 40),
        ("LEFTPADDING",  (0,0),(-1,-1), 20),
        ("RIGHTPADDING", (0,0),(-1,-1), 20),
        ("ROUNDEDCORNERS", [8]),
    ]))
    story.append(cover_bg)
    story.append(Spacer(1, 14))

    story.append(Paragraph(
        "Refactorización con Patrones de Diseño",
        S["cover_sub"],
    ))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Strategy  ·  Template Method  ·  Decorator  ·  Principios SOLID",
        S["cover_sub"],
    ))
    story.append(Spacer(1, 20))
    rule(story)
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Arquitectura de Software Senior — Python &amp; Pygame",
        S["cover_meta"],
    ))
    story.append(PageBreak())

    # ── ÍNDICE ─────────────────────────────────────────────────
    story.append(Paragraph("Tabla de Contenidos", S["h1"]))
    rule(story)
    toc_items = [
        ("1.", "Contexto y código original"),
        ("2.", "Áreas de mejora identificadas"),
        ("3.", "Patrón Strategy — Movimiento del jugador"),
        ("4.", "Patrón Strategy — Spawn de enemigos"),
        ("5.", "Patrón Template Method — Decoradores de aura"),
        ("6.", "Principios SOLID aplicados"),
        ("7.", "Estructura final de archivos"),
        ("8.", "Guía de extensión rápida"),
    ]
    toc_data = [[Paragraph(f"<b>{n}</b>", S["body"]),
                 Paragraph(t, S["body"])] for n, t in toc_items]
    toc_t = Table(toc_data, colWidths=[1.2*cm, W - 4*cm - 1.2*cm])
    toc_t.setStyle(TableStyle([
        ("VALIGN",      (0,0),(-1,-1), "TOP"),
        ("LEFTPADDING", (0,0),(-1,-1), 0),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LINEBELOW",   (0,-1),(-1,-1), 0.3, C_MUTED),
    ]))
    story.append(toc_t)
    story.append(PageBreak())

    # ── SECCIÓN 1 ─────────────────────────────────────────────
    story.append(Paragraph("1. Contexto y código original", S["h1"]))
    rule(story)
    story.append(Paragraph(
        "El proyecto <b>Dino Aura</b> es un juego en Python/Pygame donde un dinosaurio "
        "animado recolecta power-ups representados como gemas. Cada power-up envuelve al "
        "personaje con un decorador de aura que modifica su comportamiento:",
        S["body"],
    ))

    powers = [
        (C_FIRE,    "🔥 Fuego",    "FireDecorator",    "+3 velocidad, +2 ataque, anima «Run»"),
        (C_ICE,     "❄  Hielo",    "IceDecorator",     "Absorbe 1 golpe mortal (escudo)"),
        (C_THUNDER, "⚡ Rayo",     "ThunderDecorator",  "Invencibilidad total, anima «Jump»"),
        (C_NATURE,  "🌿 Naturaleza","NatureDecorator",  "Regenera 1 vida cada 1.5 segundos"),
    ]
    pw_data = [[
        Paragraph("<b>Power-up</b>", S["body"]),
        Paragraph("<b>Clase</b>", S["body"]),
        Paragraph("<b>Efecto</b>", S["body"]),
    ]] + [[
        Paragraph(name, S["body"]),
        Paragraph(f"<font name='Courier' size='9'>{cls}</font>", S["body"]),
        Paragraph(efecto, S["body"]),
    ] for (col, name, cls, efecto) in powers]

    pw_t = Table(pw_data, colWidths=[3.2*cm, 4.2*cm, W - 4*cm - 3.2*cm - 4.2*cm])
    row_colors = [C_FIRE, C_ICE, C_THUNDER, C_NATURE]
    ts = [
        ("BACKGROUND",   (0,0),(-1,0),  HexColor("#EDE8FF")),
        ("FONTNAME",     (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0,0),(-1,-1), 9),
        ("GRID",         (0,0),(-1,-1), 0.4, HexColor("#CCBBEE")),
        ("VALIGN",       (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",   (0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING",  (0,0),(-1,-1), 7),
    ]
    for i, col in enumerate(row_colors, start=1):
        ts.append(("BACKGROUND", (0,i),(-1,i), HexColor(f"{col.hexval()}22")))
    pw_t.setStyle(TableStyle(ts))
    story.append(pw_t)
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        "La arquitectura original usaba correctamente el patrón <b>Decorator</b> "
        "(EntityComponent → AuraDecorator → Fire/Ice/Thunder/NatureDecorator), "
        "pero presentaba tres áreas de mejora estructural descritas en la siguiente sección.",
        S["body"],
    ))
    story.append(PageBreak())

    # ── SECCIÓN 2 ─────────────────────────────────────────────
    story.append(Paragraph("2. Áreas de mejora identificadas", S["h1"]))
    rule(story)

    problems = [
        (
            "A — Lógica de movimiento acoplada al jugador",
            C_FIRE,
            "Player.update() mezclaba lectura de teclado, física, límites de pantalla "
            "y selección de animación en un único método monolítico. "
            "Añadir un nuevo modo de control (táctil, IA, dash) requería modificar "
            "Player directamente → <b>violación del principio OCP</b>.",
            [
                "def update(self):",
                "    keys = pygame.key.get_pressed()",
                "    if keys[K_LEFT] and self.rect.left > 0:",
                "        self.rect.x -= self.speed   # hard-coded",
                "        self.facing_right = False",
                "    # ... 20 líneas más mezclando física + animación",
            ],
        ),
        (
            "B — Esqueleto de algoritmo repetido en los 4 decoradores",
            C_ICE,
            "Cada decorador (Fire, Ice, Thunder, Nature) repetía el mismo flujo en "
            "update() y draw(): verificar expiración → aplicar efecto → actualizar "
            "partículas → dibujar capas. Cualquier cambio al flujo común exigía editar "
            "las cuatro clases → <b>violación del principio DRY y OCP</b>.",
            [
                "# En FireDecorator, IceDecorator, ThunderDecorator, NatureDecorator:",
                "def update(self):",
                "    if not self.expired:",
                "        # [efecto específico]   ← única parte diferente",
                "        self._entity.update()  # ← repetido en los 4",
                "        self.timer += 1         # ← repetido en los 4",
                "    else:",
                "        self._entity.update()  # ← repetido en los 4",
            ],
        ),
        (
            "C — Curva de dificultad incrustada en Game",
            C_NATURE,
            "maybe_spawn_enemy() en Game mezclaba la decisión de cuándo spawnear, "
            "cuántos spawnear y con qué velocidad. Cambiar la curva de dificultad "
            "implicaba modificar la clase Game directamente → <b>violación de OCP y SRP</b>.",
            [
                "def maybe_spawn_enemy(self):   # en Game",
                "    self.spawn_enemy_timer += 1",
                "    interval = max(MIN, BASE - self.score // 200)  # hard-coded",
                "    bonus = self.score // 3000                      # hard-coded",
                "    if self.spawn_enemy_timer >= interval:",
                "        self.enemies.add(Enemy(speed_bonus=bonus))",
                "        self.spawn_enemy_timer = 0",
            ],
        ),
    ]

    for title, color, desc, code in problems:
        block_data = [[Paragraph(f"<b>{title}</b>", S["h3"])]]
        block_t = Table(block_data, colWidths=[W - 4*cm])
        block_t.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), HexColor(f"{color.hexval()}18")),
            ("LINEBEFORETRUE",(0,0),(-1,-1), 4, color),
            ("LEFTPADDING",   (0,0),(-1,-1), 10),
            ("TOPPADDING",    (0,0),(-1,-1), 7),
            ("BOTTOMPADDING", (0,0),(-1,-1), 7),
        ]))
        story.append(block_t)
        story.append(Paragraph(desc, S["body"]))
        story.append(CodeBlock(code))
        story.append(Spacer(1, 10))

    story.append(PageBreak())

    # ── SECCIÓN 3 ─────────────────────────────────────────────
    story.append(Paragraph("3. Patrón Strategy — Movimiento del jugador", S["h1"]))
    rule(story)
    story.append(Paragraph(
        "El patrón <b>Strategy</b> permite definir una familia de algoritmos, "
        "encapsular cada uno y hacerlos intercambiables. Se aplica al movimiento "
        "del jugador mediante la interfaz <font name='Courier' size='9'>MovementStrategy</font>, "
        "que declara dos contratos:",
        S["body"],
    ))

    story.append(CodeBlock([
        "class MovementStrategy(ABC):             # Interfaz Strategy",
        "    @abstractmethod",
        "    def compute_move(self, rect, speed) -> tuple[int, int, bool | None]:",
        "        ...  # Calcula (dx, dy, facing_right) para este frame",
        "",
        "    @abstractmethod",
        "    def select_animation(self, dx, dy, speed) -> str:",
        "        ...  # Devuelve el nombre de la animación correspondiente",
    ]))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Estrategias concretas incluidas:", S["h2"]))

    strats = [
        (
            "KeyboardMovementStrategy",
            "Comportamiento original",
            "Flechas del teclado + límites de pantalla. Selecciona «Run» si hay "
            "boost de velocidad, «Walk» en movimiento normal, «Idle» en reposo.",
        ),
        (
            "DashMovementStrategy",
            "Extensión nueva",
            "Idéntica al teclado pero añade un dash (SPACE) que multiplica la velocidad "
            "×3 durante 10 frames, seguido de 45 frames de cooldown. "
            "Implementada sin tocar Player ni Game.",
        ),
    ]
    for cls, badge_txt, desc in strats:
        row = [[
            Paragraph(f"<font name='Courier' size='10'><b>{cls}</b></font>", S["body"]),
            Paragraph(f"<i>{badge_txt}</i>", S["body"]),
        ]]
        t = Table(row, colWidths=[6*cm, W - 4*cm - 6*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), HexColor("#F0EBFF")),
            ("LINEBEFORETRUE",(0,0),(-1,-1), 3, C_ACCENT),
            ("LEFTPADDING",   (0,0),(-1,-1), 8),
            ("TOPPADDING",    (0,0),(-1,-1), 6),
            ("BOTTOMPADDING", (0,0),(-1,-1), 6),
            ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ]))
        story.append(t)
        story.append(Paragraph(desc, S["body"]))
        story.append(Spacer(1, 4))

    story.append(Paragraph("Cómo Player consume la Strategy:", S["h2"]))
    story.append(CodeBlock([
        "class Player(EntityComponent):",
        "    def __init__(self, x, y, movement_strategy=None):",
        "        # Inyección de dependencia (DIP)",
        "        self._movement = movement_strategy or KeyboardMovementStrategy()",
        "",
        "    def set_movement_strategy(self, strategy: MovementStrategy):",
        "        self._movement = strategy   # cambio en tiempo de ejecución",
        "",
        "    def update(self):",
        "        dx, dy, facing = self._movement.compute_move(self.rect, self.speed)",
        "        self.rect.x += dx",
        "        self.rect.y += dy",
        "        if facing is not None:",
        "            self.facing_right = facing",
        "        if not self._forced_anim:",
        "            self.set_animation(self._movement.select_animation(dx, dy, self.speed))",
    ]))
    story.append(Spacer(1, 6))
    callout(story,
        "<b>Beneficio OCP:</b> para añadir movimiento con IA o modo multijugador "
        "basta crear una nueva subclase de MovementStrategy. "
        "Player, Game y los decoradores permanecen intactos.",
        styles=styles,
    )
    story.append(PageBreak())

    # ── SECCIÓN 4 ─────────────────────────────────────────────
    story.append(Paragraph("4. Patrón Strategy — Spawn de enemigos", S["h1"]))
    rule(story)
    story.append(Paragraph(
        "La misma técnica se aplica a la generación de enemigos. "
        "<font name='Courier' size='9'>EnemySpawnStrategy</font> encapsula "
        "<i>cuándo</i> y <i>cuántos</i> enemigos generar, junto con el bono de velocidad. "
        "Game se limita a consultar la estrategia cada frame:",
        S["body"],
    ))
    story.append(CodeBlock([
        "class EnemySpawnStrategy(ABC):",
        "    @abstractmethod",
        "    def tick(self, score: int) -> int:",
        "        ...  # frames que retornan el nº de enemigos a generar",
        "",
        "    @property",
        "    @abstractmethod",
        "    def speed_bonus(self) -> int: ...",
        "",
        "# En Game.maybe_spawn_enemy() — de 8 líneas a 2:",
        "def maybe_spawn_enemy(self):",
        "    count = self._spawn_strategy.tick(self.score)",
        "    for _ in range(count):",
        "        self.enemies.add(Enemy(speed_bonus=self._spawn_strategy.speed_bonus))",
    ]))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Estrategias concretas:", S["h2"]))

    sp_data = [
        [Paragraph("<b>Clase</b>", S["body"]),
         Paragraph("<b>Descripción</b>", S["body"]),
         Paragraph("<b>Dificultad</b>", S["body"])],
        [Paragraph("<font name='Courier' size='8'>LinearSpawnStrategy</font>", S["body"]),
         Paragraph("Comportamiento original. El intervalo entre spawns se reduce linealmente con el score.", S["body"]),
         Paragraph("Gradual", S["body"])],
        [Paragraph("<font name='Courier' size='8'>WaveSpawnStrategy</font>", S["body"]),
         Paragraph("Extensión nueva. 3 s de calma → oleada de 4 enemigos simultáneos → repite.", S["body"]),
         Paragraph("Picos", S["body"])],
    ]
    sp_t = Table(sp_data, colWidths=[4.2*cm, W - 4*cm - 4.2*cm - 2.5*cm, 2.5*cm])
    sp_t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  HexColor("#EDE8FF")),
        ("BACKGROUND",    (0,1),(-1,1),  HexColor("#F8F5FF")),
        ("BACKGROUND",    (0,2),(-1,2),  HexColor("#FFF3E8")),
        ("GRID",          (0,0),(-1,-1), 0.4, HexColor("#CCBBEE")),
        ("FONTSIZE",      (0,0),(-1,-1), 9),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 7),
    ]))
    story.append(sp_t)
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "En <b>main.py</b> o con la tecla <b>S</b> durante el juego se puede cambiar la "
        "estrategia sin reiniciar la partida, demostrando el intercambio en caliente:",
        S["body"],
    ))
    story.append(CodeBlock([
        "# main.py — elegir estrategia al arrancar",
        "Game(spawn_strategy=WaveSpawnStrategy()).run()",
        "",
        "# En Game — cambio en caliente con tecla S",
        "def _toggle_spawn_strategy(self):",
        "    if isinstance(self._spawn_strategy, LinearSpawnStrategy):",
        "        self._spawn_strategy = WaveSpawnStrategy()",
        "    else:",
        "        self._spawn_strategy = LinearSpawnStrategy()",
    ]))
    story.append(PageBreak())

    # ── SECCIÓN 5 ─────────────────────────────────────────────
    story.append(Paragraph("5. Patrón Template Method — Decoradores de aura", S["h1"]))
    rule(story)
    story.append(Paragraph(
        "El patrón <b>Template Method</b> define el esqueleto de un algoritmo en la "
        "clase base y deja que las subclases rellenen los pasos variables mediante "
        "métodos <i>hook</i>. Se aplica a los decoradores de aura a través de "
        "<font name='Courier' size='9'>AuraTemplate</font>, que reemplaza al "
        "<font name='Courier' size='9'>AuraDecorator</font> original.",
        S["body"],
    ))

    story.append(Paragraph("Algoritmo fijo definido en AuraTemplate:", S["h2"]))
    story.append(CodeBlock([
        "class AuraTemplate(EntityComponent):    # Template Method + Decorator base",
        "",
        "    def update(self):                   # ← algoritmo FIJO (no sobreescribir)",
        "        if not self.expired:",
        "            self._apply_behavior_effect()  # hook: velocidad, animación…",
        "            self._entity.update()          # delegación al decorado",
        "            self._update_particles()       # hook: mover partículas",
        "            self.timer += 1",
        "        else:",
        "            self._entity.update()",
        "            self._on_expire()              # hook: limpieza al expirar",
        "",
        "    def draw(self, screen):             # ← algoritmo FIJO",
        "        self._draw_background_fx(screen)   # hook: fx detrás del sprite",
        "        self._entity.draw(screen)          # el sprite siempre en el medio",
        "        if not self.expired:",
        "            self._draw_foreground_fx(screen)  # hook: aura encima",
        "",
        "    # Hooks con implementación vacía (las subclases sobreescriben solo los suyos)",
        "    def _apply_behavior_effect(self): pass",
        "    def _update_particles(self): pass",
        "    def _on_expire(self): pass",
        "    def _draw_background_fx(self, screen): pass",
        "    def _draw_foreground_fx(self, screen): pass",
    ]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Hooks implementados por cada decorador concreto:", S["h2"]))

    hook_data = [
        [
            Paragraph("<b>Clase</b>", S["body"]),
            Paragraph("<b>_apply_behavior_effect</b>", S["body"]),
            Paragraph("<b>_update_particles</b>", S["body"]),
            Paragraph("<b>_on_expire</b>", S["body"]),
            Paragraph("<b>_draw_bg_fx</b>", S["body"]),
            Paragraph("<b>_draw_fg_fx</b>", S["body"]),
        ],
        ["FireDecorator",    "✓", "✓", "✓", "✓", "✓"],
        ["IceDecorator",     "—", "✓", "—", "✓", "✓"],
        ["ThunderDecorator", "✓", "✓", "✓", "—*","✓"],
        ["NatureDecorator",  "—", "✓", "—", "✓", "✓"],
    ]
    hook_rows = [[Paragraph(str(c), S["body"]) if i == 0 else
                  Paragraph(f"<b>{c}</b>" if c == "✓" else c, S["body"])
                  for c in row]
                 for i, row in enumerate(hook_data)]

    hk_t = Table(hook_rows, colWidths=[3.5*cm, 3*cm, 2.8*cm, 2.4*cm, 2.4*cm, 2.4*cm])
    hk_ts = [
        ("BACKGROUND",    (0,0),(-1,0),  HexColor("#EDE8FF")),
        ("GRID",          (0,0),(-1,-1), 0.4, HexColor("#CCBBEE")),
        ("FONTSIZE",      (0,0),(-1,-1), 8.5),
        ("ALIGN",         (1,0),(-1,-1), "CENTER"),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 5),
    ]
    row_bgs = [
        HexColor(f"{C_FIRE.hexval()}15"),
        HexColor(f"{C_ICE.hexval()}15"),
        HexColor(f"{C_THUNDER.hexval()}10"),
        HexColor(f"{C_NATURE.hexval()}15"),
    ]
    for i, bg in enumerate(row_bgs, start=1):
        hk_ts.append(("BACKGROUND", (0,i),(-1,i), bg))
    hk_t.setStyle(TableStyle(hk_ts))
    story.append(hk_t)
    story.append(Paragraph(
        "* ThunderDecorator sobreescribe draw() completo para implementar el parpadeo eléctrico.",
        S["caption"],
    ))

    story.append(Paragraph("Utilidades compartidas en AuraTemplate:", S["h2"]))
    story.append(Paragraph(
        "Se extrajeron dos métodos reutilizables que antes se duplicaban "
        "en varios decoradores:",
        S["body"],
    ))
    story.append(CodeBlock([
        "def _draw_timer_bar(self, screen, color, offset_y=0):",
        "    # Barra de duración bajo el sprite — usada por los 4 decoradores",
        "",
        "def _pulsing_aura(self, screen, color, base_radius, pulse_amplitude=8, ...):",
        "    # Aura circular pulsante — reutilizada por Fire y Nature sin repetición",
    ]))
    story.append(PageBreak())

    # ── SECCIÓN 6 ─────────────────────────────────────────────
    story.append(Paragraph("6. Principios SOLID aplicados", S["h1"]))
    rule(story)

    solid = [
        (
            "S — Single Responsibility Principle",
            C_FIRE,
            "Cada archivo tiene una única razón para cambiar. "
            "movement_strategy.py solo cambia si cambia cómo se mueve el jugador. "
            "spawn_strategy.py solo cambia si cambia la curva de dificultad. "
            "aura_template.py solo cambia si cambia el flujo común de los decoradores.",
        ),
        (
            "O — Open/Closed Principle",
            C_ICE,
            "Añadir un nuevo modo de movimiento, una nueva curva de dificultad o un "
            "nuevo decorador de aura no requiere modificar ninguna clase existente: "
            "se crea una nueva subclase. El código está abierto a la extensión "
            "y cerrado a la modificación.",
        ),
        (
            "L — Liskov Substitution Principle",
            C_THUNDER,
            "Cualquier MovementStrategy puede sustituir a KeyboardMovementStrategy "
            "en Player sin romper su comportamiento. "
            "Cualquier EnemySpawnStrategy puede sustituir a LinearSpawnStrategy en Game. "
            "Todos los decoradores son sustituibles entre sí gracias a AuraTemplate.",
        ),
        (
            "I — Interface Segregation Principle",
            C_ACCENT,
            "Las interfaces son pequeñas y específicas. MovementStrategy expone "
            "solo compute_move y select_animation. EnemySpawnStrategy expone solo "
            "tick y speed_bonus. Ningún implementador está obligado a depender "
            "de métodos que no usa.",
        ),
        (
            "D — Dependency Inversion Principle",
            C_NATURE,
            "Player depende de la abstracción MovementStrategy, no de "
            "KeyboardMovementStrategy. Game depende de EnemySpawnStrategy, no de "
            "LinearSpawnStrategy. Las dependencias concretas se inyectan desde main.py "
            "(composición en el nivel más alto).",
        ),
    ]

    for title, color, desc in solid:
        row = [[
            Paragraph(f"<b>{title}</b>", S["h3"]),
        ]]
        t = Table(row, colWidths=[W - 4*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), HexColor(f"{color.hexval()}18")),
            ("LINEBEFORETRUE",(0,0),(-1,-1), 4, color),
            ("LEFTPADDING",   (0,0),(-1,-1), 10),
            ("TOPPADDING",    (0,0),(-1,-1), 7),
            ("BOTTOMPADDING", (0,0),(-1,-1), 7),
        ]))
        story.append(KeepTogether([t, Paragraph(desc, S["body"]), Spacer(1, 6)]))

    story.append(PageBreak())

    # ── SECCIÓN 7 ─────────────────────────────────────────────
    story.append(Paragraph("7. Estructura final de archivos", S["h1"]))
    rule(story)
    story.append(Paragraph(
        "El proyecto refactorizado añade tres archivos nuevos y modifica tres "
        "existentes. Los archivos enemy.py y powerup.py permanecen sin cambios.",
        S["body"],
    ))

    files = [
        ("setting.py",           "Sin cambios",   C_MUTED,   "Constantes centralizadas del juego"),
        ("base_entity.py",       "Sin cambios",   C_MUTED,   "Interfaz Component del patrón Decorator"),
        ("movement_strategy.py", "NUEVO",         C_NATURE,  "Strategy: KeyboardMovement + DashMovement"),
        ("spawn_strategy.py",    "NUEVO",         C_NATURE,  "Strategy: LinearSpawn + WaveSpawn"),
        ("aura_template.py",     "NUEVO",         C_NATURE,  "Template Method: esqueleto de decoradores"),
        ("decorators.py",        "Refactorizado", C_ACCENT,  "Solo hooks, sin esqueleto repetido"),
        ("player.py",            "Refactorizado", C_ACCENT,  "Inyecta MovementStrategy (DIP)"),
        ("game.py",              "Refactorizado", C_ACCENT,  "Inyecta EnemySpawnStrategy (DIP)"),
        ("enemy.py",             "Sin cambios",   C_MUTED,   "Asteroide prehistórico"),
        ("powerup.py",           "Sin cambios",   C_MUTED,   "Gemas recolectables"),
        ("main.py",              "Actualizado",   C_ICE,     "Composición explícita de estrategias"),
    ]

    file_data = [[
        Paragraph("<b>Archivo</b>", S["body"]),
        Paragraph("<b>Estado</b>", S["body"]),
        Paragraph("<b>Responsabilidad</b>", S["body"]),
    ]]
    for fname, estado, color, desc in files:
        file_data.append([
            Paragraph(f"<font name='Courier' size='8'>{fname}</font>", S["body"]),
            Paragraph(f"<b>{estado}</b>", ParagraphStyle(
                "st", fontSize=8, fontName="Helvetica-Bold",
                textColor=color, leading=12,
            )),
            Paragraph(desc, S["body"]),
        ])

    ft = Table(file_data, colWidths=[4.2*cm, 2.8*cm, W - 4*cm - 4.2*cm - 2.8*cm])
    fts = [
        ("BACKGROUND",    (0,0),(-1,0),  HexColor("#EDE8FF")),
        ("GRID",          (0,0),(-1,-1), 0.4, HexColor("#CCBBEE")),
        ("FONTSIZE",      (0,0),(-1,-1), 9),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 7),
    ]
    for i, (_, estado, color, _) in enumerate(files, start=1):
        if estado == "NUEVO":
            fts.append(("BACKGROUND", (0,i),(-1,i), HexColor(f"{C_NATURE.hexval()}18")))
        elif estado == "Refactorizado":
            fts.append(("BACKGROUND", (0,i),(-1,i), HexColor(f"{C_ACCENT.hexval()}12")))
        elif estado == "Actualizado":
            fts.append(("BACKGROUND", (0,i),(-1,i), HexColor(f"{C_ICE.hexval()}18")))
    ft.setStyle(TableStyle(fts))
    story.append(ft)
    story.append(PageBreak())

    # ── SECCIÓN 8 ─────────────────────────────────────────────
    story.append(Paragraph("8. Guía de extensión rápida", S["h1"]))
    rule(story)
    story.append(Paragraph(
        "Gracias a los patrones aplicados, añadir nuevas funcionalidades "
        "no requiere modificar código existente. Aquí se muestran tres "
        "ejemplos concretos de extensión:",
        S["body"],
    ))

    extensions = [
        (
            "Nuevo modo de movimiento (p.ej. movimiento con inercia)",
            C_FIRE,
            [
                "# 1. Crear subclase en movement_strategy.py",
                "class InertiaMovementStrategy(MovementStrategy):",
                "    def __init__(self):",
                "        self._vx, self._vy = 0.0, 0.0",
                "",
                "    def compute_move(self, rect, speed):",
                "        keys = pygame.key.get_pressed()",
                "        if keys[K_RIGHT]: self._vx += 0.5",
                "        self._vx *= 0.85  # fricción",
                "        return int(self._vx), int(self._vy), ...",
                "",
                "    def select_animation(self, dx, dy, speed): ...",
                "",
                "# 2. Inyectar al arrancar — nadie más cambia",
                "player = Player(x, y, movement_strategy=InertiaMovementStrategy())",
            ],
        ),
        (
            "Nueva curva de dificultad (p.ej. dificultad exponencial)",
            C_ICE,
            [
                "# 1. Crear subclase en spawn_strategy.py",
                "class ExponentialSpawnStrategy(EnemySpawnStrategy):",
                "    def __init__(self):",
                "        self._timer = 0",
                "",
                "    def tick(self, score: int) -> int:",
                "        self._timer += 1",
                "        interval = max(10, int(60 * 0.995 ** (score // 100)))",
                "        if self._timer >= interval:",
                "            self._timer = 0",
                "            return 1",
                "        return 0",
                "",
                "    @property",
                "    def speed_bonus(self) -> int: return 0",
                "",
                "# 2. Pasar a Game — nadie más cambia",
                "Game(spawn_strategy=ExponentialSpawnStrategy()).run()",
            ],
        ),
        (
            "Nuevo decorador de aura (p.ej. aura de veneno)",
            C_NATURE,
            [
                "# 1. Crear subclase de AuraTemplate en decorators.py",
                "class PoisonDecorator(AuraTemplate):",
                "    NAME  = 'Veneno +DoT'",
                "    COLOR = (180, 50, 200)   # morado",
                "",
                "    def _apply_behavior_effect(self):",
                "        pass  # sin efecto de movimiento",
                "",
                "    def _update_particles(self):",
                "        pass  # añadir partículas de veneno",
                "",
                "    def _draw_foreground_fx(self, screen):",
                "        self._pulsing_aura(screen, self.COLOR, PLAYER_SIZE//2+12)",
                "        self._draw_timer_bar(screen, self.COLOR, self._get_bar_offset())",
                "",
                "# 2. Registrar en DECORATOR_MAP de game.py — solo 1 línea",
                "DECORATOR_MAP['poison'] = PoisonDecorator",
            ],
        ),
    ]

    for title, color, code in extensions:
        hdr = [[Paragraph(f"<b>{title}</b>", S["h3"])]]
        ht = Table(hdr, colWidths=[W - 4*cm])
        ht.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), HexColor(f"{color.hexval()}18")),
            ("LINEBEFORETRUE",(0,0),(-1,-1), 4, color),
            ("LEFTPADDING",   (0,0),(-1,-1), 10),
            ("TOPPADDING",    (0,0),(-1,-1), 7),
            ("BOTTOMPADDING", (0,0),(-1,-1), 7),
        ]))
        story.append(ht)
        story.append(CodeBlock(code))
        story.append(Spacer(1, 10))

    # ── CONCLUSIÓN ────────────────────────────────────────────
    story.append(Spacer(1, 10))
    callout(story,
        "<b>Conclusión:</b> La combinación de Decorator (estructura original) + "
        "Strategy (variantes de comportamiento) + Template Method (algoritmo común) "
        "produce una arquitectura donde cada clase tiene una única razón para cambiar, "
        "las extensiones se hacen por adición y no por modificación, y la composición "
        "de estrategias en main.py hace explícitas todas las decisiones de diseño "
        "sin esconderlas en implementaciones concretas.",
        bg=HexColor("#EDE8FF"),
        border=C_ACCENT,
        styles=styles,
    )

    return story


# ── Encabezado/pie de página ───────────────────────────────────
def on_page(canvas, doc):
    canvas.saveState()
    W, H = A4
    # Pie
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(C_MUTED)
    canvas.drawString(2*cm, 1.2*cm, "Dino Aura — Refactorización con Patrones de Diseño")
    canvas.drawRightString(W - 2*cm, 1.2*cm, f"Página {doc.page}")
    # Línea de pie
    canvas.setStrokeColor(C_RULE)
    canvas.setLineWidth(0.5)
    canvas.line(2*cm, 1.6*cm, W - 2*cm, 1.6*cm)
    canvas.restoreState()


# ── Main ───────────────────────────────────────────────────────
styles = build_styles()

out_path = "/mnt/user-data/outputs/dino_aura_refactorizacion.pdf"
doc = SimpleDocTemplate(
    out_path,
    pagesize=A4,
    leftMargin=2*cm, rightMargin=2*cm,
    topMargin=2.2*cm, bottomMargin=2.2*cm,
    title="Dino Aura — Refactorización con Patrones de Diseño",
    author="Arquitecto de Software Senior",
    subject="Strategy + Template Method + Decorator + SOLID",
)

story = build_story(styles)
doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"PDF generado: {out_path}")
