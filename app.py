import csv
import io
from urllib.parse import urlencode
from flask import Flask, Response, render_template, request

import analysis
import charts
import data as D

app = Flask(__name__)


def build_charts():
    grade_cols = ["#4c1d95", "#6d28d9", "#8b5cf6", "#a78bfa", "#c4b5fd", "#e879a9"]
    s = D.STATS
    return dict(
        missing=charts.hbar_missing(D.MISSING),
        grades=charts.bar_chart(D.GRADES, colors=grade_cols, y_label="Number of students", decimals=0, step=200, ymax=1200),
        scores=charts.bar_chart(D.AVG_SCORES, colors=["#d8a7e6", "#8b5cf6", "#5b21b6"], y_label="Average score", ymax=70),
        internet=charts.bar_chart(D.INTERNET, colors=["#d8a7e6", "#6d28d9"], y_label="Avg final exam score", ymax=70),
        trend=charts.trend_chart(s["quiz"]["mean"], s["final"]["mean"], D.R_QUIZ_FINAL,
                                 s["quiz"]["std"], s["final"]["std"]),
        sleep=charts.bar_chart(D.SLEEP, colors=["#c4b5fd", "#a78bfa", "#8b5cf6", "#6d28d9"], y_label="Avg final exam score", ymax=70),
        study=charts.bar_chart(D.STUDY, colors=["#c4b5fd", "#a78bfa", "#8b5cf6", "#6d28d9"], y_label="Avg final exam score", ymax=80),
        attendance=charts.bar_chart(D.ATTENDANCE, colors=["#c4b5fd", "#a78bfa", "#8b5cf6", "#6d28d9"], y_label="Avg final exam score", ymax=70),
        completion=charts.bar_chart(D.COMPLETION, colors=["#c4b5fd", "#8b5cf6", "#6d28d9"], y_label="Avg final exam score", ymax=70),
    )


def heatmap():
    rows = []
    for i, row in enumerate(D.CORR):
        cells = []
        for v in row:
            bg, fg = charts.heat_color(v)
            cells.append((f"{v:.2f}", bg, fg))
        rows.append((D.CORR_LABELS[i], cells))
    return rows


@app.route("/", methods=["GET", "POST"])
def index():
    values, errors, result = {}, {}, None
    active_preset = None

    if request.method == "POST":
        values, errors = analysis.parse(request.form)
        if not errors:
            result = analysis.analyse(values)
    else:
        preset_key = request.args.get("preset")
        if preset_key and preset_key in analysis.PRESETS:
            values = dict(analysis.PRESETS[preset_key]["data"])
            result = analysis.analyse(values)
            active_preset = preset_key
        elif request.args.get("sample"):
            values = dict(analysis.SAMPLE)
            result = analysis.analyse(values)
            active_preset = "sample"
        elif "quiz" in request.args:
            values, errors = analysis.parse(request.args)
            if not errors:
                result = analysis.analyse(values)

    values.setdefault("internet", "yes")

    ring, bell, radar = None, None, None
    export_query = ""
    if result:
        color = "#16a34a" if result["est"] >= 70 else "#7c3aed" if result["est"] >= 55 else "#e11d48"
        ring = charts.score_ring(result["est"], color)
        bell = charts.bell_curve(result["est"], D.STATS["final"]["mean"], D.STATS["final"]["std"], result["pct"])
        radar = charts.radar_chart(result["radar_axes"])
        export_query = urlencode({k: values.get(k, "") for k, _, _, _, _, _, _ in analysis.FIELDS} | {"internet": values.get("internet", "yes")})

    top = max(D.GRADES, key=lambda g: g[1])
    should_scroll = bool(request.method == "POST" or request.args.get("preset") or request.args.get("sample") or "quiz" in request.args)

    return render_template(
        "index.html", D=D, charts=build_charts(), heat=heatmap(), fields=analysis.FIELDS,
        values=values, errors=errors, result=result, ring=ring, bell=bell, radar=radar,
        top_grade=top, presets=analysis.PRESETS, active_preset=active_preset,
        export_query=export_query,
        study_gain=D.STUDY[-1][1] - D.STUDY[0][1],
        att_gain=D.ATTENDANCE[-1][1] - D.ATTENDANCE[0][1],
        net_gain=D.INTERNET[1][1] - D.INTERNET[0][1],
        scroll=should_scroll,
    )


@app.route("/about")
def about():
    return render_template("about.html", D=D, collaborators=D.COLLABORATORS)


@app.route("/export")
def export():
    values, errors = analysis.parse(request.args)
    if errors or not values:
        values = dict(analysis.SAMPLE)
    result = analysis.analyse(values)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Student Academic & Performance Report"])
    writer.writerow(["AI Students Success & Performance Dashboard"])
    writer.writerow([])
    writer.writerow(["--- ESTIMATED OUTCOME ---"])
    writer.writerow(["Estimated Final Exam Score", f"{result['est']:.1f} / 100"])
    writer.writerow(["Estimated Grade", result["grade"]])
    writer.writerow(["95% Confidence Interval", f"{result['ci_low']} to {result['ci_high']} pts (margin +/-{result['ci_margin']} pts)"])
    writer.writerow(["Cohort Percentile", f"{result['pct']:.1f}th percentile"])
    writer.writerow(["Cohort Comparison", f"{result['above']:+.1f} pts relative to student average ({D.STATS['final']['mean']:.1f})"])
    writer.writerow(["Verdict", result["verdict"]])
    writer.writerow([])
    writer.writerow(["--- YOUR METRICS VS COHORT AVERAGE ---"])
    writer.writerow(["Metric", "Your Score", "Cohort Average", "Status"])
    for c in result["compare"]:
        status = "Above average" if c["z"] >= 0.5 else ("Below average" if c["z"] <= -0.5 else "Around average")
        writer.writerow([c["name"], f"{c['you']:.1f}{c['suf']}", f"{c['avg']:.1f}{c['suf']}", status])
    writer.writerow([])
    if result.get("target_advice") and result["target_advice"].get("next_grade"):
        ta = result["target_advice"]
        writer.writerow(["--- NEXT GRADE TARGET GOAL ---"])
        writer.writerow(["Target Grade", ta["next_grade"]])
        writer.writerow(["Score Needed", ta["target_score"]])
        writer.writerow(["Point Gap", f"+{ta['gap']:.1f} pts"])
        writer.writerow(["Recommended Actions"])
        for act in ta["actions"]:
            writer.writerow(["-", act])
        writer.writerow([])
    writer.writerow(["--- IDENTIFIED STRENGTHS ---"])
    for s in result["strengths"] or ["No areas significantly above average"]:
        writer.writerow(["+", s])
    writer.writerow([])
    writer.writerow(["--- FOCUS AREAS ---"])
    for f in result["focus"] or ["No areas significantly below average"]:
        writer.writerow(["!", f])
    writer.writerow([])
    writer.writerow(["--- ACTIONABLE TIPS ---"])
    for i, tip in enumerate(result["tips"], 1):
        writer.writerow([f"{i}.", tip])

    csv_content = output.getvalue()
    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=student_performance_report.csv"}
    )


@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", code=404, title="Page Not Found",
                           message="The requested page could not be found. Please check the address or return to the main dashboard."), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, title="Server Error",
                           message="An internal error occurred while processing your request. Please try again shortly."), 500


if __name__ == "__main__":
    app.run(debug=True)
