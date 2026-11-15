"""Genera el logo de Dayanna en SVG (texto convertido a trazos) y lo exporta a PNG.

Uso:  python3 generar_logo.py
"""
import subprocess
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

AQUI = Path(__file__).parent
FUENTES = AQUI / "fuentes"
SALIDA = AQUI / "logo"
SALIDA.mkdir(exist_ok=True)

# ---------- Paleta ----------
FRAMBUESA = "#B8336A"   # rosa principal (legible sobre claro)
ROSA = "#E87FA3"        # rosa medio
ROSA_PALO = "#F6C6D5"   # rosa suave
RUBOR = "#FDF1F5"       # fondo
TINTA = "#4A2233"       # texto ciruela
DORADO = "#C9A15B"      # acento


def cargar(nombre, peso=None):
    f = TTFont(FUENTES / nombre)
    if peso is not None and "fvar" in f:
        f = instantiateVariableFont(f, {"wght": peso})
    return f


def texto_a_trazo(font, texto, size, tracking=0.0):
    """Devuelve (path_d, ancho, ascent) del texto en coordenadas SVG (y hacia abajo)."""
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    upm = font["head"].unitsPerEm
    esc = size / upm
    hmtx = font["hmtx"]
    kern = {}
    pen = SVGPathPen(gs)
    x = 0.0
    nombres = [cmap.get(ord(c)) for c in texto]
    for i, g in enumerate(nombres):
        if g is None:
            x += size * 0.3
            continue
        tp = TransformPen(pen, (esc, 0, 0, -esc, x, 0))
        gs[g].draw(tp)
        x += hmtx[g][0] * esc + tracking * size
    ancho = x - tracking * size
    return pen.getCommands(), ancho


def bbox_de_trazo(font, texto, size, tracking=0.0):
    from fontTools.pens.boundsPen import BoundsPen
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    esc = size / font["head"].unitsPerEm
    bp = BoundsPen(gs)
    x = 0.0
    for c in texto:
        g = cmap.get(ord(c))
        if g is None:
            x += size * 0.3
            continue
        gs[g].draw(TransformPen(bp, (esc, 0, 0, -esc, x, 0)))
        x += font["hmtx"][g][0] * esc + tracking * size
    return bp.bounds  # xmin, ymin, xmax, ymax


SCRIPT = cargar("GreatVibes-Regular.ttf")
SERIF = cargar("CormorantGaramond-Variable.ttf", 600)
SERIF_IT = cargar("CormorantGaramond-Italic-Variable.ttf", 500)


def isotipo(cx, cy, s, color=FRAMBUESA, relleno=RUBOR, corazon=FRAMBUESA, hilo=ROSA):
    """Sobre con solapa abierta, corazón-sello y costura de hilo (carta + tejido).
    s = ancho del sobre."""
    w, h = s, s * 0.66
    x0, y0 = cx - w / 2, cy - h / 2
    r = s * 0.06
    sw = s * 0.035
    m = s * 0.075  # margen de la costura
    # corazón centrado en el vértice de la solapa
    hx, hy, hs = cx, y0 + h * 0.56, s * 0.22
    corazon_d = (
        f"M{hx},{hy + hs * 0.42} "
        f"C{hx - hs * 0.95},{hy - hs * 0.15} {hx - hs * 0.55},{hy - hs * 0.78} {hx},{hy - hs * 0.32} "
        f"C{hx + hs * 0.55},{hy - hs * 0.78} {hx + hs * 0.95},{hy - hs * 0.15} {hx},{hy + hs * 0.42}Z"
    )
    return f"""
  <g stroke-linecap="round" stroke-linejoin="round">
    <rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="{r}" fill="{relleno}" stroke="{color}" stroke-width="{sw}"/>
    <rect x="{x0 + m}" y="{y0 + m}" width="{w - 2 * m}" height="{h - 2 * m}" rx="{r * 0.5}" fill="none"
          stroke="{hilo}" stroke-width="{sw * 0.55}" stroke-dasharray="{s * 0.045} {s * 0.035}"/>
    <path d="M{x0 + sw},{y0 + sw * 0.8} L{hx},{hy} L{x0 + w - sw},{y0 + sw * 0.8}" fill="none" stroke="{color}" stroke-width="{sw}"/>
    <path d="{corazon_d}" fill="{corazon}"/>
  </g>"""


