#!/usr/bin/env python3
"""
Regenera las tarjetas de /equipo/ y las páginas individuales /equipo/<slug>/
a partir de team-data.json (única fuente de contenido real del equipo).

Uso:
    python3 scripts/build_team.py

No inventa contenido: si "published" es false para una persona, su página
individual siempre muestra el bloque "Perfil en preparación", aunque
bio/approach tengan texto a medias en el JSON.
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(ROOT, "team-data.json"), encoding="utf-8") as f:
    DATA = json.load(f)
MEMBERS = DATA["members"]

EQUIPO_PATH = os.path.join(ROOT, "equipo", "index.html")
equipo_html = open(EQUIPO_PATH, encoding="utf-8").read()

# ---- extraer HEADER y FOOTER compartidos desde equipo/index.html (ya está al día) ----
header_start = equipo_html.index("<body>")
header_end = equipo_html.index("</header>") + len("</header>")
HEADER = equipo_html[header_start:header_end]

footer_start = equipo_html.index("<footer>")
footer_end = equipo_html.index("</html>") + len("</html>")
FOOTER = equipo_html[footer_start:footer_end]

SILHOUETTE_SVG = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4">'
    '<circle cx="12" cy="8" r="4"/><path d="M4 21c1.5-4.5 5-6 8-6s6.5 1.5 8 6"/></svg>'
)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") if s else s


# ---------------------------------------------------------------------------
# 1) Tarjetas de /equipo/
# ---------------------------------------------------------------------------
def team_card_juan():
    return '''        <div class="team-card reveal">
          <div class="team-photo">
            <picture>
              <source srcset="/assets/juan-flores-hero.webp" type="image/webp">
              <img src="/assets/juan-flores-hero.jpg" alt="Juan Flores Medina, psicólogo sanitario colegiado MU02958" width="1254" height="1254" loading="lazy" decoding="async">
            </picture>
          </div>
          <div class="tc-body">
            <h3>Juan Flores</h3>
            <span class="role">Director</span>
            <a class="tc-more" href="/juan-flores-psicologo/">Ver más →</a>
          </div>
        </div>
'''


def photo_picture_html(photo_path, alt, object_position=None):
    """<picture> con webp (si existe junto al jpg/png) + fallback, o solo <img> si no hay webp."""
    style = f' style="object-position:{object_position}"' if object_position else ""
    root, ext = os.path.splitext(photo_path)
    webp_path = root + ".webp"
    webp_fs_path = os.path.join(ROOT, webp_path.lstrip("/"))
    if ext.lower() in (".jpg", ".jpeg", ".png") and os.path.exists(webp_fs_path):
        mime = "image/jpeg" if ext.lower() in (".jpg", ".jpeg") else "image/png"
        return (
            f'<picture><source srcset="{webp_path}" type="image/webp">'
            f'<img src="{photo_path}" alt="{alt}" loading="lazy" decoding="async"{style}></picture>'
        )
    return f'<img src="{photo_path}" alt="{alt}" loading="lazy" decoding="async"{style}>'


def team_card_member(m):
    name = esc(m["name"]) or "Nombre Apellido"
    role = esc(m["role"]) or "Psicólogo/a"
    if m.get("photo"):
        photo_html = photo_picture_html(
            m["photo"], f"{name}, psicólogo/a en Juan Flores Psicólogos",
            object_position=m.get("photo_position")
        )
    else:
        photo_html = SILHOUETTE_SVG
    return f'''        <div class="team-card reveal">
          <div class="team-photo">{photo_html}</div>
          <div class="tc-body">
            <h3>{name}</h3>
            <span class="role">{role}</span>
            <a class="tc-more" href="/equipo/{m["slug"]}/">Ver más →</a>
          </div>
        </div>
'''


cards_html = team_card_juan() + "".join(team_card_member(m) for m in MEMBERS)

new_grid = (
    '      <div class="team-grid">\n'
    + cards_html
    + "      </div>"
)

equipo_html = re.sub(
    r'      <div class="team-grid">.*?\n      </div>',
    new_grid.replace("\\", "\\\\"),
    equipo_html,
    count=1,
    flags=re.DOTALL,
)
open(EQUIPO_PATH, "w", encoding="utf-8").write(equipo_html)
print(f"equipo/index.html actualizado con {len(MEMBERS) + 1} tarjetas (Juan Flores + {len(MEMBERS)})")


# ---------------------------------------------------------------------------
# 2) Páginas individuales /equipo/<slug>/
# ---------------------------------------------------------------------------
def page_head(m, name, role):
    title = f"{name} | Juan Flores Psicólogos"
    desc = f"{name}, {role.lower()} en Juan Flores Psicólogos, Guadalupe, Murcia." if m["published"] else \
           f"Perfil de {name} en el equipo de Juan Flores Psicólogos. Próximamente más información."
    canonical = f"https://juanflorespsicologos.com/equipo/{m['slug']}/"
    return f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canonical}">
<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
<meta property="og:type" content="profile">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:locale" content="es_ES">
<meta property="og:site_name" content="Juan Flores Psicólogos">
<meta name="twitter:card" content="summary">
<link rel="stylesheet" href="/styles.css">
{'' if (m["published"] and m["bio"]) else '<meta name="robots" content="noindex, follow">' + chr(10)}</head>
'''


def render_section(section):
    heading = section.get("heading")
    paragraphs = section.get("paragraphs", [])
    quote = section.get("quote")
    quote_position = section.get("quote_position", "start")  # "start" | "end"
    parts = []
    if heading:
        parts.append(f'          <h3 class="director-subhead reveal">{esc(heading)}</h3>')

    quote_html = ""
    if quote:
        quote_html = f'''          <div class="director-ideas reveal">
            <blockquote>{esc(quote)}</blockquote>
          </div>'''

    if quote and quote_position == "start":
        parts.append(quote_html)
    if paragraphs:
        p_html = "\n            ".join(f"<p>{esc(p)}</p>" for p in paragraphs)
        parts.append(f'''          <div class="director-text reveal">
            {p_html}
          </div>''')
    if quote and quote_position == "end":
        parts.append(quote_html)
    return "\n".join(parts)


def page_main_published(m, name, role):
    if m.get("photo"):
        photo_block = photo_picture_html(
            m["photo"], f"{esc(name)}, {esc(role)} en Juan Flores Psicólogos",
            object_position=m.get("photo_position")
        )
    else:
        photo_block = SILHOUETTE_SVG

    bio_paragraphs = "\n            ".join(f"<p>{esc(p)}</p>" for p in m["bio"])

    # Compatibilidad con el esquema antiguo (approach: [...]) y el nuevo (sections: [...])
    sections = m.get("sections")
    if sections is None and m.get("approach"):
        sections = [{"heading": "Mi enfoque", "paragraphs": m["approach"]}]
    sections = sections or []

    approach_section = "\n".join(render_section(s) for s in sections)
    if approach_section:
        approach_section = "\n" + approach_section + "\n"

    return f'''<main>

  <section class="page-header">
    <div class="container">
      <span class="eyebrow">El equipo</span>
      <h1>{esc(name)}</h1>
    </div>
  </section>

  <section class="director" id="perfil">
    <div class="container">
      <div class="director-grid">

        <aside class="director-aside reveal">
          <div class="director-photo">
            {photo_block}
          </div>
          <h3>{esc(name)}</h3>
          <span class="director-role">{esc(role)}</span>
        </aside>

        <div class="director-body">
          <div class="director-text reveal">
            {bio_paragraphs}
          </div>
{approach_section}
        </div>
      </div>
    </div>
  </section>

<!-- CTA BANNER -->
  <section style="padding-top:0">
    <div class="cta-banner reveal">
      <div>
        <h2>¿Listo/a para dar el primer paso?</h2>
        <p>Pide tu cita hoy mismo, presencial u online.</p>
      </div>
      <div class="cta-actions">
        <a href="https://wa.me/34665692132" class="btn btn-primary">Pedir cita por WhatsApp</a>
        <a href="mailto:juan@juanflorespsicologos.com" class="btn btn-outline">Escribir email</a>
      </div>
    </div>
  </section>

</main>
'''


def page_main_pending(m, name, role):
    return f'''<main>

  <section class="page-header">
    <div class="container">
      <span class="eyebrow">El equipo</span>
      <h1>{esc(name)}</h1>
    </div>
  </section>

  <section class="director" id="perfil">
    <div class="container">
      <div class="director-grid">

        <aside class="director-aside reveal">
          <div class="director-photo">
            {SILHOUETTE_SVG}
          </div>
          <h3>{esc(name)}</h3>
          <span class="director-role">{esc(role)}</span>
        </aside>

        <div class="director-body">
          <div class="profile-pending reveal">
            <span class="pp-tag">Perfil en preparación</span>
            <p>Estamos preparando la ficha completa de {esc(name)}, con su foto, formación y enfoque terapéutico. Mientras tanto, puedes pedir cita a través del equipo de Juan Flores Psicólogos y te asignaremos al profesional más adecuado para tu caso.</p>
          </div>
        </div>
      </div>
    </div>
  </section>

<!-- CTA BANNER -->
  <section style="padding-top:0">
    <div class="cta-banner reveal">
      <div>
        <h2>¿Listo/a para dar el primer paso?</h2>
        <p>Pide tu cita hoy mismo, presencial u online.</p>
      </div>
      <div class="cta-actions">
        <a href="https://wa.me/34665692132" class="btn btn-primary">Pedir cita por WhatsApp</a>
        <a href="mailto:juan@juanflorespsicologos.com" class="btn btn-outline">Escribir email</a>
      </div>
    </div>
  </section>

</main>
'''


for m in MEMBERS:
    name = m["name"] or "Nombre Apellido"
    role = m["role"] or "Psicólogo/a"
    slug_dir = os.path.join(ROOT, "equipo", m["slug"])
    os.makedirs(slug_dir, exist_ok=True)

    head = page_head(m, name, role)
    if m["published"] and m["bio"]:
        main = page_main_published(m, name, role)
    else:
        main = page_main_pending(m, name, role)

    html = head + HEADER + "\n\n" + main + "\n" + FOOTER + "\n"
    out_path = os.path.join(slug_dir, "index.html")
    open(out_path, "w", encoding="utf-8").write(html)
    print(f"generado equipo/{m['slug']}/index.html ({'publicado' if m['published'] and m['bio'] else 'en preparación'})")

print("Listo.")
