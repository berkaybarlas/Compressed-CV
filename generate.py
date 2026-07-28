#!/usr/bin/env python3
"""Generate LaTeX resume files from resume-data.json."""

import json
import os
import subprocess
import sys

def load_data(path="resume-data.json"):
    with open(path, "r") as f:
        return json.load(f)


def escape_tex(text):
    """Pass through text as-is since LaTeX commands are stored in JSON."""
    return text


def render_items(items, env="cvitems"):
    """Render a list of bullet points inside a cvitems/cvghostitems environment."""
    lines = [f"    \\begin{{{env}}}"]
    for item in items:
        lines.append(f"      \\item {{{item}}}")
    lines.append(f"    \\end{{{env}}}")
    return "\n".join(lines)


# --- Section Generators ---

def gen_experience(section):
    lines = [
        f"\\cvsection{{{section['title']}}}",
        "\\begin{cventries}",
    ]

    for entry in section["entries"]:
        if entry["type"] == "double":
            pos1, pos2 = entry["positions"][0], entry["positions"][1]
            company = entry["company"]
            location = entry["location"]
            lines.append("\\cvexpentrydouble")
            lines.append(f"  {{{pos1['title']}}}")
            lines.append(f"  {{{company}}}")
            lines.append(f"  {{{location}}}")
            lines.append(f"  {{{pos1['dates']}}}")
            lines.append("  {")
            lines.append(render_items(pos1["items"]))
            lines.append("  }")
            lines.append(f"  {{{pos2['title']}}}")
            lines.append(f"  {{{pos2['dates']}}}")
            lines.append("  {")
            lines.append(render_items(pos2["items"]))
            lines.append("  }")
        elif entry["type"] == "single":
            company = entry.get("company", "")
            if entry.get("company_url"):
                company = f"\\href{{{entry['company_url']}}}{{{company}}}"
            lines.append("  \\cvexpentry")
            lines.append(f"   {{{entry['title']}}}")
            lines.append(f"    {{{company}}}")
            lines.append(f"    {{{entry['location']}}}")
            lines.append(f"    {{{entry['dates']}}}")
            lines.append("    {")
            lines.append(render_items(entry["items"]))
            lines.append("    }")

    lines.append("\\end{cventries}")
    return "\n".join(lines) + "\n"


def gen_education(section):
    lines = [
        f"\\cvsection{{{section['title']}}}",
        "\\begin{cventries}",
        "\\vspace{2mm}",
    ]

    for entry in section["entries"]:
        entry_type = entry.get("entry_type", "cventry")
        lines.append(f"\\{entry_type}")
        lines.append(f"    {{{entry['degree']}}}")
        lines.append(f"    {{{entry['institution']}}}")
        lines.append(f"    {{{entry['location']}}}")
        lines.append(f"    {{{entry['dates']}}}")
        lines.append("    {")
        lines.append(render_items(entry["details"], env="cvghostitems"))
        lines.append("    }")

    lines.append("\\end{cventries}")
    return "\n".join(lines) + "\n"


def gen_patents(section):
    lines = [
        f"\\cvsection{{{section['title']}}}",
        "\\begin{cvskills}",
    ]

    for entry in section["entries"]:
        lines.append("\\cvskill")
        lines.append(f"    {{{entry['category']}}}")
        lines.append(f"    {{{entry['description']}}}")

    lines.append("\\end{cvskills}")
    return "\n".join(lines) + "\n"


def gen_committees(section):
    lines = [
        f"\\cvsection{{{section['title']}}}",
        "\\begin{cvhonors}",
    ]

    for entry in section["entries"]:
        lines.append("  \\cvhonor")
        lines.append(f"    {{{entry['position']}}}")
        lines.append(f"    {{{entry['description']}}}")
        lines.append(f"    {{{entry.get('location', '')}}}")
        lines.append(f"    {{{entry['date']}}}")

    lines.append("\\end{cvhonors}")
    return "\n".join(lines) + "\n"


def gen_projects(section):
    lines = [
        f"\\cvsection{{{section['title']}}}",
        "\\begin{cventries}",
    ]

    for entry in section["entries"]:
        lines.append("\\cvopenentry")
        lines.append(f"    {{{entry['title']}}}")
        lines.append(f"    {{{entry['subtitle']}}}")
        lines.append(f"    {{{entry['award']}}}")
        lines.append(f"    {{{entry['dates']}}}")
        lines.append("    {")
        lines.append(render_items(entry["items"]))
        lines.append("    }")

    lines.append("\\end{cventries}")
    return "\n".join(lines) + "\n"


def gen_skills(section):
    lines = [
        f"\\cvsection{{{section['title']}}}",
        "\\begin{cvskills}",
    ]

    for entry in section["entries"]:
        lines.append("  \\cvskill")
        lines.append(f"    {{{entry['category']}}}")
        lines.append(f"    {{{entry['skills']}}}")

    lines.append("\\end{cvskills}")
    return "\n".join(lines) + "\n"


