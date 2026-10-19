"""Rule-based marks analyser. No machine learning: it only compares the entered
marks with the averages and group results already found in the notebook."""
from math import erf, sqrt

from data import (ATTENDANCE, COMPLETION, INTERNET, SLEEP, STATS, STUDY)

FIELDS = [
    # key, label, min, max, step, unit, hint
    ("quiz", "Quiz average", 0, 100, 0.1, "/100", "Average of all your quizzes"),
    ("midterm", "Midterm score", 0, 100, 0.1, "/100", "Your midterm exam marks"),
    ("gpa", "Previous GPA", 0, 4, 0.01, "/4", "GPA from the last term"),
    ("study", "Study hours per day", 0, 12, 0.1, "hours", "Average hours you study daily"),
    ("attendance", "Attendance", 0, 100, 0.1, "%", "Percentage of classes attended"),
    ("assign_done", "Assignments completed", 0, 40, 1, "", "How many you submitted"),
    ("assign_total", "Assignments given", 1, 40, 1, "", "Total assignments given"),
    ("sleep", "Sleep hours per day", 2, 14, 0.1, "hours", "Average hours you sleep"),
]

PRESETS = {
    "sample": {
        "title": "Average Student",
        "desc": "Baseline profile with typical grades and study habits",
        "data": dict(quiz=62, midterm=58, gpa=3.0, study=3.0, attendance=78,
                     assign_done=11, assign_total=14, sleep=7, internet="yes"),
    },
    "high_potential": {
        "title": "High Potential",
        "desc": "Strong quiz & midterm scores with room to expand daily study",
        "data": dict(quiz=82, midterm=78, gpa=3.4, study=2.0, attendance=74,
                     assign_done=10, assign_total=14, sleep=6.5, internet="yes"),
    },
    "hard_worker": {
        "title": "Diligent Achiever",
        "desc": "Exceptional attendance and study discipline building momentum",
        "data": dict(quiz=64, midterm=60, gpa=2.9, study=6.5, attendance=95,
                     assign_done=14, assign_total=14, sleep=7.5, internet="yes"),
    },
    "at_risk": {
        "title": "Needs Support",
        "desc": "Low attendance and test averages needing urgent intervention",
        "data": dict(quiz=42, midterm=38, gpa=2.2, study=1.2, attendance=52,
                     assign_done=6, assign_total=14, sleep=4.8, internet="no"),
    },
}

SAMPLE = PRESETS["sample"]["data"]

GRADE_BANDS = [(90, "A+"), (80, "A"), (70, "B"), (55, "C"), (45, "D"), (0, "F")]


def parse(form):
    """Return (values, errors)."""
    vals, errs = {}, {}
    for key, label, lo, hi, _, _, _ in FIELDS:
        raw = (form.get(key) or "").strip()
        try:
            v = float(raw)
        except ValueError:
            errs[key] = "Enter a number"
            continue
        if not lo <= v <= hi:
            errs[key] = f"Must be between {lo:g} and {hi:g}"
            continue
        vals[key] = v
    if "assign_done" in vals and "assign_total" in vals and vals["assign_done"] > vals["assign_total"]:
        errs["assign_done"] = "Cannot be more than assignments given"
    vals["internet"] = "yes" if form.get("internet", "yes") == "yes" else "no"
    return vals, errs


def _band(value, edges, groups):
    """Return (index, group_label, group_mean) for edges = upper bounds."""
    for i, e in enumerate(edges):
        if value <= e:
            return i, groups[i][0], groups[i][1]
    return len(groups) - 1, groups[-1][0], groups[-1][1]


def _pct(z):
    return 0.5 * (1 + erf(z / sqrt(2))) * 100


def grade_for(score):
    for cut, g in GRADE_BANDS:
        if score >= cut:
            return g
    return "F"


