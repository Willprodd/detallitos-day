"""Fotos ilustradas (tipo flat-lay) de los productos de ejemplo, hechas con las texturas de la marca.

Uso:  python3 generar_productos.py   -> web/img/productos/*.jpg
"""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

RAIZ = Path(__file__).resolve().parent.parent
TEX = RAIZ / "texturas"
FUENTES = RAIZ / "marca" / "fuentes"
OUT = Path(__file__).parent / "img" / "productos"
OUT.mkdir(parents=True, exist_ok=True)

N = 900
FRAMBUESA = (184, 51, 106)
ROSA = (232, 127, 163)
ROSA_PALO = (246, 198, 213)
RUBOR = (253, 241, 245)
CREMA = (251, 246, 239)
TINTA = (74, 34, 51)
DORADO = (201, 161, 91)
VERDE = (150, 178, 140)
ROJO = (200, 60, 80)
MARFIL = (252, 248, 244)
KRAFT = (226, 205, 180)
SALVIA = (169, 187, 163)
SALVIA_HONDO = (140, 160, 134)


def textura(nombre, w, h, escala=1.0):
    t = Image.open(TEX / nombre).convert("RGB")
    if escala != 1.0:
        t = t.resize((int(t.width * escala), int(t.height * escala)), Image.LANCZOS)
    lienzo = Image.new("RGB", (w, h))
    for x in range(0, w, t.width):
        for y in range(0, h, t.height):
            lienzo.paste(t, (x, y))
    return lienzo


def teñir(img, color, claro=1.15):
    g = ImageOps.grayscale(img)
    g = ImageOps.autocontrast(g, cutoff=2)
    oscuro = tuple(int(c * 0.6) for c in color)
    luz = tuple(min(255, int(c * claro + 25)) for c in color)
    return ImageOps.colorize(g, oscuro, luz)


def papel_color(img, color):
    """Teñido suave: conserva la textura del papel sin exagerar el grano."""
    g = np.asarray(ImageOps.grayscale(img), dtype=float)
    g = 1 + (g - g.mean()) / 255 * 1.6
    arr = np.clip(np.array(color, dtype=float)[None, None, :] * g[..., None], 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def fondo(nombre="lino-avena.png", escala=1.0):
    return textura(nombre, N, N, escala)


def pegar(base, capa, x, y, rot=0, sombra=18):
    """Pega una capa RGBA rotada con una sombra suave debajo."""
    capa = capa.rotate(rot, resample=Image.BICUBIC, expand=True)
    alfa = capa.split()[3]
    som = Image.new("RGBA", capa.size, (60, 20, 35, 0))
    som.putalpha(alfa.point(lambda a: int(a * 0.32)))
    pad = sombra * 3
    s2 = Image.new("RGBA", (capa.width + pad * 2, capa.height + pad * 2), (0, 0, 0, 0))
    s2.paste(som, (pad, pad))
    s2 = s2.filter(ImageFilter.GaussianBlur(sombra))
    base.alpha_composite(s2, (int(x - capa.width / 2 - pad + sombra * 0.5), int(y - capa.height / 2 - pad + sombra * 0.9)))
    base.alpha_composite(capa, (int(x - capa.width / 2), int(y - capa.height / 2)))


def rect(w, h, relleno, radio=6):
    capa = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radio, fill=255)
    capa.paste(relleno.convert("RGBA") if isinstance(relleno, Image.Image) else Image.new("RGBA", (w, h), relleno + (255,)), (0, 0), m)
    return capa


def fuente(nombre, size):
    return ImageFont.truetype(str(FUENTES / nombre), size)


SCRIPT = lambda s: fuente("GreatVibes-Regular.ttf", s)  # noqa: E731
SERIF = lambda s: fuente("CormorantGaramond-Variable.ttf", s)  # noqa: E731


def corazon_pts(cx, cy, s, pasos=80):
    pts = []
    for i in range(pasos):
        t = 2 * math.pi * i / pasos
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((cx + x * s / 32, cy + y * s / 32))
    return pts


