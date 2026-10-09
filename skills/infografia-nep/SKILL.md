---
name: infografia-nep
description: Convierte el boletín diario de Nada Está Perdido 2.0 en una infografía con la línea gráfica de NEP (papel durazno, verde y naranja, logo, cifra del día y las noticias numeradas con su "qué implica"), en formato feed 1080x1350 y story 1080x1920, lista para Instagram y WhatsApp. Úsala después de cada boletín, o cuando pidan "la infografía", "la infografía del boletín", "el resumen visual de las noticias" o "la pieza del día para redes".
---

# Infografía del boletín NEP

> **En aprobación.** La rutina de nube todavía no la ejecuta; por ahora se usa a mano en el PC.

La infografía es el boletín en una imagen: alguien que no abre el correo entiende en 20 segundos qué hizo el poder ayer y por qué importa. Sale **del boletín ya verificado**: no se busca ni se agrega nada nuevo. El diseño lo pone el código (`infografia.py`); tu trabajo es elegir y condensar bien.

## 1. Llena los datos (JSON)

Parte del boletín del día (el que acabas de enviar, o el último `Boletín NEP · …` de Gmail). Escribe `datos.json`:

```json
{
  "fecha": "2026-10-08",
  "edicion": "diaria",
  "cubre": "Lo que pasó el miércoles 7",
  "titulo": "Un Gobierno que avanza a punta de *anuncios y confrontaciones*",
  "cifra": {"valor": "$4,4 billones", "texto": "en pagos del Fomag *sin soportes*, según la Contraloría", "fuente": "Infobae · El Tiempo"},
  "noticias": [
    {"frente": "salud", "nivel": "anuncio", "titulo": "…", "dato": "…", "implica": "…", "fuente": "Medio · Medio"}
  ],
  "sigue": ["…", "…"]
}
```

| Campo | Regla |
|---|---|
| `fecha` | Fecha de la edición (AAAA-MM-DD). |
| `edicion` | `diaria`, o `especial` el domingo. |
| `cubre` | Corto: "Lo que pasó el miércoles 7" · lunes: "Viernes 2 a domingo 4" · domingo: "Semana del 1 al 6 de octubre". |
| `titulo` | El pulso del día en una frase, **máx. 70 caracteres**. Marca entre `*asteriscos*` 1 a 3 palabras clave (salen en naranja). |
| `cifra` | El dato más fuerte del boletín. `valor` máx. 14 caracteres ("$4,4 billones", "20 muertos", "5 días"); `texto` máx. 100. Si ningún número pesa, omite `cifra`. |
| `noticias` | **4 o 5** (máx. 6), en el orden del boletín. El domingo: las 5 de la semana. |
| `frente` | Uno de: poder, gobierno, libertades, protesta, derechos, seguridad, ambiente, animales, economia, salud, educacion, territorio, democracia, paz, justicia, corrupcion. |
| `nivel` | `hecho` (✅ firmado, votado, dicho en público), `anuncio`, `declaracion` u `omision`. |
| `titulo` (noticia) | **Máx. 60 caracteres**, que quepa en una línea. Directo, sin adjetivos. |
| `dato` | El hecho o la cifra clave, **máx. 60**. Solo hecho, nunca opinión. |
| `implica` | La lectura de "Qué implica", **máx. 100**. Es opinión 🔍: atribuible al movimiento, sin intenciones no documentadas. |
| `fuente` | Los medios del boletín, separados por ` · `. Sin fuente no entra. |
| `sigue` | 2-3 pendientes a vigilar, máx. 50 c/u (solo aparecen en la story). |

Las reglas del boletín aplican idénticas: **víctimas primero** (si hay violencia, el `dato` lleva civiles y menores con la cifra más grave), **lenguaje incluyente** (todxs, lxs maestrxs), hecho separado de lectura, cero datos que no estén en el boletín.

## 2. Renderiza y revisa

```bash
python3 -c "import PIL" 2>/dev/null || pip install -q pillow
python3 skills/infografia-nep/infografia.py <carpeta>/datos.json
```

Sale `infografia-AAAA-MM-DD-feed.png` y `-story.png` en la misma carpeta. Si avisa que algo es largo o no cabe, acorta el texto (no lo partas en más noticias). **Abre los dos PNG y míralos**: nada cortado, nada encimado, las tildes bien, ninguna noticia sin fuente. La escala que imprime debe ser 0.85 o más en el feed; si sale menor, acorta titulares.

## 3. Entrega

**En la rutina de nube** (después de enviar el boletín):

1. Publica las imágenes: `bash skills/infografia-nep/publicar.sh <carpeta> <AAAA-MM-DD>`. Las sube a la rama `claude/serene-faraday` del repo e imprime un enlace directo por imagen.
2. Envía **un correo solo a `foreman1204@gmail.com`** (nunca al webhook de Make ni a la lista), con asunto `Infografía NEP · [día] [fecha]` y **solo `body` en texto plano** (sin `htmlBody`):
   - los dos enlaces (feed y story);
   - un copy para Instagram: 2-3 líneas que inviten a leer, lenguaje incluyente, cierre "Boletín diario gratis: link en la bio" y 5-8 hashtags (#NadaEstáPerdido siempre).
3. Si la publicación falla, envía igual el correo diciendo qué falló (el error en una línea). Nunca afecta al boletín: ese ya salió.

**En el PC:** guarda los PNG en `Boletin de noticias/Infografias/AAAA-MM-DD/` y muéstralos.

## Ejemplo

`ejemplos/2026-10-08.json` es el boletín del jueves 8 de octubre de 2026 convertido. Úsalo de referencia de tono y largo.
