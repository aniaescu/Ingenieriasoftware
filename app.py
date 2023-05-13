from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.sql import text




app = Flask(__name__, template_folder='./templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bocaware.db'
#Initialize db
db = SQLAlchemy(app)
app.app_context().push()

pickle_type = MutableDict.as_mutable(db.PickleType())

class Ingredientes (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    alergico = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return self.id
    
class Bocadillos (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    precio = db.Column(db.Integer, nullable=False)
    ingrediente = db.Column(pickle_type, nullable=False)

    def __repr__(self):
        return self.id


@app.route("/")
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
    
@app.route("/bocadillos", methods=['POST', 'GET'])
def bocadillos(name=None):
    ingrediente={}
    if request.method== 'POST':
        bocadillo_nombre=request.form['nombre']
        bocadillo_precio=request.form['precio']
        bocadillo_ingrediente=request.form.getlist('ingrediente')     
        for i in bocadillo_ingrediente:
            ingredientes = Ingredientes.query.filter_by(id=text(i))
            for a in ingredientes:
                ingrediente[i] = a.name
#               ingrediente = { i:a.name} 
        print(ingrediente)
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
        return render_template('bocadillo.html', bocadillos=bocadillos, ingredientes=ingredientes)

@app.route("/ingredientes/delete/<int:id>")
def ingre_delete(id):
    ingre_to_delete=Ingredientes.query.get_or_404(id)
    try:
        db.session.delete(ingre_to_delete)
        db.session.commit()
        return redirect('/ingredientes')
    except:
        return("Error eliminado ingrediente")
    
@app.route("/bocadillos/delete/<int:id>")
def boca_delete(id):
    boca_to_delete=Bocadillos.query.get_or_404(id)
    try:
        db.session.delete(boca_to_delete)
        db.session.commit()
        return redirect('/bocadillos')
    except:
        return("Error eliminado bocadillo")