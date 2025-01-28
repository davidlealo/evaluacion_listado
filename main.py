from flask import Flask, request
import pandas as pd
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # 1. Verificamos si en la solicitud POST viene un archivo bajo la clave 'file'
        if 'file' not in request.files:
            return "No se encontró ningún archivo en la solicitud.", 400

        file = request.files['file']

        # 2. Verificamos que el usuario efectivamente haya seleccionado un archivo
        if file.filename == '':
            return "No se seleccionó ningún archivo.", 400

        # 3. Guardamos el archivo en el directorio actual de Replit
        file.save(os.path.join('.', file.filename))

        # 4. Procesamos el archivo con pandas
        try:
            # Lee el archivo Excel (suponiendo que tiene hojas: Vida, Salud, Dental, Catastrófico)
            excel_data = pd.ExcelFile(file.filename)
            df_vida = pd.read_excel(excel_data, sheet_name="Vida")
            df_salud = pd.read_excel(excel_data, sheet_name="Salud")
            df_dental = pd.read_excel(excel_data, sheet_name="Dental")
            df_catastrofico = pd.read_excel(excel_data, sheet_name="Catastrófico")

            # Concatenamos en un solo DataFrame
            dfs = [df_vida, df_salud, df_dental, df_catastrofico]
            df_consolidado = pd.concat(
                dfs, 
                keys=["Vida", "Salud", "Dental", "Catastrófico"], 
                names=["Póliza"]
            )
            df_consolidado.reset_index(level=1, drop=True, inplace=True)
            df_consolidado.reset_index(inplace=True)

            # Creamos una tabla pivote
            df_pivot = pd.pivot_table(
                df_consolidado, 
                index=["Nombre", "RUT"], 
                columns="Póliza", 
                values="Valor Prima (UF)", 
                aggfunc="sum", 
                fill_value=0
            )

            # Convertimos el DataFrame final a HTML para mostrarlo
            html_table = df_pivot.to_html()

            # Mostramos la tabla resultante
            return f"""
            <h2>Archivo {file.filename} subido exitosamente y procesado.</h2>
            <h3>Resultados de la tabla pivote:</h3>
            {html_table}
            <br><br>
            <a href="/">Volver</a>
            """

        except Exception as e:
            return f"Ocurrió un error al procesar el archivo: {e}", 500

    # Si la solicitud es GET, mostramos un formulario simple para subir el Excel
    return '''
    <html>
    <head>
        <title>Subir un archivo Excel</title>
    </head>
    <body>
        <h1>Subir un archivo Excel</h1>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="file">
            <button type="submit">Subir</button>
        </form>
    </body>
    </html>
    '''

if __name__ == '__main__':
    # En Replit suele funcionar con host='0.0.0.0' y un puerto como el 81 o 8080
    app.run(host='0.0.0.0', port=81)
