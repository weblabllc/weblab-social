# Higgsfield: covers for the 20–26.10 posts

One short clip per post. It becomes slide 01 of the carousel (a video cover) and a separate Reel.
Title, logo and the rest of the text are added afterwards by `tools/overlay.py`; never ask the
video model for text — Cyrillic comes out garbled.

## Settings for every clip

- **Aspect ratio:** 9:16 (it gets cropped to 4:5 for the carousel, so keep the subject centred).
- **Length:** 5 s. **Audio:** off.
- **Composition:** subject in the **lower half**, top half dark and empty — the title goes there.
- Best consistency: first make a still with text-to-image, then animate it with image-to-video.

Append this style line to every prompt:

> Cinematic macro shot, warm near-black background, glowing teal liquid, soft amber rim light,
> shallow depth of field, slow subtle camera push-in, subject in the lower half of the frame,
> upper half dark and empty, no text, no letters, no numbers, no logos, no people, 9:16.

## Prompts

| Date | Slug | Prompt |
|---|---|---|
| вт 20.10 | `2026-10-20-website-cost` | Five laboratory glass beakers in a row on a dark surface, filled with teal liquid to different heights like a bar chart, the liquid level slowly rising in each beaker, fine measuring marks on the glass. |
| ср 21.10 | `2026-10-21-ai-tasks` | A glass Erlenmeyer flask with glowing teal liquid; small blank sheets of paper and envelopes slowly drift down and dissolve into the liquid with soft rising bubbles. |
| чт 22.10 | `2026-10-22-ecommerce-sells` | A minimalist frosted-glass shopping bag standing on a dark reflective surface, slowly filling from the bottom with swirling teal liquid, gentle reflections. |
| пт 23.10 | `2026-10-23-website-myths` | A cracked glass flask on a dark surface; the cracks slowly seal themselves in reverse-shatter motion and the teal liquid inside settles calm and clear. |
| сб 24.10 | `2026-10-24-first-call-prep` | A glass flask with teal liquid on a dark desk beside a closed notebook and a pen; a single drop falls into the flask and creates slow ripples. |
| нд 25.10 | `2026-10-25-ai-glossary` | Macro view inside a glass flask: tiny glowing teal particles drift, find each other and connect into a loose network of dots and thin lines, like neurons. |
| пн 26.10 | `2026-10-26-selfhosted-vs-api` | Two glass flasks side by side: the left one has a thin glass tube rising out of the top of the frame, the right one sits on a small dark server block with tiny amber status lights; teal liquid flows gently in both. |

## Hand-off

Name each clip by its slug and either attach it in the chat or commit it to
`higgsfield/in/<slug>.mp4`. Then:

```bash
python3 tools/overlay.py <slug> higgsfield/in/<slug>.mp4
# → out/<slug>/cover-4x5.mp4, reel-9x16.mp4, cover-4x5.jpg
```
