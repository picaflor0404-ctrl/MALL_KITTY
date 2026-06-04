import webbrowser
from flask import Flask, render_template_string, request
import sqlite3

app = Flask(__name__)

def crear_base_datos():
    with sqlite3.connect('mallkitty.db') as conn:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS contactos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            imagen TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_comprador TEXT NOT NULL,
            correo TEXT NOT NULL,
            direccion TEXT NOT NULL,
            total REAL NOT NULL,
            metodo_pago TEXT NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS detalle_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER,
            producto_id INTEGER
        )
        """)

        cursor.execute("SELECT COUNT(*) FROM productos")

        if cursor.fetchone()[0] == 0:
            productos = [
                ("Vestido Floral", 29.99, "👗"),
                ("Bolso Elegante", 19.99, "👜"),
                ("Reloj Moderno", 39.99, "⌚"),
                ("Zapatillas Urban", 49.99, "👟"),
                ("Chaqueta Denim", 59.99, "🧥"),
                ("Gafas de Sol", 15.99, "🕶️")
            ]

            cursor.executemany(
                "INSERT INTO productos(nombre, precio, imagen) VALUES (?, ?, ?)",
                productos
            )

crear_base_datos()
HTML_BASE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mall Kitty</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Poppins', sans-serif;
            background: #fdf2f8;
            color: #333;
            line-height: 1.6;
        }
        
        header {
            background: #ec4899;
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 18px 50px;
            flex-wrap: wrap;
        }
        
        .logo h1 {
            font-size: 1.8em;
            font-weight: 700;
        }
        
        nav ul {
            list-style: none;
            display: flex;
            gap: 25px;
        }
        
        nav a {
            color: white;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.95em;
        }
        
        nav a:hover { text-decoration: underline; }
        
        .btn-pagar {
            background: #fbbf24;
            color: #333 !important;
            padding: 10px 22px;
            border-radius: 25px;
            font-weight: 700;
        }
        
        .btn-pagar:hover { background: #f59e0b; text-decoration: none !important; }
        
        .hero {
            background: linear-gradient(135deg, #ec4899, #f472b6);
            color: white;
            text-align: center;
            padding: 100px 20px;
        }
        
        .hero h2 {
            font-size: 2.8em;
            margin-bottom: 15px;
            font-weight: 700;
        }
        
        .hero p {
            font-size: 1.2em;
            margin-bottom: 30px;
            font-weight: 300;
        }
        
        .boton {
            background: white;
            color: #ec4899;
            padding: 15px 45px;
            text-decoration: none;
            border-radius: 50px;
            font-weight: 700;
            font-size: 1.1em;
            display: inline-block;
            border: none;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .boton:hover { background: #fce7f3; transform: translateY(-2px); }
        
        .boton-outline {
            background: transparent;
            border: 2px solid white;
            color: white;
        }
        
        .boton-outline:hover { background: white; color: #ec4899; }
        
        .contenedor-tarjetas {
            display: flex;
            justify-content: center;
            gap: 30px;
            padding: 70px 40px;
            flex-wrap: wrap;
        }
        
        .tarjeta {
            background: white;
            padding: 35px 30px;
            border-radius: 20px;
            text-align: center;
            width: 300px;
            box-shadow: 0 5px 20px rgba(236,72,153,0.1);
        }
        
        .tarjeta h2 {
            margin-bottom: 15px;
            color: #ec4899;
            font-weight: 600;
        }
        
        .seccion {
            max-width: 700px;
            margin: 50px auto;
            padding: 45px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 5px 20px rgba(236,72,153,0.1);
        }
        
        .seccion h2 {
            text-align: center;
            margin-bottom: 25px;
            color: #ec4899;
            font-weight: 700;
        }
        
        form input, form textarea, form select {
            width: 100%;
            padding: 14px;
            margin: 10px 0;
            border: 2px solid #fce7f3;
            border-radius: 10px;
            font-family: 'Poppins', sans-serif;
            font-size: 0.95em;
            transition: border 0.3s;
        }
        
        form input:focus, form textarea:focus, form select:focus {
            outline: none;
            border-color: #ec4899;
        }
        
        form textarea { height: 130px; resize: vertical; }
        
        form button {
            background: #ec4899;
            color: white;
            border: none;
            padding: 16px;
            border-radius: 50px;
            font-weight: 700;
            font-size: 1.1em;
            cursor: pointer;
            width: 100%;
            margin-top: 15px;
            transition: all 0.3s;
        }
        
        form button:hover { background: #db2777; }
        
        .producto-check {
            display: block;
            padding: 16px;
            margin: 8px 0;
            background: #fdf2f8;
            border-radius: 10px;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s;
        }
        
        .producto-check:hover { background: #fce7f3; }
        
        .mensaje {
            padding: 18px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
            font-weight: 600;
        }
        
        .exito { background: #d1fae5; color: #065f46; }
        .error { background: #fee2e2; color: #991b1b; }
        
        .galeria { padding: 50px 40px; text-align: center; }
        .galeria h2 { margin-bottom: 25px; color: #ec4899; font-weight: 700; }
        .galeria-imagenes { display: flex; gap: 20px; justify-content: center; flex-wrap: wrap; }
        .galeria-imagenes img { border-radius: 15px; width: 320px; height: 220px; object-fit: cover; }
        
        .whatsapp-float {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #25d366;
            color: white;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            text-align: center;
            font-size: 28px;
            line-height: 60px;
            box-shadow: 0 4px 15px rgba(37,211,102,0.4);
            z-index: 999;
            transition: all 0.3s;
            text-decoration: none;
            font-weight: bold;
        }
        
        .whatsapp-float:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 20px rgba(37,211,102,0.6);
        }
        
        .metodo-pago-card {
            background: #fdf2f8;
            padding: 22px;
            margin: 12px 0;
            border-radius: 10px;
        }
        
        .metodo-pago-card h3 {
            color: #ec4899;
            margin-bottom: 8px;
        }
        
        footer {
            background: #333;
            color: white;
            text-align: center;
            padding: 25px;
            font-size: 0.9em;
            margin-top: 50px;
        }
        
        @media (max-width: 600px) {
            header { flex-direction: column; gap: 15px; padding: 15px 20px; }
            nav ul { flex-direction: column; align-items: center; gap: 10px; }
            .hero h2 { font-size: 2em; }
            .contenedor-tarjetas { padding: 30px 15px; }
            .galeria-imagenes img { width: 100%; }
            .seccion { margin: 25px 15px; padding: 25px 20px; }
        }
    </style>
</head>
<body>
    <header>
        <div class="logo"><h1>Mall Kitty</h1></div>
        <nav>
            <ul>
                <li><a href="/">Inicio</a></li>
                <li><a href="/productos">Productos</a></li>
                <li><a href="/como-pagar">Como Pagar</a></li>
                <li><a href="/contacto">Contacto</a></li>
                <li><a href="/pagar" class="btn-pagar">Pagar</a></li>
            </ul>
        </nav>
    </header>
    
    {{ contenido | safe }}
    
    <a href="https://wa.me/51975615687?text=Hola%20Mall%20Kitty,%20quiero%20informacion%20sobre%20sus%20productos" 
       class="whatsapp-float" 
       target="_blank" 
       title="Escribenos por WhatsApp">
       W
    </a>
    
    <footer>
        <p>2026 Mall Kitty | Todos los derechos reservados</p>
        <p style="margin-top:5px; color:#f472b6;">Contactanos: +51 975 615 687</p>
    </footer>
</body>
</html>
"""

