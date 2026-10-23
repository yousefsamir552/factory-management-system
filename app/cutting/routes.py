from flask import Blueprint, render_template, request, redirect, url_for
from app.models import db, DesignModel, CuttingRecord, log_action

cutting_bp = Blueprint('cutting', __name__, url_prefix='/cutting')

@cutting_bp.route('/')
def index():
    models = DesignModel.query.filter_by(status='في القص', is_deleted=False).all()
    log_action("زيارة قسم", "فتح قائمة القص")
    return render_template('cutting/index.html', models=models)

@cutting_bp.route('/model/<int:model_id>')
def model_details(model_id):
    model = DesignModel.query.get_or_404(model_id)
    return render_template('cutting/details.html', model=model)

@cutting_bp.route('/model/<int:model_id>/add_record', methods=['POST'])
def add_record(model_id):
    color_name = request.form.get('color_name')
    cutter_name = request.form.get('cutter_name')
    layers_count = request.form.get('layers_count', type=int)
    layer_weight = request.form.get('layer_weight', type=float)
    pieces_count = request.form.get('pieces_count', type=int)
    shade_degree = request.form.get('shade_degree')

    record = CuttingRecord(
        model_id=model_id,
        color_name=color_name,
        cutter_name=cutter_name,
        layers_count=layers_count,
        layer_weight=layer_weight,
        pieces_count=pieces_count,
        shade_degree=shade_degree
    )
    db.session.add(record)
    db.session.commit()

    log_action("تسجيل قص", f"تم تسجيل قص لـ {color_name} بعدد {pieces_count} قطعة")
    return redirect(url_for('cutting.model_details', model_id=model_id))

@cutting_bp.route('/model/<int:model_id>/finish', methods=['POST'])
def finish_cutting(model_id):
    model = DesignModel.query.get_or_404(model_id)
    model.status = 'فرز وكنترول'
    db.session.commit()
    log_action("إنهاء قص", f"تم إنهاء القص للموديل {model.model_code} وتحويله للفرز")
    return redirect(url_for('cutting.index'))