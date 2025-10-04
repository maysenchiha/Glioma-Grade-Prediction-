from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import os
import joblib
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import bcrypt
import logging
import pandas as pd
from lime.lime_tabular import LimeTabularExplainer
import dill 
from flask import Flask, jsonify
app = Flask(__name__)


model = joblib.load('LogisticRegression.pkl')
scaler = joblib.load('scaler.pkl')
# Configuration de la base de données MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/glioma_db'  # Remplacez "root" si nécessaire
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

# Initialiser Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'authentication_login'  # Redirige vers cette route si l'utilisateur n'est pas connecté

# Initialiser la base de données
db = SQLAlchemy(app)

# Modèle pour les utilisateurs
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='medecin')  # 'admin' ou 'medecin'
    profile_image = db.Column(db.String(120), default='unknownUser.png')  # Nouvelle colonne pour l'image de profil
    prenom = db.Column(db.String(100), nullable=False)  # Prénom du médecin
    specialite = db.Column(db.String(100), default='Neurologie')  # Spécialité du médecin
    phone = db.Column(db.String(20), nullable=True)  # Téléphone du médecin
    adresse = db.Column(db.String(255), nullable=True)  # Adresse du médecin
    dob = db.Column(db.Date, nullable=True)  # Date de naissance du médecin
    sexe = db.Column(db.String(10), nullable=True)  # Sexe du médecin
    about = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)  

    def __repr__(self):
        return f"User('{self.name}', '{self.email}', '{self.role}')"
    
# Charger un utilisateur par son ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()  # Cela ajoutera les nouvelles colonnes dans la base de donnée

# Route pour la page d'accueil
@app.route('/')
def index():
    # Passer le nom de l'utilisateur connecté au template
    return render_template('accueil.html', user_name=current_user.name if current_user.is_authenticated else None)

@app.route('/accueil')
def accueil():
    if current_user.is_authenticated:
        # Récupérer les 10 derniers patients
        patients = Patient.query.order_by(Patient.id.desc()).limit(10).all()
        # Rediriger vers le tableau de bord en passant les patients
        return render_template('medecin_dashboard.html', patients=patients)
    else:
        # Sinon, afficher la page d'accueil
        return render_template('accueil.html', user_name=None)





@app.route('/user-profile')
@login_required
def user_profile():
    # La page userProfile.html affichera les informations de l'utilisateur connecté
    return render_template('userProfile.html')


