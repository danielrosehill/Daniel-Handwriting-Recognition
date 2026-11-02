# Daniel Handwriting Recognition

Minimal viable pipeline to fine-tune a handwriting text recognition (HTR) model on one person's handwriting (Daniel's, English, print/cursive as it naturally comes).

Status (2026-11-02): **data collection stage.** No photos or training code yet.

## Approach

- **Model:** fine-tune [`microsoft/trocr-base-handwritten`](https://huggingface.co/microsoft/trocr-base-handwritten) (TrOCR, ~334M params). It reads **one line of text per image**, so the dataset is line crops paired with their text.
- **Why this works with little data:** the base model already reads English handwriting (trained on IAM). Adapting it to a single writer typically needs a few hundred lines, not thousands.
- **Ground truth:** you copy fixed, known text by hand, so every line's transcription is known in advance. No manual labelling.

## Data collection protocol

### Materials

| Item | Choice | Why |
|---|---|---|
| Paper | **A4, plain unruled white** printer paper | Matches how you write day to day; plain background is easiest to segment |
| Line guide | Optional: a sheet of bold-ruled paper (or a printed ~12 mm line guide) *under* the page | Keeps lines straight and separated without the lines appearing in the photo |
| Pen | **Black** ballpoint or gel, the one you normally use | High contrast; match your real-world pen |
| Pages | **20 pages, 12 lines each = 240 lines** (`ground-truth/pages.txt`) | MVP. Phase 2 (optional): write the same 20 pages again on a different day/pen for ~480 lines |

### Writing rules

1. Write the page code (`P01` … `P20`) small in the **top-right corner**. It identifies the photo; it is not a text line.
2. Copy each line of `ground-truth/pages.txt` as **one handwritten line**. Do not wrap a line onto two, and do not merge two lines into one.
3. Leave a **clear gap between lines** (roughly one line height). Touching lines are what makes automatic cropping fail.
4. Copy the text **exactly**: same capitals, punctuation, numbers. Line breaks in the file are deliberate.
5. Write **naturally**, at your normal speed and size. Neat "exam" handwriting trains a model that can't read your real notes.
6. **Mistakes:** don't correct in place. Either cross the whole line out and rewrite it on the next line, or note the page and line number (e.g. `P07 L4`) in `ground-truth/corrections.txt` with what you actually wrote. Easiest is to just keep going and tell the agent which lines to fix.
7. Leave ~2 cm margins on all sides.

### Photographing

- One photo per page, **phone held flat above the page**, whole sheet in frame, no fingers on the paper.
- Even daylight or overhead light, **no flash**, no strong shadow from the phone.
- Dark, plain background behind the sheet (helps automatic page detection).
- Highest resolution, no filters. A scanner app (Google Drive scan, Adobe Scan) is fine too; save as JPG, not PDF if possible.
- File name doesn't matter; the page code in the corner identifies it. Drop them in the Drive `fe/` folder or `photos/raw/`.

## Pipeline (to build once photos exist)

1. `photos/raw/` → deskew + crop page (OpenCV).
2. Line segmentation: horizontal projection profile, constrained to the known count of 12 lines per page. Check visually; fall back to a VLM pass for messy pages.
3. Pair each crop with its line from `ground-truth/pages.txt` → `data/lines/*.png` + `data/labels.jsonl`.
4. Split by page (e.g. 16 train / 2 val / 2 test pages) so test lines are never seen in training.
5. Fine-tune TrOCR (Hugging Face `VisionEncoderDecoderModel`), a few epochs on one consumer GPU or a rented one. Report **CER** (character error rate) on the test pages before and after fine-tuning.
6. Optional: push the model to Hugging Face.

Python environments use `uv`.

## Layout

```
ground-truth/pages.txt   text to copy, one line per handwritten line
photos/raw/              page photos (as received)
```
