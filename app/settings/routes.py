from flask import Blueprint, render_template, request, redirect, url_for
from app.models import db, Supplier, SizeDef, PrintShop

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/')
def index():
    suppliers = Supplier.query.all()
    sizes = SizeDef.query.all()
    printshops = PrintShop.query.all()
    return render_template('settings/index.html', suppliers=suppliers, sizes=sizes, printshops=printshops)

@settings_bp.route('/add_supplier', methods=['POST'])
def add_supplier():
    name = request.form.get('name')
    phone = request.form.get('phone')
    if name and not Supplier.query.filter_by(name=name).first():
        db.session.add(Supplier(name=name, phone=phone))
        db.session.commit()
    return redirect(url_for('settings.index'))

@settings_bp.route('/add_size', methods=['POST'])
def add_size():
    name = request.form.get('name')
    if name and not SizeDef.query.filter_by(name=name).first():
        db.session.add(SizeDef(name=name))
        db.session.commit()
    return redirect(url_for('settings.index'))

@settings_bp.route('/add_printshop', methods=['POST'])
def add_printshop():
    name = request.form.get('name')
    if name and not PrintShop.query.filter_by(name=name).first():
        db.session.add(PrintShop(name=name))
        db.session.commit()
    return redirect(url_for('settings.index'))