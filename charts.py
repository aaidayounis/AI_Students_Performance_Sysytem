"""Tiny server-side SVG chart helpers (no JavaScript, no plotting library)."""
import math
from html import escape
from markupsafe import Markup

PURPLES = ["#4c1d95", "#6d28d9", "#8b5cf6", "#a78bfa", "#c4b5fd", "#ddd6fe"]


def _nice_max(v, step):
    return (int(v // step) + 1) * step


def bar_chart(items, *, colors=None, y_label="", step=None, ymax=None,
              decimals=1, width=520, height=330, label_suffix=""):
    """Vertical bar chart. items = [(label, value), ...]"""
    left, right, top, bottom = 58, 16, 24, 52
    pw, ph = width - left - right, height - top - bottom
    vmax = max(v for _, v in items)
    step = step or (200 if vmax > 300 else 10 if vmax > 40 else 1)
    ymax = ymax or _nice_max(vmax, step)
    n = len(items)
    slot = pw / n
    bw = min(slot * 0.62, 110)
    out = [f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(y_label)} bar chart">']
    out.append('<defs>')
    cols = colors or [PURPLES[2]] * n
    for i, c in enumerate(cols):
        out.append(f'<linearGradient id="g{id(items)%9999}_{i}" x1="0" y1="0" x2="0" y2="1">'
                   f'<stop offset="0" stop-color="{c}"/><stop offset="1" stop-color="{c}" stop-opacity=".72"/></linearGradient>')
    out.append('</defs>')
    t = 0
    while t <= ymax:
        y = top + ph - ph * t / ymax
        out.append(f'<line class="grid" x1="{left}" x2="{width-right}" y1="{y:.1f}" y2="{y:.1f}"/>')
        out.append(f'<text class="tick" x="{left-10}" y="{y+4:.1f}" text-anchor="end">{t:g}</text>')
        t += step
    for i, (lab, v) in enumerate(items):
        cx = left + slot * i + slot / 2
        h = ph * v / ymax
        y = top + ph - h
        txt = f"{v:,.{decimals}f}{label_suffix}"
        out.append(f'<g class="bar"><title>{escape(lab)}: {txt}</title>'
                   f'<rect x="{cx-bw/2:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="9" fill="url(#g{id(items)%9999}_{i})"/>'
                   f'<text class="val" x="{cx:.1f}" y="{y-8:.1f}" text-anchor="middle">{txt}</text></g>')
        out.append(f'<text class="xlab" x="{cx:.1f}" y="{height-bottom+24}" text-anchor="middle">{escape(lab)}</text>')
    out.append(f'<text class="axis" transform="translate(14 {top+ph/2}) rotate(-90)" text-anchor="middle">{escape(y_label)}</text>')
    out.append('</svg>')
    return Markup("".join(out))


def hbar_missing(rows, width=640):
    """Horizontal bars for the missing-value table."""
    rh = 30
    left, right = 190, 70
    height = rh * len(rows) + 8
    vmax = max(r[1] for r in rows)
    pw = width - left - right
    out = [f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="Missing values per column">']
    for i, (name, n, how) in enumerate(rows):
        y = 4 + i * rh
        w = pw * n / vmax
        out.append(f'<g class="bar"><title>{escape(name)}: {n} missing, filled with {how}</title>'
                   f'<text class="xlab" x="{left-12}" y="{y+17}" text-anchor="end">{escape(name)}</text>'
                   f'<rect x="{left}" y="{y+4}" width="{w:.1f}" height="16" rx="8" fill="{PURPLES[2] if how=="median" else "#e879a9"}"/>'
                   f'<text class="val" x="{left+w+8:.1f}" y="{y+17}">{n}</text></g>')
    out.append('</svg>')
    return Markup("".join(out))


def trend_chart(mean_x, mean_y, r, sd_x, sd_y, width=520, height=330):
    """Quiz vs Final: straight trend line implied by the correlation (no raw points)."""
    left, right, top, bottom = 58, 20, 24, 52
    pw, ph = width - left - right, height - top - bottom
    slope = r * sd_y / sd_x
    icpt = mean_y - slope * mean_x

    def X(v): return left + pw * v / 100

    def Y(v): return top + ph - ph * v / 100
    out = [f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="Quiz average versus final exam trend">']
    out.append('<defs><linearGradient id="tl" x1="0" x2="1"><stop offset="0" stop-color="#c4b5fd"/><stop offset="1" stop-color="#6d28d9"/></linearGradient>'
               '<linearGradient id="ta" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8b5cf6" stop-opacity=".28"/><stop offset="1" stop-color="#8b5cf6" stop-opacity="0"/></linearGradient></defs>')
    for t in range(0, 101, 20):
        out.append(f'<line class="grid" x1="{left}" x2="{width-right}" y1="{Y(t):.1f}" y2="{Y(t):.1f}"/>')
        out.append(f'<text class="tick" x="{left-10}" y="{Y(t)+4:.1f}" text-anchor="end">{t}</text>')
        out.append(f'<text class="tick" x="{X(t):.1f}" y="{height-bottom+20}" text-anchor="middle">{t}</text>')
    x0, x1 = 10, 100
    y0, y1 = icpt + slope * x0, min(100, icpt + slope * x1)
    x1 = (y1 - icpt) / slope
    out.append(f'<polygon fill="url(#ta)" points="{X(x0):.1f},{Y(0):.1f} {X(x0):.1f},{Y(y0):.1f} {X(x1):.1f},{Y(y1):.1f} {X(x1):.1f},{Y(0):.1f}"/>')
    out.append(f'<line x1="{X(x0):.1f}" y1="{Y(y0):.1f}" x2="{X(x1):.1f}" y2="{Y(y1):.1f}" stroke="url(#tl)" stroke-width="5" stroke-linecap="round"/>')
    for q in (30, 50, 70, 90):
        y = icpt + slope * q
        out.append(f'<g class="bar"><title>Quiz {q} → expected final ≈ {y:.0f}</title>'
                   f'<circle cx="{X(q):.1f}" cy="{Y(y):.1f}" r="8" fill="#fff" stroke="#6d28d9" stroke-width="4"/>'
                   f'<text class="val" x="{X(q):.1f}" y="{Y(y)-16:.1f}" text-anchor="middle">{y:.0f}</text></g>')
    out.append(f'<text class="axis" x="{left+pw/2}" y="{height-8}" text-anchor="middle">Quiz average</text>')
    out.append(f'<text class="axis" transform="translate(14 {top+ph/2}) rotate(-90)" text-anchor="middle">Expected final exam score</text>')
    out.append('</svg>')
    return Markup("".join(out))


def _mix(c1, c2, t):
    return tuple(round(a + (b - a) * t) for a, b in zip(c1, c2))


def heat_color(v):
    """White-lavender -> deep purple for 0..1 (negatives clamp to 0)."""
    t = max(0.0, min(1.0, v))
    lo, mid, hi = (245, 243, 255), (167, 139, 250), (76, 29, 149)
    rgb = _mix(lo, mid, t / 0.5) if t < 0.5 else _mix(mid, hi, (t - 0.5) / 0.5)
    lum = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
    return f"rgb{rgb}", "#fff" if lum < 150 else "#2e1065"


def score_ring(score, color="#7c3aed", size=190):
    r = 78
    circ = 2 * 3.14159265 * r
    dash = circ * max(0, min(100, score)) / 100
    return Markup(
        f'<svg class="ring" viewBox="0 0 {size} {size}" role="img" aria-label="Estimated score {score:.0f} out of 100">'
        f'<circle cx="{size/2}" cy="{size/2}" r="{r}" class="ring-bg"/>'
        f'<circle cx="{size/2}" cy="{size/2}" r="{r}" fill="none" stroke="{color}" stroke-width="16" stroke-linecap="round" '
        f'stroke-dasharray="{dash:.1f} {circ:.1f}" transform="rotate(-90 {size/2} {size/2})"/>'
        f'<text x="50%" y="52%" text-anchor="middle" class="ring-num">{score:.0f}</text>'
        f'<text x="50%" y="66%" text-anchor="middle" class="ring-sub">out of 100</text></svg>')


def bell_curve(score, mean=59.50, std=18.93, pct=50.0, width=540, height=220):
    """Normal distribution bell curve showing cohort spread and user percentile."""
    left, right, top, bottom = 44, 44, 30, 42
    pw, ph = width - left - right, height - top - bottom

    def pdf(x):
        return (1.0 / (std * math.sqrt(2 * math.pi))) * math.exp(-0.5 * ((x - mean) / std) ** 2)

    ymax = pdf(mean) * 1.15

    def X(x_val):
        return left + pw * max(0.0, min(100.0, x_val)) / 100.0

    def Y(y_val):
        return top + ph - ph * (y_val / ymax)

    xs = [x for x in range(0, 101, 1)]
    pts = [(X(x), Y(pdf(x))) for x in xs]

    user_s = max(0.0, min(100.0, score))
    shade_pts = [(X(x), Y(pdf(x))) for x in xs if x <= user_s]
    shade_pts.append((X(user_s), Y(pdf(user_s))))
    shade_poly = [f"{X(0):.1f},{Y(0):.1f}"] + [f"{x:.1f},{y:.1f}" for x, y in shade_pts] + [f"{X(user_s):.1f},{Y(0):.1f}"]

    out = [f'<svg class="chart bell-chart" viewBox="0 0 {width} {height}" role="img" aria-label="Cohort bell curve distribution">']
    out.append('<defs>')
    out.append('<linearGradient id="bellShade" x1="0" y1="0" x2="0" y2="1">'
               '<stop offset="0" stop-color="#8b5cf6" stop-opacity=".45"/>'
               '<stop offset="1" stop-color="#8b5cf6" stop-opacity=".05"/></linearGradient>')
    out.append('<linearGradient id="bellLine" x1="0" y1="0" x2="1" y2="0">'
               '<stop offset="0" stop-color="#c4b5fd"/>'
               '<stop offset="50%" stop-color="#8b5cf6"/>'
               '<stop offset="1" stop-color="#6d28d9"/></linearGradient>')
    out.append('</defs>')

    out.append(f'<line class="grid" x1="{left}" x2="{width-right}" y1="{top+ph:.1f}" y2="{top+ph:.1f}"/>')
    out.append(f'<polygon points="{" ".join(shade_poly)}" fill="url(#bellShade)"/>')

    line_d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    out.append(f'<path d="{line_d}" fill="none" stroke="url(#bellLine)" stroke-width="3" stroke-linecap="round"/>')

    mx = X(mean)
    my = Y(pdf(mean))
    out.append(f'<line x1="{mx:.1f}" y1="{my:.1f}" x2="{mx:.1f}" y2="{top+ph:.1f}" stroke="#a78bfa" stroke-width="1.5" stroke-dasharray="4 3"/>')
    out.append(f'<text class="tick" x="{mx:.1f}" y="{top+ph+16}" text-anchor="middle">Avg ({mean:.1f})</text>')

    for tick in (0, 25, 50, 75, 100):
        tx = X(tick)
        out.append(f'<line class="grid" x1="{tx:.1f}" x2="{tx:.1f}" y1="{top+ph}" y2="{top+ph+4}"/>')
        if abs(tick - mean) > 12:
            out.append(f'<text class="tick" x="{tx:.1f}" y="{top+ph+16}" text-anchor="middle">{tick}</text>')

    ux = X(user_s)
    uy = Y(pdf(user_s))
    out.append(f'<line x1="{ux:.1f}" y1="{uy:.1f}" x2="{ux:.1f}" y2="{top+ph:.1f}" stroke="#7c3aed" stroke-width="2.5"/>')
    out.append(f'<circle cx="{ux:.1f}" cy="{uy:.1f}" r="6" fill="#fff" stroke="#7c3aed" stroke-width="3"/>')

    tag_y = max(top + 10, uy - 12)
    tag_anchor = "start" if ux < width - 120 else "end"
    tag_x = ux + 8 if tag_anchor == "start" else ux - 8
    out.append(f'<g class="bar"><title>Your Score: {score:.1f} ({pct:.0f}th percentile)</title>'
               f'<text class="val" x="{tag_x:.1f}" y="{tag_y:.1f}" text-anchor="{tag_anchor}" fill="#6d28d9">'
               f'You: {score:.1f} ({pct:.0f}%)</text></g>')

    out.append(f'<text class="axis" x="{left+pw/2:.1f}" y="{height-4}" text-anchor="middle">Final exam score percentile range</text>')
    out.append('</svg>')
    return Markup("".join(out))


def radar_chart(axes_data, width=400, height=340):
    """Multi-axis polygon radar chart comparing user with cohort average."""
    cx = width / 2
    cy = height / 2 - 10
    radius = 105
    n = len(axes_data)
    if n < 3:
        return Markup("")

    angles = [-math.pi / 2 + i * (2 * math.pi / n) for i in range(n)]

    out = [f'<svg class="chart radar-chart" viewBox="0 0 {width} {height}" role="img" aria-label="Multi-factor radar chart">']
    out.append('<defs>')
    out.append('<linearGradient id="radarGrad" x1="0" y1="0" x2="0" y2="1">'
               '<stop offset="0" stop-color="#8b5cf6" stop-opacity=".40"/>'
               '<stop offset="1" stop-color="#6d28d9" stop-opacity=".15"/></linearGradient>')
    out.append('</defs>')

    for level in (0.25, 0.50, 0.75, 1.0):
        r_lvl = radius * level
        pts = [f"{cx + r_lvl * math.cos(a):.1f},{cy + r_lvl * math.sin(a):.1f}" for a in angles]
        out.append(f'<polygon points="{" ".join(pts)}" fill="none" stroke="var(--grid)" stroke-width="1.2"/>')

    for (name, _, _), a in zip(axes_data, angles):
        x2 = cx + radius * math.cos(a)
        y2 = cy + radius * math.sin(a)
        out.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="var(--grid)" stroke-width="1.2"/>')

        lx = cx + (radius + 20) * math.cos(a)
        ly = cy + (radius + 14) * math.sin(a)
        cos_a = math.cos(a)
        anchor = "middle" if abs(cos_a) < 0.25 else ("start" if cos_a > 0 else "end")
        out.append(f'<text class="xlab" x="{lx:.1f}" y="{ly+4:.1f}" text-anchor="{anchor}" font-size="12px">{escape(name)}</text>')

    avg_pts = [f"{cx + radius * (avg / 100.0) * math.cos(a):.1f},{cy + radius * (avg / 100.0) * math.sin(a):.1f}"
               for (_, _, avg), a in zip(axes_data, angles)]
    out.append(f'<polygon points="{" ".join(avg_pts)}" fill="none" stroke="#a78bfa" stroke-width="2" stroke-dasharray="4 3"/>')

    user_pts = [(cx + radius * (max(0.0, min(100.0, u)) / 100.0) * math.cos(a),
                 cy + radius * (max(0.0, min(100.0, u)) / 100.0) * math.sin(a))
                for (_, u, _), a in zip(axes_data, angles)]
    user_poly_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in user_pts)
    out.append(f'<polygon points="{user_poly_str}" fill="url(#radarGrad)" stroke="#7c3aed" stroke-width="2.5"/>')

    for (x, y), (name, u, _) in zip(user_pts, axes_data):
        out.append(f'<g class="bar"><title>{escape(name)}: {u:.1f}%</title>'
                   f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="#fff" stroke="#6d28d9" stroke-width="2.5"/></g>')

    leg_y = height - 12
    out.append(f'<g transform="translate({cx-85}, {leg_y})">'
               f'<circle cx="0" cy="0" r="5" fill="#7c3aed"/>'
               f'<text class="tick" x="10" y="4">You</text>'
               f'<line x1="50" y1="0" x2="68" y2="0" stroke="#a78bfa" stroke-width="2" stroke-dasharray="3 2"/>'
               f'<text class="tick" x="76" y="4">Cohort Avg</text></g>')

    out.append('</svg>')
    return Markup("".join(out))
