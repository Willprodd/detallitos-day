"""Más productos de ejemplo para el catálogo (mismo estilo que generar_productos.py).

Uso:  python3 generar_productos_extra.py   -> web/img/productos/*.jpg
"""
import math
import random

from PIL import Image, ImageDraw

from generar_productos import (CORAZON_PC, DORADO, FRAMBUESA, KRAFT, MARFIL, N, ROSA, ROSA_PALO, SALVIA,
                               SALVIA_HONDO, SCRIPT, SERIF, TINTA, VERDE, carta_escrita, corazon_pts, fondo,
                               forma_tejida, guardar, papel_color, pegar, punto_cruz, rect, sobre, textura, teñir)

rnd = random.Random(8)
VIDRIO = (235, 242, 240)


def lienzo(w, h=None):
    return Image.new("RGBA", (w, h or w), (0, 0, 0, 0))


def etiqueta(texto, w=240, h=100, size=50):
    e = rect(w, h, textura("papel-carta-crema.png", w, h), 6)
    ImageDraw.Draw(e).text((w / 2, h / 2 + 2), texto, font=SCRIPT(size), anchor="mm", fill=FRAMBUESA + (255,))
    return e


def p_frasco():
    base = fondo("papel-avena.png").convert("RGBA")
    W, H = 420, 560
    f = lienzo(W, H)
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).rounded_rectangle([20, 110, W - 20, H - 10], 60, fill=255)
    rollos = lienzo(W, H)
    rd = ImageDraw.Draw(rollos)
    for _ in range(170):
        x, y = rnd.uniform(30, W - 30), rnd.uniform(150, H - 30)
        c = rnd.choice([MARFIL, KRAFT, ROSA_PALO, (220, 232, 214)])
        largo, a = rnd.uniform(46, 70), rnd.uniform(0, math.pi)
        dx, dy = math.cos(a) * largo / 2, math.sin(a) * largo / 2
        rd.line([(x - dx, y - dy), (x + dx, y + dy)], fill=tuple(int(v * 0.85) for v in c) + (255,), width=17)
        rd.line([(x - dx, y - dy), (x + dx, y + dy)], fill=c + (255,), width=13)
    f.paste(rollos, (0, 0), m)
    d = ImageDraw.Draw(f)
    d.rounded_rectangle([20, 110, W - 20, H - 10], 60, outline=(200, 214, 210, 255), width=6)
    d.rounded_rectangle([40, 130, 70, H - 60], 14, fill=(255, 255, 255, 90))
    d.rounded_rectangle([50, 50, W - 50, 120], 14, fill=DORADO + (255,))
    d.ellipse([20, 10, W - 20, 90], fill=ROSA_PALO + (255,))
    for x in range(40, W - 40, 26):
        d.line([(x, 52), (x + 13, 52)], fill=FRAMBUESA + (255,), width=4)
    d.rectangle([60, 92, W - 60, 110], fill=FRAMBUESA + (255,))
    pegar(base, f, 430, 470, 0)
    pegar(base, etiqueta("365 razones", 290, 100, 54), 610, 770, -8, sombra=8)
    guardar(base, "frasco-365.jpg")


def pulsera(color):
    S = 340
    p = lienzo(S)
    d = ImageDraw.Draw(p)
    c, r = S / 2, 130
    for k in range(64):
        a = 2 * math.pi * k / 64
        x, y = c + math.cos(a) * r, c + math.sin(a) * r * 0.62
        col = color if k % 2 == 0 else MARFIL
        d.ellipse([x - 13, y - 9, x + 13, y + 9], fill=tuple(int(v * 0.82) for v in col) + (255,))
        d.ellipse([x - 11, y - 8, x + 9, y + 6], fill=col + (255,))
    d.polygon(corazon_pts(c, c + r * 0.62 + 26, 46), fill=DORADO + (255,))
    return p


def p_pulseras():
    base = fondo("lino-salvia.png").convert("RGBA")
    tarjeta = rect(560, 380, textura("papel-carta-crema.png", 560, 380), 6)
    ImageDraw.Draw(tarjeta).text((280, 330), "tú y yo", font=SCRIPT(64), anchor="mm", fill=FRAMBUESA + (255,))
    pegar(base, tarjeta, 450, 480, -4)
    pegar(base, pulsera(FRAMBUESA), 340, 400, -12, sombra=10)
    pegar(base, pulsera(SALVIA_HONDO), 570, 420, 10, sombra=10)
    guardar(base, "pulseras-pareja.jpg")


