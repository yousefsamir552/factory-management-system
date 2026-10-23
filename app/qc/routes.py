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