"""Logo Dayanna v2: sobre inclinado con sello de lacre, y una aguja cuyo hilo dibuja un corazón.

Uso:  python3 generar_logo_v2.py   (genera marca/logo/v2/*.svg y *.png)
"""
import math
import subprocess
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

AQUI = Path(__file__).parent
FUENTES = AQUI / "fuentes"
SALIDA = AQUI / "logo" / "v2"
SALIDA.mkdir(parents=True, exist_ok=True)

FRAMBUESA = "#B8336A"
ROSA = "#E87FA3"
ROSA_PALO = "#F6C6D5"
RUBOR = "#FDF1F5"
TINTA = "#4A2233"
DORADO = "#C9A15B"


def cargar(nombre, peso=None):
    f = TTFont(FUENTES / nombre)
    if peso is not None and "fvar" in f:
        f = instantiateVariableFont(f, {"wght": peso})
    return f


SCRIPT = cargar("GreatVibes-Regular.ttf")
SERIF = cargar("CormorantGaramond-Variable.ttf", 600)


def _dibujar(font, texto, size, pen, tracking=0.0):
    gs, cmap = font.getGlyphSet(), font.getBestCmap()
    esc = size / font["head"].unitsPerEm
    x = 0.0
    for c in texto:
        g = cmap.get(ord(c))
        if g is None:
            x += size * 0.3
            continue
        gs[g].draw(TransformPen(pen, (esc, 0, 0, -esc, x, 0)))
        x += font["hmtx"][g][0] * esc + tracking * size
    return x - tracking * size


def trazo(font, texto, size, tracking=0.0):
    pen = SVGPathPen(font.getGlyphSet())
    w = _dibujar(font, texto, size, pen, tracking)
    return pen.getCommands(), w


def caja(font, texto, size, tracking=0.0):
    bp = BoundsPen(font.getGlyphSet())
    _dibujar(font, texto, size, bp, tracking)
    return bp.bounds


def corazon_param(cx, cy, s, t):
    x = 16 * math.sin(t) ** 3
    y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
    return cx + x * s / 32, cy + y * s / 32


def sello_lacre(cx, cy, r, color, interior):
    pts = []
    n = 11
    for i in range(n * 8):
        a = 2 * math.pi * i / (n * 8)
        rr = r * (1 + 0.07 * math.sin(n * a) + 0.03 * math.sin(3 * a + 1))
        pts.append(f"{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}")
    hs = r * 0.95
    corazon = " ".join(f"{x:.1f},{y:.1f}" for x, y in
                       (corazon_param(cx, cy + r * 0.05, hs, 2 * math.pi * k / 60) for k in range(60)))
    return (f'<polygon points="{" ".join(pts)}" fill="{color}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r * 0.72:.1f}" fill="none" stroke="{interior}" stroke-opacity=".45" stroke-width="{r * 0.06:.1f}"/>'
            f'<polygon points="{corazon}" fill="{interior}"/>')


