# AI Students Success & Performance – Flask Dashboard

A website that shows the full analysis from `project.ipynb` and lets you enter your own marks for an instant analysis.
Python + Flask + HTML/CSS only. **No JavaScript, no machine learning.**

## Quick 1-Click Launch

```bash
python run.py
```
*Automatically launches the Flask server and opens http://127.0.0.1:5000 in your default browser.*

## Manual Run

```bash
pip install -r requirements.txt
python app.py
```
Open **http://127.0.0.1:5000** for the dashboard, or **http://127.0.0.1:5000/about** for the Problem Statement, Documentation & Team Collaborators.

## Run Tests

```bash
python -m unittest discover tests
```

## Folder Structure

```
student_dashboard/
├── run.py            # 1-click launcher (starts server + opens browser)
├── app.py            # Flask routes ('/', '/about', '/export', error handlers)
├── analysis.py       # Rule-based analyser, presets, CI, target seeker
├── charts.py         # SVG charts (bars, trend, bell curve, radar, ring)
├── data.py           # Numbers, statistics & collaborators metadata
├── about.html        # Standalone documentation & team page
├── templates/
│   ├── index.html    # Full dashboard template
│   ├── about.html    # Project documentation & collaborators cards template
│   └── error.html    # Custom 404 & 500 error page
├── static/
│   └── style.css     # Responsive design system & print stylesheet
└── tests/            # Automated test suite (analysis, charts, routes)
```

## Features
- **Zero JavaScript**: Server-rendered SVG charts dynamically generated in pure Python.
- **Team & Collaborators**: Showcase cards with GitHub/portfolio links, roles, and biographies.
- **Problem Statement & Documentation**: Deep dive into educational challenges and interpretable AI.
- **Statistical Confidence Intervals**: Estimated scores include a 95% confidence interval ($\pm 8.5$ points).
- **Visualizations**: Cohort Gaussian bell curve with percentile marker and 6-axis normalized radar chart.
- **Target Grade Seeker**: Concrete recommendations and gap calculations to reach the next higher grade tier.
- **Quick Archetype Presets**: One-click test scenarios (Average Student, High Potential, Diligent Achiever, Needs Support).
- **Export & Print**: One-click CSV performance report download (`/export`) and clean print-friendly PDF styling (`@media print`).
