# إنشاء مستخدم المشرف في قاعدة البيانات
from app import app, db
from models import User
import logging

logging.basicConfig(level=logging.INFO)

def create_admin_user():
    with app.app_context():
        try:
            # التحقق من وجود مستخدم admin
            admin = User.query.filter_by(username='admin').first()
            
            if admin is None:
                # إنشاء مستخدم جديد إذا لم يكن موجودًا
                admin = User(username='admin', is_admin=True)
                admin.set_password('omantel2025')
                
                # إضافة إلى قاعدة البيانات
                db.session.add(admin)
                db.session.commit()
                logging.info('تم إنشاء مستخدم المشرف بنجاح')
                print('تم إنشاء مستخدم المشرف بنجاح')
            else:
                logging.info('مستخدم المشرف موجود بالفعل')
                print('مستخدم المشرف موجود بالفعل')
            
            # عرض جميع المستخدمين
            users = User.query.all()
            print(f'عدد المستخدمين في قاعدة البيانات: {len(users)}')
            for user in users:
                print(f'- {user.username} (admin: {user.is_admin})')
                
        except Exception as e:
            db.session.rollback()
            logging.error(f'خطأ في إنشاء مستخدم المشرف: {str(e)}')
            print(f'حدث خطأ: {str(e)}')

if __name__ == "__main__":
    create_admin_user()