import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { User, LogOut, TrendingDown } from 'lucide-react'
import SearchFilters from './components/SearchFilters'
import ResultsTable from './components/ResultsTable'
import AuthModal from './components/AuthModal'
import SavedSearches from './components/SavedSearches'
import './App.css'

function App() {
  const [user, setUser] = useState(null)
  const [authModalOpen, setAuthModalOpen] = useState(false)
  const [searchResults, setSearchResults] = useState([])
  const [isSearching, setIsSearching] = useState(false)
  const [currentFilters, setCurrentFilters] = useState({})
  const [searchParams, setSearchParams] = useState(null)

  useEffect(() => {
    // Vérifier si l'utilisateur est déjà connecté
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/auth/me')
      if (response.ok) {
        const data = await response.json()
        setUser(data.user)
      }
    } catch (error) {
      console.error('Erreur lors de la vérification de l\'authentification:', error)
    }
  }

  const handleSearch = async (filters) => {
    setIsSearching(true)
    setCurrentFilters(filters)
    setSearchParams(filters)
    
    try {
      const response = await fetch('http://localhost:5001/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(filters),
      })

      if (response.ok) {
        const data = await response.json()
        setSearchResults(data.results)
      } else {
        console.error('Erreur lors de la recherche')
        setSearchResults([])
      }
    } catch (error) {
      console.error('Erreur lors de la recherche:', error)
      setSearchResults([])
    } finally {
      setIsSearching(false)
    }
  }

  const handleLogin = (userData) => {
    setUser(userData)
  }

  const handleLogout = async () => {
    try {
      await fetch('http://localhost:5001/api/auth/logout', { method: 'POST' })
      setUser(null)
    } catch (error) {
      console.error('Erreur lors de la déconnexion:', error)
    }
  }

  const handleLoadSearch = (filters) => {
    handleSearch(filters)
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <TrendingDown className="h-8 w-8 text-primary" />
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
                  <span className="text-sm text-muted-foreground">
                    Bonjour, {user.username}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleLogout}
                  >
                    <LogOut className="h-4 w-4 mr-2" />
                    Déconnexion
                  </Button>
                </div>
              ) : (
                <Button
                  variant="outline"
                  onClick={() => setAuthModalOpen(true)}
                >
                  <User className="h-4 w-4 mr-2" />
                  Connexion
                </Button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
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
      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        onLogin={handleLogin}
      />
    </div>
  )
}

export default App
