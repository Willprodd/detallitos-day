# Detallitos Day

Tienda web de **Detallitos Day**: cartas, flores tejidas, bordados, llaveros y cajas sorpresa hechos a mano por Dayanna. Los pedidos se hacen por WhatsApp.

Web: https://willprodd.github.io/detallitos-day/

## Carpetas

| Carpeta | Qué hay |
|---|---|
| `web/` | La página (`index.html`) y sus imágenes. Es lo que se publica. |
| `marca/logo/detallitos-day/` | Logo final en SVG y PNG: color, blanco, una tinta, sello y favicon. |
| `marca/fuentes/` | Tipografías libres (Google Fonts, licencia OFL) usadas para dibujar el logo. |
| `texturas/` | Fondos y patrones: papel, lino, tejido, bordado, festividades. |

## Antes de abrir la tienda

1. En `web/index.html`, cambia `const WHATSAPP = "570000000000"` por el número real (código de país + número, sin `+` ni espacios).
2. Los productos, precios y fotos son de ejemplo. Se editan en la lista `PRODUCTOS` de `web/index.html` y las fotos van en `web/img/productos/`.

## Regenerar imágenes

Requiere Python 3 con `pillow`, `numpy` y `fonttools`, más ImageMagick.

```bash
python3 marca/generar_logo_detallitos_day.py   # logo
python3 texturas/generar_texturas.py          # texturas
cd web && python3 generar_productos.py && python3 generar_productos_extra.py && python3 generar_recortes.py
```

Cada vez que se sube un cambio a `main`, GitHub Actions publica la carpeta `web/` en GitHub Pages.