def lacre(r, color=FRAMBUESA, simbolo="corazon"):
    S = r * 2 + 10
    capa = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    c = S / 2
    pts = []
    for i in range(120):
        a = 2 * math.pi * i / 120
        rr = r * (1 + 0.07 * math.sin(9 * a) + 0.04 * math.sin(4 * a + 1))
        pts.append((c + rr * math.cos(a), c + rr * math.sin(a)))
    d.polygon(pts, fill=color + (255,))
    d.ellipse([c - r * 0.72, c - r * 0.72, c + r * 0.72, c + r * 0.72], outline=tuple(int(v * 0.8) for v in color) + (255,), width=max(2, r // 12))
    if simbolo == "corazon":
        d.polygon(corazon_pts(c, c + r * 0.04, r * 0.85), fill=tuple(int(v * 0.78) for v in color) + (255,))
    else:
        f = SCRIPT(int(r * 1.2))
        d.text((c, c), simbolo, font=f, anchor="mm", fill=tuple(int(v * 0.75) for v in color) + (255,))
    # brillo
    d.ellipse([c - r * 0.55, c - r * 0.65, c - r * 0.15, c - r * 0.35], fill=(255, 255, 255, 60))
    return capa


def sobre(w, h, color=RUBOR, linea=FRAMBUESA, sello=True, texto=None):
    papel = papel_color(textura("papel-rosa-rubor.png", w, h), color)
    capa = rect(w, h, papel, 8)
    d = ImageDraw.Draw(capa)
    sombra = tuple(int(c * 0.86) for c in color) + (255,)
    d.polygon([(0, h), (w / 2, h * 0.5), (w, h)], fill=tuple(int(c * 0.95) for c in color) + (255,))
    d.line([(4, h - 4), (w / 2, h * 0.5), (w - 4, h - 4)], fill=sombra, width=3)
    d.polygon([(0, 0), (w / 2, h * 0.58), (w, 0)], fill=tuple(int(c * 0.97) for c in color) + (255,))
    d.line([(2, 2), (w / 2, h * 0.58), (w - 2, 2)], fill=sombra, width=4)
    if texto:
        d.text((w * 0.5, h * 0.82), texto, font=SCRIPT(int(h * 0.16)), anchor="mm", fill=linea + (255,))
    if sello:
        l = lacre(int(min(w, h) * 0.15))
        capa.alpha_composite(l, (int(w / 2 - l.width / 2), int(h * 0.58 - l.height / 2)))
    return capa


def carta_escrita(w, h, lineas, titulo=None, papel="papel-carta-crema.png"):
    capa = rect(w, h, textura(papel, w, h), 4)
    d = ImageDraw.Draw(capa)
    y = h * 0.12
    if titulo:
        d.text((w * 0.1, y), titulo, font=SCRIPT(int(h * 0.09)), fill=FRAMBUESA + (255,))
        y += h * 0.14
    f = SCRIPT(int(h * 0.058))
    for ln in lineas:
        d.text((w * 0.1, y), ln, font=f, fill=TINTA + (230,))
        y += h * 0.085
    return capa


def tejido(w, h, color, escala=0.5, radio=10):
    t = teñir(textura("tejido-punto-rosa.png", w, h, escala), color, 1.05)
    return rect(w, h, t, radio)


def forma_tejida(mascara, color, escala=0.35):
    t = teñir(textura("tejido-punto-rosa.png", mascara.width, mascara.height, escala), color, 1.05).convert("RGBA")
    t.putalpha(mascara)
    # relieve suave en el borde
    borde = mascara.filter(ImageFilter.GaussianBlur(6))
    sombra = Image.new("RGBA", t.size, (0, 0, 0, 0))
    sombra.putalpha(Image.eval(ImageOps.invert(borde), lambda v: int(v * 0.35)))
    t.alpha_composite(Image.composite(sombra, Image.new("RGBA", t.size, (0, 0, 0, 0)), mascara))
    return t


def guardar(img, nombre):
    img.convert("RGB").save(OUT / nombre, quality=86, optimize=True)
    print("ok", nombre)


# ---------------------------------------------------------------- productos

def p_abre_cuando():
    base = fondo("papel-salvia.png").convert("RGBA")
    textos = ["…estés triste", "…me extrañes", "…cumplamos un año", "…no puedas dormir", "…necesites reír", "…estemos lejos"]
    pos = [(250, 230, -8), (640, 220, 6), (230, 470, 5), (660, 460, -5), (260, 700, -4), (640, 700, 7)]
    colores = [MARFIL, KRAFT, ROSA_PALO, MARFIL, KRAFT, MARFIL]
    for (x, y, r), t, c in zip(pos, textos, colores):
        s = sobre(330, 210, c, texto="Ábrela cuando" if False else None)
        d = ImageDraw.Draw(s)
        d.text((165, 185), t, font=SCRIPT(30), anchor="mm", fill=FRAMBUESA + (255,))
        pegar(base, s, x, y, r)
    guardar(base, "abre-cuando.jpg")


def p_carta_tejida():
    base = fondo("papel-avena.png").convert("RGBA")
    pegar(base, sobre(520, 340, KRAFT), 560, 640, 12)
    w, h = 470, 600
    carta = tejido(w, h, (243, 214, 222))
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).polygon(corazon_pts(w / 2, h * 0.42, 300), fill=255)
    carta.alpha_composite(forma_tejida(m, FRAMBUESA, 0.3))
    d = ImageDraw.Draw(carta)
    d.text((w / 2, h * 0.84), "te quiero", font=SCRIPT(84), anchor="mm", fill=FRAMBUESA + (255,))
    # costura del borde
    for x in range(20, w - 20, 22):
        d.line([(x, 16), (x + 12, 16)], fill=RUBOR + (255,), width=4)
        d.line([(x, h - 16), (x + 12, h - 16)], fill=RUBOR + (255,), width=4)
    pegar(base, carta, 400, 420, -6)
    guardar(base, "carta-tejida.jpg")


def punto_cruz(d, cx, cy, celda, patron, color):
    filas = len(patron)
    cols = len(patron[0])
    x0, y0 = cx - cols * celda / 2, cy - filas * celda / 2
    k = celda * 0.38
    for i, fila in enumerate(patron):
        for j, v in enumerate(fila):
            if v == "#":
                x, y = x0 + j * celda + celda / 2, y0 + i * celda + celda / 2
                d.line([(x - k, y - k), (x + k, y + k)], fill=color + (255,), width=max(3, int(celda * 0.22)))
                d.line([(x - k, y + k), (x + k, y - k)], fill=color + (255,), width=max(3, int(celda * 0.22)))


CORAZON_PC = [
    ".##...##.",
    "####.####",
    "#########",
    "#########",
    ".#######.",
    "..#####..",
    "...###...",
    "....#....",
]


def p_carta_bordada():
    base = fondo("papel-marfil.png").convert("RGBA")
    # bastidor (aro de bordar)
    S = 640
    aro = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(aro)
    tela = textura("lino-rosa.png", S, S).convert("RGBA")
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).ellipse([20, 20, S - 20, S - 20], fill=255)
    tela = papel_color(tela, CREMA).convert("RGBA")
    aro.paste(tela, (0, 0), m)
    d.ellipse([14, 14, S - 14, S - 14], outline=(214, 170, 120, 255), width=26)
    d.ellipse([22, 22, S - 22, S - 22], outline=(190, 145, 98, 255), width=4)
    d.rectangle([S / 2 - 30, 0, S / 2 + 30, 30], fill=(190, 145, 98, 255))
    punto_cruz(d, S / 2, S * 0.43, 30, CORAZON_PC, FRAMBUESA)
    d.text((S / 2, S * 0.75), "D & S", font=SCRIPT(86), anchor="mm", fill=ROSA + (255,))
    pegar(base, aro, 470, 450, -4, sombra=22)
    # carretes de hilo
    for (x, y, c) in [(150, 760, FRAMBUESA), (790, 160, ROSA)]:
        car = Image.new("RGBA", (130, 130), (0, 0, 0, 0))
        dd = ImageDraw.Draw(car)
        dd.ellipse([5, 5, 125, 125], fill=(214, 170, 120, 255))
        dd.ellipse([18, 18, 112, 112], fill=c + (255,))
        for r in range(24, 50, 7):
            dd.ellipse([65 - r, 65 - r, 65 + r, 65 + r], outline=tuple(int(v * 0.85) for v in c) + (255,), width=2)
        dd.ellipse([55, 55, 75, 75], fill=(214, 170, 120, 255))
        pegar(base, car, x, y, 0, sombra=10)
    guardar(base, "carta-bordada.jpg")


