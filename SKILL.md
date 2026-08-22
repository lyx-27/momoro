---
name: ip-mascot-logo
description: Generate an extremely simple, cute, personified square mascot character usable as a product logo — one rounded chunky silhouette, two character colors on one solid background color, readable at 32x32. Use when the user asks for a mascot, IP character, or character-style logo (animal, creature, robot, ghost, plant, or object). The skill infers product-relevant directions, proposes six candidates, and can run a bundled gpt-image-2 generator directly when no agent-native image tool is available.
---

# IP Mascot Logo

Produce the simplest possible cute mascot: a compact, lovable symbol that stays recognizable at `32 × 32`, not a detailed character illustration. The mascot doubles as a brand logo, but you never tell the image model that.

## Two ways to generate

This skill supports two execution paths. Pick the first one that is available.

1. **Agent-native image tool.** If the running agent can generate images directly (Codex ImageGen, Doubao, Coze, Gemini apps, or any configured image model), send the prompt from the Prompt Skeleton below. This is the preferred path.
2. **Bundled generator (no agent image tool needed).** If no native image tool exists, run the included script (set `OPENROUTER_API_KEY` first — see `.env.example`):

   ```bash
   export OPENROUTER_API_KEY=sk-or-...
   python3 generate_mascot.py --subject "rounded ghost" --ip1 "#3B5BDB" --ip2 "#FFD43B" --bg "#0B1021" --count 6
   ```

   The script saves each candidate as its own PNG and writes an HTML preview page. Never claim an image was produced without one of these two paths actually running.

## Workflow

1. Read the request for an explicit mascot subject and any product context. Do not ask the user to pick a color mode unless they ask to control it.
2. If no subject is given and the current directory is a product repo, read available read-only context first: README, product docs, package or app metadata, landing copy, design tokens. Treat context as sufficient once you can infer the product's purpose, audience, and intended personality with reasonable confidence.
3. If context is still thin, ask ONE consolidated round of questions: what the product does, who it serves, how it should feel. Do not open a second questionnaire. Continue with the best-supported reading afterward.
4. Once context is sufficient, present three directions in plain language, then propose generating six candidates in one batch. Wait for agreement unless the request already authorizes six outputs.
5. Choose the three directions deliberately:
   - Subject given: keep it, propose three distinct treatments differing in composition, silhouette, secondary color region, or personality.
   - Subject open: propose three genuinely different subjects, each tied to a specific product attribute or brand promise. No three random animals without reasons.
6. Map the user's response to a labeling scheme:
   - Accept all three directions + six images: two variants per direction, labeled `A1 A2 B1 B2 C1 C2`.
   - Pick one direction + six images: six controlled variants of it, labeled `A1`–`A6`.
   - Reject the count or split: follow the user's replacement instruction without defending the default.
7. Default every candidate to exactly three semantic colors: two IP colors + one background color. Reuse the two IP colors for facial marks instead of adding a third. Only change the count if the user asks.
8. Generate each candidate as its own full-resolution square asset. Never ask a model to compose a grid or contact sheet.
9. Deliver every returned image as-is. Do not inspect, rank, filter, retry, or post-process. Refinements happen only when the user asks for another draw.
10. Report per candidate: label, subject direction + rationale, saved path, the color mapping used, and dimensions.

## Complexity budget

- One dominant continuous silhouette from roughly `4–7` large basic shapes. Merge or drop any shape that does not carry identity, expression, or recognition.
- At most one species-defining feature (one big beak, one pair of curled horns, one broad visor).
- At most two broad internal color regions matching the two IP colors. Face is two eyes plus, only if needed, one tiny mouth. No eyebrows, highlights, nostrils, texture, outlines, or decorative marks unless essential.
- Prefer a head or compact upper-body crop. Do not depict full anatomy, costume, or machinery.
- Remove repeated feathers, scales, fur tufts, plates, buttons, screws, numbers, and labels.
- Make simplification, cuteness, and baby-like appeal the decisive qualities: large head, compact proportions, soft cheeks, wide-set simple eyes, calm friendly expression.
- Must read as a clean black silhouette and stay recognizable at `32 × 32`. If a feature turns to noise at that size, enlarge, merge, or remove it.

