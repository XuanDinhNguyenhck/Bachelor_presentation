# PDF / Beamer Reference for this Deck

> Scope: how to turn `presentation_en.qmd` into a PDF, the difference between the
> **reveal.js print-to-PDF** path (what `build.sh` already does) and the
> **Beamer** path (a separate LaTeX engine), and what survives each route.
> Sources: <https://quarto.org/docs/presentations/beamer.html> and
> <https://quarto.org/docs/reference/formats/presentations/beamer.html>.

---

## TL;DR — answering the three questions

1. **"When I export to PDF, will it look the same as the HTML?"**
   - **reveal.js → PDF (the current `build.sh` route):** *Yes, essentially identical.*
     It literally prints the HTML deck (your `custom.scss`, CTU-blue theme, Lato
     font, columns, figures) one slide per page. The only change is that it is
     **static**: fragments collapse to their final state, transitions/animations
     are gone.
   - **Beamer → PDF (`--to beamer`):** **No — completely different look.** Beamer
     re-renders the Markdown through LaTeX with its *own* theme system. None of
     `custom.scss`, `lato-font.html`, reveal classes (`.roadmap`, `.kp`,
     `.takehome`), `background-color`/`background-video`, transitions, or
     `.smaller`/`.scrollable` carry over. You get a stock Beamer theme unless you
     re-style it in LaTeX.

2. **"Better or worse?"** Neither is universally better — it's a trade-off:
   | | reveal print-to-PDF (current) | Beamer PDF |
   |---|---|---|
   | Matches your designed deck | ✅ pixel-faithful | ❌ different theme entirely |
   | Math / equations | good (raster of MathJax) | ✅ native LaTeX, razor-sharp |
   | Text crispness | browser-rendered | ✅ true vector text |
   | File size | larger (embedded raster) | usually smaller |
   | Effort | zero (already wired up) | high (re-theme to look like CTU deck) |
   | Animations / fragments | frozen at final state | frozen at final state |
   | **Video (Q&A loop)** | **frozen still frame** | **does not appear at all** |

