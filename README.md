# AI Students Success & Performance – Flask Dashboard

A website that shows the full analysis from `project.ipynb` and lets you enter your own marks for an instant analysis.
Python + Flask + HTML/CSS only. **No JavaScript, no machine learning.**

## Run

```bash
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000

## Run Tests

```bash
python -m unittest discover tests
```

## Folder

```
student_dashboard/
├── app.py            # Flask routes ('/', '/export', error handlers)
├── analysis.py       # Rule-based analyser, presets, CI, target seeker
├── charts.py         # SVG charts (bars, trend, bell curve, radar, ring)
├── data.py           # Numbers and statistics taken from notebook analysis
├── templates/
│   ├── index.html    # Full dashboard template
│   └── error.html    # Custom 404 & 500 error page
├── static/
│   └── style.css     # Responsive design system & print stylesheet
└── tests/            # Automated test suite (analysis, charts, routes)
```

## Features
- **Zero JavaScript**: Server-rendered SVG charts dynamically generated in pure Python.
- **Statistical Confidence Intervals**: Estimated scores include a 95% confidence interval ($\pm 8.5$ points) based on residual standard error.
- **Visualizations**: Cohort Gaussian bell curve with percentile marker and 6-axis normalized radar chart.
- **Target Grade Seeker**: Concrete recommendations and gap calculations to reach the next higher grade tier.
- **Quick Archetype Presets**: One-click test scenarios (Average Student, High Potential, Diligent Achiever, Needs Support).
- **Export & Print**: One-click CSV performance report download (`/export`) and clean print-friendly PDF styling (`@media print`).
- **Methodology & FAQ**: Expandable statistical disclosures using semantic HTML5 `<details>`.