@app.route('/')
def inicio():
    contenido = """
    <section class="hero">
        <h2>Bienvenido a Mall Kitty</h2>
        <p>Descubre ropa, accesorios y productos modernos con los mejores precios y estilos exclusivos.</p>
        <a href="/productos" class="boton">Ver Productos</a>
    </section>
    <main>
        <section class="contenedor-tarjetas">
            <article class="tarjeta">
                <h2>Ropa Moderna</h2>
                <p>Encuentra las mejores tendencias para cualquier ocasion.</p>
            </article>
            <article class="tarjeta">
                <h2>Accesorios</h2>
                <p>Bolsos, relojes y accesorios con disenos exclusivos.</p>
            </article>
            <article class="tarjeta">
                <h2>Ofertas Especiales</h2>
                <p>Aprovecha descuentos increibles en toda la tienda.</p>
            </article>
        </section>
        <section class="galeria">
            <h2>Nuestra Tienda</h2>
            <div class="galeria-imagenes">
                <img src="https://images.unsplash.com/photo-1512436991641-6745cdb1723f?w=400" alt="Tienda">
                <img src="https://images.unsplash.com/photo-1483985988355-763728e1935b?w=400" alt="Moda">
                <img src="https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400" alt="Mall">
            </div>
        </section>
    </main>
    """
    return render_template_string(HTML_BASE, contenido=contenido)

