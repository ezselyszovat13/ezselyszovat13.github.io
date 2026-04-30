#!/usr/bin/env python3
"""
Ézsely Szovát — CV Generator
Single-column layout matching the website (adroitgroup.io palette).
Output: ezsely_szovat_new_cv.pdf
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as pdf_c
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── Page geometry ──────────────────────────────────────────────────────────
PAGE_W, PAGE_H = A4
MARGIN_X = 16 * mm
MARGIN_Y = 14 * mm
LEFT  = MARGIN_X
RIGHT = PAGE_W - MARGIN_X
TOP   = PAGE_H - MARGIN_Y
USABLE_W = PAGE_W - 2 * MARGIN_X

# ── Brand colours ──────────────────────────────────────────────────────────
P    = HexColor('#00c95b')
M    = HexColor('#20a575')
MD   = HexColor('#002e1d')
W    = white
B    = black
GR   = HexColor('#737373')
DG   = HexColor('#1f1f1f')
LG   = HexColor('#f5f6f7')
MNT  = HexColor('#e9fff7')
BORD = HexColor('#e0e0e0')

# ── Section spacing ───────────────────────────────────────────────────────
GAP_BETWEEN_SECTIONS = 9 * mm

FR = FB = None

def setup_fonts():
    global FR, FB
    wf = "C:/Windows/Fonts"
    try:
        pdfmetrics.registerFont(TTFont('AR',  f'{wf}/arial.ttf'))
        pdfmetrics.registerFont(TTFont('ARB', f'{wf}/arialbd.ttf'))
        FR, FB = 'AR', 'ARB'
    except Exception:
        FR, FB = 'Helvetica', 'Helvetica-Bold'

# ── Path helpers ───────────────────────────────────────────────────────────

def round_rect_path(c, x, y, w, h, r):
    K = 0.5522847498
    p = c.beginPath()
    p.moveTo(x + r, y)
    p.lineTo(x + w - r, y)
    p.curveTo(x + w - r + K*r, y, x + w, y + r - K*r, x + w, y + r)
    p.lineTo(x + w, y + h - r)
    p.curveTo(x + w, y + h - r + K*r, x + w - r + K*r, y + h, x + w - r, y + h)
    p.lineTo(x + r, y + h)
    p.curveTo(x + r - K*r, y + h, x, y + h - r + K*r, x, y + h - r)
    p.lineTo(x, y + r)
    p.curveTo(x, y + r - K*r, x + r - K*r, y, x + r, y)
    p.close()
    return p


def draw_rounded_image(c, img_path, x, y, w, h, radius):
    c.saveState()
    p = round_rect_path(c, x, y, w, h, radius)
    c.clipPath(p, stroke=0, fill=0)
    c.drawImage(ImageReader(img_path), x, y, w, h,
                preserveAspectRatio=True, anchor='c', mask='auto')
    c.restoreState()
    c.setStrokeColor(BORD)
    c.setLineWidth(0.5)
    p2 = round_rect_path(c, x, y, w, h, radius)
    c.drawPath(p2, stroke=1, fill=0)


# ── Drawing helpers ────────────────────────────────────────────────────────

def section_header(c, cy, title):
    c.setFont(FB, 11.5)
    c.setFillColor(B)
    c.drawString(LEFT, cy, title)
    cy -= 3.8 * mm
    c.setStrokeColor(P)
    c.setLineWidth(1.5)
    c.line(LEFT, cy, RIGHT, cy)
    c.setLineWidth(0.5)
    return cy - 6.5 * mm


def wrap(c, text, x, y, max_w, fnt, size, col, lh=None):
    if lh is None:
        lh = size * 0.42 * mm + 1.2 * mm
    words = text.split()
    line = ''
    for word in words:
        t = (line + ' ' + word).strip()
        if c.stringWidth(t, fnt, size) > max_w:
            c.setFont(fnt, size); c.setFillColor(col)
            c.drawString(x, y, line)
            y -= lh; line = word
        else:
            line = t
    if line:
        c.setFont(fnt, size); c.setFillColor(col)
        c.drawString(x, y, line)
        y -= lh
    return y


def draw_bullet_list(c, items, x, y, max_w, size=8, color=None, bullet_color=None, lh=None):
    if color is None:
        color = GR
    if bullet_color is None:
        bullet_color = M
    if lh is None:
        lh = size * 0.42 * mm + 1.2 * mm

    bullet_indent = 4.5 * mm
    text_indent = bullet_indent + 0.5 * mm

    for item in items:
        c.setFillColor(bullet_color)
        c.circle(x + 1.6*mm, y + 0.9*mm, 0.7*mm, fill=1, stroke=0)
        y = wrap(c, item, x + text_indent, y, max_w - text_indent, FR, size, color, lh)
        y -= 0.4 * mm
    return y


def draw_mixed_line(c, parts, x, y, size, color_reg, color_bold=None, lh=None):
    if color_bold is None:
        color_bold = color_reg
    if lh is None:
        lh = size * 0.42 * mm + 1.2 * mm

    cur_x = x
    for text, is_bold in parts:
        f = FB if is_bold else FR
        col = color_bold if is_bold else color_reg
        c.setFont(f, size); c.setFillColor(col)
        c.drawString(cur_x, y, text)
        cur_x += c.stringWidth(text, f, size)
    return y - lh


def tl_dot(c, x, y, current=False):
    col = P if current else M
    c.setFillColor(col)
    c.setStrokeColor(W)
    c.setLineWidth(0.6)
    c.circle(x + 2*mm, y + 1.5*mm, 2*mm, fill=1, stroke=1)


# ── HEADER ─────────────────────────────────────────────────────────────────

def build_header(c):
    img_size = 40 * mm
    img_x = LEFT
    img_y = TOP - img_size

    # Portrait
    if os.path.exists("img/img1.jpg"):
        draw_rounded_image(c, "img/img1.jpg", img_x, img_y, img_size, img_size, 4*mm)

    rx = img_x + img_size + 9 * mm
    rw = RIGHT - rx
    center_x = rx + rw / 2

    # 1. NAME — uppercase, centered above the title line
    name_y = TOP - 8 * mm
    c.setFont(FB, 28)
    c.setFillColor(B)
    c.drawCentredString(center_x, name_y, "ÉZSELY SZOVÁT")

    # 2. Green line with title centered (small caps)
    line_y = name_y - 9 * mm
    title_text = "SENIOR BACKEND DEVELOPER"
    title_size = 7.5
    title_w = c.stringWidth(title_text, FB, title_size)
    title_x = center_x - title_w / 2
    gap = 3 * mm

    c.setStrokeColor(P)
    c.setLineWidth(1.2)
    c.line(rx, line_y, title_x - gap, line_y)
    c.line(title_x + title_w + gap, line_y, RIGHT, line_y)
    c.setLineWidth(0.5)

    c.setFont(FB, title_size)
    c.setFillColor(M)
    c.drawString(title_x, line_y - 0.9*mm, title_text)

    ry = line_y - 8 * mm

    # 3. Contact 2-column
    col_w = rw / 2
    contacts = [
        ("EMAIL", "ezselyszovat@gmail.com",  "LINKEDIN", "szovat-ezsely"),
        ("PHONE", "+36 (20) 279 2729",       "GITHUB",   "szovatezsely"),
    ]
    for lbl_l, val_l, lbl_r, val_r in contacts:
        c.setFont(FB, 6.5); c.setFillColor(P)
        c.drawString(rx, ry, lbl_l)
        c.setFont(FR, 9); c.setFillColor(DG)
        c.drawString(rx + 18*mm, ry, val_l)

        c.setFont(FB, 6.5); c.setFillColor(P)
        c.drawString(rx + col_w, ry, lbl_r)
        c.setFont(FR, 9); c.setFillColor(DG)
        c.drawString(rx + col_w + 18*mm, ry, val_r)
        ry -= 5.5 * mm

    ry -= 3 * mm

    # 4. Languages — small caps
    sc_size = 8
    c.setFont(FB, 6.5); c.setFillColor(P)
    c.drawString(rx, ry, "LANGUAGES")
    lang_x = rx + 18 * mm

    c.setFont(FB, sc_size); c.setFillColor(DG)
    c.drawString(lang_x, ry, "HUNGARIAN")
    hu_w = c.stringWidth("HUNGARIAN", FB, sc_size)
    c.setFont(FR, 9); c.setFillColor(GR)
    c.drawString(lang_x + hu_w + 1.5*mm, ry, "(mother tongue)")
    mid_w = hu_w + 1.5*mm + c.stringWidth("(mother tongue)", FR, 9)

    sep_x = lang_x + mid_w + 3*mm
    c.setFont(FB, 9); c.setFillColor(M)
    c.drawString(sep_x, ry, "·")

    c.setFont(FB, sc_size); c.setFillColor(DG)
    c.drawString(sep_x + 3*mm, ry, "ENGLISH")
    en_w = c.stringWidth("ENGLISH", FB, sc_size)
    c.setFont(FR, 9); c.setFillColor(GR)
    c.drawString(sep_x + 3*mm + en_w + 1.5*mm, ry, "(C1, state accredited)")

    bottom = min(ry - 2*mm, img_y)
    return bottom - GAP_BETWEEN_SECTIONS


# ── WORK EXPERIENCE ────────────────────────────────────────────────────────

def build_work_experience(c, cy):
    cy = section_header(c, cy, "WORK EXPERIENCE")

    jobs = [
        ("Oct 2025 – Present",  "Senior Backend Developer", "Adroit Group", {
            "lead": "Applying AI-powered development in a fully remote setup with projects like:",
            "bullets": [
                "extracting structured JSON from PDF invoices via OCR,",
                "developing a RAG-based AI assistant for document Q&A,",
                "scraping messages from Slack workspaces and Discord servers,",
                "maintaining a self-hosted dashboard that helps companies measure their AI tool usage.",
            ],
        }, True),
        ("May 2023 – Oct 2025", "Software Engineer", "Morgan Stanley",
         "Multiple Java and Python based projects in a mostly locked internal environment, with encouragement to improve team processes and bring in proven methodologies.", False),
        ("Nov 2021 – May 2023", "Software Engineer", "EPAM Systems",
         "Backend development in Java with international colleagues. Focused on Clean Code, Clean Design, and mentoring team members.", False),
        ("Sep 2021 – Nov 2021", "Trainee", "Kopint Datorg Kft.",
         "Manual and automated testing in web environments across numerous projects.", False),
        ("Jul 2020 – Aug 2021", "Trainee", "Leviathan Solutions Kft.",
         "Developed a nationwide access-control system that also manages working hours across many configurations.", False),
        ("Feb 2020 – Jun 2020", "Teaching Assistant", "ELTE",
         "Weekly lectures and exam supervision for Object-Oriented Programming in C++.", False),
    ]

    for date, title, company, desc, current in jobs:
        tl_dot(c, LEFT, cy, current)

        c.setFont(FB, 9.5); c.setFillColor(B)
        c.drawString(LEFT + 6*mm, cy, title)
        tw = c.stringWidth(title, FB, 9.5)
        c.setFont(FB, 9.5); c.setFillColor(M)
        c.drawString(LEFT + 6*mm + tw + 2*mm, cy, f"· {company}")

        c.setFont(FR, 7); c.setFillColor(GR)
        c.drawRightString(RIGHT, cy + 0.5*mm, date)
        cy -= 4.8 * mm

        if isinstance(desc, dict):
            cy = wrap(c, desc["lead"], LEFT + 6*mm, cy, USABLE_W - 6*mm, FR, 8, GR, lh=3.8*mm)
            cy -= 0.5 * mm
            cy = draw_bullet_list(c, desc["bullets"], LEFT + 6*mm, cy,
                                   USABLE_W - 6*mm, size=8, color=GR, bullet_color=M, lh=3.8*mm)
        else:
            cy = wrap(c, desc, LEFT + 6*mm, cy, USABLE_W - 6*mm, FR, 8, GR, lh=3.8*mm)

        cy -= 3 * mm

    return cy - GAP_BETWEEN_SECTIONS + 3*mm


# ── EDUCATION ──────────────────────────────────────────────────────────────

def build_education(c, cy):
    cy = section_header(c, cy, "EDUCATION")

    edu = [
        ("Sep 2018 – Jul 2021", "BSc Computer Science", "ELTE, Budapest", [
            [("Graduated with ", False), ("'honoured'", True), (" degree", False)],
            [("Member of ", False), ("Neumann János Talent Group", True)],
        ]),
        ("Sep 2017 – May 2018", "Software Development (OKJ)",
         "Jedlik Ányos Secondary School, Győr", []),
        ("Sep 2013 – May 2017", "Software Development",
         "Jedlik Ányos Secondary School, Győr", [
             [("Jedlik medal", True), (", golden degree", False)],
        ]),
    ]

    for date, degree, school, extras in edu:
        tl_dot(c, LEFT, cy)

        c.setFont(FB, 9.5); c.setFillColor(B)
        c.drawString(LEFT + 6*mm, cy, degree)
        dw = c.stringWidth(degree, FB, 9.5)
        c.setFont(FB, 9.5); c.setFillColor(M)
        c.drawString(LEFT + 6*mm + dw + 2*mm, cy, f"· {school}")

        c.setFont(FR, 7); c.setFillColor(GR)
        c.drawRightString(RIGHT, cy + 0.5*mm, date)
        cy -= 4.8 * mm

        for line_parts in extras:
            cy = draw_mixed_line(c, line_parts, LEFT + 6*mm, cy,
                                  size=8, color_reg=GR, color_bold=DG, lh=3.8*mm)

        cy -= 3 * mm

    return cy - GAP_BETWEEN_SECTIONS + 3*mm


# ── SKILLS ─────────────────────────────────────────────────────────────────

def build_skills(c, cy):
    cy = section_header(c, cy, "SKILLS")

    skills = [
        ("Languages",           "Java, Python, SQL, PHP, C++, C#, Kotlin"),
        ("Frameworks & Stack",  "Spring, Spring Boot, Hibernate, Maven, Gradle, Laravel, Qt"),
        ("Databases",           "PostgreSQL, MySQL, MS SQL Server, Oracle"),
        ("Tooling & DevOps",    "Git, GitHub, Bitbucket, IntelliJ IDEA, Docker, Jenkins"),
        ("Testing & Practices", "JUnit, Mockito, Clean Code, TDD, Code Review"),
        ("Methodologies",       "Scrum, Agile, Mentoring, Pair Programming"),
    ]
    label_w = 42 * mm
    for label, items in skills:
        c.setFont(FB, 8); c.setFillColor(M)
        c.drawString(LEFT, cy, label.upper())
        c.setFont(FR, 8); c.setFillColor(DG)
        c.drawString(LEFT + label_w, cy, items.upper())
        cy -= 5.4 * mm
    return cy

# ── Entry point ────────────────────────────────────────────────────────────

def main():
    out = r"C:\Programming projects\adroit\ezselyszovat13.github.io\ezsely_szovat_new_cv.pdf"
    setup_fonts()
    c = pdf_c.Canvas(out, pagesize=A4)
    c.setTitle("Ézsely Szovát — CV")
    c.setAuthor("Ézsely Szovát")
    c.setSubject("Senior Backend Developer")

    cy = build_header(c)
    cy = build_work_experience(c, cy)
    cy = build_education(c, cy)
    cy = build_skills(c, cy)

    c.save()
    print(f"Saved: {out}")
    print(f"Final y position: {cy/mm:.1f}mm from bottom (negative = overflow)")


if __name__ == '__main__':
    main()
