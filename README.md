# Daniel Handwriting Recognition

Minimal viable pipeline to fine-tune a handwriting text recognition (HTR) model on one person's handwriting (Daniel's, English, print/cursive as it naturally comes).

Status (2026-11-02): **data collection stage.** No photos or training code yet.

## Approach

- **Model:** fine-tune [`microsoft/trocr-base-handwritten`](https://huggingface.co/microsoft/trocr-base-handwritten) (TrOCR, ~334M params). It reads **one line of text per image**, so the dataset is line crops paired with their text.
- **Why this works with little data:** the base model already reads English handwriting (trained on IAM). Adapting it to a single writer typically needs a few hundred lines, not thousands.
- **Ground truth:** you copy fixed, known text by hand, so every line's transcription is known in advance. No manual labelling.

## Data collection protocol

**Print or open [`writing-sheets.pdf`](writing-sheets.pdf)**: a cover page of instructions, then one page per sheet (P01-P20) showing exactly what to write. It is built with Typst from `writing-sheets.typ`, which reads `ground-truth/pages.txt` directly: `typst compile writing-sheets.typ` (Typst 0.14.2). Rebuild after editing the text.

### Paper

- **Any size from A6 to A4; A5 is ideal.** Mixing sizes is good: the model should cope with whatever paper is to hand.
- **Ruled vs unruled matters, so do both.** Rule lines are visual noise that the model has to learn to ignore, and real notes are written on both kinds. Round 1: odd sheets unruled, even sheets ruled (shown on each PDF page). Round 2 (optional, ~480 lines total): the same text on the other paper type, ideally another day and another pen.
- Ruled: rule gap of 8 mm or more, write on every line; narrower, skip a line. Unruled: leave about one line height between lines. Avoid graph paper.
- Small paper: turn it landscape if a line won't fit across, and continue onto extra sheets (`P07a`, `P07b`). Lines are never split or merged; order is preserved, so segmentation can still match lines to text.

### Pen

Black (dark blue OK) **ballpoint 0.7-1.0 mm or gel 0.5-0.7 mm**, ideally your everyday pen. Avoid fine 0.3-0.4 mm tips (faint in phone photos), pencil, and bleeding felt-tips.

### Writing rules

1. Sheet code in the top-right corner **with a circle drawn around it** (`P07`; round 2 `P07-2`; split sheets `P07a`, `P07-2b`). The circle marks it as a label: the pipeline reads it to identify the sheet, then crops it out so it never enters the training lines.
2. One printed line = one handwritten line. Copy exactly; skip the grey line numbers.
3. Normal speed and style, not your neatest.
4. Mistakes: keep going and report them as page + line + what was written; they go in `ground-truth/corrections.txt`.

### Photographing

One photo per sheet, phone flat above it, whole sheet in frame, no flash, dark plain background. Upload to the Drive `fe/` folder (or `photos/raw/`); the corner code identifies each photo.

## Pipeline (to build once photos exist)

1. `photos/raw/` → deskew + crop page (OpenCV); detect the circled sheet code (top right), read it, then mask it out.
2. Line segmentation: horizontal projection profile, constrained to the 12 known lines per page (summed across split sheets). Ruled sheets need rule-line removal first. Check visually; fall back to a VLM pass for messy pages.
3. Pair each crop with its line from `ground-truth/pages.txt` → `data/lines/*.png` + `data/labels.jsonl`.
4. Split by page (e.g. 16 train / 2 val / 2 test pages, with both rounds of a test page held out) so test lines are never seen in training.
5. Fine-tune TrOCR (Hugging Face `VisionEncoderDecoderModel`), a few epochs on one consumer GPU or a rented one. Report **CER** (character error rate) on the test pages before and after fine-tuning.
6. Optional: push the model to Hugging Face.

Python environments use `uv`.

## Layout

```
ground-truth/pages.txt   text to copy, one line per handwritten line (source of truth)
writing-sheets.pdf       printable sheets built from pages.txt
writing-sheets.typ       Typst source for the PDF
photos/raw/              page photos (as received)
```