@app.route('/productos')
def productos():
    conn = sqlite3.connect('mallkitty.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")
    productos_lista = cursor.fetchall()
    conn.close()
    
    productos_html = '<div style="display:flex; flex-wrap:wrap; gap:25px; justify-content:center; margin-top:25px;">'
    for p in productos_lista:
        productos_html += f"""
        <div style="background:white; padding:25px; border-radius:20px; text-align:center; width:220px; box-shadow:0 5px 20px rgba(236,72,153,0.1);">
            <span style="font-size:1.1em; font-weight:600; color:#ec4899;">{p['imagen']}</span>
            <h3 style="margin:10px 0;">{p['nombre']}</h3>
            <p style="color:#ec4899; font-weight:700; font-size:1.3em;">${p['precio']:.2f}</p>
        </div>
        """
    productos_html += '</div>'
    
    contenido = f"""
    <main>
        <section class="seccion">
            <h2>Nuestros Productos</h2>
            {productos_html}
            <div style="text-align:center; margin-top:35px;">
                <a href="/pagar" class="boton" style="background:#ec4899; color:white;">Realizar Pedido</a>
            </div>
        </section>
    </main>
    """
    return render_template_string(HTML_BASE, contenido=contenido)

@app.route('/como-pagar')
def como_pagar():
    contenido = """
    <main>
        <section class="seccion">
            <h2>Como Realizar tu Pago</h2>
            <p style="text-align:center; margin-bottom:25px; color:#666;">Elige el metodo que mas te convenga</p>
            
            <div class="metodo-pago-card">
                <h3>Tarjeta de Credito / Debito</h3>
                <p>Aceptamos Visa, Mastercard, American Express. Tus datos estan protegidos.</p>
            </div>
            
            <div class="metodo-pago-card">
                <h3>Transferencia Bancaria</h3>
                <p><strong>Banco:</strong> BCP<br>
                <strong>Cuenta:</strong> 123-456789-0-12<br>
                <strong>Titular:</strong> Mall Kitty SAC<br>
                <strong>CCI:</strong> 00212345678901234567</p>
                <p style="margin-top:10px; font-size:0.9em; color:#888;">Envia el comprobante a nuestro WhatsApp para confirmar tu pedido.</p>
            </div>
            
            <div class="metodo-pago-card">
                <h3>PayPal</h3>
                <p>Realiza tu pago de forma segura a traves de PayPal a: <strong>pagos@mallkitty.com</strong></p>
            </div>
            
            <div class="metodo-pago-card">
                <h3>Yape / Plin</h3>
                <p><strong>Numero:</strong> 975 615 687<br>
                <strong>Titular:</strong> Mall Kitty</p>
                <p style="margin-top:10px; font-size:0.9em; color:#888;">Envia la captura a nuestro WhatsApp para validar tu pedido.</p>
            </div>
            
            <div style="text-align:center; margin-top:35px; background:#fdf2f8; padding:25px; border-radius:10px;">
                <h3 style="color:#ec4899;">Tienes dudas?</h3>
                <p style="margin:10px 0;">Escribenos por WhatsApp y te ayudamos con tu pedido</p>
                <a href="https://wa.me/51975615687?text=Hola%20Mall%20Kitty,%20quiero%20hacer%20un%20pedido" 
                   class="boton" 
                   target="_blank"
                   style="background:#ec4899; color:white;">
                   Escribir por WhatsApp
                </a>
            </div>
            
            <div style="text-align:center; margin-top:25px;">
                <a href="/pagar" class="boton boton-outline" style="border-color:#ec4899; color:#ec4899;">Ir a Pagar</a>
            </div>
        </section>
    </main>
    """
    return render_template_string(HTML_BASE, contenido=contenido)

@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    mensaje_html = ""
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        mensaje = request.form['mensaje']
        
        try:
            conn = sqlite3.connect('mallkitty.db')
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO contactos (nombre, correo, mensaje) VALUES (?, ?, ?)",
                (nombre, correo, mensaje)
            )
            conn.commit()
            conn.close()
            mensaje_html = '<div class="mensaje exito">Tu mensaje ha sido enviado. Te responderemos pronto.</div>'
        except Exception as e:
            mensaje_html = f'<div class="mensaje error">Error: {str(e)}</div>'
    
    contenido = f"""
    <main>
        <section class="seccion">
            <h2>Contactanos</h2>
            <p style="text-align:center; margin-bottom:25px; color:#666;">Dejanos tu consulta y te responderemos a la brevedad</p>
            {mensaje_html}
            <form method="POST">
                <input type="text" name="nombre" placeholder="Nombre completo" required>
                <input type="email" name="correo" placeholder="Correo electronico" required>
                <textarea name="mensaje" placeholder="Escribe tu mensaje aqui..." required></textarea>
                <button type="submit">Enviar Mensaje</button>
            </form>
            <div style="text-align:center; margin-top:30px; padding-top:25px; border-top:1px solid #fce7f3;">
                <p>O escribenos directamente:</p>
                <a href="https://wa.me/51975615687?text=Hola%20Mall%20Kitty" 
                   class="boton" 
                   target="_blank" 
                   style="margin-top:10px; background:#ec4899; color:white;">
                   WhatsApp
                </a>
            </div>
        </section>
    </main>
    """
    return render_template_string(HTML_BASE, contenido=contenido)