def marca(c=FRAMBUESA, relleno=RUBOR, hilo=ROSA, lacre=FRAMBUESA, interior_lacre=RUBOR, aguja=TINTA):
    """Isotipo en una caja de 360 x 250."""
    ex, ey, ew, eh = 30, 78, 210, 140          # sobre
    cx, cy = ex + ew / 2, ey + eh / 2
    vx, vy = cx, ey + eh * 0.58                # vértice de la solapa
    sw = 6
    g = [f'<g transform="rotate(-7 {cx} {cy})" stroke-linejoin="round" stroke-linecap="round">']
    g.append(f'<rect x="{ex}" y="{ey}" width="{ew}" height="{eh}" rx="10" fill="{relleno}" stroke="{c}" stroke-width="{sw}"/>')
    # costura interior
    m = 15
    g.append(f'<rect x="{ex + m}" y="{ey + m}" width="{ew - 2 * m}" height="{eh - 2 * m}" rx="5" fill="none" '
             f'stroke="{hilo}" stroke-width="3.2" stroke-dasharray="9 7"/>')
    # pliegues inferiores
    g.append(f'<path d="M{ex + 6},{ey + eh - 6} L{vx - 18},{vy + 10} M{ex + ew - 6},{ey + eh - 6} L{vx + 18},{vy + 10}" '
             f'stroke="{c}" stroke-width="{sw * 0.55}" fill="none" opacity=".55"/>')
    # solapa curva
    g.append(f'<path d="M{ex + 4},{ey + 5} Q{cx - 50},{vy - 10} {vx},{vy} Q{cx + 50},{vy - 10} {ex + ew - 4},{ey + 5}" '
             f'fill="none" stroke="{c}" stroke-width="{sw}"/>')
    g.append(sello_lacre(vx, vy, 27, lacre, interior_lacre))
    g.append("</g>")

    # hilo: sale de la esquina del sobre, dibuja un corazón y sube hasta la aguja
    hx, hy, hs = 302, 96, 84
    sx, sy = 222, 92                            # salida desde el sobre
    tip = corazon_param(hx, hy, hs, math.pi)   # punta inferior del corazón
    pts = [(sx, sy)]
    for k in range(1, 13):                      # tramo curvo hasta la punta
        t = k / 12
        pts.append((sx + (tip[0] - sx) * t + math.sin(t * math.pi) * 6,
                    sy + (tip[1] - sy) * t + math.sin(t * math.pi) * 16))
    for k in range(0, 91):                      # contorno del corazón (desde la punta)
        t = math.pi + 2 * math.pi * k / 90
        pts.append(corazon_param(hx, hy, hs, t))
    ojo = (352, 4)
    for k in range(1, 13):                      # de la punta hacia la aguja
        t = k / 12
        pts.append((tip[0] + (ojo[0] - tip[0]) * t + math.sin(t * math.pi) * 14,
                    tip[1] + (ojo[1] - tip[1]) * t))
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    g.append(f'<path d="{d}" fill="none" stroke="{hilo}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
    # aguja: cuerpo fino, inclinado, con ojo
    ang = math.radians(-62)
    largo = 74
    ax, ay = ojo
    bx, by = ax - math.cos(ang) * largo, ay - math.sin(ang) * largo
    nx, ny = -math.sin(ang), math.cos(ang)
    a = 3.6
    g.append(f'<path d="M{ax + nx * a:.1f},{ay + ny * a:.1f} L{bx:.1f},{by:.1f} L{ax - nx * a:.1f},{ay - ny * a:.1f} '
             f'A{a},{a} 0 0 0 {ax + nx * a:.1f},{ay + ny * a:.1f}Z" fill="{aguja}"/>')
    ex2, ey2 = ax - math.cos(ang) * 8, ay - math.sin(ang) * 8
    g.append(f'<ellipse cx="{ex2:.1f}" cy="{ey2:.1f}" rx="1.3" ry="4" transform="rotate({math.degrees(ang) + 90:.1f} {ex2:.1f} {ey2:.1f})" fill="{relleno if relleno != "none" else "#fff"}"/>')
    return "\n".join(g)


def svg(w, h, cuerpo, fondo=None):
    bg = f'<rect width="100%" height="100%" fill="{fondo}"/>' if fondo else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}" height="{h:.0f}">'
            f'{bg}{cuerpo}</svg>\n')


