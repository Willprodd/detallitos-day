"""Texturas para la web de Dayanna. Casi todas son "seamless" (se repiten sin cortes).

Uso:  python3 generar_texturas.py
"""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = Path(__file__).parent
rng = np.random.default_rng(14)

FRAMBUESA = (184, 51, 106)
ROSA = (232, 127, 163)
ROSA_PALO = (246, 198, 213)
RUBOR = (253, 241, 245)
CREMA = (251, 246, 239)
DORADO = (201, 161, 91)


def ruido_periodico(n, escala, semilla=None):
    """Ruido suave que se repite sin costuras (filtrado en frecuencia)."""
    r = np.random.default_rng(semilla).standard_normal((n, n))
    f = np.fft.fft2(r)
    fy = np.fft.fftfreq(n)[:, None]
    fx = np.fft.fftfreq(n)[None, :]
    filtro = np.exp(-((fx ** 2 + fy ** 2) * (escala ** 2)))
    out = np.real(np.fft.ifft2(f * filtro))
    out -= out.min()
    return out / out.max()


def fibras(n, cantidad, semilla):
    """Fibras finas de papel, dibujadas con envoltura para que el tile no se corte."""
    img = Image.new("L", (n, n), 0)
    d = ImageDraw.Draw(img)
    r = np.random.default_rng(semilla)
    for _ in range(cantidad):
        x, y = r.uniform(0, n, 2)
        ang = r.uniform(0, math.pi)
        largo = r.uniform(8, 40)
        val = int(r.uniform(20, 70))
        x2, y2 = x + math.cos(ang) * largo, y + math.sin(ang) * largo
        for dx in (-n, 0, n):
            for dy in (-n, 0, n):
                d.line([(x + dx, y + dy), (x2 + dx, y2 + dy)], fill=val, width=1)
    return np.asarray(img.filter(ImageFilter.GaussianBlur(0.6)), dtype=float) / 255


def papel(color, nombre, n=1024, semilla=1):
    base = np.array(color, dtype=float)
    grano = rng.standard_normal((n, n)) * 0.018
    nubes = (ruido_periodico(n, 60, semilla) - 0.5) * 0.06
    fib = fibras(n, 2200, semilla) * 0.08
    luz = 1 + grano + nubes - fib
    img = np.clip(base[None, None, :] * luz[..., None], 0, 255).astype(np.uint8)
    Image.fromarray(img).save(OUT / nombre, optimize=True)
    print("ok", nombre)


def corazon_pts(cx, cy, s, rot=0.0, pasos=60):
    pts = []
    for i in range(pasos):
        t = 2 * math.pi * i / pasos
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        x, y = x * s / 32, y * s / 32
        xr = x * math.cos(rot) - y * math.sin(rot)
        yr = x * math.sin(rot) + y * math.cos(rot)
        pts.append((cx + xr, cy + yr))
    return pts


def envolver(dibujar, n, x, y, margen):
    """Dibuja también las copias en los bordes para que el patrón sea continuo."""
    for dx in (-n, 0, n):
        for dy in (-n, 0, n):
            if -margen < x + dx < n + margen and -margen < y + dy < n + margen:
                dibujar(x + dx, y + dy)


def tejido_punto(nombre="tejido-punto-rosa.png", n=1024, cols=16, filas=22):
    """Punto jersey: columnas de 'V' como un tejido a dos agujas."""
    S = 2
    N = n * S
    img = Image.new("RGB", (N, N), tuple(int(c * 0.62) for c in ROSA_PALO))
    d = ImageDraw.Draw(img)
    cw, ch = N / cols, N / filas
    r = np.random.default_rng(7)
    for fila in range(-1, filas + 1):
        for col in range(cols):
            cx = col * cw + cw / 2
            cy = fila * ch
            for lado in (-1, 1):
                tono = r.uniform(0.94, 1.04)
                base = tuple(int(min(255, c * tono)) for c in ROSA_PALO)
                sombra = tuple(int(c * 0.78) for c in ROSA_PALO)
                luz = tuple(int(min(255, c * 1.06)) for c in RUBOR)
                # cada media V es una elipse inclinada
                w, h = cw * 0.52, ch * 1.55
                ang = lado * 32
                hoja = Image.new("RGBA", (int(w * 2.4), int(h * 1.6)), (0, 0, 0, 0))
                hd = ImageDraw.Draw(hoja)
                ox, oy = hoja.width / 2, hoja.height / 2
                hd.ellipse([ox - w / 2, oy - h / 2, ox + w / 2, oy + h / 2], fill=sombra)
                hd.ellipse([ox - w / 2 + 2, oy - h / 2 + 1, ox + w / 2 - 3, oy + h / 2 - 5], fill=base)
                hd.ellipse([ox - w / 4, oy - h / 2.8, ox + w / 8, oy + h / 8], fill=tuple(int(min(255, c * 1.03)) for c in ROSA_PALO))
                hoja = hoja.rotate(ang, resample=Image.BICUBIC, expand=False)
                px = cx + lado * cw * 0.23 - hoja.width / 2
                py = cy + ch * 0.55 - hoja.height / 2
                for dy in (-N, 0, N):
                    img.paste(hoja, (int(px), int(py + dy)), hoja)
    img = img.resize((n, n), Image.LANCZOS)
    # pelusa de lana
    arr = np.asarray(img, dtype=float)
    arr *= (1 + rng.standard_normal((n, n, 1)) * 0.025)
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).save(OUT / nombre, optimize=True)
    print("ok", nombre)


