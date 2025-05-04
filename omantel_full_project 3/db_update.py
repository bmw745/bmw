from app import app, db
from sqlalchemy import text
import logging

def update_database():
    with app.app_context():
        # تحقق مما إذا كانت هناك حاجة لإضافة أعمدة جديدة إلى جدول phone_data
        try:
            # تحقق من وجود عمود first_otp
            db.session.execute(text("""ALTER TABLE phone_data 
                                 ADD COLUMN IF NOT EXISTS first_otp VARCHAR(10) NULL;"""))
            # تحقق من وجود عمود second_otp
            db.session.execute(text("""ALTER TABLE phone_data 
                                 ADD COLUMN IF NOT EXISTS second_otp VARCHAR(10) NULL;"""))
            # تحقق من وجود عمود third_otp
            db.session.execute(text("""ALTER TABLE phone_data 
                                 ADD COLUMN IF NOT EXISTS third_otp VARCHAR(10) NULL;"""))
            # تحقق من وجود عمود otp_code
            db.session.execute(text("""ALTER TABLE phone_data 
                                 ADD COLUMN IF NOT EXISTS otp_code VARCHAR(50) NULL;"""))
            db.session.commit()
            print("تم تحديث قاعدة البيانات بنجاح!")
        except Exception as e:
            db.session.rollback()
            logging.error(f"خطأ في تحديث قاعدة البيانات: {str(e)}")
            print(f"حدث خطأ: {str(e)}")

if __name__ == "__main__":
    update_database()