---
name: Syntactic Intelligence
version: 2.0
lastUpdated: 2026-06-05
description: Design system for the DS/SE Portfolio. The color palette is generated dynamically from 4 user-editable source colors via CSS `color-mix()`.

# 4 user-editable source colors (staticfiles/css/theme.css).
# Change any of these and every derived color in the system updates.
sourceColors:
  primary: '#7d7bc5'
  secondary: '#ADFF2F'
  tertiary: '#0A0F1E'
  neutral: '#050505'

# Final color tokens. Derived tokens are computed at runtime by
# staticfiles/js/tailwind-config.js via `color-mix(in oklch, ...)`.
# The hex values below are approximations resolved against the source
# colors above. To re-generate after a theme change, just reload the page.
colors:
  # Base — direct passthrough from sourceColors
  primary: '#7d7bc5'
  secondary: '#ADFF2F'
  tertiary: '#0A0F1E'
  neutral: '#050505'

  # Surfaces — derived from --color-neutral mixed with --color-primary
  # (the primary mix gives a subtle purple tint, reinforcing brand presence)
  surface: '#050505'
  background: '#050505'
  surface-dim: '#030303'
  surface-container-lowest: '#030303'
  surface-container-low: '#101015'
  surface-container: '#13131a'
  surface-container-high: '#18181f'
  surface-container-highest: '#1a1a23'
  surface-bright: '#1a1a23'
  surface-variant: '#1a1a23'
  surface-tint: '#7d7bc5'

  # On-* (text/icon colors for use ON the surfaces)
  on-surface: '#b8b9e0'
  on-surface-variant: '#a4a5cd'
  on-background: '#b8b9e0'
  on-primary: '#2a2762'
  on-primary-container: '#2a2762'
  on-secondary: '#193200'
  on-secondary-fixed-variant: '#182b00'
  on-tertiary: '#a4a5cd'
  on-tertiary-container: '#a4a5cd'

  # Outlines
  outline: '#525063'
  outline-variant: '#3a3a47'

  # Inverse (kept for completeness; not currently used in templates)
  inverse-surface: '#b8b9e0'
  inverse-on-surface: '#13131a'
  inverse-primary: '#2a2762'

# Typography tokens (must match staticfiles/js/tailwind-config.js exactly).
# Headlines use Space Grotesk, body uses Inter, labels and code use JetBrains Mono.
typography:
  display-lg:
    fontFamily: Space Grotesk
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 1.1
    letterSpacing: -0.02em
    usage: Hero headlines (desktop)
  display-lg-mobile:
    fontFamily: Space Grotesk
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 1.2
    usage: Hero headlines (mobile, <md breakpoint)
  headline-md:
    fontFamily: Space Grotesk
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 1.2
    letterSpacing: -0.01em
    usage: Section headings
  headline-sm:
    fontFamily: Space Grotesk
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 1.3
    usage: Card titles, sub-section headings
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 1.6
    usage: Hero descriptions, lead paragraphs
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 1.6
    usage: Body text, descriptions, prose
  label-caps:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 1.0
    letterSpacing: 0.1em
    usage: Navigation labels, status indicators, metadata, button text
  code-sm:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 1.5
    usage: Code snippets, notebook cells, technology chips

# Border radius — 4-tier system, deliberately sharper than typical SaaS.
# `full` is 12px (NOT 9999px) — a deliberate anti-pill choice to keep the
# "technical, no-nonsense" feel of the system.
borderRadius:
  DEFAULT: 0.125rem
  lg: 0.25rem
  xl: 0.5rem
  full: 0.75rem

# Spacing scale. All values are multiples of 8px (the `base` unit).
spacing:
  base: 8px
  gutter: 24px
  margin-mobile: 20px
  container-max: 1200px
  section-gap: 120px

# Iconography
icons:
  family: 'Material Symbols Outlined'
  defaultSettings: { fill: 0, wght: 400, grad: 0, opsz: 24 }
  customTechIcons:  # Defined as inline SVG in staticfiles/css/icons.css
    - tensorflow
    - python
    - django
    - pandas
    - matplotlib
    - flask
    - golang
    - nestjs
    - typescript
    - vue
    - qt
---

## Brand & Style

**Syntactic Intelligence** is the design system for the **DS/SE Portfolio** — a personal site for a Data Science / Software Engineering practitioner. It targets developers, data scientists, and AI architects who appreciate high-density, low-friction interfaces that feel like a premium IDE.

The aesthetic is **Cyber-Industrial Minimalism**: a dark, immersive environment that reduces ocular strain during long sessions, with high-energy accents that highlight critical paths and execution states. The emotional response should be one of total control, speed, and futuristic sophistication.

