# CV Generation System

This project uses a JSON-to-LaTeX pipeline to generate a CV/resume. A single `resume.json` file serves as the source of truth, and `generate.py` transforms it into LaTeX files that compile into a PDF.

## Architecture

```
resume.json ──> generate.py ──> resume.tex (main file)
                            ──> resume/experience.tex
                            ──> resume/education.tex
                            ──> resume/skills.tex
                            ──> resume/projects.tex
                            ──> resume/committees.tex
                            ──> resume/extracurricular.tex
                            ──> resume/honors.tex
                                    │
                                    ▼
                              xelatex ──> resume.pdf
```

## JSON Structure

The JSON data file has three top-level keys:

### `personal`
Contact and identity info used in the CV header: `firstname`, `lastname`, `email`, `homepage`, `github`, `linkedin`, `mobile`, `address`, `position`. Null values are omitted from output.

### `config`
LaTeX document configuration: `fontsize`, `paper` size, `geometry` margins, and accent `color`.

### `sections`
An ordered array of section objects. Each section has:
- **`type`** — determines which generator function to use (e.g. `experience`, `education`, `skills`)
- **`title`** — the section heading displayed in the CV
- **`file`** — output path for the generated `.tex` file (e.g. `resume/experience.tex`)
- **`entries`** — the section content (structure varies by type)
- **`page_break_before`** (optional) — inserts a `\newpage` before the section

## Section Types & Generators

| Type | LaTeX Environment | Entry Fields |
|---|---|---|
| `experience` | `cventries` | Supports `single` and `double` (two positions at one company) entry types. Each has title, company, location, dates, and bullet items. |
| `education` | `cventries` | `degree`, `institution`, `location`, `dates`, `details`. Uses `cvghostitems` for bullet styling. |
| `skills` | `cvskills` | `category` and `skills` (a string of comma-separated skills). |
| `projects` | `cventries` | `title`, `subtitle`, `award`, `dates`, `items`. Uses `\cvopenentry`. |
| `committees` | `cvhonors` | `position`, `description`, `location`, `date`. |
| `honors` | `cvhonors` | `award`, `description`, `location`, `date`. |
| `extracurricular` | `cventries` | `role`, `organization`, `location`, `dates`, `items`. Uses `\cvopenentry`. |
| `patents` | `cvskills` | `category`, `description`. |

## How Generation Works

1. **Load JSON** — `generate()` reads the data file.
2. **Generate `resume.tex`** — `gen_resume_tex()` builds the main document with:
   - Document class and geometry from `config`
   - Header fields from `personal`
   - `\input{}` lines for each section file
   - Optional `\hiddenkeywords{}` for ATS optimization
3. **Generate section files** — Each section is routed to its generator via the `GENERATORS` dict. The generator produces LaTeX content and writes it to the path specified in `section["file"]`.
4. **Compile (optional)** — With `--compile` / `-c`, runs `xelatex` to produce the PDF.

## Usage

```bash
# Generate .tex files only
python generate.py resume.json

# Generate and compile to PDF
python generate.py resume.json --compile
```

The output filename is derived from the input: `resume.json` produces `resume.tex` / `resume.pdf`. A `-data` suffix is stripped automatically (`resume-data.json` also produces `resume.tex`).

## Key Design Decisions

- **LaTeX in JSON** — Bullet text contains raw LaTeX commands (e.g. `\textbf{...}`, `\href{...}{...}`). The `escape_tex()` function is intentionally a no-op passthrough.
- **Awesome-CV base** — The generated LaTeX uses the `awesome-cv` document class with custom commands like `\cvexpentry`, `\cvexpentrydouble`, `\cvopenentry`.
- **Modular output** — Each section is a separate `.tex` file included via `\input{}`, keeping the main file clean and allowing selective regeneration.
