from flask import Response

def home():
    html = """
    <html>
        <head><title>Bem-vindo</title></head>
        <body>
            <h1>Bem-vindo à Home da API!</h1>
        </body>
    </html>
    """
    return Response(html, mimetype='text/html')
