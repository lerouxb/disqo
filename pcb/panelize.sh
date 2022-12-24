#!/usr/bin/env bash

kikit panelize \
    --source 'stack: 4layer; tolerance: 10mm;' \
    --layout 'grid; rows: 1; cols: 1; space: 0mm;' \
    --tabs 'fixed; vwidth: 3mm; hwidth: 5mm; hcount: 0; vcount: 2; ' \
    --cuts 'mousebites; drill: 0.5mm; spacing: 1mm; offset: 0.2mm; prolong: 0.5mm;' \
    --framing 'tightframe; width: 2mm; space: 3mm; cuts: h; mintotalwidth: 50mm; mintotalheight: 50mm;' \
    --tooling '4hole; hoffset: 2.5mm; voffset: 2.5mm; size: 2mm; paste: true;' \
    --fiducials '3fid; hoffset: 5mm; voffset: 2.5mm; coppersize: 2mm; opening: 1mm;' \
    --text 'simple; text: JLCJLCJLCJLC; anchor: mt; voffset: 2.5mm; hjustify: center; vjustify: center;' \
    --post 'millradius: 1mm;' \
    disqo.kicad_pcb disqo-stencil.kicad_pcb
