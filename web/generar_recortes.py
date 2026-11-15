"""Detallitos recortados (PNG con fondo transparente y sombra) para la mesa del hero.

Uso:  python3 generar_recortes.py   -> web/img/hero/*.png
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw

from generar_productos import (CORAZON_PC, DORADO, FRAMBUESA, KRAFT, MARFIL, ROSA, ROSA_PALO, SALVIA,
                               SALVIA_HONDO, SCRIPT, SERIF, TINTA, VERDE, carta_escrita, corazon_pts,
                               forma_tejida, papel_color, pegar, punto_cruz, rect, sobre, textura, teñir)

OUT = Path(__file__).parent / "img" / "hero"
OUT.mkdir(parents=True, exist_ok=True)


def lienzo(n=1000):
    return Image.new("RGBA", (n, n), (0, 0, 0, 0))


def guardar(img, nombre, ancho):
    img = img.crop(img.getbbox())
    alto = round(img.height * ancho / img.width)
    img.resize((ancho, alto), Image.LANCZOS).save(OUT / nombre, optimize=True)
    print("ok", nombre, ancho, alto)


def tulipanes():
    capa = lienzo(900)
    d = ImageDraw.Draw(capa)
    tallos = [(330, 300, -14, ROSA), (450, 250, 0, FRAMBUESA), (570, 300, 14, ROSA_PALO), (390, 380, -6, ROSA_PALO), (520, 370, 7, ROSA)]
    mascaras = []
    for (x, y, a, c) in tallos:
        bx, by = 450 + (x - 450) * 0.2, 760
        d.line([(x, y + 40), (bx, by)], fill=VERDE + (255,), width=12)
        d.ellipse([(x + bx) / 2 - 40, (y + by) / 2 - 15, (x + bx) / 2 + 10, (y + by) / 2 + 25], fill=(130, 160, 120, 255))
        m = Image.new("L", (900, 900), 0)
        md = ImageDraw.Draw(m)
        md.ellipse([x - 55, y - 55, x + 55, y + 60], fill=255)
        md.polygon([(x - 55, y), (x - 40, y - 90), (x - 12, y - 40), (x, y - 100), (x + 12, y - 40), (x + 40, y - 90), (x + 55, y)], fill=255)
        mascaras.append((m.rotate(a, center=(x, y)), c))
    for m, c in mascaras:
        capa.alpha_composite(forma_tejida(m, c, 0.22))
    d2 = ImageDraw.Draw(capa)
    d2.polygon([(450, 700), (370, 660), (380, 740)], fill=FRAMBUESA + (255,))
    d2.polygon([(450, 700), (530, 660), (520, 740)], fill=FRAMBUESA + (255,))
    d2.ellipse([432, 682, 468, 718], fill=(150, 35, 85, 255))
    out = lienzo(1100)
    pegar(out, capa.crop(capa.getbbox()), 550, 550, -18, sombra=14)
    guardar(out, "tulipanes.png", 420)


def llavero():
    S = 420
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).polygon(corazon_pts(S / 2, S * 0.58, 300), fill=255)
    cor = forma_tejida(m, FRAMBUESA, 0.25)
    d = ImageDraw.Draw(cor)
    d.ellipse([S / 2 - 36, 8, S / 2 + 36, 80], outline=(196, 196, 202, 255), width=10)
    d.line([(S / 2, 76), (S / 2, 122)], fill=(196, 196, 202, 255), width=7)
    out = lienzo(700)
    pegar(out, cor.crop(cor.getbbox()), 350, 350, 14, sombra=14)
    guardar(out, "llavero.png", 300)


def aro():
    S = 640
    a = lienzo(S)
    d = ImageDraw.Draw(a)
    tela = papel_color(textura("lino-avena.png", S, S), MARFIL).convert("RGBA")
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).ellipse([20, 20, S - 20, S - 20], fill=255)
    a.paste(tela, (0, 0), m)
    d.ellipse([14, 14, S - 14, S - 14], outline=(214, 170, 120, 255), width=26)
    d.ellipse([22, 22, S - 22, S - 22], outline=(190, 145, 98, 255), width=4)
    d.rectangle([S / 2 - 30, 0, S / 2 + 30, 30], fill=(190, 145, 98, 255))
    punto_cruz(d, S / 2, S * 0.43, 30, CORAZON_PC, FRAMBUESA)
    d.text((S / 2, S * 0.75), "D & S", font=SCRIPT(86), anchor="mm", fill=SALVIA_HONDO + (255,))
    out = lienzo(900)
    pegar(out, a, 450, 450, 8, sombra=18)
    guardar(out, "bastidor.png", 380)


def carta_y_sobre():
    out = lienzo(1100)
    carta = carta_escrita(420, 540, ["Gracias por los", "domingos lentos", "y por reírte de", "mis chistes malos."], titulo="Amor:")
    pegar(out, carta, 470, 440, -7)
    pegar(out, sobre(440, 290, KRAFT), 600, 700, 6)
    guardar(out, "carta.png", 380)


def caja():
    W, H = 640, 520
    c = lienzo(W + 40)
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([0, 60, W, H], 14, fill=SALVIA + (255,))
    d.rounded_rectangle([18, 78, W - 18, H - 18], 10, fill=SALVIA_HONDO + (255,))
    meses = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
    for i, mes in enumerate(meses):
        col = [MARFIL, KRAFT, ROSA_PALO][i % 3]
        s = rect(150, 230, papel_color(textura("papel-rosa-rubor.png", 150, 230), col), 4)
        ImageDraw.Draw(s).text((75, 34), mes, font=SERIF(34), anchor="mm", fill=FRAMBUESA + (255,))
        s = s.rotate(90 + (i % 2) * 2 - 1, expand=True)
        c.alpha_composite(s, (50 + i * 46 - 20, 20 + (i % 3) * 6))
    d.rounded_rectangle([0, 230, W, H], 14, fill=SALVIA + (255,))
    et = rect(300, 110, textura("papel-carta-crema.png", 300, 110), 6)
    ImageDraw.Draw(et).text((150, 56), "Nuestro año", font=SCRIPT(58), anchor="mm", fill=FRAMBUESA + (255,))
    c.alpha_composite(et, (170, 330))
    out = lienzo(1000)
    pegar(out, c.crop(c.getbbox()), 500, 500, -5, sombra=20)
    guardar(out, "caja.png", 400)


def tarjeta_tejida():
    w, h = 420, 520
    t = teñir(textura("tejido-punto-rosa.png", w, h, 0.45), (236, 226, 214), 1.02)
    carta = rect(w, h, t, 10)
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).polygon(corazon_pts(w / 2, h * 0.42, 260), fill=255)
    carta.alpha_composite(forma_tejida(m, FRAMBUESA, 0.3))
    ImageDraw.Draw(carta).text((w / 2, h * 0.85), "te quiero", font=SCRIPT(70), anchor="mm", fill=FRAMBUESA + (255,))
    out = lienzo(800)
    pegar(out, carta, 400, 400, 10, sombra=16)
    guardar(out, "tarjeta-tejida.png", 300)


def carrete(color, nombre):
    S = 160
    c = lienzo(S)
    d = ImageDraw.Draw(c)
    d.ellipse([5, 5, S - 5, S - 5], fill=(214, 170, 120, 255))
    d.ellipse([20, 20, S - 20, S - 20], fill=color + (255,))
    for r in range(28, 62, 8):
        d.ellipse([S / 2 - r, S / 2 - r, S / 2 + r, S / 2 + r], outline=tuple(int(v * 0.85) for v in color) + (255,), width=3)
    d.ellipse([S / 2 - 13, S / 2 - 13, S / 2 + 13, S / 2 + 13], fill=(214, 170, 120, 255))
    out = lienzo(260)
    pegar(out, c, 130, 130, 0, sombra=8)
    guardar(out, nombre, 110)


def ovillo():
    S = 300
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).ellipse([10, 10, S - 10, S - 10], fill=255)
    o = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    o.paste(Image.new("RGBA", (S, S), SALVIA + (255,)), (0, 0), m)
    d = ImageDraw.Draw(o)
    for k in range(-6, 7):
        off = k * 22
        d.arc([10 + off * 0.3, 10 - abs(off) * 0.2, S - 10 + off * 0.3, S - 10 + abs(off) * 0.2], 200, 340,
              fill=SALVIA_HONDO + (255,), width=5)
        d.arc([10 - abs(off) * 0.25, 10 + off * 0.3, S - 10 + abs(off) * 0.25, S - 10 + off * 0.3], 110, 250,
              fill=(190, 205, 184, 255), width=5)
    o.putalpha(Image.composite(o.split()[3], Image.new("L", (S, S), 0), m))
    # agujas de tejer cruzadas
    out = lienzo(520)
    pegar(out, o, 260, 280, 0, sombra=12)
    d2 = ImageDraw.Draw(out)
    for (x1, y1, x2, y2) in [(70, 120, 470, 400), (60, 400, 450, 110)]:
        d2.line([(x1, y1), (x2, y2)], fill=(200, 160, 110, 255), width=12)
        d2.ellipse([x2 - 14, y2 - 14, x2 + 14, y2 + 14], fill=DORADO + (255,))
    guardar(out, "ovillo.png", 240)


if __name__ == "__main__":
    tulipanes(); llavero(); aro(); carta_y_sobre(); caja(); tarjeta_tejida()
    carrete(FRAMBUESA, "carrete-frambuesa.png"); carrete(SALVIA, "carrete-salvia.png"); ovillo()