def svg(ancho, alto, cuerpo, fondo=None):
    bg = f'<rect width="100%" height="100%" fill="{fondo}"/>' if fondo else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho:.1f} {alto:.1f}" '
            f'width="{ancho:.0f}" height="{alto:.0f}">{bg}{cuerpo}\n</svg>\n')


def nombre(x, y_base, size, color):
    d, _ = texto_a_trazo(SCRIPT, "Dayanna", size)
    return f'<path transform="translate({x:.1f},{y_base:.1f})" d="{d}" fill="{color}"/>'


def lema(cx, y_base, size, color, texto="DETALLES HECHOS A MANO", tracking=0.22):
    d, w = texto_a_trazo(SERIF, texto, size, tracking)
    return f'<path transform="translate({cx - w / 2:.1f},{y_base:.1f})" d="{d}" fill="{color}"/>', w


# ---------- 1. Logo principal (apilado) ----------
def logo_apilado(c_nombre=FRAMBUESA, c_lema=TINTA, c_iso=FRAMBUESA, fondo=None,
                 relleno=RUBOR, corazon=FRAMBUESA, hilo=ROSA, adorno=DORADO):
    W, H = 1000, 760
    size = 230
    bx0, by0, bx1, by1 = bbox_de_trazo(SCRIPT, "Dayanna", size)
    x = W / 2 - (bx0 + bx1) / 2
    yb = 520
    cuerpo = isotipo(W / 2, 200, 230, c_iso, relleno, corazon, hilo)
    cuerpo += nombre(x, yb, size, c_nombre)
    l, lw = lema(W / 2, 650, 38, c_lema)
    cuerpo += l
    # filetes dorados a los lados del lema
    for sgn in (-1, 1):
        x1 = W / 2 + sgn * (lw / 2 + 24)
        x2 = W / 2 + sgn * (lw / 2 + 110)
        cuerpo += f'<line x1="{x1}" y1="637" x2="{x2}" y2="637" stroke="{adorno}" stroke-width="2.5" stroke-linecap="round"/>'
    cuerpo += f'<circle cx="{W/2}" cy="700" r="0"/>'
    return svg(W, H, cuerpo, fondo)


# ---------- 2. Logo horizontal ----------
def logo_horizontal(c_nombre=FRAMBUESA, c_lema=TINTA, fondo=None):
    size = 170
    bx0, by0, bx1, by1 = bbox_de_trazo(SCRIPT, "Dayanna", size)
    iso_w = 200
    pad = 40
    x_txt = pad + iso_w + 50 - bx0
    W = x_txt + bx1 + pad
    H = 340
    cuerpo = isotipo(pad + iso_w / 2, 150, iso_w)
    cuerpo += nombre(x_txt, 175, size, c_nombre)
    d, w = texto_a_trazo(SERIF, "DETALLES HECHOS A MANO", 27, 0.22)
    cx_txt = x_txt + (bx0 + bx1) / 2
    cuerpo += f'<path transform="translate({cx_txt - w / 2:.1f},285)" d="{d}" fill="{c_lema}"/>'
    return svg(W, H, cuerpo, fondo)


