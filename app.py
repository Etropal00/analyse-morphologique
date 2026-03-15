# -*- coding: utf-8 -*-
"""
Application web d'analyse morphologique par IA.
Upload de photos -> analyse IA -> rapport complet.
"""
import os
import base64
import html
import json
from datetime import datetime
from pathlib import Path

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Dossier du projet (où se trouve app.py et .env)
PROJECT_DIR = Path(__file__).resolve().parent

def _load_env():
    """Charge le .env depuis le dossier du projet et le répertoire courant."""
    load_dotenv(PROJECT_DIR / ".env")
    load_dotenv()  # au cas où le cwd est le bon

_load_env()

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 Mo max
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)


def analyze_images_with_ai(image_paths: list) -> dict:
    """Envoie les images à l'API (OpenAI ou IA locale type Ollama) et retourne l'analyse."""
    _load_env()
    base_url = (os.getenv("OPENAI_BASE_URL") or "").strip()
    model = (os.getenv("OPENAI_MODEL") or os.getenv("LOCAL_AI_MODEL") or "").strip()
    key = (os.getenv("OPENAI_API_KEY") or "").strip()

    # Mode IA locale (ex: Ollama)
    use_local = bool(base_url)
    if use_local:
        if not model:
            model = "llava"  # modèle vision par défaut pour Ollama
        api_key = key or "ollama"
    else:
        if not key or key == "votre_cle_api_ici":
            return {
                "success": False,
                "error": "Clé API OpenAI manquante. Dans .env : soit OPENAI_API_KEY=votre_cle, soit IA locale avec OPENAI_BASE_URL=http://localhost:11434/v1 et OPENAI_MODEL=llava (Ollama).",
                "rapport": None,
            }
        api_key = key
        model = model or "gpt-4o"

    try:
        from openai import OpenAI
        if use_local:
            client = OpenAI(base_url=base_url, api_key=api_key)
        else:
            client = OpenAI(api_key=api_key)
    except Exception as e:
        return {"success": False, "error": str(e), "rapport": None}

    system_msg = (
        "You are a professional fashion and style consultant. When you receive photos, the user is asking for "
        "personalized style and wardrobe advice. Your job is to produce a helpful style report in French. "
        "Always respond with the full report. Do not refuse or say you cannot help."
    )

    user_text = (
        "Voici des photos fournies par l'utilisateur pour un conseil en style. "
        "Rédige un rapport détaillé EN FRANÇAIS, uniquement le rapport, sans phrase d'introduction ni refus.\n\n"
        "Structure du rapport :\n"
        "1. Description de ce qui est visible (tenue, contexte)\n"
        "2. Ce qui fonctionne bien dans le style actuel\n"
        "3. Conseils vêtements : coupes, matières, encolures à privilégier\n"
        "4. Suggestions de couleurs et d'associations\n"
        "5. Recommandations pratiques et conclusion\n\n"
        "Sois concret et bienveillant. Réponds UNIQUEMENT par le texte du rapport."
    )

    content = [{"type": "text", "text": user_text}]

    for path in image_paths:
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        ext = Path(path).suffix.lower()
        mime = "image/jpeg" if ext in (".jpg", ".jpeg") else "image/png"
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:{mime};base64,{data}"},
        })

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": content},
            ],
            max_tokens=3000,
        )
        rapport_text = response.choices[0].message.content
        return {
            "success": True,
            "error": None,
            "rapport": rapport_text,
        }
    except Exception as e:
        err = str(e)
        if "401" in err or "invalid_api_key" in err or "Incorrect API key" in err:
            err = "Clé API OpenAI invalide. Vérifiez le fichier .env : ouvrez-le et remplacez OPENAI_API_KEY par votre vraie clé (créez-en une sur https://platform.openai.com/account/api-keys). Redémarrez ensuite l'application."
        return {
            "success": False,
            "error": err,
            "rapport": None,
        }


