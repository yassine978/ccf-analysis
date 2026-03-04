# Colazzo — CCF Notebooks and Graphs

This repository contains notebooks, helper scripts, and data for the CCF analysis.

Structure
- `notebooks/` — Jupyter notebooks
- `python/` — helper scripts (e.g. `generate_graphs.py`)
- `scala/`, `zeppelin_notebooks/` — additional notebooks and artifacts
- `data/` — generated graph data (excluded from git via `.gitignore`)

Quick start

1. Initialize a local git repo (if not already):

```
git init
git add .
git commit -m "Initial commit"
```

2. Create a GitHub repository and push:

Option A — using GitHub CLI:

```
gh repo create <owner>/<repo> --public --source=. --push
```

Option B — manual (create repo on github.com then):

```
git remote add origin https://github.com/<owner>/<repo>.git
git branch -M main
git push -u origin main
```

3. Start the local services (if required):

```
docker-compose up -d
```

Notes
- Notebooks are in `notebooks/`.
- Use `python/generate_graphs.py` to regenerate graph files in `data/`.
- See `.gitignore` and `requirements.txt` for repo settings.
