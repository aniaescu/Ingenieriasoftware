from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy


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