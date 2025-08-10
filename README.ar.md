# حجز غرفة الغسيل

يتيح هذا التطبيق إدارة حجز آلات الغسيل عبر الإنترنت. مكتوب بلغة بايثون باستخدام إطار العمل فلاسك. يمكن تجربة نسخة مستضافة على [https://soury.pythonanywhere.com](https://soury.pythonanywhere.com/).

- [النسخة الفرنسية](README.md)
- [English version](README.en.md)

## الفهرس
- [التثبيت](#التثبيت)
- [التشغيل محليا](#التشغيل-محليا)
- [الإعداد](#الإعداد)
- [إدارة البيانات](#إدارة-البيانات)
- [دليل الاستخدام](#دليل-الاستخدام)
- [النشر على NanoPi Neo (أو ما شابه)](#النشر-على-nanopi-neo-أو-ما-شابه)
- [النشر على PythonAnywhere](#النشر-على-pythonanywhere)
- [الاختبارات](#الاختبارات)
- [المساهمة](#المساهمة)
- [الترخيص](#الترخيص)

## التثبيت

تأكد من وجود **بايثون 3** وأداة `git` على جهازك.

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

يوجد هذا الملف على الخادم الذي يستضيف التطبيق (مثل
[PythonAnywhere](https://www.pythonanywhere.com/)). جميع الزوار يشتركون في هذا
الملف، لذا أي حجز يتم إنشاؤه أو حذفه يصبح مرئياً لبقية المستخدمين.

## دليل الاستخدام

### إجراء حجز

1. اختر **الغرفة**.
2. حدد **التاريخ** ووقت **البداية**.
3. اختر **الآلة** المطلوبة.
4. أدخل **عدد الدورات** (من 1 إلى 3).
5. اكتب **رمزاً من أربعة أرقام** ثم أكد.

القواعد:
- يجب أن يتكون الرمز من أربعة أرقام بالضبط؛
- لا يمكن للآلة الواحدة تجاوز **ثلاث دورات يومياً**؛
- يجب أن ينتهي الحجز **قبل الساعة 23:00**.

### الإلغاء

اضغط على الحجز في التقويم وأدخل نفس الرمز لتأكيد الحذف.

## النشر على NanoPi Neo (أو ما شابه)

يشرح هذا القسم كيفية تثبيت التطبيق بالكامل على لوحة ARM صغيرة
(مثل NanoPi Neo أو Raspberry Pi) تعمل بنظام **Debian/Armbian**.

### 1. إعداد اللوحة

- حدّث النظام وثبّت الأدوات الضرورية:

  ```bash
  sudo apt update
  sudo apt install -y python3 python3-venv python3-pip git
  ```

### 2. جلب التطبيق

- استنسخ هذا المستودع ثم ادخل إلى المجلد:

  ```bash
  git clone https://github.com/votre-utilisateur/buanderie-reservation.git
  cd buanderie-reservation
  ```

- *(اختياري)* أنشئ بيئة افتراضية وثبّت الاعتمادات:

  ```bash
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```

### 3. إعداد التطبيق

عرّف متغيرات البيئة التالية (مع تعديل المسارات والقيم حسب حاجتك):

```bash
export RESERVATIONS_FILE=/home/pi/buanderie-reservation/reservations.json
export ADMIN_CODE=votre_code_secret
```

### 4. تشغيل الخادم

- للتجربة السريعة (المنفذ 5000):

  ```bash
  python app.py
  ```

- لتوفير خدمة شبكية أكثر ثباتًا (المنفذ 8080):

  ```bash
  gunicorn app:app --bind 0.0.0.0:8080
  ```

### 5. جعل الخدمة دائمة *(اختياري)*

حتى يُعاد تشغيل التطبيق تلقائيًا، أنشئ خدمة `systemd`:

```bash
sudo nano /etc/systemd/system/buanderie.service
```

أدنى محتوى للملف:

```ini
[Unit]
Description=Buanderie Reservation
After=network.target

[Service]
WorkingDirectory=/home/pi/buanderie-reservation
ExecStart=/usr/bin/python3 /home/pi/buanderie-reservation/app.py
Environment="RESERVATIONS_FILE=/home/pi/buanderie-reservation/reservations.json"
Environment="ADMIN_CODE=votre_code_secret"
Restart=always

[Install]
WantedBy=multi-user.target
```

فعّل بعدها الخدمة:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now buanderie.service
```

سيصبح التطبيق متاحًا على العنوان
`http://<ip_اللوحة>:5000` (أو على المنفذ المستخدم في `gunicorn`).

### 6. تبسيط الوصول للمستخدمين

للحصول على عنوان أسهل من `http://<ip_اللوحة>:5000` يمكن تعيين اسم مضيف محلي
وإعادة توجيه الحركة إلى المنفذ 80:

1. **تغيير اسم الجهاز إلى "buanderie"**

   حرر ملف `/etc/hosts`:

   ```bash
   sudo nano /etc/hosts
   ```

   استبدل السطر المشابه لـ:

   ```text
   127.0.1.1    ancien-nom
   ```

   بـ:

   ```text
   127.0.1.1    buanderie
   ```

2. **تفعيل حل mDNS**

   ثبّت وشغّل خدمة *Avahi* للوصول إلى الاسم
   `buanderie.local` من شبكتك:

   ```bash
   sudo apt install avahi-daemon
   sudo systemctl enable avahi-daemon
   sudo systemctl start avahi-daemon
   ```

3. **إعادة توجيه المنفذ 80 إلى 5000**

   لتجنب كتابة المنفذ في المتصفح، أعد توجيه المنفذ 80 إلى المنفذ 5000 الذي يستخدمه Flask:

   ```bash
   sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 5000

   # حفظ القاعدة لتبقى بعد إعادة التشغيل
   sudo sh -c "iptables-save > /etc/iptables.rules"

   # إعادة تحميل القواعد تلقائيًا عند الإقلاع
   sudo sh -c 'echo -e "#!/bin/sh\niptables-restore < /etc/iptables.rules" > /etc/network/if-pre-up.d/iptables'
   sudo chmod +x /etc/network/if-pre-up.d/iptables
   ```

بعد هذه الخطوات يصبح التطبيق متاحًا عبر
`http://buanderie.local` بدون الحاجة لتحديد منفذ.

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

تُشغِّل PythonAnywhere التطبيق باستخدام **Gunicorn**. ملف `Procfile` المرفق
يستدعي الأمر:

```bash
gunicorn app:app --bind 0.0.0.0:${PORT:-8080}
```

يتم التعامل مع المنفذ تلقائياً من قبل المنصة. يمكن استعمال نفس الأمر محلياً أو
على أي مستضيف متوافق.

## الاختبارات

توجد حزمة اختبارات وحدة للتأكد من المسارات الرئيسية. بعد تثبيت الاعتمادات اشغل:

```bash
pytest
```

## المساهمة

المساهمات مرحب بها! افتح مشكلة لمناقشة أي تعديل أو اقدم طلب سحب. أحرص على تشغيل `pytest` قبل الإرسال.

---

هذا المشروع مرخص تحت رخصة MIT. اطلع على [LICENSE](LICENSE) للتفاصيل.
