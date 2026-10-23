import os
from flask import Blueprint, render_template, request, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from app.models import db, Fabric, FabricColor, FabricTransaction, Supplier
from app.models import log_action

warehouse_bp = Blueprint('warehouse', __name__, url_prefix='/warehouse')

@warehouse_bp.route('/')
def index():
    fabrics = Fabric.query.all()
    suppliers = Supplier.query.all()
    selected_fabric_id = request.args.get('fabric_id', type=int)

    selected_fabric = None
    if selected_fabric_id:
        selected_fabric = Fabric.query.get(selected_fabric_id)
    elif fabrics:
        selected_fabric = fabrics[0]

    return render_template('warehouse/index.html', fabrics=fabrics, selected_fabric=selected_fabric, suppliers=suppliers)

@warehouse_bp.route('/add', methods=['POST'])
def add_fabric():
    fabric_id = request.form.get('fabric_id')
    new_fabric_name = request.form.get('new_fabric_name')

    if not fabric_id and not new_fabric_name:
        return redirect(url_for('warehouse.index'))

    if new_fabric_name:
        unit = request.form.get('unit')
        desc = request.form.get('description')
        supplier_id = request.form.get('supplier_id') or None

        fabric = Fabric(name=new_fabric_name, unit=unit, description=desc, supplier_id=supplier_id)
        db.session.add(fabric)
        db.session.flush()

        file = request.files.get('fabric_image')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            file.save(os.path.join(upload_dir, filename))
            fabric.image_url = f'/static/uploads/{filename}'
        

        db.session.commit()
    else:
        fabric = Fabric.query.get(fabric_id)
        if not fabric:
            return redirect(url_for('warehouse.index'))

    color_code = request.form.get('color_code')
    color_name = request.form.get('color_name')
    hex_code = request.form.get('hex_code', None) or None

    try:
        price = float(request.form.get('price_per_unit', 0))
    except ValueError:
        price = 0.0

    try:
        quantity = float(request.form.get('quantity', 0))
    except ValueError:
        quantity = 0.0

    existing_color = FabricColor.query.filter_by(fabric_id=fabric.id, color_code=color_code).first()

    if existing_color:
        existing_color.quantity += quantity
        if hex_code:
            existing_color.hex_code = hex_code
        if color_name:
            existing_color.color_name = color_name
        if price > 0:
            existing_color.price_per_unit = price
    else:
        color = FabricColor(fabric_id=fabric.id, color_code=color_code, color_name=color_name, hex_code=hex_code, price_per_unit=price, quantity=quantity)
        db.session.add(color)

    log_action("المخزن", f"حركة اضافه للخامات {color_code} للون {color_name} هيكس كود {hex_code}")

    db.session.commit()
    return redirect(url_for('warehouse.index', fabric_id=fabric.id))

@warehouse_bp.route('/edit_fabric', methods=['POST'])
def edit_fabric():
    fabric_id = request.form.get('fabric_id')
    fabric = Fabric.query.get(fabric_id)
    if fabric:
        file = request.files.get('fabric_image')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            file.save(os.path.join(upload_dir, filename))
            fabric.image_url = f'/static/uploads/{filename}'
            db.session.commit()
    return redirect(url_for('warehouse.index', fabric_id=fabric_id))

@warehouse_bp.route('/transaction', methods=['POST'])
def transaction():
    color_id = request.form.get('color_id')
    operation = request.form.get('operation')
    try:
        amount = float(request.form.get('amount', 0))
    except ValueError:
        amount = 0.0
    model_code_ref = request.form.get('model_code_ref')
    notes = request.form.get('notes')

    color = FabricColor.query.get(color_id)
    if color and amount > 0:
        if operation == 'add':
            color.quantity += amount
        elif operation == 'deduct':
            if color.quantity >= amount:
                color.quantity -= amount
            else:
                return redirect(url_for('warehouse.index', fabric_id=color.fabric_id))
        trans = FabricTransaction(color_id=color.id, operation=operation, amount=amount, model_code_ref=model_code_ref, notes=notes)
        db.session.add(trans)
        log_action("المخزن", f"حركة {operation} لكمية {amount} للون {color.color_code} موديل {model_code_ref}")
        db.session.commit()
        return redirect(url_for('warehouse.index', fabric_id=color.fabric_id))
    return redirect(url_for('warehouse.index'))

@warehouse_bp.route('/print_inventory')
def print_inventory():
    fabrics = Fabric.query.all()
    return render_template('warehouse/print_inventory.html', fabrics=fabrics)