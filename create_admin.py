from database import SessionLocal
from models import User
import bcrypt

# فتح جلسة الاتصال
db = SessionLocal()

# الإيميل الذي طلبته من الصورة
target_email = "gr6204616@gmail.com"

# التحقق مما إذا كان الحساب موجوداً
existing_admin = db.query(User).filter(User.email == target_email).first()

if existing_admin:
    print(f"الحساب {target_email} موجود بالفعل في قاعدة البيانات!")
    # إذا كان موجوداً ولكنه طالب، نرقيه إلى مدير
    if existing_admin.role != "admin":
        existing_admin.role = "admin"
        db.commit()
        print("تمت ترقية الحساب ليكون مشرفاً (admin).")
else:
    # ضع كلمة مرور قوية هنا بدلاً من هذه الكلمة الضعيفة
    password = "3a415c67@#" 
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # إنشاء حساب المدير الجديد
    new_admin = User(
        name="مهدي (المالك)",
        email=target_email,
        hashed_password=hashed,
        role="admin"  # الصلاحية المطلقة
    )

    db.add(new_admin)
    db.commit()
    print(f"تم إنشاء حساب المشرف {target_email} بنجاح!")

# إغلاق الاتصال
db.close()