@app.route('/pagar', methods=['GET', 'POST'])
def pagar():
    conn = sqlite3.connect('mallkitty.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")
    productos_lista = cursor.fetchall()
    conn.close()
    
    mensaje_html = ""
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        direccion = request.form['direccion']
        metodo_pago = request.form['metodo_pago']
        productos_ids = request.form['productos_ids'].split(',')
        total = float(request.form['total'])
        
        try:
            conn = sqlite3.connect('mallkitty.db')
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO pedidos (nombre_comprador, correo, direccion, total, metodo_pago) VALUES (?, ?, ?, ?, ?)",
                (nombre, correo, direccion, total, metodo_pago)
            )
            pedido_id = cursor.lastrowid
            
            for pid in productos_ids:
                if pid.strip():
                    cursor.execute(
                        "INSERT INTO detalle_pedido (pedido_id, producto_id) VALUES (?, ?)",
                        (pedido_id, int(pid.strip()))
                    )
            
            conn.commit()
            conn.close()
            mensaje_html = f"""
            <div class="mensaje exito">
                Pedido #{pedido_id} registrado.<br>
                Total: ${total:.2f}<br>
                Metodo: {metodo_pago}<br>
                <strong>Envia el comprobante a nuestro WhatsApp para confirmar.</strong>
            </div>
            """
        except Exception as e:
            mensaje_html = f'<div class="mensaje error">Error: {str(e)}</div>'
    
    productos_check = ""
    for p in productos_lista:
        productos_check += f"""
        <label class="producto-check">
            <input type="checkbox" value="{p['id']}" data-precio="{p['precio']}">
            {p['imagen']} - {p['nombre']} - <strong>${p['precio']:.2f}</strong>
        </label>
        """
    
    contenido = f"""
    <main>
        <section class="seccion">
            <h2>Realizar Pedido</h2>
            {mensaje_html}
            
            <h3 style="color:#ec4899; margin-bottom:15px;">Selecciona tus productos:</h3>
            <div id="productos-checkbox">
                {productos_check}
            </div>
            
            <p style="margin:25px 0; font-size:1.2em; text-align:right;">
                Total: <strong style="color:#ec4899; font-size:1.3em;">$<span id="total-mostrado">0.00</span></strong>
            </p>
            
            <form method="POST" id="formulario-pago">
                <input type="hidden" name="productos_ids" id="productos_ids">
                <input type="hidden" name="total" id="total_input">
                
                <h3 style="color:#ec4899; margin-top:25px;">Tus Datos</h3>
                <input type="text" name="nombre" placeholder="Nombre completo" required>
                <input type="email" name="correo" placeholder="Correo electronico" required>
                <input type="text" name="direccion" placeholder="Direccion de envio" required>
                
                <h3 style="color:#ec4899; margin-top:25px;">Metodo de Pago</h3>
                <select name="metodo_pago" required>
                    <option value="">Selecciona un metodo...</option>
                    <option value="Tarjeta de Credito">Tarjeta de Credito</option>
                    <option value="Tarjeta de Debito">Tarjeta de Debito</option>
                    <option value="Transferencia BCP">Transferencia BCP</option>
                    <option value="Yape/Plin">Yape / Plin</option>
                    <option value="PayPal">PayPal</option>
                </select>
                
                <button type="submit">Confirmar Pedido</button>
            </form>
            
            <p style="text-align:center; margin-top:20px; font-size:0.9em; color:#888;">
                No sabes como pagar? <a href="/como-pagar" style="color:#ec4899;">Mira nuestras opciones de pago</a>
            </p>
        </section>
    </main>
    
    <script>
        const checkboxes = document.querySelectorAll('#productos-checkbox input[type="checkbox"]');
        const totalSpan = document.getElementById('total-mostrado');
        const totalInput = document.getElementById('total_input');
        const idsInput = document.getElementById('productos_ids');
        
        checkboxes.forEach(cb => cb.addEventListener('change', actualizarTotal));
        
        function actualizarTotal() {{
            let total = 0;
            let ids = [];
            checkboxes.forEach(cb => {{
                if (cb.checked) {{
                    total += parseFloat(cb.dataset.precio);
                    ids.push(cb.value);
                }}
            }});
            totalSpan.textContent = total.toFixed(2);
            totalInput.value = total.toFixed(2);
            idsInput.value = ids.join(',');
        }}
    </script>
    """
    return render_template_string(HTML_BASE, contenido=contenido)

