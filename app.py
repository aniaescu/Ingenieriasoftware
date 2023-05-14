from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import difflib

app = Flask(__name__, template_folder='./templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bocaware.db'
#Initialize db
db = SQLAlchemy(app)
app.app_context().push()

class Ingredientes (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    alergico = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return self.id


@app.route("/")
@app.route("/<name>")
def hello_world(name=None):
    return render_template('hello.html', name=name)

@app.route("/ingredientes", methods=['POST', 'GET'])
def ingredientes(name=None):
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

@app.route("/ingredientes/delete/<int:id>")
def ingre_delete(id):
    ingre_to_delete=Ingredientes.query.get_or_404(id)
    try:
        db.session.delete(ingre_to_delete)
        db.session.commit()
        return redirect('/ingredientes')
    except:
        return("Error eliminado ingrediente")
    
@app.route("/busqueda", methods=['POST', 'GET'])
def busqueda():
    if request.method == 'POST':
        search = request.form['buscador']
        items = db.session.query(Ingredientes).filter(Ingredientes.name.ilike(f"%{search}%")).all()
        if not items:
            all_ingredient_names = [ingredient.name for ingredient in db.session.query(Ingredientes).all()]
            similar_words = similitud_palabras(search, all_ingredient_names)
            items = [ingrediente for ingrediente in db.session.query(Ingredientes).all() if ingrediente.name in similar_words]
        try:
            return render_template('busqueda.html', items=items)
        except:
            return("Error al buscar un ingrediente")
    else:   
        items = Ingredientes.query.order_by(Ingredientes.id)    
        return render_template('busqueda.html', items=items)

    
def similitud_palabras(palabra, lista_palabras, umbral=0.6):
    palabra = palabra.lower()
    lista_palabras_lower = [p.lower() for p in lista_palabras]
    palabras_similares_lower = difflib.get_close_matches(palabra, lista_palabras_lower, n=100, cutoff=umbral)
    palabras_similares = [lista_palabras[i] for i, pal in enumerate(lista_palabras_lower) if pal.lower() in palabras_similares_lower]
    return palabras_similares