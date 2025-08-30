import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import { Save, Bookmark, Trash2, Play } from 'lucide-react'

const SavedSearches = ({ user, currentFilters, onLoadSearch }) => {
  const [savedSearches, setSavedSearches] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [saveDialogOpen, setSaveDialogOpen] = useState(false)
  const [searchName, setSearchName] = useState('')

  useEffect(() => {
    if (user) {
      loadSavedSearches()
    }
  }, [user])

  const loadSavedSearches = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/auth/saved-searches')
      if (response.ok) {
        const data = await response.json()
        setSavedSearches(data.saved_searches)
      }
    } catch (error) {
      console.error('Erreur lors du chargement des recherches:', error)
    }
  }

  const saveCurrentSearch = async () => {
    if (!searchName.trim()) return

    setIsLoading(true)
    try {
      const response = await fetch('http://localhost:5001/api/auth/saved-searches', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: searchName,
          parameters: currentFilters,
        }),
      })

      if (response.ok) {
        setSaveDialogOpen(false)
        setSearchName('')
        loadSavedSearches()
      }
    } catch (error) {
      console.error('Erreur lors de la sauvegarde:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const deleteSearch = async (searchId) => {
    try {
      const response = await fetch(`http://localhost:5001/api/auth/saved-searches/${searchId}`, {
        method: 'DELETE',
      })

      if (response.ok) {
        loadSavedSearches()
      }
    } catch (error) {
      console.error('Erreur lors de la suppression:', error)
    }
  }

  const formatSearchParams = (params) => {
    const parts = []
    if (params.indices) parts.push(`Indices: ${params.indices.join(', ')}`)
    if (params.lookback_years) parts.push(`${params.lookback_years} ans`)
    if (params.threshold_pct) parts.push(`≤ ${params.threshold_pct}%`)
    return parts.join(' • ')
  }

  if (!user) {
    return (
      <Card>
        <CardContent className="p-6 text-center text-muted-foreground">
          Connectez-vous pour sauvegarder et gérer vos recherches
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Bookmark className="h-5 w-5" />
            Recherches Sauvegardées
          </CardTitle>
          <Dialog open={saveDialogOpen} onOpenChange={setSaveDialogOpen}>
            <DialogTrigger asChild>
              <Button size="sm" variant="outline">
                <Save className="h-4 w-4 mr-2" />
                Sauvegarder
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Sauvegarder la recherche actuelle</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="search-name">Nom de la recherche</Label>
                  <Input
                    id="search-name"
                    value={searchName}
                    onChange={(e) => setSearchName(e.target.value)}
                    placeholder="ex: Actions tech sous-évaluées"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Paramètres actuels</Label>
                  <div className="text-sm text-muted-foreground bg-muted p-2 rounded">
                    {formatSearchParams(currentFilters)}
                  </div>
                </div>
                <Button 
                  onClick={saveCurrentSearch} 
                  disabled={!searchName.trim() || isLoading}
                  className="w-full"
                >
                  {isLoading ? 'Sauvegarde...' : 'Sauvegarder'}
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </CardHeader>
      <CardContent>
        {savedSearches.length === 0 ? (
          <div className="text-center text-muted-foreground py-4">
            Aucune recherche sauvegardée
          </div>
        ) : (
          <div className="space-y-3">
            {savedSearches.map((search) => (
              <div
                key={search.id}
                className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50"
              >
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium truncate">{search.name}</h4>
                  <p className="text-sm text-muted-foreground truncate">
                    {formatSearchParams(search.parameters)}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {new Date(search.created_at).toLocaleDateString('fr-FR')}
                  </p>
                </div>
                <div className="flex items-center gap-2 ml-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => onLoadSearch(search.parameters)}
                  >
                    <Play className="h-3 w-3" />
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => deleteSearch(search.id)}
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default SavedSearches

