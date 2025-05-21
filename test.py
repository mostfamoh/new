from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from models import db, Utilisateur, Client, Seller, Administrateur, Service, Commande, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://flaskuser:admin@localhost/backend'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret123'

# مسار رفع الملفات الثابت
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db.init_app(app)
CORS(app)

@app.route('/')
def home():
    return "مرحبا بك في API الخاص بنا!"

@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify(error="يجب إرسال البيانات بصيغة JSON!"), 400

    data = request.get_json()
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()

    if not email or not password:
        return jsonify(error="يرجى إدخال البريد الإلكتروني وكلمة المرور"), 400

    user = Utilisateur.query.filter_by(email=email).first()
    if not user:
        return jsonify(error="البريد الإلكتروني غير صحيح"), 404

    if not check_password_hash(user.password, password):
        return jsonify(error="كلمة المرور غير صحيحة"), 401

    session['user_id'] = user.utilisateur_id
    return jsonify(message="مرحباً بك!"), 200


@app.route("/signup", methods=['POST'])
def signup():
    if not request.is_json:
        return jsonify({'error': 'يجب إرسال البيانات بصيغة JSON!'}), 400

    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    email = data.get("email", "").strip()

    if not username or not password or not email:
        return jsonify({'error': "يرجى إدخال كل المعلومات المطلوبة"}), 400

    existing_user = Utilisateur.query.filter(
        (Utilisateur.username == username) | (Utilisateur.email == email)
    ).first()
    if existing_user:
        return jsonify({'error': 'اسم المستخدم أو البريد الإلكتروني مسجل مسبقاً!'}), 400

    hashed_password = generate_password_hash(password)
    new_user = Utilisateur(
        username=username,
        password=hashed_password,
        email=email,
    )

    db.session.add(new_user)
    db.session.commit()

    nouveau_client = Client(utilisateur_id=new_user.utilisateur_id, email=email, username=username)
    db.session.add(nouveau_client)
    db.session.commit()

    return jsonify({'message': 'تم إنشاء الحساب بنجاح!'}), 201


@app.route("/becomaseller", methods=['POST'])
def becomaseller():
    if 'user_id' not in session:
        return jsonify({'error': 'يجب تسجيل الدخول أولاً'}), 401

    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()
    description = request.form.get("description", "").strip()
    image = request.files.get("image")
    service = request.form.get("service", "").strip()
    categorie = request.form.get("Categorie", "").strip()
    utilisateur_id = session['user_id']

    if not first_name or not last_name or not service or not categorie:
        return jsonify({'error': "يرجى إدخال كل المعلومات المطلوبة"}), 400

    existing_seller = Seller.query.filter_by(utilisateur_id=utilisateur_id).first()
    if existing_seller:
        return jsonify({'error': 'لقد قمت بإنشاء بائع بالفعل'}), 400

    image_filename = None
    if image:
        # تأكد من أن اسم الملف آمن (يمكن استخدام werkzeug.utils secure_filename في تطبيق حقيقي)
        image_filename = f"{first_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{image.filename}"
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        image.save(image_path)

    new_seller = Seller(
        utilisateur_id=utilisateur_id,
        first_name=first_name,
        last_name=last_name,
        nom=f"{first_name} {last_name}",
        description=description,
        image=image_filename,
        service=service,
        categorie=categorie,
    )

    db.session.add(new_seller)
    db.session.commit()

    return jsonify({'message': 'تم إنشاء البائع بنجاح!'}), 201


@app.route("/message", methods=['POST'])
def envoyer_message():
    if 'user_id' not in session:
        return jsonify({'error': 'المستخدم غير مسجل دخول'}), 401

    sender_id = request.form.get("sender_id")
    receiver_id = request.form.get("receiver_id")
    message_text = request.form.get("message", "").strip()
    image = request.files.get("image")

    if not sender_id or not receiver_id or not message_text:
        return jsonify({"error": "الرجاء ملء جميع الحقول المطلوبة"}), 400

    try:
        sender_id = int(sender_id)
        receiver_id = int(receiver_id)
    except (TypeError, ValueError):
        return jsonify({"error": "معرّف المرسل أو المستقبل غير صالح"}), 400

    image_path = None
    if image:
        image_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{image.filename}"
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        image.save(image_path)

    new_message = Message(
        message=message_text,
        sender_id=sender_id,
        receiver_id=receiver_id,
        date_envoi=datetime.now(),
        status="non vue",
        image_path=image_filename if image else None
    )

    db.session.add(new_message)
    db.session.commit()

    return jsonify({"message": "تم إرسال الرسالة بنجاح"}), 201


with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
