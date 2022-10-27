#!/usr/bin/env bash

kikit panelize \
    --source 'stack: 4layer;' \
    --layout 'grid; rows: 2; cols: 2; space: 2mm;' \
    --tabs 'fixed; vwidth: 3mm; hwidth: 5mm; hcount: 1; vcount: 2;' \
    --cuts 'mousebites; drill: 0.5mm; spacing: 1mm; offset: 0.2mm; prolong: 0.5mm;' \
    --framing 'tightframe; width: 5mm; space: 3mm; cuts: h; mintotalwidth: 100mm; mintotalheight: 100mm;' \
    --tooling '4hole; hoffset: 2.5mm; voffset: 2.5mm; size: 1.5mm; paste: true;' \
    --fiducials '3fid; hoffset: 5mm; voffset: 2.5mm; coppersize: 2mm; opening: 1mm;' \
    --text 'simple; text: JLCJLCJLCJLC; anchor: mt; voffset: 2.5mm; hjustify: center; vjustify: center;' \
    --post 'millradius: 1mm;' \
    wristpad.kicad_pcb panel.kicad_pcb