import os
from flask import Blueprint, render_template, request, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from app.models import db, DesignModel, Fabric, FabricColor, ModelRequirement, ModelAccessory, get_egypt_time, log_action

design_bp = Blueprint('design', __name__, url_prefix='/design')

@design_bp.route('/')
def index():
    models = DesignModel.query.filter_by(is_deleted=False).order_by(DesignModel.created_at.desc()).all()
    log_action("زيارة قسم", "فتح قائمة التصميم والتخطيط")
    return render_template('design/index.html', models=models)

@design_bp.route('/inventory')
def model_inventory():
    search_query = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '')

    query = DesignModel.query.filter_by(is_deleted=False)

    if search_query:
        query = query.filter(DesignModel.model_code.contains(search_query) | DesignModel.model_type.contains(search_query))
    
    if status_filter:
        query = query.filter_by(status=status_filter)

    models = query.order_by(DesignModel.created_at.desc()).all()
    log_action("جرد الموديلات", f"بحث في جرد الموديلات بكلمة: {search_query}")
    return render_template('design/inventory.html', models=models, search_query=search_query, status_filter=status_filter)

@design_bp.route('/add', methods=['POST'])
def add_model():
    model_code = request.form.get('model_code')
    model_type = request.form.get('model_type')
    sizes_selected = request.form.get('sizes_selected')
    file = request.files.get('model_image')

    if file and file.filename != '':
        filename = secure_filename(file.filename)
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        file.save(os.path.join(upload_dir, filename))
        image_url = f'/static/uploads/{filename}'

        new_model = DesignModel(model_code=model_code, model_type=model_type, sizes_selected=sizes_selected, image_url=image_url)
        db.session.add(new_model)
        db.session.commit()

        log_action("إضافة موديل", f"تم رفع موديل جديد بكود: {model_code}")

    return redirect(url_for('design.index'))

@design_bp.route('/model/<int:model_id>')
def model_details(model_id):
    model = DesignModel.query.get_or_404(model_id)
    fabrics = Fabric.query.filter_by(is_deleted=False).all()
    return render_template('design/details.html', model=model, fabrics=fabrics)

@design_bp.route('/model/<int:model_id>/add_color', methods=['POST'])
def add_color(model_id):
    color_id = request.form.get('color_id')
    part_name = request.form.get('part_name')
    req = ModelRequirement(model_id=model_id, color_id=color_id, part_name=part_name, planned_quantity=0.0)
    db.session.add(req)
    
    model = DesignModel.query.get(model_id)
    if not model.colored_at:
        model.colored_at = get_egypt_time()

    db.session.commit()
    log_action("تلوين موديل", f"تم إضافة لون للقطعة ({part_name}) في الموديل {model.model_code}")
    return redirect(url_for('design.model_details', model_id=model_id))

@design_bp.route('/model/<int:model_id>/add_accessory', methods=['POST'])
def add_accessory(model_id):
    name = request.form.get('accessory_name')
    acc = ModelAccessory(model_id=model_id, accessory_name=name, planned_quantity=0.0)
    db.session.add(acc)
    db.session.commit()
    log_action("إضافة إكسسوار", f"تم إضافة ({name}) للموديل رقم {model_id}")
    return redirect(url_for('design.model_details', model_id=model_id))

@design_bp.route('/model/<int:model_id>/plan_quantities', methods=['POST'])
def plan_quantities(model_id):
    model = DesignModel.query.get_or_404(model_id)
    # حجز كميات القماش
    for req in model.requirements:
        val = request.form.get(f'req_{req.id}', type=float)
        if val is not None:
            diff = val - req.planned_quantity
            req.color.reserved_quantity += diff
            req.planned_quantity = val
            
    # حجز الإكسسوارات
    for acc in model.accessories:
        val = request.form.get(f'acc_{acc.id}', type=float)
        if val is not None:
            acc.planned_quantity = val

    model.sizes_selected = request.form.get('sizes_selected')
    model.main_marker_url = request.form.get('main_marker_url')
    model.print_marker_url = request.form.get('print_marker_url')
    model.notes_shirt = request.form.get('notes_shirt')

    db.session.commit()
    log_action("تخطيط كميات", f"تم حجز كميات للموديل {model.model_code}")
    return redirect(url_for('design.model_details', model_id=model_id))

@design_bp.route('/model/<int:model_id>/issue', methods=['POST'])
def issue_fabric(model_id):
    model = DesignModel.query.get_or_404(model_id)
    
    # خصم الكميات المحجوزة من المخزن الفعلي عند الصرف
    for req in model.requirements:
        if req.planned_quantity > 0:
            req.color.quantity -= req.planned_quantity
            req.color.reserved_quantity -= req.planned_quantity
            
            # تسجيل حركة الصرف في الدفتر
            from app.models import FabricTransaction
            trans = FabricTransaction(color_id=req.color_id, operation='deduct', amount=req.planned_quantity, model_code_ref=model.model_code, notes="صرف تلقائي للقص")
            db.session.add(trans)

    model.status = 'في القص'
    model.cut_at = get_egypt_time()
    db.session.commit()
    log_action("صرف قماش", f"تم صرف قماش الموديل {model.model_code} وتحويله للقص")
    return redirect(url_for('design.model_details', model_id=model_id))

@design_bp.route('/inventory/model/<int:model_id>')
def inventory_model_details(model_id):
    model = DesignModel.query.get_or_404(model_id)
    return render_template('design/inventory_details.html', model=model) # اصنع ملف HTML بسيط يعرض البيانات بدون جداول ادخال