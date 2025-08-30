from flask import Blueprint, jsonify, request, session
from src.models.user import User, db
from src.models.saved_search import SavedSearch

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Inscription d'un nouvel utilisateur
    """
    try:
        data = request.json
        
        # Vérifier que tous les champs requis sont présents
        if not all(k in data for k in ('username', 'email', 'password')):
            return jsonify({'error': 'Champs manquants'}), 400
        
        # Vérifier si l'utilisateur existe déjà
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Nom d\'utilisateur déjà utilisé'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email déjà utilisé'}), 400
        
        # Créer le nouvel utilisateur
        user = User(
            username=data['username'],
            email=data['email']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Connecter automatiquement l'utilisateur
        session['user_id'] = user.id
        
        return jsonify({
            'message': 'Utilisateur créé avec succès',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Connexion d'un utilisateur
    """
    try:
        data = request.json
        
        if not all(k in data for k in ('username', 'password')):
            return jsonify({'error': 'Nom d\'utilisateur et mot de passe requis'}), 400
        
        user = User.query.filter_by(username=data['username']).first()
        
        if user and user.check_password(data['password']):
            session['user_id'] = user.id
            return jsonify({
                'message': 'Connexion réussie',
                'user': user.to_dict()
            })
        else:
            return jsonify({'error': 'Nom d\'utilisateur ou mot de passe incorrect'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Déconnexion d'un utilisateur
    """
    session.pop('user_id', None)
    return jsonify({'message': 'Déconnexion réussie'})

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """
    Retourne les informations de l'utilisateur connecté
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    return jsonify({'user': user.to_dict()})

@auth_bp.route('/saved-searches', methods=['GET'])
def get_saved_searches():
    """
    Retourne les recherches sauvegardées de l'utilisateur connecté
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    searches = SavedSearch.query.filter_by(user_id=session['user_id']).all()
    return jsonify({
        'saved_searches': [search.to_dict() for search in searches]
    })

@auth_bp.route('/saved-searches', methods=['POST'])
def save_search():
    """
    Sauvegarde une nouvelle recherche pour l'utilisateur connecté
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        data = request.json
        
        if not all(k in data for k in ('name', 'parameters')):
            return jsonify({'error': 'Nom et paramètres requis'}), 400
        
        search = SavedSearch(
            user_id=session['user_id'],
            name=data['name']
        )
        search.set_parameters(data['parameters'])
        
        db.session.add(search)
        db.session.commit()
        
        return jsonify({
            'message': 'Recherche sauvegardée avec succès',
            'saved_search': search.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/saved-searches/<int:search_id>', methods=['DELETE'])
def delete_saved_search(search_id):
    """
    Supprime une recherche sauvegardée
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    search = SavedSearch.query.filter_by(
        id=search_id, 
        user_id=session['user_id']
    ).first_or_404()
    
    db.session.delete(search)
    db.session.commit()
    
    return jsonify({'message': 'Recherche supprimée avec succès'})