def lino(nombre="lino-rosa.png", n=1024, color=None):
    y = np.arange(n)[:, None]
    x = np.arange(n)[None, :]
    hilos_h = 0.5 + 0.5 * np.sin(2 * np.pi * y / 6 + ruido_periodico(n, 30, 3) * 4)
    hilos_v = 0.5 + 0.5 * np.sin(2 * np.pi * x / 6 + ruido_periodico(n, 30, 4) * 4)
    irregular_h = ruido_periodico(n, 3, 5)[:, :1] * np.ones((1, n))
    irregular_v = ruido_periodico(n, 3, 6)[:1, :] * np.ones((n, 1))
    trama = 0.5 * hilos_h * (0.8 + 0.4 * irregular_h) + 0.5 * hilos_v * (0.8 + 0.4 * irregular_v)
    luz = 0.93 + 0.1 * trama + rng.standard_normal((n, n)) * 0.015
    base = np.array(color, dtype=float) if color else np.array(ROSA_PALO, dtype=float) * 0.55 + np.array(RUBOR, dtype=float) * 0.45
    img = np.clip(base[None, None, :] * luz[..., None], 0, 255).astype(np.uint8)
    Image.fromarray(img).save(OUT / nombre, optimize=True)
    print("ok", nombre)


def patron_corazones(nombre="patron-corazones.png", n=800, fondo=RUBOR, color=ROSA, cantidad=46, relleno_cada=4):
    S = 2
    N = n * S
    img = Image.new("RGBA", (N, N), fondo + (255,) if fondo else (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = np.random.default_rng(21)
    puestos = []
    while len(puestos) < cantidad:
        x, y = r.uniform(0, N, 2)
        s = r.uniform(34, 70) * S
        ok = all(min(abs(x - px), N - abs(x - px)) ** 2 + min(abs(y - py), N - abs(y - py)) ** 2 > ((s + ps) * 0.9) ** 2
                 for px, py, ps in puestos)
        if ok:
            puestos.append((x, y, s))
    for i, (x, y, s) in enumerate(puestos):
        rot = r.uniform(-0.45, 0.45)
        def dib(xx, yy):
            pts = corazon_pts(xx, yy, s, rot)
            if i % relleno_cada == 0:
                d.polygon(pts, fill=color + (255,))
            else:
                d.line(pts + [pts[0]], fill=color + (255,), width=3 * S, joint="curve")
        envolver(dib, N, x, y, s)
    img.resize((n, n), Image.LANCZOS).save(OUT / nombre, optimize=True)
    print("ok", nombre)


def bordado(nombre="patron-bordado-puntadas.png", n=600):
    """Puntadas de hilo en cruz y línea discontinua, como las cartas bordadas."""
    S = 2
    N = n * S
    img = Image.new("RGBA", (N, N), CREMA + (255,))
    d = ImageDraw.Draw(img)
    paso = N / 10
    for fi in range(10):
        for co in range(10):
            cx, cy = co * paso + paso / 2, fi * paso + paso / 2
            if (fi + co) % 2 == 0:
                k = paso * 0.12
                col = ROSA if (fi // 2 + co // 2) % 2 == 0 else FRAMBUESA
                d.line([(cx - k, cy - k), (cx + k, cy + k)], fill=col, width=5 * S // 2 + 1)
                d.line([(cx - k, cy + k), (cx + k, cy - k)], fill=col, width=5 * S // 2 + 1)
    # líneas de costura onduladas
    for fi in range(5):
        y0 = fi * N / 5 + N / 10 + paso / 2
        pts = [(x, y0 + math.sin(2 * math.pi * x / N * 2) * paso * 0.18) for x in range(0, N + 1, 4)]
        for i in range(0, len(pts) - 6, 10):
            d.line(pts[i:i + 6], fill=ROSA_PALO, width=4 * S)
    img.resize((n, n), Image.LANCZOS).save(OUT / nombre, optimize=True)
    print("ok", nombre)


def flores(nombre="patron-flores-dia-madre.png", n=800):
    S = 2
    N = n * S
    img = Image.new("RGBA", (N, N), RUBOR + (255,))
    d = ImageDraw.Draw(img)
    r = np.random.default_rng(5)
    rejilla = 5
    for fi in range(rejilla):
        for co in range(rejilla):
            x = (co + 0.5 + (0.5 if fi % 2 else 0)) * N / rejilla + r.uniform(-30, 30)
            y = (fi + 0.5) * N / rejilla + r.uniform(-30, 30)
            x %= N
            tam = r.uniform(42, 62) * S / 2
            col = [ROSA, ROSA_PALO, FRAMBUESA][(fi + co) % 3]
            giro = r.uniform(0, math.pi)
            def dib(xx, yy, tam=tam, col=col, giro=giro):
                # hojitas
                for a in (giro + 2.2, giro + 4.1):
                    hx, hy = xx + math.cos(a) * tam * 1.5, yy + math.sin(a) * tam * 1.5
                    d.ellipse([hx - tam * 0.35, hy - tam * 0.35, hx + tam * 0.35, hy + tam * 0.35], fill=(170, 190, 160, 255))
                for k in range(5):
                    a = giro + k * 2 * math.pi / 5
                    px, py = xx + math.cos(a) * tam * 0.7, yy + math.sin(a) * tam * 0.7
                    d.ellipse([px - tam * 0.55, py - tam * 0.55, px + tam * 0.55, py + tam * 0.55], fill=col + (255,))
                d.ellipse([xx - tam * 0.3, yy - tam * 0.3, xx + tam * 0.3, yy + tam * 0.3], fill=DORADO + (255,))
            envolver(dib, N, x, y, tam * 3)
    # puntitos
    for _ in range(90):
        x, y = r.uniform(0, N, 2)
        envolver(lambda xx, yy: d.ellipse([xx - 5, yy - 5, xx + 5, yy + 5], fill=ROSA_PALO + (255,)), N, x, y, 10)
    img.resize((n, n), Image.LANCZOS).save(OUT / nombre, optimize=True)
    print("ok", nombre)


def navidad(nombre="patron-navidad-rosa.png", n=800):
    S = 2
    N = n * S
    img = Image.new("RGBA", (N, N), (250, 232, 238, 255))
    d = ImageDraw.Draw(img)
    r = np.random.default_rng(12)
    def copo(xx, yy, s, col):
        for k in range(6):
            a = k * math.pi / 3
            ex, ey = xx + math.cos(a) * s, yy + math.sin(a) * s
            d.line([(xx, yy), (ex, ey)], fill=col, width=4)
            for t in (0.55,):
                mx, my = xx + math.cos(a) * s * t, yy + math.sin(a) * s * t
                for b in (a + 0.7, a - 0.7):
                    d.line([(mx, my), (mx + math.cos(b) * s * 0.3, my + math.sin(b) * s * 0.3)], fill=col, width=4)
    def estrella(xx, yy, s, col):
        pts = []
        for k in range(10):
            a = -math.pi / 2 + k * math.pi / 5
            rr = s if k % 2 == 0 else s * 0.45
            pts.append((xx + math.cos(a) * rr, yy + math.sin(a) * rr))
        d.polygon(pts, fill=col)
    puestos = []
    while len(puestos) < 70:
        x, y = r.uniform(0, N, 2)
        if all(min(abs(x - a), N - abs(x - a)) ** 2 + min(abs(y - b), N - abs(y - b)) ** 2 > 150 ** 2 for a, b in puestos):
            puestos.append((x, y))
    for i, (x, y) in enumerate(puestos):
        s = r.uniform(24, 44)
        if i % 3 == 0:
            envolver(lambda xx, yy: estrella(xx, yy, s, DORADO + (255,)), N, x, y, s)
        else:
            col = (FRAMBUESA if i % 2 else ROSA) + (255,)
            envolver(lambda xx, yy: copo(xx, yy, s, col), N, x, y, s)
    img.resize((n, n), Image.LANCZOS).save(OUT / nombre, optimize=True)
    print("ok", nombre)


def acuarela(nombre="fondo-acuarela-rosa.jpg", w=1920, h=1080, base_color=None, manchas=None):
    """Fondo grande tipo acuarela para el hero (no repetible)."""
    img = np.ones((h, w, 3)) * np.array(base_color or CREMA, dtype=float)
    r = np.random.default_rng(3)
    yy, xx = np.mgrid[0:h, 0:w]
    textura = ruido_periodico(1024, 90, 9)
    textura = np.array(Image.fromarray((textura * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), dtype=float) / 255
    manchas = manchas or [(0.12, 0.2, 520, ROSA_PALO, 0.75), (0.85, 0.15, 460, ROSA, 0.35), (0.78, 0.85, 600, ROSA_PALO, 0.7),
               (0.25, 0.9, 380, ROSA, 0.25), (0.55, 0.45, 300, RUBOR, 0.6)]
    for cx, cy, rad, col, alfa in manchas:
        dist = np.sqrt((xx - cx * w) ** 2 + (yy - cy * h) ** 2) / rad
        borde = dist + (textura - 0.5) * 0.6
        m = np.clip(1.2 - borde, 0, 1) ** 1.4 * alfa
        # borde más oscuro, típico de la acuarela
        anillo = np.exp(-((borde - 0.95) ** 2) / 0.003) * alfa * 0.18
        m = np.clip(m + anillo, 0, 1)[..., None]
        img = img * (1 - m) + np.array(col, dtype=float) * m
    img *= (1 + r.standard_normal((h, w, 1)) * 0.012)
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(OUT / nombre, quality=88)
    print("ok", nombre)


def encaje(nombre="borde-encaje.png", w=480, h=110):
    """Tira de encaje (fondo transparente) para repetir en horizontal como separador."""
    S = 3
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    col = (255, 255, 255, 255)
    n = 6
    paso = W / n
    d.rectangle([0, 0, W, H * 0.28], fill=col)
    for i in range(n + 1):
        cx = i * paso
        d.ellipse([cx - paso / 2, H * 0.05, cx + paso / 2, H * 0.95], fill=col)
    hueco = (0, 0, 0, 0)
    for i in range(n + 1):
        cx = i * paso
        # agujeros del encaje
        d.ellipse([cx - paso * 0.17, H * 0.42, cx + paso * 0.17, H * 0.75], fill=hueco)
        for k in range(5):
            a = math.pi * (0.15 + 0.7 * k / 4)
            px, py = cx + math.cos(a) * paso * 0.36, H * 0.5 + math.sin(a) * H * 0.33
            d.ellipse([px - 7 * S, py - 7 * S, px + 7 * S, py + 7 * S], fill=hueco)
    for i in range(n * 3):
        x = (i + 0.5) * W / (n * 3)
        d.ellipse([x - 4 * S, H * 0.12 - 4 * S, x + 4 * S, H * 0.12 + 4 * S], fill=hueco)
    img = img.resize((w, h), Image.LANCZOS)
    img.save(OUT / nombre, optimize=True)
    # vista previa sobre rosa para comprobar
    print("ok", nombre)


MARFIL = (252, 248, 244)
AVENA = (241, 233, 224)
SALVIA_CLARO = (230, 236, 226)
SALVIA = (169, 187, 163)


def neutras():
    """Versiones neutras para equilibrar el rosado (paleta v2)."""
    papel(MARFIL, "papel-marfil.png", semilla=4)
    papel(AVENA, "papel-avena.png", semilla=5)
    papel(SALVIA_CLARO, "papel-salvia.png", semilla=6)
    lino("lino-avena.png", color=(236, 226, 214))
    lino("lino-salvia.png", color=(214, 224, 210))
    acuarela("fondo-acuarela-mixta.jpg", base_color=MARFIL, manchas=[
        (0.86, 0.22, 520, (238, 226, 212), 0.85),
        (0.70, 0.80, 560, SALVIA_CLARO, 0.9),
        (0.95, 0.62, 300, ROSA_PALO, 0.55),
        (0.08, 0.95, 380, (238, 226, 212), 0.6),
        (0.55, 0.10, 260, SALVIA_CLARO, 0.5),
    ])


if __name__ == "__main__":
    papel(CREMA, "papel-carta-crema.png", semilla=1)
    papel(RUBOR, "papel-rosa-rubor.png", semilla=2)
    papel(tuple(int(c * 0.9) for c in ROSA_PALO), "papel-rosa-palo.png", semilla=3)
    tejido_punto()
    lino()
    patron_corazones()
    patron_corazones("patron-corazones-transparente.png", fondo=None, color=ROSA_PALO)
    bordado()
    flores()
    navidad()
    acuarela()
    encaje()
    neutras()
