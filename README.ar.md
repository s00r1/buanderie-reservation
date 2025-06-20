# حجز غرفة الغسيل

يتيح هذا التطبيق إدارة حجز آلات الغسيل عبر الإنترنت. مكتوب بلغة بايثون باستخدام إطار العمل فلاسك. يمكن تجربة نسخة مستضافة على [https://soury.pythonanywhere.com](https://soury.pythonanywhere.com/).

- [النسخة الفرنسية](README.md)
- [English version](README.en.md)

## الفهرس
- [التثبيت](#التثبيت)
- [التشغيل محليا](#التشغيل-محليا)
- [الإعداد](#الإعداد)
- [إدارة البيانات](#إدارة-البيانات)
- [النشر على PythonAnywhere](#النشر-على-pythonanywhere)
- [الاختبارات](#الاختبارات)
- [المساهمة](#المساهمة)
- [الترخيص](#الترخيص)

## التثبيت
1. قم بتنزيل المستودع أو استنساخه.
2. *(اختياري)* أنشئ بيئة افتراضية:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. ثبّت الاعتمادات:

   ```bash
   pip install -r requirements.txt
   ```

4. عند التثبيت لأول مرة، أنشئ ملف `reservations.json` فارغ في جذر المشروع:

   ```bash
   echo "[]" > reservations.json
   ```

## التشغيل محليا

اشغل ملف `app.py` مباشرة لبدء الخادم المحلي:

```bash
python app.py
```

ستكون التطبيق متاحا ثم على [http://localhost:5000](http://localhost:5000).

## الإعداد

يتحكم متغيران للبيئة في سلوك التطبيق:

- `RESERVATIONS_FILE`: مسار ملف JSON لتخزين الحجوزات. الافتراض هو `reservations.json` في جذر المشروع.
- `ADMIN_CODE`: رمز سري يسمح بحذف أي حجز. القيمة الافتراضية `s00r1`.

## إدارة البيانات

تُحفظ الحجوزات داخل الملف المشار إليه في `RESERVATIONS_FILE`. للبدء بقاعدة بيانات فارغة يمكن إنشاء الملف بالمحتوى:

```json
[]
```

يقوم التطبيق بقفل الملف أثناء الكتابة لمنع تعارضات الوصول.

## النشر على PythonAnywhere

1. أنشئ حساباً على [pythonanywhere.com](https://www.pythonanywhere.com/) وافتح سطر أوامر Bash.
2. استنسخ المشروع ثم انتقل للمجلد:

   ```bash
   git clone https://github.com/your-user/buanderie-reservation.git
   cd buanderie-reservation
   ```

3. أنشئ بيئة افتراضية وثبّت الاعتمادات:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. من تبويب **Web** أنشئ تطبيقاً جديداً بطريقة *Manual configuration* مشيراً إلى هذا المجلد.
5. عدل ملف WSGI ليحمّل التطبيق:

   ```python
   import sys
   sys.path.insert(0, '/home/<user>/buanderie-reservation')
   from app import app as application
   ```

6. أضف المتغيرين `RESERVATIONS_FILE` و `ADMIN_CODE` في قسم *Environment Variables* (مثال: `RESERVATIONS_FILE=/home/<user>/buanderie-reservation/reservations.json`).
7. أخيراً اضغط **Reload** لتشغيل التطبيق.

## التشغيل في الإنتاج

للبيئات الإنتاجية يُنصح باستعمال Gunicorn وربط التطبيق بالمنفذ المقدم من المنصة. يعمل ذلك بنفس الطريقة على Fly.io و Railway أو أي مستضيف يحدد متغير `PORT`:

```bash
gunicorn app:app --bind 0.0.0.0:${PORT:-8080}
```

يستعمل `Procfile` المرفق هذه الأمر لتبسيط النشر على منصات مختلفة.

## الاختبارات

توجد حزمة اختبارات وحدة للتأكد من المسارات الرئيسية. بعد تثبيت الاعتمادات اشغل:

```bash
pytest
```

## المساهمة

المساهمات مرحب بها! افتح مشكلة لمناقشة أي تعديل أو اقدم طلب سحب. أحرص على تشغيل `pytest` قبل الإرسال.

---

هذا المشروع مرخص تحت رخصة MIT. اطلع على [LICENSE](LICENSE) للتفاصيل.
