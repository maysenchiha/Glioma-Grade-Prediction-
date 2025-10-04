# 🧠 Glioma Grade Prediction Application

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![Machine Learning](https://img.shields.io/badge/ML-XAI-orange.svg)

## 📝 Description

Cette application web basée sur Flask permet de **prédire le grade des gliomes** (tumeurs cérébrales) en utilisant des techniques de machine learning avancées. Le projet intègre **XAI (eXplainable AI)** pour fournir des explications détaillées et interprétables des prédictions, aidant ainsi les professionnels de santé à comprendre les facteurs influençant chaque diagnostic.

## 🏗️ Architecture du Projet

```
<PROJECT ROOT>
├── app.py                      # Application Flask principale
├── Logistic.pkl                # Modèle de régression logistique entraîné
├── LogisticRegression.pkl      # Modèle alternatif
├── scaler.pkl                  # Normalisateur des données
├── explainer.pkl               # Explainer XAI (SHAP/LIME)
├── requirements.txt            # Dépendances Python
├── README.md                   # Documentation
├── .hintrc                     # Configuration linter
│
├── __pycache__/                # Cache Python
├── venv/                       # Environnement virtuel
│
├── static/                     # Fichiers statiques
│   ├── css/                    # Styles CSS
│   ├── js/                     # Scripts JavaScript
│   └── images/                 # Images et logos
│
└── templates/                      # Templates HTML
    ├── index.html                  # Page d'accueil
    ├── accueil.html                # Page d'accueil alternative
    ├── authentication-login.html   # Page de connexion
    ├── authentication-register.html # Page d'inscription
    ├── admin_dashboard.html        # Tableau de bord administrateur
    ├── medecin_dashboard.html      # Tableau de bord médecin
    ├── userProfile.html            # Profil utilisateur
    ├── gerer-medecin.html          # Gestion des médecins
    ├── modifier_medecin.html       # Modification des médecins
    ├── prédiction.html             # Page de prédiction
    ├── ui-buttons.html             # Composants UI - Boutons
    └── ui-forms.html               # Composants UI - Formulaires
```

## 🔬 Technologies Utilisées

### Backend & Machine Learning
- **Python 3.8+** - Langage principal
- **Flask** - Framework web léger
- **Scikit-learn** - Modèles de machine learning
- **XGBoost / Logistic Regression** **/...** - Algorithmes de classification
- **Pandas & NumPy** **/...** - Manipulation de données

### Explicabilité (XAI)
- **LIME** (Local Interpretable Model-agnostic Explanations) - Explications locales
- **Matplotlib / Plotly** - Visualisations interactives

### Frontend
- **HTML5 / CSS3** - Structure et style
- **JavaScript** - Interactivité
- **Bootstrap**  - Design responsive

## 📊 Modèle de Machine Learning

### Entraînement
Le modèle a été entraîné sur un dataset médical validé contenant :
- Caractéristiques cliniques
- Marqueurs biologiques
- Historique patient

## 🔍 Explicabilité (XAI)

### Pourquoi XAI ?
Dans le domaine médical, il est crucial de comprendre **pourquoi** un modèle fait une prédiction. XAI permet :
- **Confiance** : Les médecins peuvent valider les décisions
- **Transparence** : Identification des biais potentiels
- **Apprentissage** : Découverte de nouvelles corrélations cliniques
- **Conformité** : Respect des réglementations médicales

### Techniques utilisées
#### LIME (Local Interpretable Model-agnostic Explanations)
- Explique les prédictions individuelles
- Crée un modèle local interprétable autour de chaque prédiction
- Visualisations intuitives pour les non-experts

## 🎨 Captures d'écran

### Dashboard Administrateur
![Admin Dashboard](images/admin-dashboard.png)

### Dashboard Médecin
![Doctor Dashboard](images/medecin-dashboard.png)

### Historique de Prédiction
![Manage Doctors](images/gerer-medecin.png)

### Formulaire de prédiction
![Prediction Form](images/prediction-form.png)
![Prediction Form](images/prediction-form.png)

### Résultats avec explications XAI
![Results](images/results-xai.png)

### Graphiques SHAP
![SHAP Plots](images/shap-plots.png)

### Profil utilisateur
![User Profile](images/user-profile.png)

## 📋 Dépendances (requirements.txt)

```
Flask==2.3.0
scikit-learn==1.3.0
pandas==2.0.0
numpy==1.24.0
shap==0.42.0
lime==0.2.0.1
matplotlib==3.7.0
plotly==5.14.0
Pillow==10.0.0
gunicorn==20.1.0
```

## 🔐 Sécurité et confidentialité

- ⚠️ **Données sensibles** : Les données médicales doivent être anonymisées
- 🔒 **RGPD** : Conformité avec les réglementations sur la protection des données
- 🏥 **Usage** : Cette application est destinée à un usage de recherche/éducatif
- ⚕️ **Avertissement** : Ne remplace pas un diagnostic médical professionnel

## 🚧 Limitations

- Le modèle nécessite des données de qualité pour des prédictions fiables
- Les explications XAI sont des approximations et doivent être validées cliniquement
- L'application n'est pas certifiée pour un usage clinique direct
- Nécessite une validation supplémentaire pour la production

## 📈 Améliorations futures

- [ ] **Authentification avancée** : Authentification à deux facteurs (2FA)
- [ ] **Base de données** : Migration vers PostgreSQL/MySQL pour stockage permanent
- [ ] **API REST** : Création d'API pour intégration avec systèmes hospitaliers
- [ ] **Deep Learning** : Intégration de CNN pour analyse d'images IRM
- [ ] **Notifications** : Système d'alertes email/SMS pour résultats critiques
- [ ] **Multi-langues** : Support français, anglais, arabe
- [ ] **Export rapports** : Génération automatique de rapports PDF médicaux
- [ ] **Télémédecine** : Intégration de visioconférence pour consultations
- [ ] **Dashboard analytics** : Statistiques avancées et tendances
- [ ] **Mobile app** : Application mobile iOS/Android
- [ ] **Backup automatique** : Sauvegarde régulière des données
- [ ] **Audit logs** : Traçabilité complète des actions utilisateurs
- [ ] **DICOM support** : Import direct d'images médicales DICOM
- [ ] **Collaboration** : Partage de cas entre médecins

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Forkez le projet
2. Créez une branche (`git checkout -b feature/amelioration`)
3. Committez vos changements (`git commit -m 'Ajout fonctionnalité'`)
4. Pushez vers la branche (`git push origin feature/amelioration`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👨‍💻 Auteur

**Maysen Chiha**
- GitHub: [@maysenchiha](https://github.com/maysenchiha)
- LinkedIn: [Votre profil LinkedIn]
- Email: votre.email@example.com

## 📚 Références

- [SHAP Documentation](https://shap.readthedocs.io/)
- [LIME Documentation](https://lime-ml.readthedocs.io/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Scikit-learn Guide](https://scikit-learn.org/)

## 🙏 Remerciements

- Dataset fourni par [Source du dataset]
- Inspiré par les travaux de recherche en neuro-oncologie
- Communauté open-source pour les outils XAI

---

⚠️ **Disclaimer** : Cette application est développée à des fins de recherche et d'éducation. Elle ne doit pas être utilisée comme substitut à un diagnostic médical professionnel. Consultez toujours un professionnel de santé qualifié pour toute question médicale.

**© 2024 - Glioma Grade Prediction Project**
