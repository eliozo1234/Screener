import { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { User, LogOut, TrendingDown } from 'lucide-react';
import { toast } from 'react-toastify'; // Pour les notifications utilisateur
import SearchFilters from './components/SearchFilters';
import ResultsTable from './components/ResultsTable';
import React, { Suspense } from 'react';
import SavedSearches from './components/SavedSearches';
import './App.css';

// Lazy-loading du composant AuthModal pour optimiser le chargement initial
const AuthModal = React.lazy(() => import('./components/AuthModal'));

// Service API pour centraliser les appels
const api = {
  checkAuthStatus: async () => {
    const response = await fetch(`${process.env.REACT_APP_API_URL}/auth`, {
      credentials: 'include', // Pour les cookies de session, si utilisé
    });
    if (!response.ok) throw new Error('Échec de la vérification de l\'authentification');
    return response.json();
  },
  search: async (filters, token) => {
    const response = await fetch(`${process.env.REACT_APP_API_URL}/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }), // Ajout du token si disponible
      },
      body: JSON.stringify(filters),
    });
    if (!response.ok) throw new Error('Échec de la recherche');
    return response.json();
  },
  logout: async () => {
    const response = await fetch(`${process.env.REACT_APP_API_URL}/auth/logout`, {
      method: 'POST',
      credentials: 'include',
    });
    if (!response.ok) throw new Error('Échec de la déconnexion');
  },
};

// Composant ErrorBoundary pour gérer les erreurs de rendu
class ErrorBoundary extends React.Component {
  state = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return (
        <Card>
          <CardHeader>
            <CardTitle>Erreur</CardTitle>
          </CardHeader>
          <CardContent>
            <p>Une erreur s'est produite. Veuillez réessayer plus tard.</p>
          </CardContent>
        </Card>
      );
    }
    return this.props.children;
  }
}

function App() {
  const [user, setUser] = useState(null);
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [currentFilters, setCurrentFilters] = useState({});
  const [searchParams, setSearchParams] = useState(null);

  useEffect(() => {
    // Vérifier si l'utilisateur est connecté au chargement
    const checkAuth = async () => {
      try {
        const data = await api.checkAuthStatus();
        setUser(data.user);
      } catch (error) {
        toast.error('Erreur lors de la vérification de l\'authentification');
      }
    };
    checkAuth();
  }, []);

  const handleSearch = useCallback(async (filters) => {
    setIsSearching(true);
    setCurrentFilters(filters);
    setSearchParams(filters);

    try {
      const data = await api.search(filters, user?.token);
      setSearchResults(data.results || []);
    } catch (error) {
      toast.error('Erreur lors de la recherche. Veuillez réessayer.');
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  }, [user]);

  const handleLogin = useCallback((userData) => {
    setUser(userData);
    setAuthModalOpen(false);
    toast.success(`Bienvenue, ${userData.username}`);
  }, []);

  const handleLogout = useCallback(async () => {
    try {
      await api.logout();
      setUser(null);
      toast.success('Déconnexion réussie');
    } catch (error) {
      toast.error('Erreur lors de la déconnexion');
    }
  }, []);

  const handleLoadSearch = useCallback((filters) => {
    handleSearch(filters);
  }, [handleSearch]);

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-background">
        {/* Header */}
        <header className="border-b bg-card" role="banner">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <TrendingDown className="h-8 w-8 text-primary" aria-hidden="true" />
                <div>
                  <h1 className="text-2xl font-bold">Screening Actions</h1>
                  <p className="text-sm text-muted-foreground">
                    Eurostoxx 600 & S&P 500
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                {user ? (
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-muted-foreground" aria-live="polite">
                      Bonjour, {user.username}
                    </span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleLogout}
                      aria-label="Se déconnecter"
                    >
                      <LogOut className="h-4 w-4 mr-2" aria-hidden="true" />
                      Déconnexion
                    </Button>
                  </div>
                ) : (
                  <Button
                    variant="outline"
                    onClick={() => setAuthModalOpen(true)}
                    aria-label="Se connecter"
                  >
                    <User className="h-4 w-4 mr-2" aria-hidden="true" />
                    Connexion
                  </Button>
                )}
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="container mx-auto px-4 py-8" role="main">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Sidebar */}
            <div className="lg:col-span-1 space-y-6">
              <SearchFilters
                onSearch={handleSearch}
                isLoading={isSearching}
              />
              <SavedSearches
                user={user}
                currentFilters={currentFilters}
                onLoadSearch={handleLoadSearch}
              />
            </div>

            {/* Results */}
            <div className="lg:col-span-3">
              <ResultsTable
                results={searchResults}
                isLoading={isSearching}
                searchParams={searchParams}
              />
            </div>
          </div>
        </main>

        {/* Auth Modal */}
        <Suspense fallback={<div>Chargement...</div>}>
          <AuthModal
            isOpen={authModalOpen}
            onClose={() => setAuthModalOpen(false)}
            onLogin={handleLogin}
          />
        </Suspense>
      </div>
    </ErrorBoundary>
  );
}

export default App;