@app.route("/healthz")
def healthz():
    """Health check pour Render."""
    return "", 200


@app.route("/")
def index():
    """Page d'accueil."""
    return send_from_directory("static", "index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    """
    Reçoit une ou plusieurs images, les analyse avec l'IA et retourne le rapport.
    """
    if "images" not in request.files and "image" not in request.files:
        return jsonify({"success": False, "error": "Aucune image fournie"}), 400

    files = request.files.getlist("images") or request.files.getlist("image")
    if not files or not any(f.filename for f in files):
        return jsonify({"success": False, "error": "Aucun fichier image valide"}), 400

    saved_paths = []
    try:
        for f in files:
            if not f.filename:
                continue
            ext = Path(f.filename).suffix or ".jpg"
            name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(saved_paths)}{ext}"
            path = UPLOAD_FOLDER / name
            f.save(path)
            saved_paths.append(path)

        if not saved_paths:
            return jsonify({"success": False, "error": "Aucune image enregistrée"}), 400

        result = analyze_images_with_ai(saved_paths)

        # Nettoyage des fichiers temporaires
        for p in saved_paths:
            try:
                p.unlink()
            except Exception:
                pass

        if result["success"]:
            return jsonify({
                "success": True,
                "rapport": result["rapport"],
                "date": datetime.now().isoformat(),
            })
        return jsonify({
            "success": False,
            "error": result.get("error", "Erreur d'analyse"),
        }), 500

    except Exception as e:
        for p in saved_paths:
            try:
                p.unlink()
            except Exception:
                pass
        return jsonify({"success": False, "error": str(e)}), 500


_REPORT_TITLES = {
    "fr": "Rapport de style personnalisé",
    "en": "Personal style report",
    "es": "Informe de estilo personalizado",
}
_REPORT_META = {
    "fr": "Généré le",
    "en": "Report generated on",
    "es": "Informe generado el",
}


@app.route("/api/export-report", methods=["POST"])
def export_report():
    """Génère un fichier HTML du rapport (téléchargeable)."""
    data = request.get_json() or {}
    rapport = data.get("rapport", "")
    lang = (data.get("lang") or "fr").lower()[:2]
    if lang not in _REPORT_TITLES:
        lang = "fr"
    if not rapport:
        return jsonify({"success": False, "error": "Rapport vide"}), 400

    title = _REPORT_TITLES[lang]
    meta_label = _REPORT_META[lang]
    date_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    html_lang = "fr" if lang == "fr" else "es" if lang == "es" else "en"

    html = f"""<!DOCTYPE html>
<html lang="{html_lang}">
<head>
  <meta charset="UTF-8">
  <title>{title} — StyleScan AI</title>
  <style>
    body {{ font-family: 'Segoe UI', system-ui, sans-serif; max-width: 800px; margin: 0 auto; padding: 2rem; line-height: 1.6; color: #1a1a1a; }}
    h1 {{ color: #2d3748; border-bottom: 2px solid #4a5568; padding-bottom: 0.5rem; }}
    .meta {{ color: #718096; font-size: 0.9rem; margin-bottom: 2rem; }}
    pre {{ white-space: pre-wrap; background: #f7fafc; padding: 1rem; border-radius: 8px; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <p class="meta">{meta_label} {date_str} — StyleScan AI</p>
  <div class="content">
    <pre>{html.escape(rapport)}</pre>
  </div>
</body>
</html>"""

    reports_dir = Path("static/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    filename = f"rapport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    filepath = reports_dir / filename
    filepath.write_text(html, encoding="utf-8")

    return jsonify({
        "success": True,
        "download_url": f"/static/reports/{filename}",
        "filename": filename,
    })


@app.route("/static/reports/<path:filename>")
def serve_report(filename):
    """Sert le rapport généré."""
    return send_from_directory("static/reports", filename)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "").lower() in ("1", "true", "yes")
    app.run(host="0.0.0.0", port=port, debug=debug)
