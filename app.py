from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# 🔥 Crear carpeta "data" automáticamente si no existe
UPLOAD_FOLDER = "data"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

EXCEL_PATH = os.path.join(UPLOAD_FOLDER, "contenido.xlsx")


def leer_excel():
    df = pd.read_excel(EXCEL_PATH, engine="openpyxl")

    # Limpiar nombres de columnas
    df.columns = df.columns.str.strip()

    datos_por_anio = {}

    for _, fila in df.iterrows():
        anio = str(int(fila["Año"]))

        if anio not in datos_por_anio:
            datos_por_anio[anio] = []

        datos_por_anio[anio].append({
            "tipo": str(fila["Tipo"]).strip(),
            "contenido": str(fila["Contenido_URL"]).strip(),
            "estilo": str(fila["Estilo"]).strip() if pd.notna(fila["Estilo"]) else ""
        })

    return datos_por_anio


@app.route("/")
def blog():
    if not os.path.exists(EXCEL_PATH):
        return render_template("blog.html", datos={}, sin_archivo=True)

    datos = leer_excel()
    return render_template("blog.html", datos=datos, sin_archivo=False)


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    mensaje = ""

    if request.method == "POST":
        if "archivo" not in request.files:
            mensaje = "No se seleccionó ningún archivo."
        else:
            archivo = request.files["archivo"]

            if archivo.filename == "":
                mensaje = "El archivo está vacío."
            else:
                # 🔥 Guardar archivo correctamente
                archivo.save(EXCEL_PATH)
                mensaje = "✅ Archivo subido correctamente. El blog ya se actualizó."

    return render_template("dashboard.html", mensaje=mensaje)


@app.route("/descargar-json")
def descargar_json():
    if not os.path.exists(EXCEL_PATH):
        return jsonify({"error": "No hay archivo cargado aún."})

    datos = leer_excel()
    return jsonify(datos)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)