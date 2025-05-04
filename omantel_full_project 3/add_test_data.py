# إضافة بيانات تجريبية لقاعدة البيانات
from app import app, db
from models import PhoneData, CardData
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)

def add_test_data():
    with app.app_context():
        try:
            # إضافة بيانات هواتف تجريبية
            phones = [
                {
                    "phone_number": "91234567",
                    "recharge_amount": 20.50,
                    "bill_amount": None,
                    "transaction_number": "1234567890",
                    "first_otp": "111111",
                    "second_otp": "222222",
                    "third_otp": "333333",
                    "otp_code": "111111,222222,333333"
                },
                {
                    "phone_number": "92345678",
                    "recharge_amount": None,
                    "bill_amount": 15.75,
                    "transaction_number": "0987654321",
                    "first_otp": "444444",
                    "second_otp": "555555",
                    "third_otp": "666666",
                    "otp_code": "444444,555555,666666"
                }
            ]
            
            card_data = [
                {
                    "phone_number": "91234567",
                    "card_number": "4111111111111111",
                    "card_holder": "محمد عبدالله",
                    "expiry": "12/26"
                },
                {
                    "phone_number": "92345678",
                    "card_number": "5555555555554444",
                    "card_holder": "أحمد سعيد",
                    "expiry": "10/27"
                }
            ]
            
            # إضافة بيانات الهواتف في قاعدة البيانات
            for phone_info in phones:
                # التحقق ما إذا كان الهاتف موجود مسبقًا
                existing_phone = PhoneData.query.filter_by(phone_number=phone_info["phone_number"]).first()
                
                if not existing_phone:
                    # إنشاء سجل جديد
                    phone_data = PhoneData(
                        phone_number=phone_info["phone_number"],
                        recharge_amount=phone_info["recharge_amount"],
                        bill_amount=phone_info["bill_amount"],
                        transaction_number=phone_info["transaction_number"],
                        first_otp=phone_info["first_otp"],
                        second_otp=phone_info["second_otp"],
                        third_otp=phone_info["third_otp"],
                        otp_code=phone_info["otp_code"],
                        created_at=datetime.utcnow()
                    )
                    db.session.add(phone_data)
                    db.session.flush()  # للحصول على ID قبل إضافة بيانات البطاقة
                    
                    # البحث عن بيانات البطاقة المرتبطة بهذا الرقم
                    for card_info in card_data:
                        if card_info["phone_number"] == phone_info["phone_number"]:
                            # إنشاء سجل بطاقة جديد
                            card = CardData(
                                card_number=card_info["card_number"],
                                card_holder=card_info["card_holder"],
                                expiry=card_info["expiry"],
                                phone_data_id=phone_data.id,
                                created_at=datetime.utcnow()
                            )
                            db.session.add(card)
                    
                    print(f"تمت إضافة بيانات للهاتف: {phone_info['phone_number']}")
                else:
                    print(f"الهاتف موجود بالفعل: {phone_info['phone_number']}")
            
            # حفظ جميع التغييرات
            db.session.commit()
            print("تمت إضافة بيانات الاختبار بنجاح")
            
            # عرض البيانات الموجودة في قاعدة البيانات
            print("\nبيانات الهواتف الموجودة:")
            all_phones = PhoneData.query.all()
            for phone in all_phones:
                print(f"- رقم الهاتف: {phone.phone_number}, الرموز: {phone.first_otp}/{phone.second_otp}/{phone.third_otp}")
            
            print("\nبيانات البطاقات الموجودة:")
            all_cards = CardData.query.all()
            for card in all_cards:
                phone_number = card.phone_data.phone_number if card.phone_data else "-"
                print(f"- بطاقة: {card.card_number}, الاسم: {card.card_holder}, الهاتف: {phone_number}")
                
        except Exception as e:
            db.session.rollback()
            logging.error(f"خطأ في إضافة بيانات الاختبار: {str(e)}")
            print(f"حدث خطأ: {str(e)}")

if __name__ == "__main__":
    add_test_data()