3. **"Is the video included in the PDF?"** **No — for either route.** A PDF page
   is a static image; it cannot play `assets/loop.mp4`.
   - In the **reveal print** PDF the Q&A slide becomes a frozen frame (the
     video's first/poster frame, or just the dark fallback background).
   - In **Beamer** the `background-video` attribute is reveal-only, so the video
     simply isn't there.
   - ⇒ The looping Q&A backdrop only works from the **HTML**. Keep the HTML as the
     primary defense artifact; treat any PDF purely as an offline/print fallback.
   - (There is a fragile LaTeX hack — `\movie` / the `media9` package — that some
     desktop PDF readers can play, but it is viewer-dependent, not produced by
     Quarto automatically, and not worth it here.)

**Bottom line for the defense:** present from `presentation_en.html` (video +
styling live). The `build.sh` PDF is your safe static backup. Don't switch this
deck to Beamer unless someone specifically needs a LaTeX/print artifact and
accepts losing the reveal styling.

---

## The three PDF routes (and which one we use)

| Route | Command | Engine | Looks like the HTML? |
|---|---|---|---|
| **A. reveal print-to-PDF** *(current `build.sh`)* | headless Chrome on `…html?print-pdf` | reveal.js print CSS | ✅ yes (static) |
| **B. Beamer** | `quarto render presentation_en.qmd --to beamer` | LaTeX/Beamer | ❌ no (stock Beamer theme) |
| **C. PowerPoint fallback** | `quarto render presentation_en.qmd --to pptx` | pandoc → pptx | ❌ no (loses video bg) |

`build.sh` uses **Route A** today (build.sh:33–54): it renders `--to revealjs`,
then drives headless Chrome with `?print-pdf` + `--print-to-pdf`. You can also do
Route A by hand: open `presentation_en.html?print-pdf` in Chrome → Ctrl+P → Save
as PDF, **Landscape, margins None, "Background graphics" ON**.

---

## How to generate a Beamer PDF (Route B)

### Prerequisites
Beamer compiles via LaTeX, so you need a TeX distribution. Quarto can install a
minimal one:

```bash
quarto install tinytex          # one-time: gives Quarto its own LaTeX
```

(or use a system TeX Live / MiKTeX). Without TeX, `--to beamer` fails.

### Minimal one-off render

```bash
quarto render presentation_en.qmd --to beamer
# → presentation_en.pdf (overwrites the reveal print-PDF of the same name!)
```

> ⚠️ Both routes default to `presentation_en.pdf`. If you ever generate a Beamer
> PDF, set a distinct `output-file` (see below) so it doesn't clobber the
> reveal print-PDF that `build.sh` makes.

### Recommended way: a dedicated Beamer format block

Quarto lets one `.qmd` declare multiple formats. To keep the reveal deck intact
**and** offer a Beamer build, add a `beamer:` sibling under `format:` (do this
only if a Beamer artifact is actually requested — it is not the active
deliverable):

```yaml
format:
  revealjs:            # active deliverable — unchanged
    theme: [simple, custom.scss]
    embed-resources: true
    # …existing options…
  beamer:              # optional LaTeX/print build
    aspectratio: 169          # 16:9 to match the 1280×720 reveal deck
    theme: default            # or Madrid / Frankfurt / metropolis…
    colortheme: default
    navigation: empty         # hide the nav dots
    section-titles: false
    output-file: presentation_en_beamer.pdf   # avoid clobbering the reveal PDF
    pdf-engine: xelatex       # xe/lua needed for custom mainfont (Lato)
    mainfont: "Lato"          # closest you can get to the reveal deck's font
    incremental: false
    fig-align: center
    keep-tex: true            # keep the .tex to tweak LaTeX by hand
```

Then build the Beamer one explicitly:

```bash
quarto render presentation_en.qmd --to beamer
```

### Beamer YAML option reference (the ones that matter here)

**Theme / appearance**
- `theme` — Beamer theme: `default`, `AnnArbor`, `Madrid`, `Frankfurt`,
  `metropolis` (needs the `beamertheme-metropolis` package), …
- `colortheme` — e.g. `default`, `lily`, `beaver`, `dolphin`.
- `fonttheme`, `innertheme`, `outertheme` — finer-grained theme parts.
- `themeoptions:` — list of options passed to the theme.
- `aspectratio` — `169` (16:9), `43`, `1610`, `149`, `141`, `54`, `32`.
- `navigation` — `empty` | `frame` | `vertical` | `horizontal` (nav symbols).
- `section-titles` — `true`/`false`: auto section divider pages from `#` headings.
- `logo`, `titlegraphic`, `background-image`.
- `beameroption` — inject an extra `\setbeameroption{…}`.

**Slides / structure**
- `## heading` → one slide; `# heading` → a section divider; `---` → untitled slide.
- `slide-level` — which heading level starts a new slide.
- `incremental: true` or `::: {.incremental}` for step-by-step bullets;
  `. . .` (dots on their own line) inserts a manual pause.
- Frame classes on a heading: `## Title {.fragile}` (needed for verbatim/code),
  also `.allowframebreaks`, `.plain`, `.standout`, `.shrink`, `.label`.

**Columns** (same Markdown as reveal — this *does* port over):
```markdown
:::: {.columns}
::: {.column width="45%"}
left
:::
::: {.column width="55%"}
right
:::
::::
```

**Fonts** (require `pdf-engine: xelatex` or `lualatex`)
- `mainfont`, `sansfont`, `monofont`, `mathfont`, `fontsize`, `linestretch`.

**Code**
- By default Beamer sets `echo: false`. `code-line-numbers`, `syntax-highlighting`,
  `listings: true`. Any slide containing a code block needs `{.fragile}`.

**Figures / tables**
- `fig-align`, `fig-pos`, `fig-width`, `fig-height`, `fig-format`,
  `tbl-colwidths`, `tbl-cap-location`.

**Includes / raw LaTeX**
- `include-in-header:` / `header-includes:` — inject preamble LaTeX (load
  packages, redefine colors to CTU blue `#0065BD`, etc.).
- `include-before-body:`, `include-after-body:`.
- Raw LaTeX in the body: ```` ```{=latex} … ``` ````.

**Rendering**
- `pdf-engine` — `xelatex` / `lualatex` (use these for `mainfont`), `pdflatex`,
  `latexmk`.
- `keep-tex: true` — keep the intermediate `.tex` to hand-edit LaTeX.
- `output-file` — set a distinct name (see clobber warning above).

---

## What carries over from the reveal deck to Beamer — and what doesn't

| Reveal feature in `presentation_en.qmd` | In Beamer? |
|---|---|
| `## Slide`, `:::: {.columns}` / `::: {.column width=…}` | ✅ yes |
| LaTeX math (`$$…$$`) | ✅ yes (native, sharper) |
| `::: {.notes}` speaker notes | ⚠️ become `\note{}` (needs a notes-on setup; not shown by default) |
| `::: {.incremental}`, `. . .` | ✅ yes |
| Code blocks | ✅ but the slide needs `{.fragile}` |
| `custom.scss` theme / CTU-blue accents | ❌ ignored — re-do via Beamer theme/colors |
| `lato-font.html` webfont | ❌ ignored — use `mainfont: "Lato"` + xelatex |
| `{background-color=…}`, `{background-image=…}` | ❌ reveal-only |
| **`{background-video=…}` (Q&A loop)** | ❌ reveal-only → **no video** |
| `transition`, fragments' `.fade-in` etc. | ❌ animations don't exist in PDF |
| `.smaller`, `.scrollable`, `.r-stretch`, `auto-stretch` | ❌ reveal-only sizing |
| Custom classes `.roadmap`, `.kp`, `.takehome`, `.intro-fig` | ❌ no effect (CSS classes) |
| `footer`, `logo`, `menu`, `slide-number` (reveal forms) | ❌ use Beamer equivalents |

**Practical takeaway:** porting to Beamer is a *re-theme*, not a render flag.
Budget time to recreate the CTU look (colors, font, layout) in LaTeX, and accept
that the video and all animation are gone.

---

## Quick recipes

```bash
# Current/default PDF (looks like the HTML, static, no video playback):
./build.sh                                   # → presentation_en.pdf via Chrome ?print-pdf

# Manual reveal print-to-PDF:
#   open presentation_en.html?print-pdf in Chrome → Ctrl+P → Save as PDF
#   (Landscape · margins None · Background graphics ON)

# Beamer PDF (different look; needs TeX; set output-file to avoid clobber):
quarto install tinytex                       # one-time
quarto render presentation_en.qmd --to beamer

# PowerPoint fallback (also loses video):
quarto render presentation_en.qmd --to pptx
```