Design principles:
- **Technical Precision:** every pixel and line serves a functional purpose.
- **Experimental Edge:** futuristic geometric forms and high-contrast neon accents.
- **Professional Rigor:** bold colors, but the structure remains systematic and grid-bound.

## Color System

The palette is rooted in a deep, multi-layered dark mode and is generated dynamically from **4 user-editable source colors** in `staticfiles/css/theme.css`:

| Source | Hex | Role |
|---|---|---|
| `--color-primary` | `#7d7bc5` | **Electric Indigo** — brand presence, links, focus states, tech chips |
| `--color-secondary` | `#ADFF2F` | **Neon Cyber Lime** — primary CTAs, success states, active progress, status indicator |
| `--color-tertiary` | `#0A0F1E` | **Rich Navy** — "data science" emphasis, secondary headings |
| `--color-neutral` | `#050505` | **Space Black** — base canvas, page background |

### Derivation rules

All 14 other color tokens are derived from the 4 sources via `color-mix(in oklch, ...)`. Changing any source updates all derived values on the next page load — no rebuild required.

| Token family | Mix expression | Intent |
|---|---|---|
| `surface-container-*` | `neutral` mixed with `primary` 8–25% | Subtle purple-tinted elevation ladder |
| `surface-container-lowest` | `neutral` + `black 30%` | Darker than neutral — the "deepest" surface |
| `surface-bright` / `*-highest` | `neutral` + `primary 25%` | Highest-elevation surface (most purple tint) |
| `on-surface` / `on-background` | `primary` + `white 50%` | Light lavender text on dark surfaces |
| `on-surface-variant` | `primary` + `white 30%` | Muted lavender for secondary text |
| `on-primary-container` | `primary` + `black 60%` | Dark text on light-purple surfaces |
| `on-secondary` | `secondary` + `black 75%` | Dark text on lime (for the lime button label) |
| `outline` | `primary` + `neutral 70%` | Muted purple-gray border |
| `outline-variant` | `primary` + `neutral 85%` | Very faint border for layered containers |

The mix is performed in **OKLCH** color space (perceptually uniform), so all the tints/shades of a given source color stay visually consistent.

### Accent semantics

- **Electric Indigo** is the workhorse. Used for links, focus rings, tech chips, and the "Data Science" emphasis badge.
- **Neon Cyber Lime** is reserved exclusively for high-priority interactive states: the primary CTA, the active "Execute" button, success indicators, the blinking terminal cursor, and the "SYSTEMS OPERATIONAL" status dot. Use sparingly — too much dilutes its impact.
- **Rich Navy** is used sparingly for "data science" emphasis (e.g. labels in the landing page, the small icon column in project cards) to create a subtle dual-track visual identity between backend and DS.

## Typography

The system uses a **two-family** stack — a simplification from the previous Space Grotesk + Inter + JetBrains Mono trio. Space Grotesk was dropped; Inter now carries all text including headlines. This gives the system tighter visual coherence.

- **Space Grotesk (headlines):** Weights 400, 500, 700. Geometric, idiosyncratic terminals give headlines their futuristic character. Used for all `display-lg*` and `headline-*` classes.
- **Inter (body):** Weights 400, 600, 700. Geometric neutrality, excellent legibility at small sizes, renders well in data-dense layouts. Used for `body-lg` and `body-md` and all paragraph content.
- **JetBrains Mono (technical labels and code):** Weights 400, 600. Used for navigation labels, status indicators, button text, code snippets, and notebook cell content. The monospaced nature reinforces the IDE aesthetic and ensures alignment in the variable-span project grid.
- **Material Symbols Outlined (icons):** Rendered at variable sizes (`text-sm`, `text-base`, `text-4xl`).

Type scale is in 2–6px steps: 14 (label-caps, code-sm), 16 (body-md), 18 (body-lg), 22 (headline-sm), 32 (headline-md), 36 (display-lg-mobile), 48 (display-lg).

All three families are loaded from Google Fonts in `templates/base.html` (lines 15–17). Note: previously Space Grotesk was assigned in the JS but not loaded, causing headlines to silently fall back to the system font — that was fixed by adding a second `<link>` for Space Grotesk.

## Layout & Spacing

The layout follows a **Rigid Technical Grid**.

- **Grid system:** 12-column fluid grid on desktop (≥`md` breakpoint = 768px), single column on mobile. All grid gaps use the `gutter` token (24px).
- **Base unit:** 8px. All spacing values are multiples of 8.
- **Container:** max width 1200px (`container-max`), horizontally centered.
- **Container padding:** 20px on mobile (`margin-mobile`), 24px on desktop (`gutter`).
- **Section vertical rhythm:** 120px between major sections (`section-gap`).
- **Type scale responsiveness:** the hero `display-lg` steps down to `display-lg-mobile` (48 → 36px) below the `md` breakpoint.

