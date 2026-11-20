### FORMAT: output surface

- **Rule FORMAT-1.** On a terminal that does not render Markdown extensions,
  use three formats. Draw flows, sequences, hierarchies, timelines and
  pipelines as ASCII art. Put grids, registers and memory maps in Markdown
  tables. Write math in Unicode inside a fenced block. On a surface that
  renders, use Mermaid, tables and LaTeX. Use inline SVG there only when you
  need pixel precision. In source comments, use ASCII art.
- **Rule FORMAT-2.** Align monospace art by display width: a wide East Asian
  character takes two columns, a box-drawing or arrow glyph one. Keep glyphs
  of ambiguous width out of aligned columns. Check every row's width before
  you output it.

