#!/usr/bin/env python3
"""Extract speaker notes from presentation_en.html and render a notes-only PDF.

The notes (Czech read-aloud script) live in:
  - the title slide's `data-notes="..."` attribute, and
  - one `<aside class="notes">...</aside>` per content slide.

We keep <strong>/<em> emphasis, skip the MathJax assistive <style> blocks that
bleed into some asides, drop HTML comments (real `<!-- -->` and the en-dash
`<!– –>` pseudo-comments the author used to mute lines), and label each note
with its slide title.
"""
import html
import re
from html.parser import HTMLParser

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Paragraph, SimpleDocTemplate, Spacer)

SRC = "presentation_en.html"
OUT = "presentation_en_notes.pdf"
LATO = "/usr/share/fonts/truetype/lato"

# --- font registration (Lato covers full Czech diacritics) ---------------
pdfmetrics.registerFont(TTFont("Lato", f"{LATO}/Lato-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Lato-Bold", f"{LATO}/Lato-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Lato-Italic", f"{LATO}/Lato-Italic.ttf"))
pdfmetrics.registerFont(TTFont("Lato-BoldItalic", f"{LATO}/Lato-BoldItalic.ttf"))
pdfmetrics.registerFontFamily(
    "Lato", normal="Lato", bold="Lato-Bold",
    italic="Lato-Italic", boldItalic="Lato-BoldItalic")


class NotesExtractor(HTMLParser):
    """Walk the HTML, collecting (slide_title, note_richtext) pairs."""

    SKIP = {"style", "script", "svg", "mjx-container"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.titles = []          # plain-text slide titles, in order
        self.notes = []           # reportlab-markup note bodies, in order
        self._in_title = False
        self._title_buf = []
        self._in_notes = False
        self._note_buf = []
        self._skip_depth = 0

    # ---- titles (h1/h2) ----
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ("h1", "h2"):
            self._in_title = True
            self._title_buf = []
            return
        if tag == "aside" and "notes" in (attrs.get("class") or ""):
            self._in_notes = True
            self._note_buf = []
            return
        if self._in_notes:
            if tag in self.SKIP:
                self._skip_depth += 1
            elif self._skip_depth == 0:
                if tag in ("strong", "b"):
                    self._note_buf.append("<b>")
                elif tag in ("em", "i"):
                    self._note_buf.append("<i>")
                elif tag == "br":
                    self._note_buf.append("\n")
                elif tag in ("p", "div"):
                    self._note_buf.append("\n\n")
                elif tag == "li":
                    self._note_buf.append("\n• ")
                elif tag in ("ul", "ol"):
                    self._note_buf.append("\n")

    def handle_endtag(self, tag):
        if tag in ("h1", "h2") and self._in_title:
            self._in_title = False
            self.titles.append("".join(self._title_buf).strip())
            return
        if tag == "aside" and self._in_notes:
            self._in_notes = False
            self.notes.append("".join(self._note_buf))
            return
        if self._in_notes:
            if tag in self.SKIP and self._skip_depth > 0:
                self._skip_depth -= 1
            elif self._skip_depth == 0:
                if tag in ("strong", "b"):
                    self._note_buf.append("</b>")
                elif tag in ("em", "i"):
                    self._note_buf.append("</i>")
                elif tag in ("p", "div"):
                    self._note_buf.append("\n\n")

    def handle_data(self, data):
        if self._in_title:
            self._title_buf.append(data)
        elif self._in_notes and self._skip_depth == 0:
            # escape XML special chars for reportlab, but our own <b>/<i>
            # markers are appended separately so they survive
            self._note_buf.append(
                data.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def clean(text):
    """Tidy a note body: drop comments, collapse blank runs."""
    # Author's pseudo/real comments used to mute lines. By the time text
    # reaches here the angle brackets have been escaped to &lt; / &gt; (the
    # source already stored them as entities), so strip the escaped forms;
    # also strip any raw forms for safety. Both ASCII (--) and en-dash (–).
    for pat in (r"&lt;!--.*?--&gt;", r"&lt;!–.*?–&gt;",
                r"<!--.*?-->", r"<!–.*?–>"):
        text = re.sub(pat, "", text, flags=re.S)
    # normalise whitespace per line, collapse >1 blank line
    lines = [ln.strip() for ln in text.split("\n")]
    out, blanks = [], 0
    for ln in lines:
        if not ln:
            blanks += 1
            if blanks <= 1 and out:
                out.append("")
        else:
            blanks = 0
            out.append(ln)
    while out and out[-1] == "":
        out.pop()
    return out


def main():
    raw = open(SRC, encoding="utf-8").read()

    # title-slide note from data-notes attribute
    m = re.search(r'data-notes="([^"]*)"', raw)
    title_note = html.unescape(m.group(1)) if m else ""

    p = NotesExtractor()
    p.feed(raw)

    # titles[0] is the deck/title-slide h1; the rest are h2 content slides.
    deck_title = p.titles[0] if p.titles else "Speaker notes"
    slide_titles = p.titles[1:]

    # build ordered (title, lines) sections
    sections = []
    if title_note.strip():
        sections.append((deck_title, clean(
            title_note.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))))
    for title, note in zip(slide_titles, p.notes):
        lines = clean(note)
        if lines:               # skip slides whose note is empty (e.g. Questions)
            sections.append((title, lines))

    # ---- PDF ----
    styles = getSampleStyleSheet()
    h_doc = ParagraphStyle("DocTitle", parent=styles["Title"],
                           fontName="Lato-Bold", fontSize=20, leading=24,
                           textColor=HexColor("#0065BD"), spaceAfter=4)
    h_sub = ParagraphStyle("DocSub", parent=styles["Normal"],
                           fontName="Lato-Italic", fontSize=10, leading=13,
                           textColor=HexColor("#555555"), spaceAfter=18)
    h_slide = ParagraphStyle("Slide", parent=styles["Heading2"],
                             fontName="Lato-Bold", fontSize=13.5, leading=17,
                             textColor=HexColor("#0065BD"),
                             spaceBefore=14, spaceAfter=6)
    body = ParagraphStyle("Body", parent=styles["Normal"],
                          fontName="Lato", fontSize=11.5, leading=16,
                          alignment=TA_LEFT, spaceAfter=6)

    story = [Paragraph("Speaker notes", h_doc),
             Paragraph(deck_title, h_sub)]
    for i, (title, lines) in enumerate(sections, 1):
        story.append(Paragraph(f"{i}. {title}", h_slide))
        for ln in lines:
            if ln:
                story.append(Paragraph(ln, body))
            else:
                story.append(Spacer(1, 4))

    doc = SimpleDocTemplate(
        OUT, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=1.8 * cm, bottomMargin=1.8 * cm,
        title="Speaker notes — " + deck_title)
    doc.build(story)
    print(f"Wrote {OUT}  ({len(sections)} slide notes)")


if __name__ == "__main__":
    main()
