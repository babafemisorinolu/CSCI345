# CSCI 345 slides

Lecture slides and course pages for CSCI 345, built with [Quarto](https://quarto.org/) and published through GitHub Pages.

## Set up a new repository

### 1. Create the repository

Create an empty GitHub repository, then clone it and add the project files. The repository should include:

- `_quarto.yml`
- `.github/workflows/publish.yml`
- your `.qmd` pages and any image or data files they use
- `requirements.txt` when pages execute Python code

The workflow publishes the rendered site to a `gh-pages` branch. Keep your editable Quarto source files on `main`.

### 2. Install local prerequisites

Install [Quarto](https://quarto.org/docs/get-started/) and Python 3.12. Then create a virtual environment and install the Python packages:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Windows, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Preview and render locally

Use the preview server while editing:

```bash
quarto preview
```

Before the first deployment, verify that the full site renders:

```bash
quarto render
```

This project uses Quarto's `freeze: auto` setting. Rendering creates a `_freeze/` directory containing saved Python outputs. Commit that directory so GitHub Actions does not need to rerun every notebook cell or download external data on each push.

### 4. Initialize GitHub Pages publishing

Run the following command once from the repository root:

```bash
quarto publish gh-pages
```

Follow the prompts. This creates the `gh-pages` branch and Quarto's `_publish.yml` configuration file. Commit `_publish.yml` to `main`:

```bash
git add _publish.yml _freeze
git commit -m "Configure Quarto publishing"
git push origin main
```

### 5. Configure GitHub Pages

In the GitHub repository, open **Settings → Pages** and select:

- **Source:** Deploy from a branch
- **Branch:** `gh-pages`
- **Folder:** `/(root)`

After saving, GitHub will serve the generated site from the `gh-pages` branch.

### Optional: use a custom domain

To use a custom domain, add the domain in **Settings → Pages**, configure its DNS record with your domain provider, and place the domain name in a `CNAME` file at the repository root. For a subdomain, the DNS CNAME normally points to `<your-github-username>.github.io`.

## Publishing updates

After the initial setup, only work on `main`:

```bash
git add .
git commit -m "Update lecture slides"
git push origin main
```

The **Quarto Publish** GitHub Action renders the project and updates `gh-pages` automatically. Do not edit `gh-pages` directly.

If a deployment fails, open the **Actions** tab in GitHub and inspect the failed **Quarto Publish** run.

