# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This folder hosts the **bachelor's thesis defense presentation** for *Generování trajektorií pro redundantní svařovací robot s polohovadlem* (CTU FEE, Department of Cybernetics, Xuan Dinh Nguyen, supervisor Ing. Vladimír Smutný, Ph.D.).

> ⚠️ **Active deliverable: `presentation_en.qmd` (English slides) only.**
> From now on, **only edit `presentation_en.qmd`**. The Czech version `presentation.qmd` is **frozen** — do **not** modify it unless the user explicitly says "update the Czech version" / "uprav českou verzi". Speaker notes inside `presentation_en.qmd` may stay in Czech (the talk is delivered in Czech); only the slide text is in English.

The legacy Beamer files (`presentation.tex`, `presentation.pdf`, `presentation_plan.md`, `build.sh`) are kept as **content reference only** — they were the earlier English Beamer draft. Do not edit them unless the user explicitly asks.

Do **not** modify code in `../2dof_positioner/` or thesis chapters in `../bachelor_writing/` from here. This directory is presentation-only.

## Hard Constraints for the Talk

| Constraint | Value |
|---|---|
| Slot length | 10 minutes total |
| Talk length target | **~8 minutes** (≥2 min headroom for Q&A) |
| Slide count | **9 slides** including title — *do not add more.* Density over count. |
| Language | **English** slide text, **Czech** speaker notes (talk delivered in Czech) |
| Q&A handling | The **final slide** is a **plain "Questions" slide** (no background) — the speaker takes questions in front of it. *(Earlier it had a looping video background; the user removed it. Don't re-add without asking.)* |
| Style | Match thesis terminology — see *Czech terminology* below. |

When restructuring, **cut content rather than add**. If a slide grows too dense, drop bullets — do not split it into two slides.

## Build

Quarto **1.9.37** is installed. `build.sh` renders the **English** deck (the Czech steps are commented out — `presentation.qmd` is frozen) and only **edit** `presentation_en.qmd`. Every `build.sh` run now produces **four** outputs: the self-contained `.html`, a slide `.pdf`, a notes-only `.pdf`, **and a `.pptx` PowerPoint** (always — not just on demand). Canonical commands:

```bash
./build.sh                              # render EN → .html + slide .pdf + notes .pdf + .pptx
./build.sh zip                          # the above + bundle into presentation_YYYYMMDD_HHMM.zip
quarto preview presentation_en.qmd      # live-reload preview of the English deck (active deliverable)
python3 make_pptx.py                    # PowerPoint only (needs a freshly rendered .html; build.sh runs this)
```

The HTML output is a **single self-contained file** (`embed-resources: true` in the YAML header) — figures, CSS, JS inlined. The Results `.webm` clips are *not* inlined; they stay in `figures/` and must travel with the HTML. The `zip` mode bundles HTML + both PDFs + the PPTX + `assets/` + `figures/` so everything travels together. (`assets/` is currently empty — the Q&A slide is a plain slide with no background video; see *Q&A slide* below.)

### PowerPoint (.pptx) output — **hybrid: image figure-slides + native text slides**

> ⚠️ We deliberately do **not** use Quarto's native `--to pptx`. It ignores `custom.scss` (no CTU-blue, wrong fonts), **drops every raw `{=html}` block** (the Results media), and splits multi-figure slides into ugly untitled continuation slides. Don't "fix" the PowerPoint by adding a `pptx:` format block; that brings the broken native writer back.

Instead, **`make_pptx.py`** builds a **hybrid** `.pptx` — *don't screenshot a slide that's just text* (per the user), but match the HTML exactly where there are figures:

- **Figure slides → exact image.** Slides whose rendered HTML contains an `<img>`/`<video>` (Introduction, Method, IK, Torch, Positioner, Results) **plus the designed title slide** are captured as a full-bleed headless-Chrome screenshot at 1280×720 (reveal.js auto-scales each slide to fit → one clean image). These match the reveal.js deck pixel-for-pixel. *(The title slide is text-only but is a designed solid-blue slide, so it's kept as an exact image, not rebuilt as text.)*
- **Text-only slides → real editable text.** System overview, Contribution and Questions are built as **native PowerPoint text**, styled to match the HTML: dark **Lato** title + light-blue underline rule, CTU-blue **bold** lead-ins (the deck renders `**strong**` as CTU-blue), numbered `.roadmap` items with indented `a)`/`b)`/`c)` sub-bullets, and a CTU-blue `N / 10` page number. Content is parsed from `presentation_en.qmd`. These slides are fully editable and small.
- **Screenshot hygiene.** Injects screenshot-only CSS into a temp copy of the HTML to hide the menu hamburger, nav arrows, and progress bar (keeps the slide-number footer). Figure-vs-text classification is by `<img>/<video>` presence per slide section; slide count = `1 + ## headings not inside an HTML comment`.
- **Speaker notes carry over.** The Czech `::: {.notes}` (and the title slide's `data-notes`) are read from the HTML and attached to every slide.
- **The Results video is embedded and plays.** The **Results** slide (an image slide) gets a movie shape over the two-column area showing `figures/results_compare.mp4` — a single **synced side-by-side** clip (the two RViz `.webm` renders composited by ffmpeg), with a poster frame so a PC that can't decode it still shows the right still. It's **click-to-play** (robust, valid PowerPoint XML); true autoplay+loop needs fragile timing-XML surgery that can't be verified without PowerPoint installed — add it only on request.
- **Derived asset:** `figures/results_compare.mp4` (+ `results_compare_poster.png`) is generated by **ffmpeg in `build.sh`**, only if missing. It is *not* referenced by the HTML deck. To refresh after changing a source `.webm`, delete the target and rebuild.
- **Dependencies:** headless Chrome, `ffmpeg`, and `python-pptx` (`pip install --user python-pptx`). All present on this machine.
- **Can't render .pptx here.** There's no LibreOffice/PowerPoint on this machine, so the native text slides' *appearance* can't be screenshot-verified — only their structure/styling (Lato, CTU-blue bold, numbering) is checked via the OOXML. Open the file once to eyeball the text slides after content changes.
- **Treat the .pptx as a fallback, not the canonical deck.** The reveal.js HTML is the defense deliverable (theming, speaker view, live `.webm` playback); the PPTX is for a defense PC that can't run the browser deck.

### Video in the PDF (embedded as an attachment)

A PDF cannot play video inline outside Adobe Acrobat/Reader, and even there it relied on Flash (removed 2021), so no mainstream viewer plays it — they show the still. Therefore the PDF keeps the **still frame** on the Results page (reveal's `.print-only` swap) and, after the Chrome `print-pdf` export, `build.sh` runs **`pdfattach`** (poppler-utils) to embed `figures/results_compare.mp4` *inside* the single PDF as an **attachment**. Any viewer can open/extract it from the attachments panel, and the video travels with the PDF. Verify with `pdfdetach -list presentation_en.pdf`. Re-attached on every build (the PDF is regenerated fresh each run, so no accumulation).

The legacy Beamer deck has been moved to `test/`. Do not edit it unless the user asks.

## Current Slide Map (snapshot — Czech deck)

> ⚠️ This table reflects the **frozen Czech deck** (`presentation.qmd`). The **active English deck** (`presentation_en.qmd`) has diverged — read its `##` headings directly for the current slide structure. Do not edit `presentation.qmd` to match.

| # | Title | Purpose | Target time |
|---|---|---|---|
| 1 | *(title slide)* | Metadata | 15 s |
| 2 | Motivace | Problem statement + cell photo | ~50 s |
| 3 | Přehled systému | Hardware + ROS 2 pipeline | ~60 s |
| 4 | Kinematika — analyticky tam, kde to jde | Analytical IK + IKT2 alignment equation | ~60 s |
| 5 | Klíčová myšlenka: relaxace svařovací pózy v 5 DOF | The thesis contribution: ξ, θ + α, β, γ | ~75 s |
| 6 | Optimalizace trajektorie — Ceres | 14 cost criteria + RRT-Connect | ~75 s |
| 7 | Experiment — testovací díl | Polygonal prism + 3 test scenarios | ~50 s |
| 8 | Výsledky — bez vs. s plnou relaxací | Side-by-side joint-trajectory plots | ~70 s |
| 9 | Závěr | Summary + "Děkuji za pozornost" | ~40 s |
| 10 | Dotazy *(video-background loop)* | Q&A backdrop, speaker answers in front | — |

Total content time ≈ **8 min**. Slide notes (`::: {.notes}`) carry the spoken script and time estimate — keep them updated when slide content shifts.

## Recommended Presentation Structure

When structuring the slides and story, follow this standard academic flow:

- **Introduction:** Motivation for the topic, research questions, important theoretical foundations
- **Methodology:** Which methods were used?
- **Results:** The most important results, nicely presented (e.g., as graphics)
- **Discussion:** Further interpretation of the results, critique of methods
- **Outlook:** What could be researched further?
- **Conclusion:** Take-Home-Message

## Q&A slide (final slide)

The final slide is a **plain Q&A slide** — just the heading, no background video or image:

```markdown
## Questions {transition="zoom"}
```

This is a deliberate change from an earlier design that put a looping `background-video` here. The user asked for a plain slide ("only for questions, no background"), so:

- There is **no `assets/loop.mp4`** anymore — `assets/` is empty. Don't reintroduce a Q&A background video unless the user asks.
- The slide renders identically in HTML, PDF and PPTX (white slide, dark "Questions" title, slide number).

If the user later wants a video/animation behind the Q&A again, the reveal.js attribute is `## Questions {background-video="assets/loop.mp4" background-video-loop="true" background-video-muted="true" background-video-size="cover"}` (drop a silent ≤5 MB MP4 at `assets/loop.mp4`); see git history for the previous `.qa` white-title CSS and poster setup. Ask which clip first.

## Source Material

Two upstream projects feed this presentation. Read them; do not edit them.

### `../bachelor_writing/` — the thesis itself
- `main.tex` — metadata, abstract (EN + CZ), keywords. Authoritative title and author info. The Czech abstract there is the canonical wording bank for Czech terminology.
- `chapters/` — one `.tex` per chapter. Chapters that map onto slides:
  - `system_description.tex` → slide 3
  - `kinematics.tex` → slides 4–5 (IKT2 alignment equation, 5-DOF relaxation, frame cascade)
  - `trajectory_optimization.tex` → slide 6 (Ceres cost vector, relaxation residual)
  - `results.tex` → slides 7–8 (3 test scenarios on the polygonal prism)
- `figures/` — original copies of figures used in the thesis. **Do not edit these here.** When the presentation needs a figure, **copy** it from `../bachelor_writing/figures/` into the local `presentation/figures/` folder (see *Local figures* below) so the deck remains self-contained.
- `bachelor_writing/CLAUDE.md` — fuller technical reference (joint table, 14 Ceres cost criteria, frame naming, recent implementation changes). Consult it before adjusting equations or naming frames.

### `../2dof_positioner/` — the implementation
- `CLAUDE.md` and `ARCHITECTURE.md` in that repo are authoritative for: package layout, the Ceres parameter vector (6 parameters, 14 residual blocks), IKT2/IKT6 split, OMPL RRT-Connect rapid moves.

## Local figures workflow

Figures are kept **locally** in `figures/` rather than referenced across the directory boundary. To add a new figure:

```bash
cp ../bachelor_writing/figures/<name>.png figures/
# then reference it in presentation_en.qmd as: figures/<name>.png
```

Currently in `figures/`:

| File | Slide |
|---|---|
| `system_overview.png` | 2 — Motivace |
| `weld_orientation_angles.png` | 5 — Relaxace svařovací pózy |
| `experiment_weldmodel1.png` | 7 — Testovací díl |
| `workpiece1_withoutRelax_jointVecs.png` | 8 — Výsledky (left) |
| `workpiece1_withAllRelax_jointVecs.png` | 8 — Výsledky (right) |

If the upstream thesis figure changes, **re-copy it** — there is no symlink, so `figures/` can drift from `../bachelor_writing/figures/` if you forget.

**Derived (whitespace-trimmed) figures:** `arm_relaxation_b_trim.png` (*Torch relaxation* slide) and `positioner_relaxation_angles_trim.png` (*Positioner relaxation* slide) are their `*.png` sources with the baked-in border whitespace cropped so the figure's margins are thinner. (`arm_relaxation_b` had a noticeable border; `positioner_relaxation_angles` had only ~3% — trim there is near-cosmetic.) Regenerate after re-copying the source:

```bash
cd figures
convert arm_relaxation_b.png            -fuzz 5% -trim +repage arm_relaxation_b_trim.png
convert positioner_relaxation_angles.png -fuzz 5% -trim +repage positioner_relaxation_angles_trim.png
```

`figures/` also holds the Results-slide media (not copied from upstream): the RViz renders `workpiece1_non_relax.webm` / `workpiece1_relax.webm` (shown on screen) and their `*_still.png` print fallbacks, plus the **build-generated** `results_compare.mp4` (synced side-by-side — embedded & playable in the PPTX, and attached inside the PDF) and `results_compare_poster.png`. The latter two are regenerated by `build.sh` if missing — delete them to refresh after changing a source `.webm`.

## Frame & Equation Conventions (must match thesis verbatim)

- Workpiece-attached frame: `workpiece_mount` (underscore form). `weld_flange` / `weldment_mount` are **retired** and must not appear.
- Shared `weld` frame is the terminal of both the positioner-relaxation and arm-relaxation chains.
- `arm_flange` = Cloos `Arm_6` (IKT6 chain tip). The welding-torch tip is `torch`.
- Rotations are **"multiplied in frame X"** — never *pre-multiplied* / *post-multiplied*. In Czech: "*násobeno v rámci X*", nikdy "*předem/po-násobeno*".

## Czech Terminology (use consistently across slides)

| English | Czech |
|---|---|
| robotic welding | robotické svařování |
| redundant robot / 9-DOF system | redundantní robot / 9-osý systém |
| positioner | polohovadlo |
| inverse kinematics (IK) | inverzní kinematika |
| analytical (closed-form) | analytická (v uzavřeném tvaru) |
| trajectory optimisation | optimalizace trajektorie |
| objective / cost function | účelová funkce |
| manipulability | manipulovatelnost |
| relaxation (of weld pose) | relaxace (svařovací pózy) |
| work angle / travel angle | pracovní úhel / postupový úhel |
| torch spin | rotace kolem osy hořáku |
| weld seam | svar / svařovací šev |
| rapid move (G0) | přejezd / volný pohyb |
| collision-free | bezkolizní |
| joint limits | kloubové limity |
| smoothness | plynulost |
| configuration change | změna konfigurace |
| sampling-based planner | vzorkovací plánovač |

The Czech abstract in `../bachelor_writing/main.tex` is the canonical source — when in doubt, copy phrasing from there.

## Tone and Style

- Slides should be **visual first, bullet sparingly**. Equations only where they earn their place: the IKT2 alignment equation (slide 4), the relaxation residual (slide 6), the manipulability formula (slide 6). Everything else is a figure or a one-line summary.
- Figures live in the **local `figures/` folder** — slides reference them as `figures/<name>`. With `embed-resources: true`, Quarto inlines them into the final HTML.
- Speaker notes (`::: {.notes}`) belong on **every** slide and carry the Czech spoken script + a time estimate. They are not shown to the audience — use reveal.js's speaker view (press `S` during the talk) to read them.

## Files in this Directory

| File | Role |
|---|---|
| `presentation_en.qmd` | **Active deliverable.** English Quarto/reveal.js deck. **Only edit this file.** Speaker notes inside may stay in Czech. |
| `presentation_en.html` | Rendered output of the English deck (self-contained). Open directly in a browser. |
| `presentation.qmd` | **Frozen** Czech version. Do not edit unless the user explicitly asks for a Czech-version change. |
| `presentation.html` | Rendered output of the (frozen) Czech deck. Still built by `build.sh` for archival. |
| `assets/` | **Empty.** Previously held the Q&A `loop.mp4`; the Q&A slide is now plain (no background). Kept because the YAML/reference docs still mention an `assets/` path and `zip` bundles it. |
| `figures/` | Local copies of thesis figures used in the deck. Copied from `../bachelor_writing/figures/` so the presentation folder is self-contained. |
| `custom.scss` | Custom reveal.js theme (CTU-blue accents). Layered on the `simple` base via `theme: [simple, custom.scss]`. Needed at render time; the compiled CSS is inlined into the self-contained HTML. Sets the body font to **Lato** (`$font-family-sans-serif`). |
| `lato-font.html` | Embedded **Lato** webfont — base64 WOFF2, subset to Latin + Latin-Extended-A (full Czech diacritics: ě š č ř ž ů ď ť ň). Injected via `include-in-header: lato-font.html` in the YAML so the font travels inside the self-contained HTML and renders offline on the defense PC. **Why a separate file:** Quarto's SCSS preprocessor throws `SCSSParsingError` on large `url(data:…)` strings, so the `@font-face` rules cannot live in `custom.scss`. Needed at render time; do not delete. Regenerate from the local `/usr/share/fonts/truetype/lato/*.ttf` via `fonttools` subsetting if Lato weights change. |
| `pause-videos.html` | **Pause-screen video wall.** Injected via `include-after-body: pause-videos.html`. reveal.js toggles "pause" (a plain black screen) on **b / v / .**; instead of black, this shows the deck's own clips (intro welding render + the two RViz results clips) **one after another as a looping playlist** (one full-size clip at a time). On reveal's `paused` event the script **clones** the deck's `<video>` elements into a full-screen `#pause-videos` overlay (so nothing is embedded twice and the wall auto-tracks whatever videos the deck has), then plays them in sequence — when the active clip `ended`s it advances to the next, wrapping back to the first so the sequence loops; on `resumed` it stops and clears them. The overlay CSS lives in `custom.scss` (`#pause-videos`, hidden by default → never shows on a slide, in the PDF/print export, or in the PPTX screenshots). Needed at render time; its content is inlined into the self-contained HTML. |
| `build.sh` | `./build.sh` generates the ffmpeg video assets (if missing), then renders the EN deck to HTML + slide PDF + notes PDF + **PPTX** (built on every run via `make_pptx.py`); `./build.sh zip` also produces a timestamped `presentation_YYYYMMDD_HHMM.zip` bundle (HTML + both PDFs + PPTX + `assets/` + `figures/`). |
| `make_pptx.py` | Builds the **hybrid PowerPoint** — figure slides as exact headless-Chrome screenshots, text-only slides as native CTU-blue/Lato editable text (parsed from the `.qmd`), Czech notes attached, and the **Results comparison video** embedded (click-to-play, poster). See *PowerPoint (.pptx) output* above. Needs `python-pptx` + Chrome; run after the HTML render. |
| `make_notes_pdf.py` | Extracts the Czech `::: {.notes}` speaker script from the rendered HTML into `presentation_en_notes.pdf` (reportlab, Lato font). Run by `build.sh`. |
| `beamer_reference.md` | Reference for PDF/Beamer output: the reveal print-to-PDF route (what `build.sh` does) vs. a `--to beamer` LaTeX build, what styling/video survives each, and how to add a `beamer:` format block. Consult before any Beamer/PDF-export request. |
| `presentation_*.zip` | Generated bundle(s) for transferring to the defense PC. Safe to delete; rebuilt on demand. |
| `presentation_plan.md` | Earlier 10-slide plan for the Beamer version. Useful as a content checklist but **over-targets slide count** for the Quarto deck. |
| `test/` | Archived legacy English Beamer deck (`presentation.tex`, `.pdf`, latexmk artefacts). Reference only. |

## Quarto reveal.js Feature Reference

Quick-reference for the reveal.js features available in this deck. Source: <https://quarto.org/docs/presentations/> (themes, revealjs, advanced). Syntax is Quarto-flavoured Markdown; per-slide options go in `{...}` after the `##` heading.

### Custom theme (SCSS)

Apply a base theme + a custom SCSS layer (what this deck does):

```yaml
format:
  revealjs:
    theme: [simple, custom.scss]   # base theme + overrides
```

Built-in bases: `beige blood dark default dracula league moon night serif simple sky solarized`.

A custom `.scss` file has **two sections**:

```scss
/*-- scss:defaults --*/
$body-bg: #fff;                    // Sass variables: colours, fonts, sizes
$link-color: #0065BD;
$presentation-heading-color: #1a1a1a;
$font-family-sans-serif: "Source Sans Pro", sans-serif;

/*-- scss:rules --*/
.reveal .slide h2 { border-bottom: 2px solid #0065BD; }   // raw CSS rules
```

- `scss:defaults` = `$`-variables (must usually come **before** rules). Key ones: `$body-bg`, `$body-color`, `$link-color`, `$selection-bg`, `$presentation-heading-color`, `$presentation-heading-font`, `$presentation-heading-font-weight`, `$presentation-font-size-root`, `$code-block-bg`, `$code-block-font-size`.
- `scss:rules` = CSS; target slide content with the `.reveal .slide` prefix.
- This deck's custom classes (`.kp`, `.takehome`, `.roadmap`) live in `custom.scss`. **Add new styling there, not as inline `<style>` blocks** — a raw `<style>`/content block placed *before* the first `##` heading renders as a stray blank slide.

### Transitions

```yaml
format:
  revealjs:
    transition: fade          # none | fade | slide | convex | concave | zoom
    transition-speed: default # default | fast | slow
```

Per-slide override: `## Title {transition="zoom" transition-speed="slow"}`. (Deck default: `fade`.)

### Incremental reveal & fragments

Global incremental bullets: `incremental: true` (this deck keeps it `false`). Per-block:

```markdown
::: {.incremental}
- Revealed one by one
:::

::: {.nonincremental}
- Shown all at once (when global incremental is on)
:::
```

Manual pause between any content: a line with `. . .`

Fragments (fine-grained step-in effects):

```markdown
::: {.fragment .fade-in}
Appears on next click
:::

::: {.fragment .highlight-red fragment-index=2}
Controls order with fragment-index
:::
```

Effect classes: `fade-in fade-out fade-up fade-down fade-left fade-right fade-in-then-out fade-in-then-semi-out semi-fade-out grow shrink strike highlight-red highlight-green highlight-blue highlight-current-red/green/blue`. (Deck uses `.fragment .fade-in` for the closing take-home banner.)

### Columns / layout

```markdown
:::: {.columns}
::: {.column width="55%"}
left
:::
::: {.column width="45%"}
right
:::
::::
```

### Slide backgrounds

```markdown
## Title {background-color="#f7f7f7"}
## Title {background-image="figures/x.png" background-size="cover"}
## Title {background-gradient="linear-gradient(to bottom,#283b95,#17b2c3)"}
## Title {background-iframe="https://..."}
## Dotazy {background-video="assets/loop.mp4" background-video-loop="true" background-video-muted="true" background-video-size="cover"}
```

(`background-video` is shown here only as a generic reveal.js example — the active English deck's Q&A slide is now **plain**, no background; see *Q&A slide* above.)

### Sizing & overflow

- `## Title {.smaller}` — shrink text on a dense slide; global `smaller: true` for the whole deck.
- `## Title {.scrollable}` — allow vertical scroll instead of overflow; global `scrollable: true`.
- `.r-stretch` resizes an image/video to fill the remaining vertical space; `auto-stretch` applies it to a slide's sole image automatically. **This deck sets `auto-stretch: false`** — it broke figures inside `.columns` (r-stretch pulled them out of the column). Images are sized by their explicit `width=` instead.
- **Columns gotcha:** `custom.scss` forces `.reveal .columns { display: flex !important }` + `.column { min-width: 0 }`. Without it some slides rendered `.columns` as `display:inline`, stacking the columns vertically and pushing figures off the bottom. Don't remove that rule.

### Auto-animate (matched-element morphing)

Put `auto-animate=true` on two consecutive slides; matching elements tween between them:

```markdown
## {auto-animate=true}
$$ a = b $$

## {auto-animate=true}
$$ a = R_z(q_8)\,b $$   <!-- morphs from the previous equation -->
```

Tuning: `auto-animate-easing`, `auto-animate-duration` (s), `auto-animate-delay`. Pair non-identical elements explicitly with matching `data-id="..."`. Combine with `.absolute` + `top/left/width/height` to animate position. *Not yet used here — candidate for the IKT2 equation build-up if a slide ever needs it (without adding a slide, since auto-animate consumes two `##` headings).*

### Code line highlighting

```` ```{.python code-line-numbers="1|3-4|5"} ```` — step through highlighted line ranges on successive clicks. (Deck currently uses only a plain pipeline code block, no highlighting.)

### Speaker notes & presenting

```markdown
::: {.notes}
Spoken Czech script + time estimate.
:::
```

Press **S** for speaker view (notes + timer + next-slide preview), **F** fullscreen, **O** overview, **B** blank/pause, **ESC** to exit. Every content slide here carries a `.notes` block — keep them updated when slide content shifts.

### Presenting (presenter mode)

Source: <https://quarto.org/docs/presentations/revealjs/presenting.html>.

```yaml
format:
  revealjs:
    footer: "Xuan Dinh Nguyen · Obhajoba bakalářské práce · ČVUT FEL"  # standing line on every slide
    logo: figures/logo.png      # bottom-right; only add if the file exists
    menu:                       # slide menu (press M)
      side: left
      numbers: true
    preview-links: auto         # open external links in an in-slide iframe
    slide-number: c/t           # already set
```

- **Footer / logo** show on every slide. Disable per slide with `## Title {footer=false}`. (This deck's `footer` is commented out in the YAML, so nothing shows; the styling lives in `custom.scss` `.reveal .footer` for when it's re-enabled.)
- **Per-slide footer override:** a `::: footer` div at the bottom of a slide.
- **Navigation:** arrows/Space next, **P** previous, **M** menu, **E** then Ctrl+P to export PDF (landscape, no margins, background graphics on; or append `?print-pdf` to the URL).
- **Code line highlighting:** ```` ```{.bash code-line-numbers="|1|2|3|4"} ```` steps through line ranges on each click — used on the pipeline block in *Přehled systému*. `|` starts with nothing highlighted; ranges like `2-3` or `7,9` also work.

> ⚠️ **Chalkboard is OFF and must stay off.** The `chalkboard:` plugin (draw on slides with **B**/**C**) is **incompatible with `embed-resources: true`** — Quarto errors with *"RevealChalkboard is not compatible with self-contained output."* The self-contained single-file HTML is a hard requirement here, so chalkboard cannot be enabled without giving that up. If live annotation is ever needed, use an external screen-annotation tool instead.
