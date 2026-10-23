from flask import Blueprint, render_template, request, redirect, url_for
from app.models import db, DesignModel, QCRecord, SizeDef, log_action

qc_bp = Blueprint('qc', __name__, url_prefix='/qc')

@qc_bp.route('/')
def index():
    models = DesignModel.query.filter_by(status='فرز وكنترول', is_deleted=False).all()
    log_action("زيارة قسم", "فتح قائمة الفرز والكنترول")
    return render_template('qc/index.html', models=models)

@qc_bp.route('/model/<int:model_id>')
def model_details(model_id):
    model = DesignModel.query.get_or_404(model_id)
    sizes = SizeDef.query.all()
    colors = []
    for req in model.requirements:
        color_name = f"{req.color.color_code} ({req.part_name})"
        if color_name not in colors:
            colors.append(color_name)

    return render_template('qc/details.html', model=model, sizes=sizes, colors=colors)

@qc_bp.route('/model/<int:model_id>/finish', methods=['POST'])
def finish_qc(model_id):
    model = DesignModel.query.get_or_404(model_id)
    model.status = 'جاهز للطباعة / التجميع'
    db.session.commit()
    log_action("إنهاء الفرز", f"تم إنهاء الفرز للموديل {model.model_code}")
    return redirect(url_for('qc.index'))

@qc_bp.route('/model/<int:model_id>/add_record', methods=['POST'])
def add_record(model_id):
    color_name = request.form.get('color_name')
    size = request.form.get('size')
    good_qty = request.form.get('good_qty', type=int) or 0
    defect_qty = request.form.get('defect_qty', type=int) or 0
    defect_notes = request.form.get('defect_notes', '').strip()

    # البحث عن سجل مطابق لنفس الموديل واللون والمقاس
    existing_rec = QCRecord.query.filter_by(model_id=model_id, color_name=color_name, size=size).first()

    if existing_rec:
        # تجميع الأعداد
        existing_rec.good_qty += good_qty
        existing_rec.defect_qty += defect_qty
        # دمج الملاحظات إذا وجدت
        if defect_notes:
            if existing_rec.defect_notes:
                existing_rec.defect_notes += f" | {defect_notes}"
            else:
                existing_rec.defect_notes = defect_notes
    else:
        # إنشاء سجل جديد
        rec = QCRecord(
            model_id=model_id,
            color_name=color_name,
            size=size,
            good_qty=good_qty,
            defect_qty=defect_qty,
            defect_notes=defect_notes
        )
        db.session.add(rec)
        
    db.session.commit()
    from app.models import log_action
    log_action("الفرز", f"تم تحديث فرز {good_qty} سليم و {defect_qty} هالك للون {color_name} مقاس {size}")
    return redirect(url_for('qc.model_details', model_id=model_id))