@app.route('/authentication-register', methods=['GET', 'POST'])
def authentication_register():
    if request.method == 'POST':
        name = request.form.get('name')
        prenom = request.form.get('prenom')
        email = request.form.get('email')
        password = request.form.get('password')

        # Vérifier si l'utilisateur existe déjà
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Cet e-mail est déjà utilisé. Veuillez en choisir un autre.', 'danger')
            return redirect(url_for('authentication_register'))

        # Hasher le mot de passe avant de l'enregistrer
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Définir le rôle (exemple : admin si l'email est admin@example.com)
        role = 'admin' if email == 'admin@example.com' else 'medecin'

        # Créer un nouvel utilisateur
        new_user = User(name=name,prenom=prenom, email=email, password=hashed_password.decode('utf-8'), role=role)
        db.session.add(new_user)
        db.session.commit()

        flash('Inscription réussie ! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('authentication_login'))

    return render_template('authentication-register.html')

# Route pour "Authentication Login"
@app.route('/authentication-login', methods=['GET', 'POST'])
def authentication_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password') 
        # Rechercher l'utilisateur dans la base de données
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            login_user(user)  # Connecter l'utilisateur
            if user.role == 'admin':
                flash('Bienvenue, Administrateur !', 'success')
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'medecin':
                flash('Bienvenue, Médecin !', 'success')
                return redirect(url_for('medecin_dashboard'))
        else:
            flash('E-mail ou mot de passe incorrect.', 'danger')

    return render_template('authentication-login.html')

# Route pour déconnexion
@app.route('/logout')
@login_required
def logout():
    logout_user()  # Déconnecter l'utilisateur
    flash('Vous avez été déconnecté avec succès.', 'success')
    return redirect(url_for('authentication_login'))  # Rediriger vers la page de connexion

# Route pour le tableau de bord administrateur
@app.route('/admin-dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('index'))
    
    # Récupérer tous les médecins depuis la base de données
    medecins = User.query.filter(User.role.in_(['medecin', 'bloque'])).all()
    
    # Compter le nombre de médecins directement via une requête SQL
    nombre_medecins = User.query.filter_by(role='medecin').count()
    
    # Répartition des spécialités
    specialites = db.session.query(User.specialite, db.func.count(User.specialite)).group_by(User.specialite).all()
    specialite_labels = [s[0] for s in specialites]
    specialite_counts = [s[1] for s in specialites]

    # Répartition par sexe
    sexes = db.session.query(User.sexe, db.func.count(User.sexe)).group_by(User.sexe).all()
    sexe_labels = ['Homme' if s[0] == 'male' else 'Femme' for s in sexes]
    sexe_counts = [s[1] for s in sexes]

    # Nombre de médecins actifs et inactifs
    medecins_actifs = User.query.filter_by(is_active=True, role='medecin').count()
    medecins_inactifs = User.query.filter_by(is_active=False, role='medecin').count()

    # Transmettre les données au template
    return render_template(
        'admin_dashboard.html',
        user_name=current_user.name,
        nombre_medecins=nombre_medecins,
        medecins=medecins,
        specialite_labels=specialite_labels,
        specialite_counts=specialite_counts,
        sexe_labels=sexe_labels,
        sexe_counts=sexe_counts,
        medecins_actifs=medecins_actifs,
        medecins_inactifs=medecins_inactifs
    )
    #------------------------------------
@app.route('/gerer-medecin')
@login_required
def gerer_medecin():
    if current_user.role != 'admin':
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('index'))
    
    # Récupérer tous les médecins depuis la base de données
    medecins = User.query.filter(User.role.in_(['medecin', 'bloque'])).all()
    
    # Compter le nombre de médecins directement via une requête SQL
    count_medecins = User.query.filter_by(role='medecin').count()
    
    # Transmettre les données au template
    return render_template('gerer-medecin.html', medecins=medecins, count_medecins=count_medecins, user_name=current_user.name)

# -------------------Route pour le tableau de bord médecin
@app.route('/medecin-dashboard')
@login_required
def medecin_dashboard():
    if current_user.role != 'medecin':
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('index'))
    
    # Retrieve statistics
    total_patients = Patient.query.count()  # Total number of patients
    total_predictions = Patient.query.filter(Patient.grade.isnot(None)).count()  # Total predictions made
    
    # Count LGG and GBM grades
    lgg_count = Patient.query.filter_by(grade='LGG').count()
    gbm_count = Patient.query.filter_by(grade='GBM').count()

    return render_template(
        'medecin_dashboard.html',
        user_name=current_user.name,
        total_patients=total_patients,
        total_predictions=total_predictions,
        lgg_count=lgg_count,
        gbm_count=gbm_count
    )
# Route pour la prédiction
@app.route('/ui-forms')
@login_required
def ui_forms():
    if current_user.role != 'medecin':
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('index'))
    return render_template('ui-forms.html', user_name=current_user.name)

# Route pour les données patients
@app.route('/ui-buttons')
@login_required
def ui_buttons():
    if current_user.role != 'medecin':
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('index'))

    # Récupérer les données des patients à partir de la base de données
    patients = Patient.query.all()

    # Passer les données des patients à la template
    return render_template('ui-buttons.html', user_name=current_user.name, patients=patients)


#---------------------------------------
@app.route('/update_user_settings', methods=['POST'])
def update_user_settings():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        name = request.form.get('name')
        prenom = request.form.get('prenom')
        specialite = request.form.get('specialite')
        email = request.form.get('email')
        phone = request.form.get('phone')
        adresse = request.form.get('adresse')
        dob = request.form.get('dob')  # Correction ici
        sexe = request.form.get('sexe')
        about = request.form.get('about')

        # Mettre à jour les informations dans la base de données
        current_user.name = name
        current_user.prenom = prenom
        current_user.specialite = specialite
        current_user.email = email
        current_user.phone = phone
        current_user.adresse = adresse
        if dob:  # Vérification supplémentaire
            current_user.dob = dob
        current_user.sexe = sexe
        current_user.about = about

        # Si une nouvelle image est téléchargée
        if 'profile_image' in request.files:
            profile_image = request.files['profile_image']
            if profile_image:
                filename = secure_filename(profile_image.filename)
                profile_image.save(os.path.join('static/images/profile', filename))
                current_user.profile_image = filename

        # Sauvegarder les changements dans la base de données
        db.session.commit()

        # Rediriger vers la page du profil de l'utilisateur
        return redirect(url_for('user_profile'))










