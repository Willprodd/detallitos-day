"""(base) Logo de Hilvana (estilo Line Art de la skill de logos): la palabra "hilvana" sobre un hilván
(puntadas largas) que termina en un corazón de hilo y una aguja. El punto de la i es un corazón.

Uso:  python3 generar_logo_hilvana.py   -> marca/logo/hilvana/*.svg y *.png
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
SALIDA = AQUI / "logo" / "detallitos-day"
SALIDA.mkdir(parents=True, exist_ok=True)

FRAMBUESA = "#B8336A"
CIRUELA = "#3E1F2C"
MARFIL = "#FCF8F4"
SALVIA = "#8FA58A"
ROSA_PALO = "#F6C6D5"

PALABRA = TTFont(FUENTES / "Fraunces-Variable.ttf")
PALABRA = instantiateVariableFont(PALABRA, {"opsz": 144, "wght": 480, "SOFT": 100, "WONK": 0})
LEMA = TTFont(FUENTES / "Fraunces-Italic-Variable.ttf")
LEMA = instantiateVariableFont(LEMA, {"opsz": 24, "wght": 400, "SOFT": 100, "WONK": 0})


def _dibujar(font, texto, size, pen, tracking=0.0, posiciones=None):
    gs, cmap = font.getGlyphSet(), font.getBestCmap()
    esc = size / font["head"].unitsPerEm
    x = 0.0
    for c in texto:
        g = cmap[ord(c)]
        if posiciones is not None:
            posiciones.append((c, x, font["hmtx"][g][0] * esc))
        gs[g].draw(TransformPen(pen, (esc, 0, 0, -esc, x, 0)))
        x += font["hmtx"][g][0] * esc + tracking * size
    return x - tracking * size


def trazo(font, texto, size, tracking=0.0, posiciones=None):
    pen = SVGPathPen(font.getGlyphSet())
    w = _dibujar(font, texto, size, pen, tracking, posiciones)
    return pen.getCommands(), w


def caja(font, texto, size, tracking=0.0):
    bp = BoundsPen(font.getGlyphSet())
    _dibujar(font, texto, size, bp, tracking)
    return bp.bounds


def corazon_d(cx, cy, s):
    """Corazón relleno (para el punto de la i)."""
    return (f"M{cx},{cy + s * 0.42} C{cx - s * 0.95},{cy - s * 0.15} {cx - s * 0.55},{cy - s * 0.78} {cx},{cy - s * 0.32} "
            f"C{cx + s * 0.55},{cy - s * 0.78} {cx + s * 0.95},{cy - s * 0.15} {cx},{cy + s * 0.42}Z")


def corazon_param(cx, cy, s, t):
    x = 16 * math.sin(t) ** 3
    y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
    return cx + x * s / 32, cy + y * s / 32


def hilo(x0, y, x_fin, hs, color, grosor, aguja_color):
    """Hilván punteado de x0 a x_fin, luego un corazón de hilo continuo y la aguja."""
    partes = []
    # puntadas largas del hilván (lo visible de un hilván: tramos largos con huecos cortos)
    partes.append(f'<line x1="{x0:.1f}" y1="{y:.1f}" x2="{x_fin:.1f}" y2="{y:.1f}" stroke="{color}" stroke-width="{grosor}" '
                  f'stroke-linecap="round" stroke-dasharray="{grosor * 6:.1f} {grosor * 3.2:.1f}"/>')
    # corazón: arranca en la punta, que queda sobre la línea
    hx = x_fin + hs * 0.55
    hy = y - hs * 0.42
    pts = [(x_fin, y)]
    tip = corazon_param(hx, hy, hs, math.pi)
    for k in range(1, 9):
        t = k / 8
        pts.append((x_fin + (tip[0] - x_fin) * t, y + (tip[1] - y) * t + math.sin(t * math.pi) * hs * 0.08))
    for k in range(0, 97):
        pts.append(corazon_param(hx, hy, hs, math.pi + 2 * math.pi * k / 96))
    ojo = (hx + hs * 0.95, hy - hs * 0.95)
    for k in range(1, 13):
        t = k / 12
        pts.append((tip[0] + (ojo[0] - tip[0]) * t + math.sin(t * math.pi) * hs * 0.22,
                    tip[1] + (ojo[1] - tip[1]) * t))
    d = "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts)
    partes.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{grosor}" stroke-linecap="round" stroke-linejoin="round"/>')
    # aguja
    ang = math.radians(-58)
    largo = hs * 0.95
    ax, ay = ojo
    bx, by = ax - math.cos(ang) * largo, ay - math.sin(ang) * largo
    nx, ny = -math.sin(ang), math.cos(ang)
    a = grosor * 0.95
    partes.append(f'<path d="M{ax + nx * a:.1f},{ay + ny * a:.1f} L{bx:.1f},{by:.1f} L{ax - nx * a:.1f},{ay - ny * a:.1f} '
                  f'A{a:.1f},{a:.1f} 0 0 0 {ax + nx * a:.1f},{ay + ny * a:.1f}Z" fill="{aguja_color}"/>')
    return "\n".join(partes), hx + hs * 1.05


def palabra_con_corazon(x, y, size, color, color_corazon):
    """'hilvana' con el punto de la i cambiado por un corazón."""
    texto = "hılvana"
    pos = []
    d, w = trazo(PALABRA, texto, size, -0.01, pos)
    _, ix, iw = pos[1]
    # alto de x de la fuente para ubicar el corazón encima de la i
    xh = PALABRA["OS/2"].sxHeight * size / PALABRA["head"].unitsPerEm
    cx = x + ix + iw / 2
    cy = y - xh - size * 0.17
    svg = (f'<path transform="translate({x:.1f},{y:.1f})" d="{d}" fill="{color}"/>'
           f'<path d="{corazon_d(cx, cy, size * 0.15)}" fill="{color_corazon}"/>')
    return svg, w


def svg(w, h, cuerpo, fondo=None):
    bg = f'<rect width="100%" height="100%" fill="{fondo}"/>' if fondo else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}" height="{h:.0f}">'
            f'{bg}{cuerpo}</svg>\n')


def logo_principal(texto=CIRUELA, acento=FRAMBUESA, lema_color=None, aguja=None, con_lema=True):
    size = 200
    x0b, y0b, x1b, y1b = caja(PALABRA, "hılvana", size, -0.01)
    pad = 40
    xw = pad - x0b
    yb = 230
    cuerpo, w = palabra_con_corazon(xw, yb, size, texto, acento)
    linea_y = yb + 34
    hilo_svg, fin = hilo(xw + 6, linea_y, xw + w + 18, 66, acento, 6, aguja or texto)
    cuerpo += hilo_svg
    W = max(fin, xw + w) + pad
    H = linea_y + pad + 10
    if con_lema:
        d, lw = trazo(LEMA, "detallitos hechos a mano por Dayanna", 34)
        cuerpo += f'<path transform="translate({xw + 8:.1f},{linea_y + 66:.1f})" d="{d}" fill="{lema_color or texto}"/>'
        H = linea_y + 96
    return svg(W, H, cuerpo)


def sello(fondo=FRAMBUESA, trazo_c=MARFIL):
    """Isotipo: corazón de hilo con aguja dentro de un círculo de hilván."""
    S = 600
    c = S / 2
    cuerpo = f'<circle cx="{c}" cy="{c}" r="290" fill="{fondo}"/>'
    cuerpo += (f'<circle cx="{c}" cy="{c}" r="248" fill="none" stroke="{trazo_c}" stroke-width="10" '
               f'stroke-linecap="round" stroke-dasharray="58 30" opacity=".85"/>')
    # h en Fraunces como inicial, con el hilo-corazón al lado
    x0, y0, x1, y1 = caja(PALABRA, "h", 300)
    d, _ = trazo(PALABRA, "h", 300)
    hx = c - 70 - (x0 + x1) / 2
    hy = c + 105
    cuerpo += f'<path transform="translate({hx:.1f},{hy:.1f})" d="{d}" fill="{trazo_c}"/>'
    hilo_svg, _ = hilo(c - 175, hy + 4, c + 70, 70, trazo_c, 9, trazo_c)
    cuerpo += hilo_svg.split("\n", 1)[1]  # sin la línea punteada, solo corazón y aguja
    cuerpo += (f'<line x1="{c - 175}" y1="{hy + 4}" x2="{c + 70}" y2="{hy + 4}" stroke="{trazo_c}" stroke-width="9" '
               f'stroke-linecap="round" stroke-dasharray="44 26"/>')
    return svg(S, S, cuerpo)



FIRMA = TTFont(FUENTES / "GreatVibes-Regular.ttf")


def palabra_con_corazones(texto, x, y, size, color, color_corazon):
    """Escribe el texto; cada 'i' lleva un corazón en lugar del punto."""
    t = texto.replace("i", "ı")
    pos = []
    d, w = trazo(PALABRA, t, size, -0.01, pos)
    xh = PALABRA["OS/2"].sxHeight * size / PALABRA["head"].unitsPerEm
    out = f'<path transform="translate({x:.1f},{y:.1f})" d="{d}" fill="{color}"/>'
    for c, px, pw in pos:
        if c == "ı":
            out += f'<path d="{corazon_d(x + px + pw / 2, y - xh - size * 0.16, size * 0.14)}" fill="{color_corazon}"/>'
    return out, w


def logo(texto=CIRUELA, acento=FRAMBUESA, lema_color=None, aguja=None, con_lema=True):
    size = 170
    pad = 40
    x0b, _, _, _ = caja(PALABRA, "detallıtos", size, -0.01)
    xw = pad - x0b
    yb = 300
    cuerpo, w = palabra_con_corazones("detallitos", xw, yb, size, texto, acento)
    # "Day" en firma, montado al final de la palabra
    dsize = 235
    dx0, dy0, dx1, dy1 = caja(FIRMA, "Day", dsize)
    xd = xw + w + 34 - dx0
    dd, _ = trazo(FIRMA, "Day", dsize)
    yd = yb - 48
    cuerpo += f'<path transform="translate({xd:.1f},{yd:.1f})" d="{dd}" fill="{acento}"/>'
    fin_texto = xd + dx1
    linea_y = yb + 58
    hilo_svg, fin = hilo(xw + 6, linea_y, fin_texto + 6, 70, acento, 6, aguja or texto)
    cuerpo += hilo_svg
    W = max(fin, fin_texto) + pad
    H = linea_y + pad + 10
    if con_lema:
        d, lw = trazo(LEMA, "regalos hechos a mano, con amor", 36)
        cuerpo += f'<path transform="translate({xw + 8:.1f},{linea_y + 70:.1f})" d="{d}" fill="{lema_color or texto}"/>'
        H = linea_y + 100
    # el trazo de la "y" baja bajo la línea: dejar espacio
    H = max(H, yb + dy1 + 20)
    return svg(W, H, cuerpo)


def sello_day(fondo=FRAMBUESA, trazo_c=MARFIL):
    S = 600
    c = S / 2
    cuerpo = f'<circle cx="{c}" cy="{c}" r="290" fill="{fondo}"/>'
    cuerpo += (f'<circle cx="{c}" cy="{c}" r="248" fill="none" stroke="{trazo_c}" stroke-width="10" '
               f'stroke-linecap="round" stroke-dasharray="58 30" opacity=".85"/>')
    size = 175
    x0, y0, x1, y1 = caja(FIRMA, "Day", size)
    d, _ = trazo(FIRMA, "Day", size)
    yb = c - 5
    cuerpo += f'<path transform="translate({c - (x0 + x1) / 2:.1f},{yb:.1f})" d="{d}" fill="{trazo_c}"/>'
    hilo_svg, _ = hilo(c - 120, yb + 150, c + 40, 60, trazo_c, 9, trazo_c)
    cuerpo += hilo_svg.split("\n", 1)[1]
    cuerpo += (f'<line x1="{c - 120}" y1="{yb + 150}" x2="{c + 40}" y2="{yb + 150}" stroke="{trazo_c}" stroke-width="9" '
               f'stroke-linecap="round" stroke-dasharray="44 26"/>')
    return svg(S, S, cuerpo)


variantes = {
    "detallitos-day-logo": logo(),
    "detallitos-day-logo-sin-lema": logo(con_lema=False),
    "detallitos-day-logo-blanco": logo(texto=MARFIL, acento=ROSA_PALO, lema_color=MARFIL, aguja=MARFIL),
    "detallitos-day-logo-una-tinta": logo(texto=CIRUELA, acento=CIRUELA),
    "detallitos-day-sello": sello_day(),
    "detallitos-day-sello-salvia": sello_day(fondo=SALVIA),
}
for n, s in variantes.items():
    p = SALIDA / f"{n}.svg"
    p.write_text(s, encoding="utf-8")
    subprocess.run(["magick", "-background", "none", "-density", "300", f"svg:{p}", "-resize", "1600x",
                    str(p.with_suffix(".png"))], check=True)
    print("ok", p.name)
subprocess.run(["magick", "-background", "none", "-density", "300", f"svg:{SALIDA / 'detallitos-day-sello.svg'}",
                "-define", "icon:auto-resize=64,48,32,16", str(SALIDA / "favicon.ico")], check=True)
