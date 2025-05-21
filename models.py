from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class Utilisateur(db.Model):
    __tablename__ = 'Utilisateurs'
    utilisateur_id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # يجب تحديد طول للـ String
    seller = relationship('Seller', backref='utilisateur_seller', uselist=False)
    client = relationship('Client', backref='utilisateur_client', uselist=False)

class Client(db.Model):
    __tablename__ = 'Clients'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    utilisateur_id = Column(Integer, ForeignKey('Utilisateurs.utilisateur_id'), nullable=False)

class Seller(db.Model):
    __tablename__ = 'Sellers'
    seller_id = Column(Integer, primary_key=True)
    utilisateur_id = Column(Integer, ForeignKey('Utilisateurs.utilisateur_id'), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    nom = Column(String(100), nullable=True)
    description = Column(String(255), nullable=True)
    image = Column(String(255), nullable=True)
    service = Column(String(100), nullable=True)
    categorie = Column(String(100), nullable=True)

class Administrateur(db.Model):
    __tablename__ = 'Administrateur'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('Utilisateurs.utilisateur_id'), nullable=False)

class Categorie(db.Model):
    __tablename__ = 'Categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)

    services = relationship("Service", backref="categorie", lazy=True)

class Service(db.Model):
    __tablename__ = 'Services'
    id = Column(Integer, primary_key=True)
    titre = Column(String(80), unique=True, nullable=False)
    prix = Column(Integer, nullable=False)
    freelance_id = Column(Integer, ForeignKey('Sellers.seller_id'), nullable=False)
    category_id = Column(Integer, ForeignKey('Categories.id'), nullable=False)
    commandes = relationship('Commande', backref='service', lazy=True)

class Commande(db.Model):
    __tablename__ = 'Commandes'
    commande_id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('Clients.id'), nullable=False)
    service_id = Column(Integer, ForeignKey('Services.id'), nullable=False)
    statut_ENUM = Column(Integer, nullable=False)
    date_creation = Column(DateTime, nullable=False)   # أفضل أن تكون DateTime
    date_livraison = Column(DateTime, nullable=False)  # بدلًا من Integer

class Message(db.Model):
    __tablename__ = 'Messagerie'
    message_id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, nullable=False)
    receiver_id = Column(Integer, nullable=False)
    message = Column(Text, nullable=False)
    date_envoi = Column(DateTime, nullable=False)
    status = Column(Enum('vue', 'non vue', name='status_enum'), default='non vue', nullable=False)
    image_path = Column(String(255), nullable=True)