def p_carta_lacre():
    base = fondo("lino-salvia.png").convert("RGBA")
    carta = carta_escrita(470, 620, ["Desde que llegaste,", "los lunes son más", "bonitos y el café", "sabe mejor.", "Gracias por quedarte.", "", "                Tuya, siempre"], titulo="Mi amor:")
    pegar(base, carta, 360, 450, -5)
    pegar(base, sobre(430, 280, MARFIL), 640, 690, 9)
    # ramita seca
    rama = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
    d = ImageDraw.Draw(rama)
    d.line([(40, 260), (250, 40)], fill=(160, 130, 100, 255), width=4)
    for k in range(9):
        t = 0.15 + k * 0.09
        x, y = 40 + 210 * t, 260 - 220 * t
        for sgn in (-1, 1):
            d.ellipse([x + sgn * 18 - 9, y - 6 - 9, x + sgn * 18 + 9, y - 6 + 9], fill=ROSA_PALO + (255,))
    pegar(base, rama, 720, 200, 0, sombra=8)
    guardar(base, "carta-lacre.jpg")


def p_tulipanes():
    base = fondo("papel-avena.png").convert("RGBA")
    capa = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    tallos = [(330, 300, -14, ROSA), (450, 250, 0, FRAMBUESA), (570, 300, 14, ROSA_PALO), (390, 380, -6, ROSA_PALO), (520, 370, 7, ROSA)]
    m_flores = []
    for (x, y, a, c) in tallos:
        bx, by = 450 + (x - 450) * 0.2, 760
        d.line([(x, y + 40), (bx, by)], fill=VERDE + (255,), width=12)
        d.ellipse([(x + bx) / 2 - 40, (y + by) / 2 - 15, (x + bx) / 2 + 10, (y + by) / 2 + 25], fill=(130, 160, 120, 255))
        m = Image.new("L", (N, N), 0)
        md = ImageDraw.Draw(m)
        md.ellipse([x - 55, y - 55, x + 55, y + 60], fill=255)
        md.polygon([(x - 55, y), (x - 40, y - 90), (x - 12, y - 40), (x, y - 100), (x + 12, y - 40), (x + 40, y - 90), (x + 55, y)], fill=255)
        m_flores.append((m.rotate(a, center=(x, y)), c))
    for m, c in m_flores:
        capa.alpha_composite(forma_tejida(m, c, 0.22))
    # lazo
    d2 = ImageDraw.Draw(capa)
    d2.polygon([(450, 700), (370, 660), (380, 740)], fill=FRAMBUESA + (255,))
    d2.polygon([(450, 700), (530, 660), (520, 740)], fill=FRAMBUESA + (255,))
    d2.ellipse([432, 682, 468, 718], fill=(150, 35, 85, 255))
    pegar(base, capa, 450, 450, 0, sombra=12)
    etiqueta = rect(220, 120, textura("papel-carta-crema.png", 220, 120), 6)
    ImageDraw.Draw(etiqueta).text((110, 60), "para ti", font=SCRIPT(54), anchor="mm", fill=FRAMBUESA + (255,))
    pegar(base, etiqueta, 680, 780, -10, sombra=8)
    guardar(base, "tulipanes-tejidos.jpg")