# ---------- 3. Sello / monograma (favicon, redes) ----------
def sello(fondo_circ=FRAMBUESA, letra=RUBOR, aro=ROSA_PALO):
    W = H = 600
    c = W / 2
    size = 330
    bx0, by0, bx1, by1 = bbox_de_trazo(SCRIPT, "D", size)
    x = c - (bx0 + bx1) / 2
    y = c - (by0 + by1) / 2
    d, _ = texto_a_trazo(SCRIPT, "D", size)
    # borde ondulado tipo lacre
    import math
    pts = []
    n = 28
    for i in range(n * 4):
        a = 2 * math.pi * i / (n * 4)
        rr = 285 + 9 * math.cos(n * a)
        pts.append(f"{c + rr * math.cos(a):.1f},{c + rr * math.sin(a):.1f}")
    cuerpo = f'<polygon points="{" ".join(pts)}" fill="{fondo_circ}"/>'
    cuerpo += f'<circle cx="{c}" cy="{c}" r="240" fill="none" stroke="{aro}" stroke-width="5" stroke-dasharray="14 11" stroke-linecap="round"/>'
    cuerpo += f'<path transform="translate({x:.1f},{y:.1f})" d="{d}" fill="{letra}"/>'
    # corazón pequeño
    hx, hy, hs = c, c + 185, 30
    cuerpo += (f'<path d="M{hx},{hy + hs * 0.42} C{hx - hs * 0.95},{hy - hs * 0.15} {hx - hs * 0.55},{hy - hs * 0.78} {hx},{hy - hs * 0.32} '
               f'C{hx + hs * 0.55},{hy - hs * 0.78} {hx + hs * 0.95},{hy - hs * 0.15} {hx},{hy + hs * 0.42}Z" fill="{aro}"/>')
    return svg(W, H, cuerpo)


def favicon():
    W = 64
    c = 32
    size = 58
    bx0, by0, bx1, by1 = bbox_de_trazo(SCRIPT, "D", size)
    d, _ = texto_a_trazo(SCRIPT, "D", size)
    cuerpo = f'<circle cx="{c}" cy="{c}" r="31" fill="{FRAMBUESA}"/>'
    cuerpo += f'<path transform="translate({c - (bx0 + bx1) / 2:.1f},{c - (by0 + by1) / 2:.1f})" d="{d}" fill="{RUBOR}"/>'
    return svg(W, W, cuerpo)


variantes = {
    "dayanna-logo-principal": logo_apilado(),
    "dayanna-logo-blanco": logo_apilado(c_nombre="#FFFFFF", c_lema="#FFFFFF", c_iso="#FFFFFF",
                                        relleno="none", corazon="#FFFFFF", hilo=ROSA_PALO, adorno=ROSA_PALO),
    "dayanna-logo-tinta": logo_apilado(c_nombre=TINTA, c_lema=TINTA, c_iso=TINTA, relleno="none",
                                       corazon=TINTA, hilo=TINTA, adorno=TINTA),
    "dayanna-logo-horizontal": logo_horizontal(),
    "dayanna-sello": sello(),
    "dayanna-favicon": favicon(),
}

for nombre_archivo, contenido in variantes.items():
    p = SALIDA / f"{nombre_archivo}.svg"
    p.write_text(contenido, encoding="utf-8")
    escala = "1600x" if "favicon" not in nombre_archivo else "512x512"
    subprocess.run(["magick", "-background", "none", "-density", "300", f"svg:{p}",
                    "-resize", escala, str(p.with_suffix(".png"))], check=True)
    print("ok", p.name)

# versión del logo principal con fondo blanco (lo pide la skill) y vista sobre rosa
subprocess.run(["magick", str(SALIDA / "dayanna-logo-principal.png"), "-background", "white",
                "-flatten", str(SALIDA / "dayanna-logo-principal-fondo-blanco.png")], check=True)
subprocess.run(["magick", str(SALIDA / "dayanna-logo-blanco.png"), "-background", FRAMBUESA,
                "-flatten", str(SALIDA / "dayanna-logo-sobre-frambuesa.png")], check=True)
subprocess.run(["magick", str(SALIDA / "dayanna-favicon.png"), "-define", "icon:auto-resize=48,32,16",
                str(SALIDA / "favicon.ico")], check=True)
print("listo")