@app.route('/ver-contactos')
def ver_contactos():
    conn = sqlite3.connect('mallkitty.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contactos ORDER BY fecha DESC")
    contactos = cursor.fetchall()
    conn.close()
    
    html = """
    <html><head><style>
        body { font-family: 'Poppins', sans-serif; background: #fdf2f8; padding: 40px; }
        h1 { color: #ec4899; }
        table { width: 100%; border-collapse: collapse; background: white; border-radius: 10px; overflow: hidden; }
        th { background: #ec4899; color: white; padding: 15px; }
        td { padding: 12px; border-bottom: 1px solid #fce7f3; }
        a { color: #ec4899; }
    </style></head><body>
    <h1>Mensajes Recibidos</h1>
    <table><tr><th>ID</th><th>Nombre</th><th>Correo</th><th>Mensaje</th><th>Fecha</th></tr>
    """
    for c in contactos:
        html += f"<tr><td>{c['id']}</td><td>{c['nombre']}</td><td>{c['correo']}</td><td>{c['mensaje']}</td><td>{c['fecha']}</td></tr>"
    html += "</table><br><a href='/'>Volver al inicio</a></body></html>"
    return html

@app.route('/ver-pedidos')
def ver_pedidos():
    conn = sqlite3.connect('mallkitty.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pedidos ORDER BY fecha DESC")
    pedidos = cursor.fetchall()
    conn.close()
    
    html = """
    <html><head><style>
        body { font-family: 'Poppins', sans-serif; background: #fdf2f8; padding: 40px; }
        h1 { color: #ec4899; }
        table { width: 100%; border-collapse: collapse; background: white; border-radius: 10px; overflow: hidden; }
        th { background: #ec4899; color: white; padding: 15px; }
        td { padding: 12px; border-bottom: 1px solid #fce7f3; }
        a { color: #ec4899; }
    </style></head><body>
    <h1>Pedidos Realizados</h1>
    <table><tr><th>ID</th><th>Comprador</th><th>Correo</th><th>Direccion</th><th>Total</th><th>Pago</th><th>Fecha</th></tr>
    """
    for p in pedidos:
        html += f"<tr><td>{p['id']}</td><td>{p['nombre_comprador']}</td><td>{p['correo']}</td><td>{p['direccion']}</td><td>${p['total']:.2f}</td><td>{p['metodo_pago']}</td><td>{p['fecha']}</td></tr>"
    html += "</table><br><a href='/'>Volver al inicio</a></body></html>"
    return html

if __name__ == '__main__':
    url = "http://localhost:5000"
    print(f"Mall Kitty - {url}")
    webbrowser.open(url)
    app.run()
