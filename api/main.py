import { supabase } from '../supabase';

function AuthModal() {
  const handleSignUp = async () => {
    try {
      const { user, error } = await supabase.auth.signUp({
        email: 'user@example.com',
        password: 'password123',
      });
      if (error) throw error;
      alert('Inscription réussie !');
    } catch (error) {
      alert('Erreur : ' + error.message);
    }
  };

  return <button onClick={handleSignUp}>S'inscrire</button>;
}

export default AuthModal;
