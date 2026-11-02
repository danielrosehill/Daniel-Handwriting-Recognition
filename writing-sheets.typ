// Printable handwriting collection sheets.
// Build: typst compile writing-sheets.typ   (Typst 0.14; reads ground-truth/pages.txt)
#set page(paper: "a4", margin: 18mm)
#set text(font: "DejaVu Sans", size: 10.5pt)

// ---- parse ground-truth/pages.txt -------------------------------------
#let pages = {
  let out = ()
  let cur = none
  for l in read("ground-truth/pages.txt").split("\n") {
    let m = l.match(regex("^=== (P\d+) ===$"))
    if m != none {
      if cur != none { out.push(cur) }
      cur = (code: m.captures.at(0), lines: ())
    } else if cur != none and l.trim() != "" {
      cur.lines.push(l)
    }
  }
  if cur != none { out.push(cur) }
  out
}

// Round 1: odd sheets unruled, even ruled. Round 2 swaps.
#let paper(code, round) = {
  let odd = calc.odd(int(code.slice(1)))
  if (round == 1) == odd { "UNRULED" } else { "RULED" }
}

#let circled(body) = h(4pt) + box(stroke: 1pt, radius: 50%, outset: (x: 4pt, y: 3pt), body) + h(4pt)

// ---- cover -----------------------------------------------------------
#text(size: 20pt, weight: "bold")[Handwriting collection: how to write]
#v(-4pt)
#text(size: 9pt, fill: gray)[github.com/danielrosehill/Daniel-Handwriting-Recognition]

#set par(spacing: 0.9em)

== Paper
- Any size from A6 (pocket notepad) to A4. A5 is ideal. Mixing sizes is good.
- Each sheet says RULED or UNRULED for round 1. Round 2 (optional) = same text on the other type.
- Ruled: rule gap of 8 mm or more, write on every line. Narrower, skip a line.
- Unruled: leave a clear gap (about one line height) between lines.
- Turn small paper landscape if a line won't fit across. White or cream paper; no graph paper.

== Pen
- Black (dark blue OK) ballpoint 0.7--1.0 mm or gel 0.5--0.7 mm. Ideally your everyday pen.
- Avoid fine 0.3--0.4 mm tips (faint in photos), pencil, and felt-tips that bleed.
- A second pen for round 2 makes the model more robust.

== Writing
+ Write the sheet code in the top-right corner and *draw a circle around it*, e.g. #circled[P07]. Round 2: #circled[P07-2]. The circle marks it as a label: it identifies the photo and is cropped out of the training data.
+ One printed line = one handwritten line. Never wrap a line or join two.
+ Copy exactly: capitals, punctuation, numbers. Don't copy the grey line numbers.
+ Write at your normal speed and style, not your neatest.
+ Run out of room? Continue on a new sheet: #circled[P07a], #circled[P07b] (round 2: #circled[P07-2a]). Lines stay whole and in order. Small paper often needs 2--3 sheets per page.
+ Mistake? Keep going. Report it later, e.g. "P07 line 4: wrote 'teh'".
+ Keep the circled code clear of the text, and leave about 1.5 cm margin around the edges.

== Photos
- One photo per sheet, phone flat above it, whole sheet in frame, no fingers on it.
- Daylight or even room light, no flash, dark plain background behind the paper.
- Upload to the Drive fe/ folder. File names don't matter; the circled code identifies each sheet.

// ---- one page per sheet --------------------------------------------------
#for p in pages {
  pagebreak()
  grid(
    columns: (1fr, auto),
    text(size: 34pt, weight: "bold", p.code),
    align(right)[
      #text(size: 13pt, weight: "bold")[Round 1: #paper(p.code, 1) paper] \
      #text(size: 10pt, fill: gray)[Round 2 (optional): #paper(p.code, 2)]
    ],
  )
  text(size: 9.5pt, fill: gray)[Top-right corner: write #circled[#p.code] (round 2: #circled(p.code + "-2")). One line below = one handwritten line.]
  v(10mm)
  set par(leading: 0.5em)
  for (i, l) in p.lines.enumerate() {
    grid(
      columns: (8mm, 1fr),
      column-gutter: 5mm,
      align(right, text(size: 11pt, fill: gray, str(i + 1))),
      text(font: "DejaVu Sans Mono", size: 15pt, l),
    )
    v(9mm)
  }
  place(bottom + center, dy: 8mm, text(size: 9pt, fill: gray)[#p.code -- #p.lines.len() lines -- mistakes: keep going and report page + line])
}
