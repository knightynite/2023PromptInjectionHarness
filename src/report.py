"""HTML / markdown reporting for prompt-injection harness runs.

Aggregates per-payload results into a tidy view: success rate by category,
worst-offender payloads, per-model comparison.
"""
import json
import os
from collections import defaultdict
from datetime import datetime


def load_run(path: str) -> list:
    with open(path) as f:
        return json.load(f)


def aggregate(results: list) -> dict:
    by_category = defaultdict(lambda: {'n': 0, 'flipped': 0})
    by_model = defaultdict(lambda: {'n': 0, 'flipped': 0})
    worst = []
    for r in results:
        cat = r.get('category', 'unknown')
        model = r.get('model', 'unknown')
        flipped = bool(r.get('succeeded', False))
        by_category[cat]['n'] += 1
        by_model[model]['n'] += 1
        if flipped:
            by_category[cat]['flipped'] += 1
            by_model[model]['flipped'] += 1
            worst.append(r)
    return {
        'by_category': {k: v for k, v in by_category.items()},
        'by_model': {k: v for k, v in by_model.items()},
        'worst_payloads': sorted(
            worst, key=lambda r: r.get('severity', 0), reverse=True
        )[:10],
        'totals': {
            'n': sum(v['n'] for v in by_category.values()),
            'flipped': sum(v['flipped'] for v in by_category.values()),
        },
    }


def render_markdown(agg: dict, run_label: str = '') -> str:
    out = []
    out.append(f"# Prompt-injection harness report — {run_label or datetime.utcnow().isoformat()}")
    out.append('')
    t = agg['totals']
    rate = (t['flipped'] / t['n'] * 100) if t['n'] else 0.0
    out.append(f"**Total:** {t['flipped']}/{t['n']} attacks succeeded ({rate:.1f}%)")
    out.append('')
    out.append('## By category')
    out.append('')
    out.append('| Category | Attempted | Succeeded | Rate |')
    out.append('|----------|-----------|-----------|------|')
    for cat, v in sorted(agg['by_category'].items()):
        r = (v['flipped'] / v['n'] * 100) if v['n'] else 0.0
        out.append(f"| `{cat}` | {v['n']} | {v['flipped']} | {r:.1f}% |")
    out.append('')
    out.append('## By model')
    out.append('')
    out.append('| Model | Attempted | Succeeded | Rate |')
    out.append('|-------|-----------|-----------|------|')
    for m, v in sorted(agg['by_model'].items()):
        r = (v['flipped'] / v['n'] * 100) if v['n'] else 0.0
        out.append(f"| `{m}` | {v['n']} | {v['flipped']} | {r:.1f}% |")
    out.append('')
    out.append('## Worst payloads (top 10)')
    out.append('')
    for i, r in enumerate(agg['worst_payloads'][:10], 1):
        payload = r.get('payload', '')[:80]
        out.append(f"{i}. **`{r.get('id', '?')}`** ({r.get('category', '?')}, "
                   f"sev={r.get('severity', 0)}): `{payload}`")
    return '\n'.join(out) + '\n'


def render_html(agg: dict, run_label: str = '') -> str:
    md = render_markdown(agg, run_label)
    body = (md.replace('\n', '<br>')
              .replace('**', '')
              .replace('# ', '<h1>')
              .replace('## ', '<h2>'))
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Injection report</title>
<style>body{{font-family:system-ui;max-width:900px;margin:2em auto;padding:1em}}
table{{border-collapse:collapse}}td,th{{border:1px solid #ccc;padding:4px 8px}}</style>
</head><body>{body}</body></html>"""


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--results', required=True, help='harness JSON output')
    p.add_argument('--out-md', default='results/report.md')
    p.add_argument('--out-html', default='results/report.html')
    p.add_argument('--label', default='')
    args = p.parse_args()
    agg = aggregate(load_run(args.results))
    os.makedirs(os.path.dirname(args.out_md), exist_ok=True)
    with open(args.out_md, 'w') as f:
        f.write(render_markdown(agg, args.label))
    with open(args.out_html, 'w') as f:
        f.write(render_html(agg, args.label))
    print(f"wrote {args.out_md} and {args.out_html}")


if __name__ == '__main__':
    main()