#--------------------------------
@app.route('/modifier_medecin/<int:medecin_id>', methods=['GET', 'POST'])
def modifier_medecin(medecin_id):
    medecin = User.query.get_or_404(medecin_id)  # Utilisez "User" au lieu de "Medecin"
    if request.method == 'POST':
        # Récupérer les données du formulaire
        medecin.name = request.form.get('name')
        medecin.email = request.form.get('email')
        medecin.specialite = request.form.get('specialite')
        medecin.phone = request.form.get('phone')
        medecin.adresse = request.form.get('adresse')
        medecin.sexe = request.form.get('sexe')

        db.session.commit()
        flash('Médecin mis à jour avec succès.', 'success')
        return redirect(url_for('gerer_medecin'))
    return render_template('modifier_medecin.html', medecin=medecin)
#--------------------------
@app.route('/supprimer_medecin/<int:medecin_id>', methods=['POST'])
def supprimer_medecin(medecin_id):
    medecin = User.query.get_or_404(medecin_id)
    db.session.delete(medecin)
    db.session.commit()
    return jsonify({'status': 'success'})
#-----------------
@app.route('/toggle_status/<int:medecin_id>', methods=['POST'])
def toggle_status(medecin_id):
    medecin = User.query.get_or_404(medecin_id)
    # Basculer l'état is_active
    medecin.is_active = not medecin.is_active
    db.session.commit()
    # Retourner une réponse JSON
    return jsonify({
        'status': 'success',
        'message': f'Le médecin a été {"activé" if medecin.is_active else "bloqué"} avec succès.',
        'is_active': medecin.is_active
    })

    # Route pour mettre à jour le mot de passe
@app.route('/update_password', methods=['POST'])
def update_password():
    if not current_user.is_authenticated:
        flash('You need to be logged in to update your password', 'danger')
        return redirect(url_for('authentication_login'))  # Redirection si non authentifié

    # Obtention des données du formulaire
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    # Validation des mots de passe
    if new_password != confirm_password:
        flash("New passwords don't match", 'danger')
        return redirect(url_for('user_profile'))  # Redirection vers le profil utilisateur

    if not bcrypt.checkpw(current_password.encode('utf-8'), current_user.password.encode('utf-8')):
        flash('Current password is incorrect', 'danger')
        return redirect(url_for('user_profile'))  # Redirection vers le profil utilisateur

    # Mise à jour du mot de passe
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    current_user.password = hashed_password.decode('utf-8')
    db.session.commit()

    flash('Your password has been updated successfully', 'success')
    return redirect(url_for('user_profile'))




@app.route('/prediction', methods=['GET'])
def show_prediction_result():
    # Vous pouvez récupérer la prédiction du patient inséré et l'afficher
    return render_template('prédiction.html')

@app.route('/insert_patient', methods=['GET'])
def show_insert_patient_form():
    return render_template('ui-forms.html')



# Configurez le logger
logging.basicConfig(level=logging.DEBUG)  # Définit le niveau de log à DEBUG pour afficher tous les messages
logger = logging.getLogger(__name__)
X_train = pd.read_csv('C:/Users/nadac/Downloads/X_train2.csv')
explainer = LimeTabularExplainer(
    training_data=X_train.values,  # Données d'entraînement
    feature_names=X_train.columns.tolist(),  # Noms des caractéristiques
    class_names=['LGG', 'GBM'],
    mode='classification',  # Type de modèle (classification)
    discretize_continuous=True  # Discrétiser les caractéristiques continues
)
class Patient(db.Model):
    __tablename__ = 'patient'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))  
    prenom = db.Column(db.String(255))  
    race = db.Column(db.String(100), nullable=False, default='Unknown')
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    idh1 = db.Column(db.String(255))
    pten = db.Column(db.String(255))
    atrx = db.Column(db.String(255))
    cic = db.Column(db.String(255))
    egfr = db.Column(db.String(255))
    rb1 = db.Column(db.String(255))
    fubp1 = db.Column(db.String(255))
    notch1 = db.Column(db.String(255))
    tp53 = db.Column(db.String(255))
    patient_email = db.Column(db.String(255))
    grade = db.Column(db.String(255)) 