def gen_extracurricular(section):
    lines = [
        f"\\cvsection{{{section['title']}}}",
        "\\begin{cventries}",
    ]

    for entry in section["entries"]:
        lines.append("\\cvopenentry")
        lines.append(f"    {{{entry['role']}}}")
        lines.append(f"    {{{entry['organization']}}}")
        lines.append(f"    {{{entry['location']}}}")
        lines.append(f"    {{{entry['dates']}}}")
        lines.append("    {")
        lines.append(render_items(entry["items"]))
        lines.append("    }")

    lines.append("\\end{cventries}")
    return "\n".join(lines) + "\n"


def gen_honors(section):
    lines = [
        f"\\cvsection{{{section['title']}}}",
        "\\begin{cvhonors}",
    ]

    for entry in section["entries"]:
        lines.append("  \\cvhonor")
        lines.append(f"    {{{entry['award']}}}")
        lines.append(f"    {{{entry['description']}}}")
        lines.append(f"    {{{entry.get('location', '')}}}")
        lines.append(f"    {{{entry['date']}}}")

    lines.append("\\end{cvhonors}")
    return "\n".join(lines) + "\n"


GENERATORS = {
    "experience": gen_experience,
    "education": gen_education,
    "patents": gen_patents,
    "committees": gen_committees,
    "projects": gen_projects,
    "skills": gen_skills,
    "extracurricular": gen_extracurricular,
    "honors": gen_honors,
}


def gen_resume_tex(data):
    """Generate the main resume.tex file."""
    p = data["personal"]
    c = data["config"]

    lines = [
        "%!TEX TS-program = xelatex",
        "%!TEX encoding = UTF-8 Unicode",
        "% Auto-generated from resume-data.json — do not edit directly.",
        f"\\documentclass[{c['fontsize']}, {c['paper']}]{{awesome-cv}}",
        "",
        f"\\geometry{{{c['geometry']}}}",
        "",
        "\\fontdir[fonts/]",
        "",
        f"\\colorlet{{awesome}}{{{c['color']}}}",
        "",
        "\\setbool{acvSectionColorHighlight}{true}",
        "",
        "\\renewcommand{\\acvHeaderSocialSep}{\\quad\\textbar\\quad}",
        "",
        f"\\name{{{p['firstname']}}}{{{p['lastname']}}}",
    ]

    if p.get("position"):
        lines.append(f"\\position{{{p['position']}}}")
    if p.get("address"):
        lines.append(f"\\address{{{p['address']}}}")
    if p.get("email"):
        lines.append(f"\\email{{{p['email']}}}")
    if p.get("homepage"):
        lines.append(f"\\homepage{{{p['homepage']}}}")
    if p.get("mobile"):
        lines.append(f"\\mobile{{{p['mobile']}}}")
    if p.get("github"):
        lines.append(f"\\github{{{p['github']}}}")
    if p.get("linkedin"):
        lines.append(f"\\linkedin{{{p['linkedin']}}}")

    lines += [
        "",
        "\\begin{document}",
        "\\makecvheader",
        "",
    ]

    for section in data["sections"]:
        if section.get("page_break_before"):
            lines.append("\\newpage")
        lines.append(f"\\input{{{section['file']}}}")

    if data.get("hidden_keywords"):
        lines.append(f"\\hiddenkeywords{{{data['hidden_keywords']}}}")

    lines += [
        "",
        "\\end{document}",
    ]

    return "\n".join(lines) + "\n"


def generate(data_path="resume-data.json", compile_pdf=False):
    data = load_data(data_path)

    # Derive output name from input JSON filename (e.g. resume.json -> resume.tex)
    basename = os.path.splitext(os.path.basename(data_path))[0]
    # Strip "-data" suffix if present (resume-data.json -> resume)
    if basename.endswith("-data"):
        basename = basename[: -len("-data")]
    tex_file = f"{basename}.tex"

    # Generate main .tex
    resume_tex = gen_resume_tex(data)
    with open(tex_file, "w") as f:
        f.write(resume_tex)
    print(f"Generated {tex_file}")

    # Generate each section file
    for section in data["sections"]:
        generator = GENERATORS.get(section["type"])
        if not generator:
            print(f"Warning: no generator for section type '{section['type']}', skipping")
            continue

        content = generator(section)
        filepath = section["file"]

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            f.write(content)
        print(f"Generated {filepath}")

    if compile_pdf:
        print(f"\nCompiling {basename}.pdf...")
        result = subprocess.run(
            ["xelatex", "-interaction=nonstopmode", f"-jobname={basename}", tex_file],
            capture_output=True, text=True,
        )
        if "Output written" in result.stdout:
            import re
            match = re.search(r"Output written on (.+\.pdf) \((\d+) pages?\)", result.stdout)
            if match:
                print(f"Success: {match.group(1)} ({match.group(2)} pages)")
        else:
            print(f"Compilation failed. Check {basename}.log for details.")
            return 1

    return 0


if __name__ == "__main__":
    compile_flag = "--compile" in sys.argv or "-c" in sys.argv
    data_file = "resume.json"

    for arg in sys.argv[1:]:
        if not arg.startswith("-"):
            data_file = arg

    sys.exit(generate(data_file, compile_pdf=compile_flag))
