from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz
from flask import request, session

db = SQLAlchemy()

def get_egypt_time():
    return datetime.now(pytz.timezone('Africa/Cairo'))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    real_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='staff')
    permissions = db.Column(db.Text, nullable=True)
    last_active = db.Column(db.DateTime, nullable=True)
    is_deleted = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(50), nullable=True)

class SizeDef(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)

class PrintShop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class Fabric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    unit = db.Column(db.String(20), nullable=False)
    image_url = db.Column(db.String(200), nullable=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=True)
    supplier = db.relationship('Supplier', backref='fabrics', lazy=True)
    colors = db.relationship('FabricColor', backref='fabric', lazy=True)
    is_deleted = db.Column(db.Boolean, default=False)

class FabricColor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fabric_id = db.Column(db.Integer, db.ForeignKey('fabric.id'), nullable=False)
    color_code = db.Column(db.String(50), nullable=False)
    color_name = db.Column(db.String(50), nullable=True)
    hex_code = db.Column(db.String(7), nullable=True)
    price_per_unit = db.Column(db.Float, default=0.0)
    quantity = db.Column(db.Float, default=0.0)
    reserved_quantity = db.Column(db.Float, default=0.0)
    is_deleted = db.Column(db.Boolean, default=False)

class DesignModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model_code = db.Column(db.String(50), unique=True, nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    model_type = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(50), default='تصميم')
    is_deleted = db.Column(db.Boolean, default=False)
    target_quantity = db.Column(db.Integer, default=0)
    marker_length = db.Column(db.Float, nullable=True)
    sizes_selected = db.Column(db.String(200), nullable=True)
    main_marker_url = db.Column(db.String(200), nullable=True)
    print_marker_url = db.Column(db.String(200), nullable=True)
    marker_efficiency = db.Column(db.Float, nullable=True)
    notes_shirt = db.Column(db.Text, nullable=True)
    notes_pants = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=get_egypt_time)
    colored_at = db.Column(db.DateTime, nullable=True)
    cut_at = db.Column(db.DateTime, nullable=True)
    requirements = db.relationship('ModelRequirement', backref='model', lazy=True)
    accessories = db.relationship('ModelAccessory', backref='model', lazy=True)
    cutting_records = db.relationship('CuttingRecord', backref='model', lazy=True)
    qc_records = db.relationship('QCRecord', backref='model', lazy=True)

class ModelRequirement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('design_model.id'), nullable=False)
    color_id = db.Column(db.Integer, db.ForeignKey('fabric_color.id'), nullable=False)
    part_name = db.Column(db.String(50), nullable=True)
    planned_quantity = db.Column(db.Float, default=0.0)
    color = db.relationship('FabricColor', backref='model_requirements', lazy=True)

class ModelAccessory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('design_model.id'), nullable=False)
    accessory_name = db.Column(db.String(100), nullable=False)
    planned_quantity = db.Column(db.Float, default=0.0)

class FabricTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    color_id = db.Column(db.Integer, db.ForeignKey('fabric_color.id'), nullable=False)
    model_code_ref = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    operation = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=get_egypt_time)

class CuttingRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('design_model.id'), nullable=False)
    color_name = db.Column(db.String(100), nullable=False)
    cutter_name = db.Column(db.String(100), nullable=False)
    layers_count = db.Column(db.Integer, nullable=False, default=0)
    layer_weight = db.Column(db.Float, nullable=False, default=0.0)
    pieces_count = db.Column(db.Integer, nullable=False, default=0)
    shade_degree = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=get_egypt_time)

class QCRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('design_model.id'), nullable=False)
    color_name = db.Column(db.String(100), nullable=False)
    size = db.Column(db.String(20), nullable=False)
    good_qty = db.Column(db.Integer, default=0, nullable=False)
    defect_qty = db.Column(db.Integer, default=0, nullable=False)
    defect_notes = db.Column(db.String(200), nullable=True)
    stage = db.Column(db.String(50), default='قبل الطباعة')
    created_at = db.Column(db.DateTime, default=get_egypt_time)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action = db.Column(db.String(200), nullable=False)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(200), nullable=True)
    timestamp = db.Column(db.DateTime, default=get_egypt_time)
    user = db.relationship('User', backref='logs', lazy=True)

def log_action(action, details=""):
    try:
        user_id = session.get('user_id')
        ip = request.remote_addr
        agent = request.user_agent.string
        log = AuditLog(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=ip,
            user_agent=agent
        )
        db.session.add(log)
        db.session.commit()
    except Exception:
        pass