@app.route('/insert_patient', methods=['GET', 'POST'])
def insert_patient():
    if request.method == 'POST':
        # Récupération des valeurs du formulaire
        name = request.form.get('patientName')
        prenom = request.form.get('patientprenom')
        age = request.form.get('patientAge')
        gender = request.form.get('patientGender')
        race = request.form.get('patientRace')  # Récupérer la valeur de race
        patient_email = request.form.get('patientEmail')
        idh1 = request.form.get('idh1')
        pten = request.form.get('pten')
        atrx = request.form.get('atrx')
        cic = request.form.get('cic')
        egfr = request.form.get('egfr')
        rb1 = request.form.get('rb1')
        fubp1 = request.form.get('fubp1')
        notch1 = request.form.get('notch1')
        tp53 = request.form.get('tp53')

        # Vérification si l'âge est vide
        if not age:
            flash('L\'âge est obligatoire et ne peut pas être vide.', 'error')
            return redirect('/insert_patient')

        # Vérification que l'âge est un nombre valide
        if not age.replace('.', '', 1).isdigit():  # Vérifie si age est un nombre
            flash('L\'âge doit être un nombre valide.', 'error')
            return redirect('/insert_patient')

        age = float(age)

        # Encodage des valeurs
        encoding_map = {
            'mutated': 0,
            'not_mutated': 1
        }

        # Prétraitement des données : encodez toutes les variables
        features = [
            encoding_map.get(idh1, 0),  # IDH1
            encoding_map.get(pten, 0),   # PTEN
            encoding_map.get(atrx, 0),   # ATRX
            encoding_map.get(cic, 0),    # CIC
            encoding_map.get(egfr, 0),   # EGFR
            encoding_map.get(rb1, 0),    # RB1
            encoding_map.get(fubp1, 0),  # FUBP1
            encoding_map.get(notch1, 0), # NOTCH1
            encoding_map.get(tp53, 0),   # TP53
            1 if race == 'black or african american' else 0,  # Race (encodage binaire)
            age  # L'âge, à standardiser
        ]

        # Création d'un DataFrame avec les caractéristiques pour correspondre aux noms de colonnes du modèle
        feature_names = [
            'IDH1', 'PTEN', 'ATRX', 'CIC', 'EGFR', 'RB1', 'FUBP1', 'NOTCH1', 'TP53',
            'Race_black or african american', 'Age_at_diagnosis'
        ]
        feature_df = pd.DataFrame([features], columns=feature_names)

        # Standardiser la colonne 'Age_at_diagnosis'
        feature_df['Age_at_diagnosis'] = scaler.transform(feature_df[['Age_at_diagnosis']])

        # Prédiction avec le modèle
        prediction = model.predict(feature_df)  # Utilisation du DataFrame pour la prédiction
        proba = model.predict_proba(feature_df)[0]  # Probabilités pour chaque classe (LGG et GBM)
        if prediction[0] == 0:
            grade = 'LGG'  # Si la prédiction est 1, le grade est LGG
        else:
            grade = 'GBM'  # Sinon, le grade est GBM

        # Générer une explication LIME pour ce patient
        exp = explainer.explain_instance(
            data_row=feature_df.values[0],  # Échantillon à expliquer (données du patient)
            predict_fn=model.predict_proba  # Fonction de prédiction probabiliste du modèle
        )

        # Obtenir l'explication en HTML
        lime_html = exp.as_html()  # Cette méthode génère une version HTML de l'explication LIME

        # Création de l'objet Patient et insertion dans la base de données
        new_patient = Patient(
            name=name,
            prenom=prenom,
            age=int(age),
            gender=gender,
            race=race,  # Insérer la valeur de race récupérée du formulaire
            patient_email=patient_email,
            idh1=idh1,
            pten=pten,
            atrx=atrx,
            cic=cic,
            egfr=egfr,
            rb1=rb1,
            fubp1=fubp1,
            notch1=notch1,
            tp53=tp53,
            grade=grade  # Enregistrer la prédiction dans la colonne 'grade'
        )

        db.session.add(new_patient)
        db.session.commit()

        flash('Patient ajouté avec succès!', 'success')

        # Redirection vers la page de prédiction avec les résultats
        return render_template('prédiction.html', 
                               grade=grade, 
                               proba=proba, 
                               lime_html=lime_html)

    # Affichage de la page de formulaire en GET
    return redirect('/insert_patient')

if __name__ == '__main__':
    app.run(debug=True)