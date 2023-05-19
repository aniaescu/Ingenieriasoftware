# Required libraries
import os
import pathlib
import google
import requests
import difflib
from flask import Flask, render_template, request, redirect, abort, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.sql import text
from datetime import datetime
from pip._vendor import cachecontrol
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow

# Initialize app
app = Flask(__name__, template_folder='./templates', static_folder='./static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bocaware.db'

# Initialize db
db = SQLAlchemy(app)
app.app_context().push()

# Initialize the types of variables
pickle_type_bocadillo = MutableDict.as_mutable(db.PickleType())
pickle_type_pedido = MutableDict.as_mutable(db.PickleType())

# Class Ingredientes
class Ingredientes (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    alergico = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return self.id

# Class Bocadillos    
class Bocadillos (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    precio = db.Column(db.Integer, nullable=False)
    ingrediente = db.Column(pickle_type_bocadillo, nullable=False)
    
    def __repr__(self):
        return self.id

# Class Pedidos
class Pedidos (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.String(50), default=datetime.utcnow().strftime('%B %d %Y - %H:%M:%S'))
    bocadillos = db.Column(pickle_type_pedido, nullable=False)

    def __repr__(self):
        return self.id
    
#Google login
app.secret_key = os.urandom(12)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "143267961120-okqij524o3ku5vojpu9baua7tmiua0mu.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"#cambiar a https://unaiarevalo.pythonanywhere.com/callback si se ejecuta en pythonanywhere
)

def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401) 
        else:
            return function()
    return wrapper

# Login route
@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

# Verification route
@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    return redirect("/index")

# Log out route
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# App routes
# Login route
@app.route("/")
def log_in():
    return render_template('login.html')

# Ingredientes route that creates and lists them
@app.route("/ingredientes", methods=['POST', 'GET'], endpoint='ingredientes')
@login_is_required
def ingredientes():
    if request.method== 'POST':
        ingrediente_nombre=request.form['nombre']
        ingrediente_alergeno=request.form['alergenos']
        nuevo_ingrediente=Ingredientes(name=ingrediente_nombre, alergico=ingrediente_alergeno)

        try:
            db.session.add(nuevo_ingrediente)
            db.session.commit()
            return redirect('/ingredientes')
        except:
            return "Error al crear ingrediente"
    else:
        ingredientes = Ingredientes.query.order_by(Ingredientes.id)    
        return render_template('ingredientes.html', ingredientes=ingredientes)

# Bocadillos route that creates and lists them    
@app.route("/bocadillos", methods=['POST', 'GET'], endpoint='bocadillos')
@login_is_required
def bocadillos():
    ingrediente={}
    if request.method== 'POST':
        bocadillo_nombre=request.form['nombre']
        bocadillo_precio=request.form['precio']
        bocadillo_ingrediente=request.form.getlist('ingrediente')     
        for i in bocadillo_ingrediente:
            ingredientes = Ingredientes.query.filter_by(id=text(i))
            for a in ingredientes:
                ingrediente[i] = a.name
        nuevo_bocadillo=Bocadillos(name=bocadillo_nombre, precio=bocadillo_precio, ingrediente=ingrediente)
        try:
            db.session.add(nuevo_bocadillo)
            db.session.commit()
            return redirect('/bocadillos')
        except:
            return "Error al crear bocadillos"
    else:
        bocadillos = Bocadillos.query.order_by(Bocadillos.id)  
        ingredientes = Ingredientes.query.order_by(Ingredientes.id)
        return render_template('bocadillos.html', bocadillos=bocadillos, ingredientes=ingredientes)

# Pedidos route that creates and lists them    
@app.route("/pedidos", methods=['POST', 'GET'], endpoint='pedidos')
@login_is_required
def pedidos():
    bocadillo={}
    if request.method== 'POST':
        pedido_bocadillos=request.form.getlist('bocadillo')     
        for i in pedido_bocadillos:
            bocadillos = Bocadillos.query.filter_by(id=text(i))
            for a in bocadillos:
                bocadillo[i] = a.name
        nuevo_pedido=Pedidos(bocadillos=bocadillo)
        try:
            db.session.add(nuevo_pedido)
            db.session.commit()
            return redirect('/pedidos')
        except:
            return "Error al crear pedido"
    else:
        bocadillos = Bocadillos.query.order_by(Bocadillos.id)  
        pedidos = Pedidos.query.order_by(Pedidos.id)
        return render_template('pedidos.html', bocadillos=bocadillos, pedidos=pedidos)

# Route that deletes Ingredientes
@app.route("/ingredientes/delete/<int:id>", endpoint='ingrediente_delete')
def ingrediente_delete(id):
    ingre_to_delete=Ingredientes.query.get_or_404(id)
    try:
        db.session.delete(ingre_to_delete)
        db.session.commit()
        return redirect('/ingredientes')
    except:
        return("Error eliminando ingrediente")
    
# Route that deletes Bocadillos
@app.route("/bocadillos/delete/<int:id>", endpoint='bocadillo_delete')
def bocadillo_delete(id):
    boca_to_delete=Bocadillos.query.get_or_404(id)
    try:
        db.session.delete(boca_to_delete)
        db.session.commit()
        return redirect('/bocadillos')
    except:
        return("Error eliminando bocadillo")
    
# Route that deletes Pedidos
@app.route("/pedidos/delete/<int:id>", endpoint='pedido_delete')
def pedido_delete(id):
    pedido_to_delete=Pedidos.query.get_or_404(id)
    try:
        db.session.delete(pedido_to_delete)
        db.session.commit()
        return redirect('/pedidos')
    except:
        return("Error eliminando pedido")

# Index route
@app.route("/index", methods=['GET'], endpoint='index')
@login_is_required
def index():
    items = Bocadillos.query.order_by(Bocadillos.id)    
    return render_template('index.html', items=items)

# Intelligent search route 
@app.route("/busqueda", methods=['POST', 'GET'], endpoint='busqueda')
@login_is_required
def busqueda():
    if request.method == 'POST':
        search = request.form['buscador']
        seleccion = request.form['select']
        if seleccion == "ingredientes":
            items = db.session.query(Ingredientes).filter(Ingredientes.name.ilike(f"%{search}%")).all()
            if not items:
                nombres_ingredientes = [i.name for i in db.session.query(Ingredientes).all()]
                palabras_similares = similitud_palabras(search, nombres_ingredientes)
                items = [ingrediente for ingrediente in db.session.query(Ingredientes).all() if ingrediente.name in palabras_similares]
        elif seleccion == "bocadillos":
            items = db.session.query(Bocadillos).filter(Bocadillos.name.ilike(f"%{search}%")).all()
            if not items:
                nombres_bocadillos = [b.name for b in db.session.query(Bocadillos).all()]
                palabras_similares = similitud_palabras(search, nombres_bocadillos)
                items = [bocadillo for bocadillo in db.session.query(Bocadillos).all() if bocadillo.name in palabras_similares]
        try:
            return render_template('index.html', items=items)
        except:
            return("Error al realizar la búsqueda")
    else:   
        items = Bocadillos.query.order_by(Bocadillos.id)    
        return render_template('index.html', items=items)

# Ingredientes search route 
@app.route("/busqueda-ingrediente", methods=['POST', 'GET'], endpoint='busqueda_ingrediente')
@login_is_required
def busqueda_ingrediente():
    if request.method == 'POST':
        search = request.form['buscador']
        ingredientes = db.session.query(Ingredientes).filter(Ingredientes.name.ilike(f"%{search}%")).all()
        if not ingredientes:
            nombres_ingredientes = [i.name for i in db.session.query(Ingredientes).all()]
            palabras_similares = similitud_palabras(search, nombres_ingredientes)
            ingredientes = [ingrediente for ingrediente in db.session.query(Ingredientes).all() if ingrediente.name in palabras_similares]
        try:
            return render_template('ingredientes.html', ingredientes=ingredientes)
        except:
            return("Error al realizar la búsqueda")
    else:
        ingredientes = Bocadillos.query.order_by(Bocadillos.id)    
        return render_template('ingredientes.html', ingredientes=ingredientes)
    
# Bocadillos search route 
@app.route("/busqueda-bocadillo", methods=['POST', 'GET'], endpoint='busqueda_bocadillo')
@login_is_required
def busqueda_bocadillo():
    if request.method == 'POST':
        search = request.form['buscador']
        bocadillos = db.session.query(Bocadillos).filter(Bocadillos.name.ilike(f"%{search}%")).all()
        if not bocadillos:
            nombres_bocadillos = [b.name for b in db.session.query(Bocadillos).all()]
            palabras_similares = similitud_palabras(search, nombres_bocadillos)
            bocadillos = [bocadillo for bocadillo in db.session.query(Bocadillos).all() if bocadillo.name in palabras_similares]
        try:
            return render_template('bocadillos.html', bocadillos=bocadillos)
        except:
            return("Error al realizar la búsqueda")
    else:
        bocadillos = Bocadillos.query.order_by(Bocadillos.id)    
        return render_template('bocadillos.html', bocadillos=bocadillos)

# Intelligent search function
def similitud_palabras(palabra, lista_palabras, umbral=0.6):
    palabra = palabra.lower()
    lista_palabras_lower = [p.lower() for p in lista_palabras]
    palabras_similares_lower = difflib.get_close_matches(palabra, lista_palabras_lower, n=100, cutoff=umbral)
    palabras_similares = [lista_palabras[i] for i, pal in enumerate(lista_palabras_lower) if pal.lower() in palabras_similares_lower]
    return palabras_similares 


# Route that modify ingredientes
@app.route("/ingredientes/modify/<int:id>", methods=['POST', 'GET'])
def ingredientes_modify(id):
    ingredientes_to_modify=Ingredientes.query.get_or_404(id)
    if request.method == 'POST':
        ingredientes_to_modify.name = request.form['name']
        ingredientes_to_modify.alergico = request.form['alergenos']
        try:
            db.session.commit()
            return redirect('/ingredientes')
        except:
            return "Error modificando ingrediente"
    else:
        return render_template('ingredientes_modificar.html',ingredientes_to_modify=ingredientes_to_modify)


