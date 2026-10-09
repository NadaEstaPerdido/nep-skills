"""Fábrica de infografías del boletín NEP: datos JSON -> PNG con la línea gráfica de Nada Está Perdido.

Solo necesita Pillow (pip install pillow). Fuentes y logo vienen en esta carpeta, así corre igual
en el PC que en la rutina de nube.

Uso:
  python infografia.py datos.json                -> feed (1080x1350) y story (1080x1920) junto al JSON
  python infografia.py datos.json --formato feed -> solo uno
  python infografia.py datos.json --salida carpeta/

Marcas en "titulo": *naranja*. El esquema completo está en SKILL.md.
"""
import argparse
import json
import pathlib
import random
import re
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent
FUENTES = ROOT / "fuentes"

VERDE, DURAZNO, NARANJA = (13, 59, 45), (246, 203, 169), (232, 93, 27)
CREMA = (251, 244, 236)
VERDE_SUAVE = (13, 59, 45, 150)

FORMATOS = {  # ancho, alto, margen superior, margen inferior (zonas seguras de story)
    "feed": (1080, 1350, 10, 0),
    "story": (1080, 1920, 150, 170),
}
FRENTES = {
    "poder": "PODER", "gobierno": "GOBIERNO", "libertades": "LIBERTADES", "protesta": "PROTESTA",
    "derechos": "DERECHOS", "seguridad": "SEGURIDAD", "ambiente": "AMBIENTE", "animales": "ANIMALES",
    "economia": "ECONOMÍA", "salud": "SALUD", "educacion": "EDUCACIÓN", "territorio": "TERRITORIO",
    "democracia": "DEMOCRACIA", "paz": "PAZ", "justicia": "JUSTICIA", "corrupcion": "CORRUPCIÓN",
}
NIVELES = {"hecho": "HECHO", "anuncio": "ANUNCIO", "declaracion": "DECLARACIÓN", "omision": "OMISIÓN"}
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["", "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre",
         "octubre", "noviembre", "diciembre"]

_cache = {}


def fuente(nombre, tam):
    clave = (nombre, int(tam))
    if clave not in _cache:
        archivo = {"anton": "Anton-Regular", "titular": "ArchivoNEPTitular-Regular", "bold": "ArchivoNEP-Bold",
                   "regular": "ArchivoNEP-Regular", "mono": "PlexMonoNEP-Bold"}[nombre]
        _cache[clave] = ImageFont.truetype(str(FUENTES / f"{archivo}.ttf"), int(tam))
    return _cache[clave]


# ---------------- Texto ----------------

def tokens(texto, color, acento):
    """Palabras como listas de (trozo, color); *así* va en acento. La puntuación pegada a un
    *acento* sigue en la misma palabra (sin espacio de más)."""
    palabras, actual = [], []
    for i, parte in enumerate(re.split(r"\*(.+?)\*", texto or "")):
        c = acento if i % 2 else color
        for trozo in re.split(r"([ \t\n]+)", parte):  # el espacio duro ( ) no corta
            if not trozo:
                continue
            if trozo.isspace():
                if actual:
                    palabras.append(actual)
                actual = []
            else:
                actual.append((trozo, c))
    if actual:
        palabras.append(actual)
    return palabras


def largo(f, palabra):
    return sum(f.getlength(t) for t, _ in palabra)


def envolver(texto, f, ancho, color=VERDE, acento=NARANJA):
    """Devuelve líneas: cada línea es una lista de palabras."""
    lineas, actual, esp = [], [], f.getlength(" ")
    for w in tokens(texto, color, acento):
        prueba = actual + [w]
        total = sum(largo(f, x) for x in prueba) + esp * (len(prueba) - 1)
        if actual and total > ancho:
            lineas.append(actual)
            actual = [w]
        else:
            actual = prueba
    if actual:
        lineas.append(actual)
    return lineas


def alto_bloque(lineas, f, interlineado):
    return len(lineas) * f.size * interlineado if lineas else 0


def pintar(d, lineas, f, x, y, interlineado):
    esp = f.getlength(" ")
    for linea in lineas:
        cx = x
        for palabra in linea:
            for t, c in palabra:
                d.text((cx, y), t, font=f, fill=c)
                cx += f.getlength(t)
            cx += esp
        y += f.size * interlineado
    return y


