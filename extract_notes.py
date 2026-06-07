#!/usr/bin/env python3
"""Extract all speaker notes from presentation_en.qmd into a printable script."""
import re
import sys

input_file = sys.argv[1] if len(sys.argv) > 1 else 'presentation_en.qmd'
src = open(input_file, encoding='utf-8').read()

# --- Title-slide note lives in the YAML `data-notes` attribute ---
title_note = ''
m = re.search(r'data-notes:\s*"(.*?)"\s*\n', src, flags=re.DOTALL)
if m:
    tn = m.group(1)
    tn = tn.replace('<br><br>', '\n').replace('<br>', '\n')
    tn = tn.replace('<b>', '**').replace('</b>', '**')
    out = []
    for ln in tn.split('\n'):
        ln = ln.strip()
        if not ln:
            continue
        if ln.startswith('•'):          # bullet •
            ln = '- ' + ln[1:].strip()
        out.append(ln)
    title_note = '\n'.join(out)

# --- Strip HTML comments so commented-out slides/notes are skipped ---
body = re.sub(r'<!--.*?-->', '', src, flags=re.DOTALL)
body = re.sub(r'\A---\n.*?\n---\n', '', body, flags=re.DOTALL)  # drop YAML

sections, current, in_notes, buf = [], None, False, []
for line in body.split('\n'):
    h = re.match(r'^##\s+(.*)$', line)
    if h and not in_notes:
        current = re.sub(r'\s*\{[^}]*\}\s*$', '', h.group(1)).strip()
        continue
    if line.strip() == '::: {.notes}':
        in_notes, buf = True, []
        continue
    if in_notes and line.strip() == ':::':
        in_notes = False
        content = '\n'.join(buf).strip()
        if content:
            sections.append((current, content))
        continue
    if in_notes:
        buf.append(line)

# --- Assemble the printable .qmd ---
entries = ([('Titulní slide', title_note)] if title_note else []) + sections

doc = ['''---
title: "Poznámky k obhajobě — čtecí text"
subtitle: "Generování trajektorií pro redundantní svařovací robot · Xuan Dinh Nguyen"
lang: cs
format:
  typst:
    papersize: a4
    margin: { x: 2cm, y: 2cm }
    fontsize: 12pt
---
''']
for i, (title, content) in enumerate(entries, start=1):
    doc.append(f'# {i}. {title}\n\n{content}')

import os
out_qmd = input_file.replace('.qmd', '_notes.qmd')
open(out_qmd, 'w', encoding='utf-8').write('\n\n'.join(doc) + '\n')
print(f'OK: {len(entries)} slidů → {out_qmd}')
for i, (t, _) in enumerate(entries, 1):
    print(f'  {i}. {t}')