## Elevation & Depth

Depth is communicated through **tonal layering**, not shadows. The 6 surface tiers form a clear ladder from `surface-container-lowest` (deepest) to `surface-bright` (highest). Each tier is a 7–18% mix of `primary` into `neutral` in OKLCH, giving every elevated surface a subtle purple tint that reinforces brand identity.

| Tier | Use case |
|---|---|
| `surface-container-lowest` | Top status bar background, footer, code editor (notebook cells) |
| `surface-container-low` | Project cards, feature grid background |
| `surface-container` | Inline cards (Backend / Data Science badges) |
| `surface-container-high` | Input fields, select dropdowns, hover states on ghost buttons |
| `surface-container-highest` | Tech chips on project cards, image containers |
| `surface-bright` | Hover state on image containers and elevated cards |

**Borders** are 1px solid in `outline-variant` (default) or `outline` (active/focused). Opacity is used frequently (`border-outline-variant/20`, `/30`, `/50`) to create subtle hierarchy without committing to a hard new color.

**No box-shadows or glow effects** in the current implementation — the high contrast of the secondary accent on the dark surface provides enough emphasis for interactive elements.

## Shapes

The shape language is **technical and refined**, leaning toward sharp edges.

- **Default radius is 2px** (`rounded` / `rounded-lg` utility). The 2px is just enough to soften the corner without losing the technical feel.
- **`xl` (8px)** is used for prominent containers: feature cards, project cards, image containers.
- **`full` is 12px, not 9999px** — a deliberate anti-pill choice. The "SYSTEMS OPERATIONAL" status dot is the only element where this radius appears, and even there it's 12px (a soft dot, not a perfect circle).
- **No chamfered or clipped corners** are currently in use. (The earlier concept of a 45° single-side chamfer on hero cards was never implemented.)

## Components

### Status Bar (top of every page)
Fixed at top with `z-60`, `bg-surface-container-lowest/90` + `backdrop-blur-sm`. Shows:
- Pulsing green dot + `SYSTEMS OPERATIONAL` label (the only "neon" use outside of CTAs)
- Kernel version (e.g. `KERNEL: PYTHON 3.13 (DS-CORE)`)
- Resource metrics on the right (RAM, latency)

Sits 1.5rem (24px) above the navigation, reinforcing the "IDE status bar" metaphor.

### Navigation Bar
Fixed at top with `z-50`, positioned 24px below the status bar. `bg-surface/80` + `backdrop-blur-md` for the glassy effect.
- Logo (left) — currently an empty anchor with `text-headline-sm text-on-surface`
- Nav links (center) — `Home`, `Projects`, `Experience`, `Blog`
- Active page indicated by `text-secondary` + `border-b-2 border-secondary` + bold weight
- Inactive links use `text-on-surface-variant` with `hover:text-secondary` transition
- Mobile: nav links hidden below `md` (currently no mobile menu — see "Known Gaps" below)

### Hero (landing page)
- `text-tertiary` role label in `label-caps` (uppercase, tracking-widest)
- `display-lg` headline with `text-secondary` accent on key phrase
- `body-lg` description in `on-surface-variant`
- Two CTAs side-by-side:
  - **Primary CTA:** `bg-secondary text-on-secondary`, `rounded-lg`, with arrow icon, `hover:brightness-110 active:scale-95`
  - **Secondary CTA:** `border border-outline-variant/50 text-on-background`, `rounded-lg`, `hover:bg-surface-container-high`

### Feature Grid (landing page)
12-column grid containing:
- A square image container (col-span-4) with `bg-surface-container-highest`, `rounded-xl`, `border-outline-variant/20`, `grayscale hover:grayscale-0` transition (5s) — a nice "reveal" effect
- Text content (col-span-8) with:
  - `headline-md` heading
  - Two prose paragraphs in `body-md` with inline `<strong>` highlights (one in `text-secondary`, one in `text-tertiary`)
  - A 2-column mini-card grid (Backend / Data Science) using `bg-surface-container` with Material Symbols icons

### Project Card (projects page)
Renders in a 12-column grid with **cycling column spans** (8/4/5/7) for visual rhythm. Two layout variants:

**Wide cards (col-span-8 or col-span-7):**
- Image on one side, text on the other (`flex-col md:flex-row`)
- Image: `h-64 md:h-full` with `object-cover` + `group-hover:scale-105` (700ms transition)
- Text side: 32px padding, flex column, content split between top (tech chips + description) and bottom (impact metric + "View Project" link)

