#!/usr/bin/env bash
# Build the Quarto presentation (English only — Czech version is frozen).
#
# Usage:
#   ./build.sh         Render EN deck → HTML + slide PDF + speaker-notes PDF + PPTX
#   ./build.sh zip     Render EN and bundle the HTML + PDFs + PPTX + assets/ into a .zip
#
# Each run produces:
#   - a self-contained .html (open directly in a browser; the canonical deck),
#   - a slide .pdf exported via headless Chrome (reveal.js print-pdf mode),
#   - a notes-only .pdf (Czech read-aloud script) extracted from the HTML, and
#   - a .pptx PowerPoint that LOOKS IDENTICAL to the HTML (see make_pptx.py).
# The .zip is what you copy to a USB stick / Drive for the defense PC.
#
# The .pptx is built by make_pptx.py as a HYBRID (not Quarto native): slides
# with a figure/video become a full-bleed screenshot of the rendered slide (so
# they match the HTML exactly), and text-only slides (System overview,
# Contribution, Questions) become real editable text styled CTU-blue/Lato. The
# Results comparison video is embedded so it plays in PowerPoint; ffmpeg builds
# that video (figures/results_compare.mp4) below.
#
# NOTE: Czech-version build steps are commented out below. To rebuild the
# frozen Czech deck, uncomment the lines marked with "# [CS frozen]".

set -euo pipefail

cd "$(dirname "$0")"

# English deck (active deliverable). The Czech deck variables are kept
# commented below in case the frozen Czech version ever needs a one-off rebuild.
# QMD_CS="presentation.qmd"          # [CS frozen]
# HTML_CS="presentation.html"        # [CS frozen]
# PDF_CS="presentation.pdf"          # [CS frozen]
QMD_EN="presentation_en.qmd"
HTML_EN="presentation_en.html"
PDF_EN="presentation_en.pdf"
NOTES_PDF="presentation_en_notes.pdf"
PPTX_EN="presentation_en.pptx"

# --- Generate the Results comparison video (ffmpeg) ------------------------
# figures/results_compare.mp4 = the two RViz .webm renders composited synced
# side-by-side on white, + a poster frame. Embedded (playable) in the .pptx.
# Generated only if missing — delete the target to refresh after a source change.
if command -v ffmpeg >/dev/null 2>&1; then
    SRC_NR="figures/workpiece1_non_relax.webm"; SRC_R="figures/workpiece1_relax.webm"
    if [[ ! -f figures/results_compare.mp4 && -f "$SRC_NR" && -f "$SRC_R" ]]; then
        ffmpeg -y -i "$SRC_NR" -i "$SRC_R" -filter_complex "\
            [0:v]scale=-2:680,pad=760:720:(ow-iw)/2:(oh-ih)/2:color=white[l];\
            [1:v]scale=-2:680,pad=760:720:(ow-iw)/2:(oh-ih)/2:color=white[r];\
            [l][r]hstack=inputs=2[s]" -map "[s]" -an -c:v libx264 \
            -profile:v high -pix_fmt yuv420p -crf 28 -preset veryfast -shortest \
            -movflags +faststart figures/results_compare.mp4 -loglevel error \
            && echo "asset: figures/results_compare.mp4"
    fi
    [[ ! -f figures/results_compare_poster.png && -f figures/results_compare.mp4 ]] \
        && ffmpeg -y -ss 6 -i figures/results_compare.mp4 -frames:v 1 figures/results_compare_poster.png -loglevel error \
        && echo "asset: figures/results_compare_poster.png"
else
    echo "WARNING: ffmpeg missing — the PowerPoint Results video won't be embedded."
fi

# --- Render HTML -----------------------------------------------------------
# quarto render "$QMD_CS" --to revealjs   # [CS frozen]
quarto render "$QMD_EN" --to revealjs

# --- Export PDF (headless Chrome, reveal.js ?print-pdf mode) ---------------
# Pick whatever Chromium-family browser is installed.
CHROME=""
for c in google-chrome google-chrome-stable chromium chromium-browser brave-browser; do
    if command -v "$c" >/dev/null 2>&1; then CHROME="$c"; break; fi
done