## Shape and composition

- Thick, rounded, weighty contours; broad color masses.
- No sharp corners, pointed ears or beaks, needle tails, thin antennae, thin smiles, narrow gaps, or acute tips. Every necessary tip ends visibly blunt and rounded.
- Show both members of any paired feature (ears, horns, wings, gills, bells).
- Let the mascot rise from the lower-left or lower-right corner, filling about `75–85%` of the canvas. Bottom/side cropping is intentional; never crop a paired identifying feature.
- Keep the artwork upright. Never rotate or tilt the main mark without an explicit request.

## Color and canvas

- Default: exactly three semantic colors — two IP colors + one background.
- Choose the two IP colors from product context, subject identity, and personality. Organize both into broad purposeful masses; reuse one for facial marks, keep the other in one continuous region.
- Choose the background independently, or use a user-supplied one. Example palettes are inspiration, never an allowlist.
- Keep clear separation between silhouette, facial marks, and background. If a supplied background weakens separation, adjust the subject colors first.
- Name the intended solid background color directly. Ask for it to fill the square and stay visible in all four corners and every open area, with normal square outer corners.
- Do NOT use image-mode words like `transparent`, `alpha`, or `opaque` in the generation prompt.
- Generate a true `1:1` square. Request about `1536 × 1536`; accept and keep a native `1024 × 1024` result. Never upscale just to hit a number.

## Prompt skeleton

Describe the requested visual as an image only. NEVER tell the image model the result is a `logo`, `brand mark`, `app icon`, or `icon`. Do not prepend use-case scaffolding that reveals such use. This rule applies only to the generation prompt — the surrounding conversation and this skill's name may still say "logo".

For modern instruction-following models (gpt-image-2, Nano Banana Pro, Seedream), send one positive prompt and express exclusions as a natural-language `Constraints:` line inside it. Do not build a separate negative-prompt payload for these models.

```text
Create one complete full-bleed 1:1 square image.
Background: fill the entire square with solid <background>. Keep <background> clearly visible in all four square corners and every open area around the character.
Subject: one extremely simplified, cute, endearing <subject> character, reduced to one soft rounded continuous silhouette plus one defining feature.
Complexity: only 4-7 large basic shapes and at most two broad internal color regions. Two simple eyes; add one tiny mouth only if it helps the expression. Remove every nonessential line, outline, anatomical detail, texture, and decoration. Stay readable at 32x32.
Color: exactly three colors in the whole image — two character colors <ip1> and <ip2> plus the background. Organize the two character colors into broad masses and reuse them for facial marks. Keep character, facial marks, and background clearly separated.
Composition: upright, emerging from the <corner>, filling 75-85% of the square, both paired identifying features visible.
Style: make simplification, cuteness, and lovable baby-like appeal the strongest qualities. Large soft forms, compact proportions, thick rounded contours, ultra-clean graphic treatment. Prefer one clear shape over explanatory detail. Add an extremely subtle, almost imperceptible sense of depth.
Finish: only the character on the full-canvas background, clean surfaces, normal square outer corners.
Constraints: no text, no watermark, no borders, frames, cards, or presentation masks. One character only, no extra subjects or scenery. No fragile lines, sharp tips, unnecessary outlines, tiny details, or decorative marks. No photorealistic material, dramatic bevel, glossy hotspot, deep occlusion, strong 3D rendering, or external cast shadow. Keep the background solid and uniform with no texture, vignette, or lighting variation.
```

## Delivery behavior

- Treat generation as a stochastic draw, not a conformance test.
- Generate the requested count once and deliver every returned image.
- Do not inspect or report alpha, transparency, or background mode by default.
- Do not block, rank, mark recommended/non-recommended, or auto-retry a result because of its background, colors, detail, composition, gradient, shading, or dimensionality.
- Do not post-process a result to look more compliant. Generate a new independent candidate only when the user explicitly asks.
