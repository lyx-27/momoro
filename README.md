# Momoro

A skill for generating **extremely simple, cute, personified square mascot avatars** — one rounded chunky character, two character colors on one contrasting background, readable even at 32×32 — plus **Momoro**, a gallery of 124 ready-made clay-style meme-flavored mascots.

![Momoro mascots](docs/momoro-poster.png)

![Mascot showcase](docs/mascot-reel.gif)

## What's in here

- **`SKILL.md`** — the mascot skill: art-direction rules, a prompt skeleton, and a workflow an agent can follow to propose directions and produce candidates.
- **`generate_mascot.py`** — a zero-dependency bundled generator (calls an OpenRouter-hosted image model) for when no agent-native image tool is available.
- **`palettes.json`** — a curated set of bright, contrasting background colors used by the generator's `--palette contrast` mode.
- **`site/`** — **Momoro**, a self-contained dark-theme gallery of 124 mascots (search, categories, favorites, lightbox, EN/中文, one-click PNG download). No build step, no backend.

## The skill

Momoro produces the *simplest possible* lovable mascot: a compact symbol that still reads at tiny sizes, not a detailed illustration. It works two ways:

1. **Agent-native image tool** — send the prompt from the skeleton in `SKILL.md` to whatever image model the agent has.
2. **Bundled generator** — no native tool needed:

   ```bash
   cp .env.example .env      # then paste your OpenRouter key into .env
   python3 generate_mascot.py --subject "rounded owl" --count 6
   # or drive the palette automatically:
   python3 generate_mascot.py --subject "chubby fox" --ip1 "#FF6B35" --ip2 "#FFE0C2" --palette contrast --count 6
   ```

   Each candidate is saved as its own PNG in `output/`, alongside an HTML preview page. Full rules and options live in [`SKILL.md`](SKILL.md).

### Configure the API key

The generator reads `OPENROUTER_API_KEY` from the environment or a local `.env` (git-ignored).

- Get a key at <https://openrouter.ai/keys> (format `sk-or-v1-...`).
- Copy `.env.example` → `.env` and paste it in, or `export OPENROUTER_API_KEY=...`.
- Optional: `OPENROUTER_IMAGE_MODEL` to pick the image model, `IMAGE_PROXY` if the model is region-locked for you.

No other dependencies — `generate_mascot.py` is pure Python 3 standard library.

## The Momoro gallery

![Momoro gallery](docs/momoro-interface.png)

A plain static site in `site/`. Run it locally:

```bash
cd site
python3 -m http.server 8123
# open http://127.0.0.1:8123/
```

Deploy anywhere static (GitHub Pages, Cloudflare Pages, Netlify, Vercel, or any object storage + CDN) — it's just files. See [`site/README.md`](site/README.md) for details.

## Notes

The mascots are original, AI-generated characters in a consistent clay style. Names (e.g. "Doge", "Grumpy Cat") are **descriptive references to internet culture** for discoverability, not claims of ownership; the underlying meme characters may be subject to their own trademarks or copyrights. Use the generated art thoughtfully and check the rights of any specific character before commercial use.

## Credits & license

The mascot **skill** in this repo (`SKILL.md` and its art-direction rules) is adapted from **[s1dashu/ip-as-logo-skill](https://github.com/s1dashu/ip-as-logo-skill)**, an open-source Agent Skill released under the MIT License. Huge thanks to the original author. The **Momoro gallery** (`site/`) and the generated mascot set are this project's own additions.

In accordance with the MIT License, the original copyright and permission notice are retained:

```
MIT License

Copyright (c) 2026 s1dashu

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