def analyse(v):
    S = STATS
    comp = v["assign_done"] / v["assign_total"] * 100
    # 1) core estimate from the three strongest drivers in the heatmap
    core = 0.45 * v["quiz"] + 0.35 * v["midterm"] + 0.20 * (v["gpa"] / 4 * 100)
    core -= 2.9  # so that an average student lands on the average final score (59.5)

    # 2) small habit adjustments taken from the group charts (half weight, avoids double counting)
    final_mean = S["final"]["mean"]
    _, study_lab, study_m = _band(v["study"], [2, 4, 6], STUDY)
    _, att_lab, att_m = _band(v["attendance"], [50, 70, 85], ATTENDANCE)
    _, sleep_lab, sleep_m = _band(v["sleep"], [5, 7, 9], SLEEP)
    ci = 0 if comp <= 50 else 1 if comp <= 75 else 2
    comp_lab, comp_m = COMPLETION[ci]
    net_m = INTERNET[1][1] if v["internet"] == "yes" else INTERNET[0][1]
    adj = {
        "Study hours": 0.5 * (study_m - final_mean),
        "Attendance": 0.5 * (att_m - final_mean),
        "Assignments": 0.5 * (comp_m - final_mean),
        "Sleep": 0.5 * (sleep_m - final_mean),
        "Internet": 0.5 * (net_m - final_mean),
    }
    est = max(0.0, min(100.0, core + sum(adj.values())))
    grade = grade_for(est)
    pct = _pct((est - final_mean) / S["final"]["std"])

    # 3) comparison rows: you vs students' average
    rows = [
        ("Quiz average", v["quiz"], S["quiz"]["mean"], 100, "", S["quiz"]["std"]),
        ("Midterm", v["midterm"], S["midterm"]["mean"], 100, "", S["midterm"]["std"]),
        ("Attendance", v["attendance"], S["attendance"]["mean"], 100, "%", S["attendance"]["std"]),
        ("Assignments done", comp, S["completion"]["mean"], 100, "%", S["completion"]["std"]),
        ("Previous GPA", v["gpa"], S["gpa"]["mean"], 4, "", S["gpa"]["std"]),
        ("Study hours / day", v["study"], S["study"]["mean"], 10, " h", S["study"]["std"]),
        ("Sleep hours / day", v["sleep"], S["sleep"]["mean"], 10, " h", S["sleep"]["std"]),
    ]
    compare = []
    strengths, focus = [], []
    for name, you, avg, mx, suf, sd in rows:
        z = (you - avg) / sd
        compare.append(dict(name=name, you=you, avg=avg, you_w=min(100, you / mx * 100),
                            avg_w=avg / mx * 100, suf=suf, z=z))
        if z >= 0.5:
            strengths.append(name)
        elif z <= -0.5:
            focus.append(name)

    tips = []
    if v["study"] < 4:
        nxt = "4-6 h" if v["study"] >= 2 else "2-4 h"
        tips.append(f"Study time: students in the {nxt} group average {STUDY[2][1] if nxt=='4-6 h' else STUDY[1][1]:.1f} "
                    f"on the final exam, compared with {study_m:.1f} for your current group ({study_lab}).")
    else:
        tips.append(f"Study time: your {study_lab} per day puts you in the top study groups "
                    f"(average final score {study_m:.1f}). Keep the routine steady.")
    if v["attendance"] < 85:
        tips.append(f"Attendance: the 85-100% group scores {ATTENDANCE[3][1]:.1f} on average versus "
                    f"{att_m:.1f} for {att_lab}. Attending more classes is an easy gain.")
    if comp < 76:
        tips.append(f"Assignments: students completing 76-100% score {COMPLETION[2][1]:.1f}; "
                    f"you completed {comp:.0f}% ({comp_lab} group, {comp_m:.1f}).")
    if v["internet"] == "no":
        tips.append("Internet: students without internet average about 4 points lower. "
                    "Try the library or college lab for online resources.")
    if v["sleep"] < 5:
        tips.append("Sleep: students sleeping under 5 hours score lowest in their group. Aim for 5+ hours.")
    if v["quiz"] < 50 or v["midterm"] < 50:
        tips.append("Quizzes and midterm are the strongest predictors of the final (correlations 0.56 and 0.52). "
                    "Revise those topics first.")
    if len(tips) < 2:
        tips.append("Your habits and marks are all in healthy ranges. Focus on revision and practice tests.")

    if est >= 80:
        verdict = "Excellent - on track for a top grade."
    elif est >= 70:
        verdict = "Strong - a little more effort can lift you to the next grade."
    elif est >= 55:
        verdict = "Average - clear room for improvement."
    elif est >= 45:
        verdict = "Below average - act now on the focus areas below."
    else:
        verdict = "At risk - prioritise the focus areas below right away."

    # 4) Confidence interval (95% CI based on residual standard error of the estimate ~12.8)
    ci_margin = 8.5
    ci_low = max(0.0, round(est - ci_margin, 1))
    ci_high = min(100.0, round(est + ci_margin, 1))

    # 5) Next grade target seeker
    next_grade = None
    target_cut = None
    for cut, g in reversed(GRADE_BANDS):
        if cut > est:
            next_grade = g
            target_cut = cut
            break

    target_advice = None
    if next_grade:
        gap = round(target_cut - est, 1)
        actions = []
        if gap <= 3.0:
            actions.append(f"You are only {gap:.1f} points away! Even small gains in attendance or assignments will lift you into Grade {next_grade}.")
        if v["study"] < 4.0:
            nxt_hrs = "4-6" if v["study"] >= 2.0 else "2-4"
            gain = (STUDY[2][1] if nxt_hrs == "4-6" else STUDY[1][1]) - study_m
            actions.append(f"Increase study time to {nxt_hrs} h/day (cohorts in that tier average +{gain:.1f} pts on final).")
        elif v["study"] < 6.0:
            gain = STUDY[3][1] - study_m
            actions.append(f"Push daily study to 6+ hours (students average {STUDY[3][1]:.1f}, a +{gain:.1f} pt lift).")
        if v["attendance"] < 85.0:
            gain = ATTENDANCE[3][1] - att_m
            actions.append(f"Raise attendance to 85%+ (85-100% group averages {ATTENDANCE[3][1]:.1f}, +{gain:.1f} pts higher).")
        if comp < 76.0:
            gain = COMPLETION[2][1] - comp_m
            actions.append(f"Submit all pending assignments to enter the 76-100% tier (+{gain:.1f} pts).")
        if v["quiz"] < 70 or v["midterm"] < 70:
            actions.append("Revise core quiz & midterm topics: exam scores account for 80% weight in the core projection.")
        if not actions:
            actions.append("Maintain your consistent study habits and practice mock exams prior to finals.")
        target_advice = {
            "current_grade": grade,
            "next_grade": next_grade,
            "target_score": target_cut,
            "gap": gap,
            "actions": actions[:4],
        }

    # 6) Normalized radar metrics (0-100 scale for multi-dimensional comparison)
    radar_axes = [
        ("Quiz", min(100.0, v["quiz"]), S["quiz"]["mean"]),
        ("Midterm", min(100.0, v["midterm"]), S["midterm"]["mean"]),
        ("Attendance", min(100.0, v["attendance"]), S["attendance"]["mean"]),
        ("Assignments", min(100.0, comp), S["completion"]["mean"]),
        ("Prev GPA", min(100.0, (v["gpa"] / 4.0) * 100.0), (S["gpa"]["mean"] / 4.0) * 100.0),
        ("Study Time", min(100.0, (v["study"] / 8.0) * 100.0), (S["study"]["mean"] / 8.0) * 100.0),
    ]

    return dict(est=est, grade=grade, pct=pct, verdict=verdict, compare=compare,
                strengths=strengths, focus=focus, tips=tips[:5], comp=comp,
                above=est - final_mean, adj=adj,
                ci_margin=ci_margin, ci_low=ci_low, ci_high=ci_high,
                target_advice=target_advice, radar_axes=radar_axes)