make_pdf() {
    local html="$1" pdf="$2"
    # ?print-pdf switches reveal.js into one-slide-per-page print layout.
    # --virtual-time-budget gives the deck's JS time to lay out before printing.
    if "$CHROME" --headless=new --disable-gpu --no-sandbox --hide-scrollbars \
            --no-pdf-header-footer --run-all-compositor-stages-before-draw \
            --virtual-time-budget=15000 \
            --print-to-pdf="$pdf" \
            "file://$PWD/${html}?print-pdf" >/dev/null 2>&1; then
        echo "PDF created: $pdf"
    else
        echo "WARNING: PDF export failed for $html — HTML is still fine. Export manually in Chrome (open ${html}?print-pdf, Ctrl+P → Save as PDF, Landscape, no margins, background graphics on)."
        return 1
    fi
}

if [[ -n "$CHROME" ]]; then
    # Don't let a PDF hiccup abort the build (HTML is the real deliverable).
    # make_pdf "$HTML_CS" "$PDF_CS" || true   # [CS frozen]
    make_pdf "$HTML_EN" "$PDF_EN" || true
else
    echo "WARNING: no Chrome/Chromium found — skipping PDF export. Install Chrome or export manually (open ${HTML_EN}?print-pdf, Ctrl+P → Save as PDF)."
fi

# --- Embed the Results video INSIDE the PDF (as an attachment) --------------
# A PDF can't play video inline outside Adobe Reader (and that needs Flash,
# removed in 2021), so the Results page keeps its still frame and we attach the
# .mp4 *inside* the single PDF instead. Any viewer can open/extract it from the
# attachments panel; the video then travels with the PDF. Regenerated each run.
if [[ -f "$PDF_EN" ]] && command -v pdfattach >/dev/null 2>&1 \
        && [[ -f figures/results_compare.mp4 ]]; then
    if pdfattach "$PDF_EN" figures/results_compare.mp4 "${PDF_EN}.tmp" >/dev/null 2>&1; then
        mv "${PDF_EN}.tmp" "$PDF_EN"
        echo "Embedded results_compare.mp4 inside $PDF_EN (attachments panel)."
    else
        rm -f "${PDF_EN}.tmp"
        echo "WARNING: could not attach the Results video to $PDF_EN — PDF is still fine."
    fi
fi

# --- Speaker-notes PDF (notes-only, extracted from the rendered HTML) -------
# make_notes_pdf.py reads $HTML_EN and writes the Czech read-aloud script to
# $NOTES_PDF. A failure here must not abort the build (decks are the real
# deliverable), so it's guarded like the slide-PDF step above.
if command -v python3 >/dev/null 2>&1 && [[ -f make_notes_pdf.py ]]; then
    python3 make_notes_pdf.py \
        || echo "WARNING: notes PDF generation failed — decks are still fine. (Need reportlab: pip install reportlab)"
else
    echo "WARNING: python3 or make_notes_pdf.py missing — skipping notes PDF."
fi

# --- PowerPoint (.pptx): hybrid (image figure-slides + native text slides) --
# make_pptx.py screenshots the figure slides from $HTML_EN with headless Chrome
# (exact HTML match) and builds the text-only slides as editable CTU-blue/Lato
# text, with Czech speaker notes and the playable Results comparison video.
# Guarded so a failure can't abort the build (HTML/PDF are the real deliverables).
if command -v python3 >/dev/null 2>&1 && [[ -f make_pptx.py ]]; then
    python3 make_pptx.py \
        || echo "WARNING: PPTX generation failed — HTML/PDF are still fine. (Need python-pptx + Chrome: pip install python-pptx)"
else
    echo "WARNING: python3 or make_pptx.py missing — skipping PPTX."
fi

# --- Optional zip bundle ----------------------------------------------------
if [[ "${1:-}" == "zip" ]]; then
    stamp="$(date +%Y%m%d_%H%M)"
    bundle="presentation_${stamp}.zip"

    # Keep assets/ and figures/ as subfolders so the Q&A video loop and any
    # non-inlined figures resolve correctly on the target machine. Figures
    # referenced from the .qmd are inlined by embed-resources, but shipping
    # figures/ alongside keeps the bundle self-explanatory if a deck is
    # ever re-rendered on the defense PC. PDFs are included when present.
    files=("$HTML_EN")
    # [[ -f "$PDF_CS" ]] && files+=("$PDF_CS")   # [CS frozen]
    [[ -f "$PDF_EN" ]] && files+=("$PDF_EN")
    [[ -f "$NOTES_PDF" ]] && files+=("$NOTES_PDF")
    [[ -f "$PPTX_EN" ]] && files+=("$PPTX_EN")
    zip -r "$bundle" "${files[@]}" assets/ figures/

    echo
    echo "Bundle ready: $bundle"
    echo "Copy it to USB, unzip on the defense PC, and open $HTML_EN in a browser."
fi