def p_dia_madre():
    base = fondo("patron-flores-dia-madre.png", 0.6).convert("RGBA")
    velo = Image.new("RGBA", (N, N), MARFIL + (175,))
    base.alpha_composite(velo)
    w, h = 520, 660
    carta = rect(w, h, textura("papel-carta-crema.png", w, h), 4)
    d = ImageDraw.Draw(carta)
    # flores bordadas: pétalos de puntadas
    for (cx, cy, c) in [(170, 230, ROSA), (330, 190, FRAMBUESA), (260, 330, ROSA_PALO)]:
        d.line([(cx, cy + 30), (w / 2, 470)], fill=VERDE + (255,), width=5)
        for k in range(6):
            a = k * math.pi / 3
            x2, y2 = cx + math.cos(a) * 52, cy + math.sin(a) * 52
            d.line([(cx + math.cos(a) * 10, cy + math.sin(a) * 10), (x2, y2)], fill=c + (255,), width=14)
        d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=DORADO + (255,))
    d.text((w / 2, 540), "Gracias, mamá", font=SCRIPT(72), anchor="mm", fill=FRAMBUESA + (255,))
    pegar(base, carta, 450, 450, 4)
    guardar(base, "dia-madre-bordada.jpg")


def p_caja_anio():
    base = fondo("papel-marfil.png").convert("RGBA")
    W, H = 640, 520
    caja = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(caja)
    d.rounded_rectangle([0, 60, W, H], 14, fill=SALVIA + (255,))
    d.rounded_rectangle([18, 78, W - 18, H - 18], 10, fill=SALVIA_HONDO + (255,))
    meses = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
    for i, mes in enumerate(meses):
        x = 50 + i * 46
        col = [MARFIL, KRAFT, ROSA_PALO][i % 3]
        s = rect(150, 230, papel_color(textura("papel-rosa-rubor.png", 150, 230), col), 4)
        sd = ImageDraw.Draw(s)
        sd.text((75, 34), mes, font=SERIF(34), anchor="mm", fill=FRAMBUESA + (255,))
        s = s.rotate(90 + (i % 2) * 2 - 1, expand=True)
        caja.alpha_composite(s, (x - 20, 20 + (i % 3) * 6))
    d.rounded_rectangle([0, 230, W, H], 14, fill=SALVIA + (255,))
    etiqueta = rect(300, 110, textura("papel-carta-crema.png", 300, 110), 6)
    ImageDraw.Draw(etiqueta).text((150, 56), "Nuestro año", font=SCRIPT(58), anchor="mm", fill=FRAMBUESA + (255,))
    caja.alpha_composite(etiqueta, (170, 330))
    pegar(base, caja, 450, 480, -3, sombra=24)
    guardar(base, "caja-nuestro-anio.jpg")