def p_marcapaginas():
    base = fondo("papel-marfil.png").convert("RGBA")
    libro = lienzo(720, 480)
    d = ImageDraw.Draw(libro)
    for lado in (0, 1):
        x0 = 10 + lado * 350
        pag = rect(340, 460, textura("papel-carta-crema.png", 340, 460), 4)
        pd = ImageDraw.Draw(pag)
        for y in range(60, 420, 26):
            pd.line([(40, y), (300 - (y * 7) % 60, y)], fill=(200, 188, 178, 255), width=4)
        libro.alpha_composite(pag, (x0, 10))
    d.line([(360, 14), (360, 470)], fill=(210, 196, 184, 255), width=4)
    pegar(base, libro, 450, 430, -3)
    w, h = 130, 520
    mp = rect(w, h, textura("papel-carta-crema.png", w, h), 4)
    md = ImageDraw.Draw(mp)
    md.rounded_rectangle([6, 6, w - 7, h - 7], 4, outline=SALVIA + (255,), width=4)
    for i, cy in enumerate((110, 250, 390)):
        punto_cruz(md, w / 2, cy, 11, CORAZON_PC, [FRAMBUESA, ROSA, SALVIA_HONDO][i])
    md.ellipse([w / 2 - 9, 18, w / 2 + 9, 36], fill=(200, 188, 178, 255))
    capa = lienzo(260, 760)
    capa.alpha_composite(mp, (65, 20))
    cd = ImageDraw.Draw(capa)
    for k in range(-5, 6):
        cd.line([(130, 30), (130 + k * 7, 0 - 0)], fill=FRAMBUESA + (255,), width=3)
    cd.line([(130, 30), (130, 8)], fill=FRAMBUESA + (255,), width=6)
    pegar(base, capa, 600, 520, 14, sombra=12)
    guardar(base, "marcapaginas-bordado.jpg")


def p_album():
    base = fondo("lino-avena.png").convert("RGBA")
    W, H = 560, 640
    tapa = rect(W, H, teñir(textura("lino-salvia.png", W, H), (178, 196, 172), 1.0), 14)
    d = ImageDraw.Draw(tapa)
    d.rectangle([0, 0, 50, H], fill=SALVIA_HONDO + (255,))
    foto = lienzo(280, 300)
    fd = ImageDraw.Draw(foto)
    fd.rectangle([0, 0, 280, 300], fill=MARFIL + (255,))
    fd.rectangle([18, 18, 262, 230], fill=(226, 205, 180, 255))
    fd.ellipse([70, 70, 130, 130], fill=(200, 170, 140, 255))
    fd.ellipse([150, 70, 210, 130], fill=(190, 160, 130, 255))
    fd.polygon(corazon_pts(140, 175, 60), fill=FRAMBUESA + (255,))
    fd.text((140, 266), "nosotros", font=SCRIPT(40), anchor="mm", fill=TINTA + (255,))
    tapa.alpha_composite(foto.rotate(-4, expand=True, resample=Image.BICUBIC), (150, 90))
    e = etiqueta("Nuestra historia", 340, 96, 50)
    tapa.alpha_composite(e, (150, 480))
    pegar(base, tapa, 450, 450, 5, sombra=20)
    cinta = lienzo(90, 300)
    ImageDraw.Draw(cinta).polygon([(20, 0), (70, 0), (70, 300), (45, 270), (20, 300)], fill=FRAMBUESA + (255,))
    pegar(base, cinta, 690, 770, 8, sombra=6)
    guardar(base, "album-historia.jpg")


def p_taza():
    base = fondo("papel-salvia.png").convert("RGBA")
    W, H = 520, 560
    t = lienzo(W, H)
    d = ImageDraw.Draw(t)
    d.ellipse([340, 170, 500, 400], outline=MARFIL + (255,), width=34)
    d.rounded_rectangle([40, 80, 400, 520], 40, fill=MARFIL + (255,))
    d.ellipse([40, 50, 400, 120], fill=(240, 234, 228, 255))
    d.ellipse([62, 62, 378, 112], fill=(120, 80, 60, 255))
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).rectangle([40, 230, 400, 430], fill=255)
    t.alpha_composite(forma_tejida(m, FRAMBUESA, 0.28))
    d.ellipse([195, 300, 245, 350], fill=MARFIL + (255,))
    d.ellipse([207, 312, 214, 319], fill=(200, 190, 180, 255))
    d.ellipse([226, 312, 233, 319], fill=(200, 190, 180, 255))
    pegar(base, t, 430, 470, 0, sombra=18)
    pegar(base, etiqueta("buenos días, amor", 340, 90, 42), 640, 800, -6, sombra=8)
    guardar(base, "taza-funda.jpg")


