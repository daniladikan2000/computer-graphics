"""
Веб-сервер Flask для Лабораторной работы №2.
Обеспечивает REST API для обработки изображений и динамического сохранения загрузок.
"""

import os
import time
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, send_from_directory
from processing import load_image, process, to_base64

app = Flask(__name__)
IMAGES_DIR = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(IMAGES_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/presets")
def get_presets():
    """Возвращает список всех изображений из папки images."""
    files = [
        f for f in sorted(os.listdir(IMAGES_DIR))
        if os.path.splitext(f.lower())[1] in ALLOWED_EXTENSIONS
    ]
    return jsonify({"presets": files})


@app.route("/api/presets/<filename>")
def serve_preset(filename):
    return send_from_directory(IMAGES_DIR, filename)


@app.route("/api/upload", methods=["POST"])
def upload_image():
    """Сохраняет загруженное изображение в папку images и делает его доступным в пресетах."""
    if "file" not in request.files or not request.files["file"].filename:
        return jsonify({"error": "Файл не выбран"}), 400

    file = request.files["file"]
    orig_name = file.filename
    clean_name = secure_filename(orig_name)
    if not clean_name:
        clean_name = f"image_{int(time.time())}.png"

    # Проверяем расширение
    ext = os.path.splitext(clean_name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        clean_name += ".png"

    filepath = os.path.join(IMAGES_DIR, clean_name)
    file.save(filepath)

    return jsonify({
        "status": "success",
        "filename": clean_name
    })


@app.route("/api/process", methods=["POST"])
def process_endpoint():
    try:
        preset_name = request.form.get("preset")
        if preset_name:
            path = os.path.join(IMAGES_DIR, preset_name)
            if not os.path.exists(path):
                return jsonify({"error": "Файл не найден в images"}), 404
            with open(path, "rb") as f:
                img = load_image(f.read())
        elif "file" in request.files and request.files["file"].filename:
            # Если файл передан напрямую в process, также сохраняем его в images
            file = request.files["file"]
            fname = secure_filename(file.filename) or f"img_{int(time.time())}.png"
            filepath = os.path.join(IMAGES_DIR, fname)
            file_bytes = file.read()
            with open(filepath, "wb") as f:
                f.write(file_bytes)
            img = load_image(file_bytes)
        else:
            return jsonify({"error": "Изображение не выбрано"}), 400

        mode = request.form.get("mode", "point")
        params = {
            "brightness": request.form.get("brightness", 0),
            "contrast": request.form.get("contrast", 1.0),
            "gamma": request.form.get("gamma", 1.0),
            "invert": request.form.get("invert", "false") == "true"
        }

        result = process(img, mode, params)
        return jsonify({
            "status": "success",
            "data": result,
            "original": to_base64(img)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True, port=5001)
