"""Assemble the foundation reading editions; does not implement NeuroCVguard."""
from __future__ import annotations
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    index = json.loads((ROOT / "state/document_index.json").read_text(encoding="utf-8"))
    sections = index["sections"]
    stages = json.loads((ROOT / "state/stage_plan.json").read_text(encoding="utf-8"))
    parts = ["# NeuroCVguard\n\n# End-to-end foundation and Codex implementation playbook\n\n"
             "**Foundation 1.0.0 · 12 September 2026 · Target software v0.1.0**\n\n"
             "**Status:** specification and implementation instructions. Not an implemented or validated software release.\n\n"
             "The split source documents, contracts and stage files in the companion bundle are authoritative. "
             "This complete reading copy includes the scientific contract, implementation stages, acceptance cases, "
             "schemas, examples and operating instructions.\n\n"]
    nav = [("start", "Start here"), ("stage-map", "Stage map")]
    parts += ["## Contents\n\n- [Start here](#start)\n- [Stage map](#stage-map)\n"]
    for s in sections:
        anchor = "spec-" + s["slug"]
        parts.append(f'- [{s["title"]}](#{anchor})\n')
        nav.append((anchor, s["title"]))
    parts.append("\n### Execution prompts\n\n")
    for s in stages:
        anchor = "stage-" + s["id"].lower()
        parts.append(f'- [{s["id"]} — {s["title"]}](#{anchor})\n')
        nav.append((anchor, s["id"] + " — " + s["title"]))
    extras = [
        ("agents", "Root AGENTS instructions", "AGENTS.md"),
        ("rules", "Stable rule catalog", "qa/RULE_CATALOG.md"),
        ("cases", "Exact acceptance cases", "qa/ACCEPTANCE_CASES.md"),
        ("resume", "Resume prompt", "prompts/RESUME.md"),
        ("review", "Independent review prompt", "prompts/REVIEW.md"),
        ("change", "Change-request prompt", "prompts/CHANGE_REQUEST.md"),
    ]
    for a,t,p in extras:
        parts.append(f'- [{t}](#{a})\n')
        nav.append((a,t))
    parts.append('\n<a id="start"></a>\n\n'+(ROOT/"START_HERE.md").read_text(encoding="utf-8"))
    parts.append('\n<a id="stage-map"></a>\n\n'+(ROOT/"state/STAGE_MAP.md").read_text(encoding="utf-8"))
    for s in sections:
        parts.append(f'\n---\n\n<a id="spec-{s["slug"]}"></a>\n\n'+(ROOT/s["path"]).read_text(encoding="utf-8"))
    for s in stages:
        parts.append(f'\n---\n\n<a id="stage-{s["id"].lower()}"></a>\n\n'+(ROOT/s["prompt_file"]).read_text(encoding="utf-8"))
    for a,t,p in extras:
        parts.append(f'\n---\n\n<a id="{a}"></a>\n\n'+(ROOT/p).read_text(encoding="utf-8"))
    parts.append('\n---\n\n# Appendix — record templates\n\n')
    for p in sorted((ROOT/'templates').glob('*.md')):
        parts.append(f'\n## File: `{p.relative_to(ROOT)}`\n\n'+p.read_text(encoding='utf-8'))
    parts.append('\n---\n\n# Appendix — exact JSON schemas\n\nThese are standalone local schemas. Semantic invariants remain mandatory in addition to structural schema validation.\n\n')
    for p in sorted((ROOT/'contracts').glob('*.json')):
        parts.append(f'\n## File: `{p.relative_to(ROOT)}`\n\n```json\n'+p.read_text(encoding='utf-8')+'```\n')
    parts.append('\n---\n\n# Appendix — synthetic contract fixtures\n\n'+(ROOT/'fixtures/README.md').read_text(encoding='utf-8'))
    for p in sorted((ROOT/'fixtures').iterdir()):
        if p.suffix not in {'.json','.tsv'}: continue
        lang='json' if p.suffix=='.json' else 'text'
        parts.append(f'\n## File: `{p.relative_to(ROOT)}`\n\n```{lang}\n'+p.read_text(encoding='utf-8')+'```\n')
    master='\n'.join(parts)
    (ROOT/'NeuroCVguard_MASTER_SPEC.md').write_text(master,encoding='utf-8')
    try:
        from markdown_it import MarkdownIt
    except ImportError:
        print('Master Markdown generated. Install markdown-it-py to regenerate the optional HTML reader.')
        return
    body=MarkdownIt('commonmark', {'html':True}).enable('table').render(master)
    toc=''.join(f'<a href="#{html.escape(a)}">{html.escape(t)}</a>' for a,t in nav)
    css="""
    :root{--ink:#182d40;--muted:#526477;--line:#d8e1e8;--accent:#176575;--paper:#fff;--back:#f2f5f8}
    *{box-sizing:border-box}body{margin:0;color:var(--ink);background:var(--back);font:16px/1.68 system-ui,-apple-system,Segoe UI,sans-serif}
    nav{position:fixed;left:0;top:0;bottom:0;width:290px;overflow:auto;padding:24px 20px;background:#132b3b;color:white}
    nav h2{font-size:19px;margin:0 0 8px;color:#ffffff}nav p{font-size:13px;color:#bdd0de}nav a{display:block;color:#dce8f0;font-size:12px;line-height:1.45;text-decoration:none;padding:7px 0;border-bottom:1px solid #304656}
    nav a:hover{color:white;text-decoration:underline}main{margin-left:290px;max-width:1230px;padding:48px 64px 80px;background:var(--paper);min-height:100vh;overflow-wrap:anywhere}
    h1,h2,h3,h4{line-height:1.25;color:#183e53;scroll-margin-top:25px}h1{font-size:32px;margin-top:52px;border-bottom:3px solid var(--accent);padding-bottom:14px}h2{font-size:24px;margin-top:38px}h3{font-size:19px;margin-top:28px}
    a{color:var(--accent)}p{margin:12px 0}hr{border:0;border-top:1px solid var(--line);margin:50px 0}
    table{border-collapse:collapse;width:100%;font-size:13px;line-height:1.5;margin:22px 0;table-layout:fixed}th,td{padding:10px 11px;border:1px solid var(--line);vertical-align:top;overflow-wrap:anywhere}th{background:#eaf1f5;text-align:left}tr:nth-child(even){background:#f8fafb}
    pre{background:#f0f4f7;padding:18px;border-radius:8px;overflow-x:auto;border:1px solid var(--line);font-size:12px;line-height:1.55}code{font-family:ui-monospace,Consolas,monospace;font-size:.91em}p code,li code{background:#edf2f5;padding:2px 4px;border-radius:3px}
    blockquote{border-left:4px solid var(--accent);padding:10px 20px;margin:20px 0;background:#f1f7f8}li{margin:4px 0}.reader-note{font-size:13px;color:var(--muted);padding:14px;background:#edf5f7;border:1px solid var(--line);border-radius:8px}
    @media(max-width:950px){nav{position:relative;width:auto;max-height:330px}main{margin:0;padding:25px 20px}h1{font-size:26px}table{font-size:12px}}
    @media print{nav{display:none}main{margin:0;max-width:none;padding:0}body{background:white;font-size:10pt}pre{white-space:pre-wrap;overflow-wrap:anywhere}h1,h2,h3{break-after:avoid}table{font-size:8pt}tr{break-inside:avoid}a{color:inherit}}
    """
    page='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NeuroCVguard — Foundation 1.0.0</title><style>'+css+'</style></head><body><nav aria-label="Document navigation"><h2>NeuroCVguard</h2><p>Foundation 1.0.0<br>Scientific specification + Codex playbook</p>'+toc+'</nav><main><div class="reader-note">Offline reading edition. This is the implementation foundation, not a completed software release. The source bundle contains separate stage prompts, schemas and synthetic acceptance fixtures.</div>'+body+'</main></body></html>'
    (ROOT/'NeuroCVguard_READABLE.html').write_text(page,encoding='utf-8')
    print(f'Generated master ({len(master):,} characters) and offline HTML reader.')

if __name__=='__main__':
    main()