def rosa_tejida():
    S = 300
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).ellipse([20, 20, S - 20, S - 20], fill=255)
    r = forma_tejida(m, FRAMBUESA, 0.2)
    d = ImageDraw.Draw(r)
    c = S / 2
    for k in range(9):
        rr = 18 + k * 13
        ini = (k * 70) % 360
        d.arc([c - rr, c - rr, c + rr, c + rr], ini, ini + 250, fill=(140, 30, 80, 255), width=6)
    return r


def p_rosa():
    base = fondo("papel-marfil.png").convert("RGBA")
    capa = lienzo(700, 900)
    d = ImageDraw.Draw(capa)
    d.line([(350, 300), (330, 860)], fill=VERDE + (255,), width=16)
    for (x, y, a) in [(340, 520, -1), (336, 660, 1)]:
        m = Image.new("L", (700, 900), 0)
        ImageDraw.Draw(m).ellipse([x + (a * 100 if a > 0 else -120), y - 30, x + (a * 100 if a > 0 else -120) + 120, y + 30], fill=255)
        capa.alpha_composite(forma_tejida(m, (130, 160, 120), 0.2))
    capa.alpha_composite(rosa_tejida(), (200, 120))
    pegar(base, capa, 430, 450, -12, sombra=14)
    pegar(base, etiqueta("no se marchita", 300, 90, 46), 670, 760, 8, sombra=8)
    guardar(base, "rosa-tejida.jpg")


def p_adviento():
    base = fondo("lino-avena.png").convert("RGBA")
    W, H = 760, 620
    tabla = rect(W, H, papel_color(textura("papel-salvia.png", W, H), (214, 226, 208)), 10)
    for i in range(24):
        fila, col = divmod(i, 6)
        c = [MARFIL, KRAFT, ROSA_PALO][(fila + col) % 3]
        s = sobre(108, 72, c, sello=False)
        ImageDraw.Draw(s).text((54, 54), str(i + 1), font=SERIF(28), anchor="mm", fill=FRAMBUESA + (255,))
        s = s.rotate(rnd.uniform(-4, 4), expand=True, resample=Image.BICUBIC)
        tabla.alpha_composite(s, (int(30 + col * 120), int(110 + fila * 122)))
    ImageDraw.Draw(tabla).text((W / 2, 62), "Cuenta regresiva", font=SCRIPT(60), anchor="mm", fill=FRAMBUESA + (255,))
    pegar(base, tabla, 450, 450, -3, sombra=20)
    guardar(base, "adviento-cartas.jpg")


def osito(color, rot):
    W, H = 300, 380
    m = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(m)
    md.ellipse([60, 170, 240, 370], fill=255)
    md.ellipse([55, 20, 245, 200], fill=255)
    md.ellipse([50, 10, 110, 70], fill=255)
    md.ellipse([190, 10, 250, 70], fill=255)
    md.ellipse([30, 220, 90, 290], fill=255)
    md.ellipse([210, 220, 270, 290], fill=255)
    o = forma_tejida(m, color, 0.18)
    d = ImageDraw.Draw(o)
    d.ellipse([115, 95, 130, 110], fill=TINTA + (255,))
    d.ellipse([170, 95, 185, 110], fill=TINTA + (255,))
    d.ellipse([125, 120, 175, 160], fill=MARFIL + (255,))
    d.ellipse([142, 126, 158, 138], fill=TINTA + (255,))
    d.ellipse([92, 130, 112, 145], fill=ROSA + (160,))
    d.ellipse([188, 130, 208, 145], fill=ROSA + (160,))
    return o.rotate(rot, expand=True, resample=Image.BICUBIC)


def p_amigurumis():
    base = fondo("papel-rosa-rubor.png").convert("RGBA")
    base.alpha_composite(Image.new("RGBA", (N, N), MARFIL + (170,)))
    pegar(base, osito((214, 190, 160), 6), 330, 470, 0, sombra=14)
    pegar(base, osito(ROSA_PALO, -6), 570, 470, 0, sombra=14)
    m = Image.new("L", (200, 200), 0)
    ImageDraw.Draw(m).polygon(corazon_pts(100, 110, 170), fill=255)
    pegar(base, forma_tejida(m, FRAMBUESA, 0.2), 450, 560, 0, sombra=8)
    pegar(base, etiqueta("juntitos", 230, 90, 50), 450, 800, -3, sombra=8)
    guardar(base, "amigurumis-pareja.jpg")


if __name__ == "__main__":
    for f in (p_frasco, p_pulseras, p_marcapaginas, p_album, p_taza, p_rosa, p_adviento, p_amigurumis):
        f()
