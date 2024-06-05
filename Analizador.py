from flask import Flask, request, render_template_string
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'cargas/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

keywords = {
    'int': 'Palabra reservada',
    'for': 'Palabra reservada',
    'if': 'Palabra reservada',
    'else': 'Palabra reservada',
    'while': 'Palabra reservada',
    'return': 'Palabra reservada',
    'public': 'Palabra reservada',
    'class': 'Palabra reservada',
    'static': 'Palabra reservada',
    'void': 'Palabra reservada',
    'System.out.println': 'Palabra reservada'
}

def lexical_analysis(code):
    result = []
    lines = code.split('\n')
    for line_number, line in enumerate(lines, start=1):
        index = 0
        while index < len(line):
            token_detected = False
            for keyword in keywords:
                if line[index:].startswith(keyword) and (index + len(keyword) == len(line) or not line[index + len(keyword)].isalnum()):
                    result.append((line_number, index, keywords[keyword], keyword))
                    index += len(keyword)
                    token_detected = True
                    break
            if token_detected:
                continue

            char = line[index]
            if char in [';', '{', '}', '(', ')', '[', ']']:
                tipo = 'Punto y coma' if char == ';' else 'Llave' if char in ['{', '}'] else 'Paréntesis' if char in ['(', ')'] else 'Corchete'
                result.append((line_number, index, tipo, char))
                index += 1
            elif char.isdigit():
                start = index
                while index < len(line) and line[index].isdigit():
                    index += 1
                result.append((line_number, start, 'Número', line[start:index]))
            elif char.isalpha() or char == '_':
                start = index
                while index < len(line) and (line[index].isalnum() or line[index] == '_'):
                    index += 1
                result.append((line_number, start, 'Identificador', line[start:index]))
            else:
                index += 1
    return result

def syntactic_analysis(code):
    result = []
    lines = code.split('\n')
    for line_number, line in enumerate(lines, start=1):
        stripped_line = line.strip()
        if stripped_line.startswith('System.out.'):
            if stripped_line.startswith('System.out.println'):
                result.append((line_number, 'System.out.println', True))
            else:
                result.append((line_number, stripped_line.split('(')[0], False))
        elif 'System' in stripped_line or '.out' in stripped_line:
            result.append((line_number, stripped_line.split('(')[0], False))
        else:
            tokens = stripped_line.split()
            if len(tokens) > 0:
                if tokens[0] in keywords:
                    result.append((line_number, tokens[0].capitalize(), True))
                elif any(keyword in tokens[0] for keyword in keywords):
                    result.append((line_number, tokens[0].capitalize(), False))
                else:
                    result.append((line_number, tokens[0], False))
    return result

@app.route('/', methods=['GET', 'POST'])
def index():
    code = ""
    lexical_result = []
    syntactic_result = []
    if request.method == 'POST':
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            with open(file_path, 'r') as f:
                code = f.read()
        elif 'code' in request.form and request.form['code'].strip() != '':
            code = request.form['code']
        else:
            return "No file selected or code provided"
        
        lexical_result = lexical_analysis(code)
        syntactic_result = syntactic_analysis(code)
        
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Roboto', sans-serif;
                background-color: #f3f4f6;
                color: #333;
                margin: 0;
                padding: 20px;
            }
            h1, h2 {
                color: #5c67f2;
                text-align: center;
            }
            form {
                background: #ffffff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                width: 90%;
                max-width: 600px;
                margin: 20px auto;
            }
            input[type="file"], input[type="submit"], textarea {
                width: 100%;
                padding: 12px;
                margin-top: 10px;
                border-radius: 8px;
                border: 1px solid #ccc;
                box-sizing: border-box;
            }
            input[type="submit"] {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
            }
            input[type="submit"]:hover {
                background-color: #45a049;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            th, td {
                padding: 10px;
                border: 1px solid #ccc;
                text-align: left;
            }
            th {
                background-color: #eee;
            }
        </style>
        <title>Analizador Léxico y Sintáctico</title>
    </head>
    <body>
        <h1>Analizador Léxico y Sintáctico</h1>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="file">
            <textarea name="code" placeholder="O ingresa el código aquí...">{{ code }}</textarea>
            <input type="submit" value="Ejecutar">
        </form>

        {% if lexical_result %}
        <h2>Análisis Léxico</h2>
        <table>
            <tr>
                <th>Línea</th>
                <th>Posición</th>
                <th>Tipo de Token</th>
                <th>Token</th>
            </tr>
            {% for line in lexical_result %}
            <tr>
                <td>{{ line[0] }}</td>
                <td>{{ line[1] }}</td>
                <td>{{ line[2] }}</td>
                <td>{{ line[3] }}</td>
            </tr>
            {% endfor %}
        </table>
        {% endif %}

        {% if syntactic_result %}
        <h2>Análisis Sintáctico</h2>
        <table>
            <tr>
                <th>Línea</th>
                <th>Tipo de Estructura</th>
            </tr>
            {% for line in syntactic_result %}
            <tr>
                <td>{{ line[0] }}</td
                <td>{{ line[1] }}</td>
                <td>{{ 'Correcta' if line[2] else 'Incorrecta' }}</td>
            </tr>
            {% endfor %}
        </table>
        {% endif %}
    </body>
    </html>
    """, code=code, lexical_result=lexical_result, syntactic_result=syntactic_result)

if __name__ == '__main__':
    app.run(debug=True)