def apilado(c_nombre=FRAMBUESA, c_lema=TINTA, adorno=DORADO, **kw):
    W, H = 1000, 820
    size = 240
    x0, y0, x1, y1 = caja(SCRIPT, "Dayanna", size)
    cuerpo = f'<g transform="translate({W / 2 - 195 * 1.3:.1f},18) scale(1.3)">{marca(**kw)}</g>'
    d, _ = trazo(SCRIPT, "Dayanna", size)
    cuerpo += f'<path transform="translate({W / 2 - (x0 + x1) / 2:.1f},570)" d="{d}" fill="{c_nombre}"/>'
    d, w = trazo(SERIF, "DETALLES HECHOS A MANO", 36, 0.24)
    cuerpo += f'<path transform="translate({W / 2 - w / 2:.1f},712)" d="{d}" fill="{c_lema}"/>'
    for sgn in (-1, 1):
        cuerpo += (f'<line x1="{W / 2 + sgn * (w / 2 + 22)}" y1="699" x2="{W / 2 + sgn * (w / 2 + 92)}" y2="699" '
                   f'stroke="{adorno}" stroke-width="2.5" stroke-linecap="round"/>')
    return svg(W, H, cuerpo)


def horizontal(c_nombre=FRAMBUESA, c_lema=TINTA, **kw):
    size = 175
    x0, y0, x1, y1 = caja(SCRIPT, "Dayanna", size)
    esc = 0.78
    xt = 360 * esc + 40 - x0
    W = xt + x1 + 30
    xt += 12; W += 12
    H = 300
    cuerpo = f'<g transform="translate(10,40) scale({esc})">{marca(**kw)}</g>'
    d, _ = trazo(SCRIPT, "Dayanna", size)
    cuerpo += f'<path transform="translate({xt:.1f},185)" d="{d}" fill="{c_nombre}"/>'
    d, w = trazo(SERIF, "DETALLES HECHOS A MANO", 25, 0.24)
    cuerpo += f'<path transform="translate({xt + (x0 + x1) / 2 - w / 2:.1f},282)" d="{d}" fill="{c_lema}"/>'
    return svg(W, H, cuerpo)


def solo_marca(**kw):
    return svg(400, 280, f'<g transform="translate(10,30)">{marca(**kw)}</g>')


def sello_redondo():
    W = 600
    c = W / 2
    pts = []
    for i in range(28 * 4):
        a = 2 * math.pi * i / (28 * 4)
        rr = 285 + 9 * math.cos(28 * a)
        pts.append(f"{c + rr * math.cos(a):.1f},{c + rr * math.sin(a):.1f}")
    cuerpo = f'<polygon points="{" ".join(pts)}" fill="{FRAMBUESA}"/>'
    cuerpo += f'<circle cx="{c}" cy="{c}" r="240" fill="none" stroke="{ROSA_PALO}" stroke-width="5" stroke-dasharray="14 11" stroke-linecap="round"/>'
    cuerpo += f'<g transform="translate({c - 190},{c - 150}) scale(1.08)">{marca(c=RUBOR, relleno="none", hilo=ROSA_PALO, lacre=RUBOR, interior_lacre=FRAMBUESA, aguja=RUBOR)}</g>'
    return svg(W, W, cuerpo)


variantes = {
    "dayanna-logo-principal": apilado(),
    "dayanna-logo-horizontal": horizontal(),
    "dayanna-logo-blanco": apilado(c_nombre="#fff", c_lema="#fff", adorno=ROSA_PALO, c="#fff", relleno="none",
                                   hilo=ROSA_PALO, lacre="#fff", interior_lacre=FRAMBUESA, aguja="#fff"),
    "dayanna-logo-horizontal-blanco": horizontal(c_nombre="#fff", c_lema="#fff", c="#fff", relleno="none",
                                                 hilo=ROSA_PALO, lacre="#fff", interior_lacre=FRAMBUESA, aguja="#fff"),
    "dayanna-marca": solo_marca(),
    "dayanna-sello": sello_redondo(),
}
for n, s in variantes.items():
    p = SALIDA / f"{n}.svg"
    p.write_text(s, encoding="utf-8")
    subprocess.run(["magick", "-background", "none", "-density", "300", f"svg:{p}", "-resize", "1600x",
                    str(p.with_suffix(".png"))], check=True)
    print("ok", p.name)
