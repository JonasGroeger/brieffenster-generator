# Brieffenster-Generator

A Flask web application that generates PDF letter headers (Briefköpfe) for printing on German DIN 5008-compliant letterhead paper aligned with envelope windows (Brieffenster).

## Architecture

- **Framework**: Flask with Jinja2 templates
- **PDF generation**: ReportLab (canvas API, precise mm positioning)
- **Fonts**: Latin Modern Roman TrueType fonts (bundled in `src/brieffenster_generator/fonts/`)
- **Package manager**: uv
- **Production server**: Gunicorn (4 workers, 4 threads)

## Project Structure

```
src/brieffenster_generator/
├── app.py          # Flask app, routes, PDF generation logic
├── wsgi.py         # WSGI entry point for Gunicorn
├── fonts/          # Latin Modern Roman TrueType fonts
└── templates/
    ├── layout.html # Base HTML template
    └── form.html   # Input form (German UI)
```

## Routes

- `GET /` — Renders the input form
- `POST /generate/` — Validates form fields, calls `generate_pdf_data()`, returns `Briefkopf.pdf`

### Form fields

| Field        | Description                     |
|--------------|---------------------------------|
| `abs_name`   | Sender name                     |
| `abs_street` | Sender street                   |
| `abs_city`   | Sender postal code + city       |
| `empf_name`  | Recipient name                  |
| `empf_street`| Recipient street                |
| `empf_city`  | Recipient postal code + city    |

## Development

```bash
# Install dependencies
uv sync

# Run dev server
uv run python -m brieffenster_generator.app
```

## Docker

```bash
# Build and run
docker compose up --build

# Access at http://localhost:10000/
```

The `docker-entrypoint.sh` runs Gunicorn bound to `0.0.0.0:10000`. The Compose file maps it to `127.0.0.1:10000` only.

## Known Issues / TODOs

- `SECRET_KEY` in `app.py` is hardcoded — set via environment variable for production
- Client-side form validation is not yet implemented (see `TODO.txt`)