# ---------------- Fondo y piezas ----------------

def fondo(w, h):
    """Papel kraft durazno con grano y viñeta suave (procedural, sin archivos)."""
    rnd = random.Random(7)
    base = Image.new("RGB", (w, h), DURAZNO)
    ruido = Image.effect_noise((w // 2, h // 2), 28).resize((w, h)).filter(ImageFilter.GaussianBlur(0.6))
    tinte = Image.new("RGB", (w, h), (196, 140, 98))
    base = Image.composite(tinte, base, ruido.point(lambda v: max(0, v - 128) // 4))
    fibra = ImageDraw.Draw(base)
    for _ in range(900):
        x, y = rnd.randrange(w), rnd.randrange(h)
        fibra.line((x, y, x + rnd.randint(-14, 14), y + rnd.randint(-3, 3)), fill=(222, 170, 132), width=1)
    viñeta = Image.new("L", (w, h), 0)
    ImageDraw.Draw(viñeta).rectangle((0, 0, w, h), outline=70, width=60)
    base = Image.composite(Image.new("RGB", (w, h), (214, 160, 120)), base, viñeta.filter(ImageFilter.GaussianBlur(80)))
    return base


def logo(alto):
    im = Image.open(ROOT / "marca" / "logo_nep.png")
    return im.resize((round(im.width * alto / im.height), alto), Image.LANCZOS)


def chip(d, x, y, texto, f, relleno, tinta, borde=None, pad=(12, 5)):
    ancho = f.getlength(texto) + pad[0] * 2
    alto = f.size + pad[1] * 2 + 2
    d.rounded_rectangle((x, y, x + ancho, y + alto), radius=alto / 2, fill=relleno, outline=borde, width=2 if borde else 0)
    d.text((x + pad[0], y + pad[1] - 1), texto, font=f, fill=tinta)
    return x + ancho


def check(d, cx, cy, r, color):
    d.line((cx - r * .55, cy, cx - r * .15, cy + r * .45, cx + r * .6, cy - r * .5), fill=color, width=max(3, int(r * .28)),
           joint="curve")


def fecha_larga(iso):
    a, m, dd = (int(x) for x in iso.split("-"))
    import datetime
    dia = DIAS[datetime.date(a, m, dd).weekday()]
    return dia, f"{dd} de {MESES[m]} de {a}"


# ---------------- Composición ----------------

def componer(datos, formato, s):
    """Arma la pieza a escala s. Devuelve (imagen, sobrante); sobrante < 0 = no cabe."""
    W, H, top, bottom = FORMATOS[formato]
    M = 60
    ancho = W - 2 * M
    img = fondo(W, H)
    d = ImageDraw.Draw(img)
    especial = datos.get("edicion") == "especial"

    # --- Cabecera ---
    y = top + 34
    lg = logo(116)
    img.paste(lg, (M - 4, y), lg)
    dia, fecha = fecha_larga(datos["fecha"])
    etiqueta = "ESPECIAL DE LA SEMANA" if especial else "INFOGRAFÍA DEL DÍA"
    d.text((W - M, y + 2), etiqueta, font=fuente("mono", 19), fill=NARANJA, anchor="ra")
    d.text((W - M, y + 26), dia.upper(), font=fuente("anton", 58), fill=VERDE, anchor="ra")
    d.text((W - M, y + 96), fecha, font=fuente("bold", 24), fill=VERDE, anchor="ra")
    alto_der = 126
    if datos.get("cubre"):
        d.text((W - M, y + 128), datos["cubre"], font=fuente("regular", 20), fill=VERDE, anchor="ra")
        alto_der = 156
    y += max(lg.height, alto_der) + 16

    # --- Titular del día ---
    ft = fuente("titular", 56 * s)
    lt = envolver(datos["titulo"], ft, ancho)
    y = pintar(d, lt, ft, M, y, 1.08) + 18 * s

    # --- La cifra ---
    c = datos.get("cifra")
    if c:
        fv = fuente("anton", 108 * s)
        fx = fuente("bold", 25 * s)
        fs = fuente("mono", 16 * s)
        ancho_valor = min(fv.getlength(c["valor"]), ancho * .52)
        while fv.getlength(c["valor"]) > ancho * .52 and fv.size > 50:
            fv = fuente("anton", fv.size - 4)
        ancho_txt = ancho - ancho_valor - 48 - 34
        lx = envolver(c["texto"], fx, ancho_txt, color=DURAZNO, acento=CREMA)
        alto_txt = 30 * s + alto_bloque(lx, fx, 1.2) + fs.size + 14
        alto_caja = max(fv.size * 1.15, alto_txt) + 24 * s
        d.rounded_rectangle((M, y, W - M, y + alto_caja), radius=26, fill=VERDE)
        d.text((M + 28, y + alto_caja / 2), c["valor"], font=fv, fill=NARANJA, anchor="lm")
        tx = M + 28 + ancho_valor + 30
        ty = y + (alto_caja - alto_txt) / 2
        d.text((tx, ty), "LA CIFRA", font=fuente("mono", 18 * s), fill=NARANJA)
        ty = pintar(d, lx, fx, tx, ty + 30 * s, 1.2)
        if c.get("fuente"):
            d.text((tx, ty + 6), "Fuente: " + c["fuente"], font=fs, fill=DURAZNO)
        y += alto_caja + 22 * s

    # --- Noticias: se miden primero para repartir el aire sobrante ---
    fn_num = fuente("anton", 50 * s)
    fchip = fuente("mono", max(14, 15 * s))
    ftit = fuente("bold", 30 * s)
    fdato = fuente("bold", 22 * s)
    fimp = fuente("regular", 21 * s)
    col = M + 82 * s
    ancho_col = W - M - col
    filas = []
    for n in datos["noticias"]:
        lt_ = envolver(n["titulo"], ftit, ancho_col)
        ld = envolver(n.get("dato", ""), fdato, ancho_col - 26 * s, color=NARANJA, acento=VERDE)
        li = envolver(n.get("implica", ""), fimp, ancho_col - fuente("bold", fimp.size).getlength("Qué implica: "))
        alto = fchip.size + 18 + alto_bloque(lt_, ftit, 1.1) + 6
        alto += alto_bloque(ld, fdato, 1.2) + 4 if ld else 0
        alto += alto_bloque(li, fimp, 1.25) if li else 0
        filas.append((n, lt_, ld, li, alto))

    sigue = (datos.get("sigue") or []) if formato == "story" else []  # en el feed no cabe
    fsig = fuente("regular", 20 * s)
    lsig = envolver(" ·  ".join(sigue), fsig, ancho - fuente("mono", 17 * s).getlength("LO QUE SIGUE  ")) if sigue else []
    alto_sigue = (alto_bloque(lsig, fsig, 1.25) + 28) if sigue else 0
    alto_pie = 92
    fuentes_txt = "Fuentes: " + ", ".join(dict.fromkeys(
        f.strip() for n in datos["noticias"] for f in re.split(r"[·|,]", n.get("fuente", "")) if f.strip()))
    ffu = fuente("regular", 17)
    lfu = envolver(fuentes_txt, ffu, ancho)
    alto_fuentes = alto_bloque(lfu, ffu, 1.25) + 10

    limite = H - bottom - alto_pie - alto_fuentes - alto_sigue - 14
    gap_min = 22 * s
    usado = sum(f[4] for f in filas) + gap_min * (len(filas) - 1)
    sobrante = limite - y - usado
    if sobrante < 0:
        return img, sobrante
    gap = gap_min + min(sobrante / max(1, len(filas)), 60)

    for i, (n, lt_, ld, li, alto) in enumerate(filas):
        if i:
            yl = y - gap / 2
            for x in range(M, W - M, 18):  # línea punteada
                d.line((x, yl, x + 9, yl), fill=(13, 59, 45), width=2)
        r = 34 * s
        cx, cy = M + r, y + r + 4
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=NARANJA)
        d.text((cx, cy + 2), str(i + 1), font=fn_num, fill=CREMA, anchor="mm")
        x = col
        x = chip(d, x, y, FRENTES.get(n.get("frente", ""), n.get("frente", "").upper()), fchip, VERDE, DURAZNO) + 8
        nivel = n.get("nivel", "hecho")
        if nivel == "hecho":
            fin = chip(d, x, y, "HECHO     ", fchip, None, VERDE, borde=VERDE)
            check(d, fin - 22 * s, y + (fchip.size + 12) / 2 + 1, 9 * s, VERDE)
        else:
            chip(d, x, y, NIVELES.get(nivel, nivel.upper()), fchip, None, NARANJA, borde=NARANJA)
        yy = y + fchip.size + 18
        yy = pintar(d, lt_, ftit, col, yy, 1.1) + 6
        if ld:
            d.polygon([(col, yy + 7 * s), (col + 14 * s, yy + 14 * s), (col, yy + 21 * s)], fill=NARANJA)
            yy = pintar(d, ld, fdato, col + 24 * s, yy, 1.2) + 4
        if li:
            d.text((col, yy), "Qué implica:", font=fuente("bold", fimp.size), fill=VERDE)
            sangria = fuente("bold", fimp.size).getlength("Qué implica:") + fimp.getlength(" ")
            primera, resto = li[0], li[1:]
            pintar(d, [primera], fimp, col + sangria, yy, 1.25)
            pintar(d, resto, fimp, col, yy + fimp.size * 1.25, 1.25)
        y += alto + gap

    # --- Lo que sigue ---
    y = limite + 10
    if sigue:
        fl = fuente("mono", 17 * s)
        d.text((M, y + 2), "LO QUE SIGUE", font=fl, fill=NARANJA)
        pintar(d, lsig, fsig, M + fl.getlength("LO QUE SIGUE  "), y, 1.25)
        y += alto_sigue

    # --- Fuentes y pie ---
    pintar(d, lfu, ffu, M, y, 1.25)
    yp = H - bottom - alto_pie + 14
    d.rounded_rectangle((M - 20, yp, W - M + 20, yp + alto_pie - 28), radius=22, fill=VERDE)
    mid = yp + (alto_pie - 28) / 2
    d.text((M + 6, mid), "@nadaestaperdido_bogota", font=fuente("bold", 25), fill=DURAZNO, anchor="lm")
    cta = "Boletín diario gratis · link en la bio"
    d.text((W - M - 6, mid), cta, font=fuente("bold", 23), fill=NARANJA, anchor="rm")
    return img, sobrante


def renderizar(datos, formato, salida):
    for s in [x / 100 for x in range(100, 69, -3)]:
        img, sobrante = componer(datos, formato, s)
        if sobrante >= 0:
            img.save(salida, optimize=True)
            return s
    raise SystemExit(f"[{formato}] El contenido no cabe ni a escala 0.70: acorta titulares, datos o 'implica' "
                     f"(o deja 5 noticias).")


def validar(datos):
    avisos = []
    for k in ("fecha", "titulo", "noticias"):
        if not datos.get(k):
            raise SystemExit(f"Falta el campo obligatorio '{k}'.")
    if not 3 <= len(datos["noticias"]) <= 6:
        avisos.append(f"Hay {len(datos['noticias'])} noticias; lo ideal son 4 a 6.")
    if len(datos["titulo"].replace("*", "")) > 70:
        avisos.append(f"Titular del día de {len(datos['titulo'])} caracteres (máx. 70).")
    for i, n in enumerate(datos["noticias"], 1):
        for campo, maximo in (("titulo", 60), ("dato", 60), ("implica", 100)):
            if len(n.get(campo, "")) > maximo:
                avisos.append(f"Noticia {i}: '{campo}' de {len(n[campo])} caracteres (máx. {maximo}).")
        if not n.get("fuente"):
            avisos.append(f"Noticia {i}: sin fuente. No se publica una noticia sin fuente.")
    return avisos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("datos")
    ap.add_argument("--formato", choices=[*FORMATOS, "todos"], default="todos")
    ap.add_argument("--salida")
    a = ap.parse_args()
    ruta = pathlib.Path(a.datos)
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    for aviso in validar(datos):
        print("AVISO:", aviso)
    carpeta = pathlib.Path(a.salida) if a.salida else ruta.parent
    carpeta.mkdir(parents=True, exist_ok=True)
    for f in (FORMATOS if a.formato == "todos" else [a.formato]):
        destino = carpeta / f"infografia-{datos['fecha']}-{f}.png"
        s = renderizar(datos, f, destino)
        print(f"OK {destino} (escala {s:.2f})")


if __name__ == "__main__":
    sys.exit(main())