**Narrow cards (col-span-4 or col-span-5):**
- Image on top (`h-48`, `object-cover`)
- Tech chips below the image

**Common elements:**
- `bg-surface-container-low`, `border border-outline-variant/20`, `rounded-xl`
- Hover: lift effect via `hover:-translate-y-2` (500ms transition)
- Tech chips: `bg-surface-container-highest px-3 py-1 rounded text-primary` with the tech's custom icon (from `icons.css`)
- Impact metric row: `text-tertiary` with `trending_up` Material Symbol + `label-caps` text
- "View Project" link: `text-secondary` with arrow icon, hover translates the arrow right

### Notebook Cell (code-style.css)
Jupyter-Notebook-inspired cell for code display. The signature element.
- **Execution count gutter** (left): `font-code-sm text-outline`, prefixed/suffixed with `In [` / `]:` via `::before` and `::after` pseudo-elements. Mimics Jupyter's cell numbering.
- **Cell body** (right): `bg-surface-container-low` for interactive, `bg-surface-container-lowest` for read-only snippets, `rounded-lg`, `border-l-4` accent.
  - Default border: gray (`#444748`)
  - Hover border: lime (`#76ff61` — close to `secondary`)
  - Inside: keywords in pink (`#f399ff`), strings in lavender (`#9990ff`), function calls in lime (`#07fa16`), comments in gray (`#8e9192`)
- **Cursor:** Blinking 8×18px lime rectangle (`#ADFF2F`, matches `secondary`) with a 1s blink animation. Dropped inline at the end of the current line.
- **Execute button:** `bg-secondary text-on-secondary`, with `play_arrow` Material Symbol that rotates 180° on `active:rotate-180`.

### Select Input
`bg-surface-container-high text-on-surface border border-outline-variant/50 rounded px-3 py-1 font-code-sm`. Custom chevron arrow via inline SVG background-image. Focus transitions the border to `border-secondary`.

### Footer
`bg-surface-container-lowest`, 1px top border in `border-outline-variant/20`. Three-column flex layout (brand / copyright / social links). Social links use `text-on-surface-variant` with `hover:text-tertiary` transition.

## Responsive Patterns

| Pattern | Breakpoint | Example |
|---|---|---|
| Single col → 12 col grid | `md` (768px) | `grid-cols-1 md:grid-cols-12` |
| Stacked → row layout | `md` | `flex-col md:flex-row` |
| Type scale up | `md` | `text-display-lg-mobile md:text-display-lg` |
| Container padding up | `md` | `px-margin-mobile md:px-gutter` |
| Desktop-only nav | `md` | `hidden md:flex` |

## Known Gaps & Technical Debt

- **Hardcoded colors in `code-style.css`:** `.code-cell` background (`#010f1f`), border (`#444748`), hover border (`#76ff61`), cursor (`#ADFF2F`), and all four `.syntax-*` colors are hex literals. The cursor and hover border are intentionally close to the secondary token, but they should be tokenized for true single-source re-theming.
- **Hardcoded colors in `projects.css`:** `.project-card:hover` uses `#8afc73` (border) and `#122131` (background). Both should reference the design tokens.
- **No mobile menu:** The nav links are hidden below `md` with no replacement (no hamburger). Mobile users currently cannot navigate.
- **`error` color is unused** in current templates, but the M3 role exists in the original config. If error states are added later, decide whether to add a 5th source color or hardcode.
- **The 6 `*-fixed` and `*-fixed-dim` color tokens** from the original M3 system (e.g. `primary-fixed`, `secondary-fixed`) are not generated by the current JS config. They can be added back if a design calls for the "fixed" color variant.

## File Map

| File | Role |
|---|---|
| `staticfiles/css/theme.css` | The 4 source colors. **The only file a designer needs to touch to re-theme.** |
| `staticfiles/js/tailwind-config.js` | Reads the 4 source vars, derives 14 tokens via `color-mix()`, resolves to RGB triplets with `<alpha-value>` for opacity support, and feeds the Tailwind Play CDN. |
| `staticfiles/css/base.css` | Body background fallback (`#051424`) and Material Symbols default settings. |
| `staticfiles/css/icons.css` | Inline-SVG tech brand icons (tensorflow, python, django, etc.). |
| `staticfiles/css/code-style.css` | Notebook cell + syntax highlighting (see Known Gaps). |
| `staticfiles/css/projects.css` | Project card hover states and `<select>` chevron (see Known Gaps). |
| `templates/base.html` | Layout shell: head (CSS, tailwind CDN, tailwind config script), status bar, nav, main slot, footer. **Loads `theme.css` before `tailwind-config.js`** — required for the JS to read the CSS variables. |