def p_llavero():
    base = fondo("lino-avena.png").convert("RGBA")
    carta = carta_escrita(380, 480, ["Para que me", "lleves contigo", "a todas partes."], titulo="Amor:")
    pegar(base, carta, 330, 470, -8)
    S = 400
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).polygon(corazon_pts(S / 2, S * 0.58, 300), fill=255)
    cor = forma_tejida(m, FRAMBUESA, 0.25)
    d = ImageDraw.Draw(cor)
    d.ellipse([S / 2 - 34, 10, S / 2 + 34, 78], outline=(200, 200, 205, 255), width=9)
    d.line([(S / 2, 74), (S / 2, 120)], fill=(200, 200, 205, 255), width=6)
    pegar(base, cor, 640, 420, 12)
    guardar(base, "llavero-corazon.jpg")


def p_navidad():
    base = fondo("patron-navidad-rosa.png", 0.7).convert("RGBA")
    base.alpha_composite(Image.new("RGBA", (N, N), MARFIL + (150,)))
    w, h = 500, 640
    carta = tejido(w, h, (250, 236, 240), 0.45)
    m = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(m)
    for k in range(3):
        top = 110 + k * 95
        half = 90 + k * 45
        md.polygon([(w / 2, top), (w / 2 - half, top + 170), (w / 2 + half, top + 170)], fill=255)
    carta.alpha_composite(forma_tejida(m, (120, 160, 120), 0.3))
    d = ImageDraw.Draw(carta)
    d.rectangle([w / 2 - 22, 470, w / 2 + 22, 510], fill=(160, 120, 90, 255))
    for (x, y) in [(220, 260), (300, 330), (190, 400), (320, 430), (250, 350)]:
        d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=FRAMBUESA + (255,))
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        r = 34 if k % 2 == 0 else 15
        pts.append((w / 2 + math.cos(a) * r, 100 + math.sin(a) * r))
    d.polygon(pts, fill=DORADO + (255,))
    d.text((w / 2, 575), "Feliz Navidad", font=SCRIPT(66), anchor="mm", fill=FRAMBUESA + (255,))
    pegar(base, carta, 450, 450, -4)
    guardar(base, "navidad-tejida.jpg")


def p_cumple():
    base = fondo("lino-salvia.png").convert("RGBA")
    w, h = 600, 420
    tarjeta = rect(w, h, textura("papel-carta-crema.png", w, h), 6)
    d = ImageDraw.Draw(tarjeta)
    # banderines bordados
    for i in range(7):
        x = 60 + i * 80
        c = [ROSA, FRAMBUESA, ROSA_PALO][i % 3]
        d.polygon([(x, 60), (x + 60, 60), (x + 30, 130)], fill=c + (255,))
        for t in range(0, 60, 12):
            d.line([(x + t, 66), (x + t + 6, 66)], fill=RUBOR + (255,), width=3)
    d.line([(40, 58), (w - 40, 58)], fill=TINTA + (255,), width=3)
    d.text((w / 2, 250), "Feliz cumple", font=SCRIPT(98), anchor="mm", fill=FRAMBUESA + (255,))
    d.text((w / 2, 340), "que este año te quiera tanto como yo", font=SCRIPT(34), anchor="mm", fill=TINTA + (255,))
    pegar(base, sobre(520, 340, KRAFT), 480, 640, -8)
    pegar(base, tarjeta, 450, 380, 5)
    guardar(base, "cumple-banderines.jpg")


def p_hero():
    """Imagen de apoyo para redes / vista previa al compartir el enlace (1200x630)."""
    pass


if __name__ == "__main__":
    for f in (p_abre_cuando, p_carta_tejida, p_carta_bordada, p_carta_lacre, p_tulipanes,
              p_dia_madre, p_caja_anio, p_llavero, p_navidad, p_cumple):
        f()
