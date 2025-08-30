import { useState, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { User, Mail, Lock, LogIn, UserPlus } from 'lucide-react';
import { toast } from 'react-toastify';
import PropTypes from 'prop-types';

// Service API pour centraliser les appels
const api = {
  login: async (credentials) => {
    const response = await fetch(`${process.env.REACT_APP_API_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // Support des cookies de session
      body: JSON.stringify(credentials),
    });
    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || 'Erreur de connexion');
    }
    return response.json();
  },
  register: async (userData) => {
    const response = await fetch(`${process.env.REACT_APP_API_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify(userData),
    });
    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || 'Erreur lors de l\'inscription');
    }
    return response.json();
  },
};

const AuthModal = ({ isOpen, onClose, onLogin }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [loginForm, setLoginForm] = useState({ username: '', password: '' });
  const [registerForm, setRegisterForm] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });

  const handleLogin = useCallback(async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    // Validation simple côté client
    if (!loginForm.username || !loginForm.password) {
      setError('Veuillez remplir tous les champs');
      setIsLoading(false);
      return;
    }

    try {
      const data = await api.login(loginForm);
      onLogin(data.user);
      onClose();
      toast.success('Connexion réussie');
    } catch (err) {
      setError(err.message);
      toast.error(err.message);
    } finally {
      setIsLoading(false);
    }
  }, [loginForm, onLogin, onClose]);

  const handleRegister = useCallback(async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    // Validation côté client
    if (registerForm.password !== registerForm.confirmPassword) {
      setError('Les mots de passe ne correspondent pas');
      setIsLoading(false);
      return;
    }
    if (registerForm.password.length < 8) {
      setError('Le mot de passe doit contenir au moins 8 caractères');
      setIsLoading(false);
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(registerForm.email)) {
      setError('Veuillez entrer un email valide');
      setIsLoading(false);
      return;
    }

    try {
      const data = await api.register({
        username: registerForm.username,
        email: registerForm.email,
        password: registerForm.password,
      });
      onLogin(data.user);
      onClose();
      toast.success('Inscription réussie');
    } catch (err) {
      setError(err.message);
      toast.error(err.message);
    } finally {
      setIsLoading(false);
    }
  }, [registerForm, onLogin, onClose]);

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]" aria-describedby="auth-dialog-description">
        <DialogHeader>
          <DialogTitle>Authentification</DialogTitle>
          <div id="auth-dialog-description" className="sr-only">
            Fenêtre modale pour la connexion ou l'inscription
          </div>
        </DialogHeader>

        <Tabs defaultValue="login" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="login">Connexion</TabsTrigger>
            <TabsTrigger value="register">Inscription</TabsTrigger>
          </TabsList>

          <TabsContent value="login">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <LogIn className="h-5 w-5" aria-hidden="true" />
                  Connexion
                </CardTitle>
                <CardDescription>
                  Connectez-vous pour sauvegarder vos recherches
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleLogin} className="space-y-4" noValidate>
                  <div className="space-y-2">
                    <Label htmlFor="login-username">Nom d'utilisateur</Label>
                    <div className="relative">
                      <User className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" aria-hidden="true" />
                      <Input
                        id="login-username"
                        type="text"
                        placeholder="Votre nom d'utilisateur"
                        className="pl-10"
                        value={loginForm.username}
                        onChange={(e) => setLoginForm((prev) => ({ ...prev, username: e.target.value }))}
                        required
                        aria-required="true"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="login-password">Mot de passe</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" aria-hidden="true" />
                      <Input
                        id="login-password"
                        type="password"
                        placeholder="Votre mot de passe"
                        className="pl-10"
                        value={loginForm.password}
                        onChange={(e) => setLoginForm((prev) => ({ ...prev, password: e.target.value }))}
                        required
                        aria-required="true"
                      />
                    </div>
                  </div>

                  {error && (
                    <div
                      className="text-sm text-destructive bg-destructive/10 p-2 rounded"
                      role="alert"
                      aria-live="assertive"
                    >
                      {error}
                    </div>
                  )}

                  <Button
                    type="submit"
                    className="w-full"
                    disabled={isLoading}
                    aria-label={isLoading ? 'Connexion en cours' : 'Se connecter'}
                  >
                    {isLoading ? 'Connexion...' : 'Se connecter'}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="register">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <UserPlus className="h-5 w-5" aria-hidden="true" />
                  Inscription
                </CardTitle>
                <CardDescription>
                  Créez un compte pour sauvegarder vos recherches
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleRegister} className="space-y-4" noValidate>
                  <div className="space-y-2">
                    <Label htmlFor="register-username">Nom d'utilisateur</Label>
                    <div className="relative">
                      <User className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" aria-hidden="true" />
                      <Input
                        id="register-username"
                        type="text"
                        placeholder="Choisissez un nom d'utilisateur"
                        className="pl-10"
                        value={registerForm.username}
                        onChange={(e) => setRegisterForm((prev) => ({ ...prev, username: e.target.value }))}
                        required
                        aria-required="true"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="register-email">Email</Label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" aria-hidden="true" />
                      <Input
                        id="register-email"
                        type="email"
                        placeholder="votre@email.com"
                        className="pl-10"
                        value={registerForm.email}
                        onChange={(e) => setRegisterForm((prev) => ({ ...prev, email: e.target.value }))}
                        required
                        aria-required="true"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="register-password">Mot de passe</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" aria-hidden="true" />
                      <Input
                        id="register-password"
                        type="password"
                        placeholder="Choisissez un mot de passe"
                        className="pl-10"
                        value={registerForm.password}
                        onChange={(e) => setRegisterForm((prev) => ({ ...prev, password: e.target.value }))}
                        required
                        aria-required="true"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="register-confirm">Confirmer le mot de passe</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" aria-hidden="true" />
                      <Input
                        id="register-confirm"
                        type="password"
                        placeholder="Confirmez votre mot de passe"
                        className="pl-10"
                        value={registerForm.confirmPassword}
                        onChange={(e) => setRegisterForm((prev) => ({ ...prev, confirmPassword: e.target.value }))}
                        required
                        aria-required="true"
                      />
                    </div>
                  </div>

                  {error && (
                    <div
                      className="text-sm text-destructive bg-destructive/10 p-2 rounded"
                      role="alert"
                      aria-live="assertive"
                    >
                      {error}
                    </div>
                  )}

                  <Button
                    type="submit"
                    className="w-full"
                    disabled={isLoading}
                    aria-label={isLoading ? 'Inscription en cours' : 'S\'inscrire'}
                  >
                    {isLoading ? 'Inscription...' : 'S\'inscrire'}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};

// Validation des props avec PropTypes
AuthModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onLogin: PropTypes.func.isRequired,
};

export default AuthModal;
