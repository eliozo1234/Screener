import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { Search, Filter } from 'lucide-react'

const SearchFilters = ({ onSearch, isLoading }) => {
  const [filters, setFilters] = useState({
    indices: ['sp500', 'eurostoxx600'],
    lookback_years: 5,
    threshold_pct: 50,
    countries: [],
    sectors: [],
    min_market_cap_usd: '',
    min_volume: '',
    sort_by: 'pct_of_high'
  })

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }))
  }

  const handleIndicesChange = (index, checked) => {
    setFilters(prev => ({
      ...prev,
      indices: checked 
        ? [...prev.indices, index]
        : prev.indices.filter(i => i !== index)
    }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    const searchParams = {
      ...filters,
      min_market_cap_usd: filters.min_market_cap_usd ? parseInt(filters.min_market_cap_usd) : 0,
      min_volume: filters.min_volume ? parseInt(filters.min_volume) : 0
    }
    onSearch(searchParams)
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Filter className="h-5 w-5" />
          Filtres de Recherche
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Indices */}
          <div className="space-y-3">
            <Label className="text-sm font-medium">Indices</Label>
            <div className="flex gap-4">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="sp500"
                  checked={filters.indices.includes('sp500')}
                  onCheckedChange={(checked) => handleIndicesChange('sp500', checked)}
                />
                <Label htmlFor="sp500">S&P 500</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="eurostoxx600"
                  checked={filters.indices.includes('eurostoxx600')}
                  onCheckedChange={(checked) => handleIndicesChange('eurostoxx600', checked)}
                />
                <Label htmlFor="eurostoxx600">Eurostoxx 600</Label>
              </div>
            </div>
          </div>

          {/* Période et Seuil */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="lookback">Période Lookback</Label>
              <Select 
                value={filters.lookback_years.toString()} 
                onValueChange={(value) => handleFilterChange('lookback_years', parseInt(value))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">1 an</SelectItem>
                  <SelectItem value="3">3 ans</SelectItem>
                  <SelectItem value="5">5 ans</SelectItem>
                  <SelectItem value="10">10 ans</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="threshold">Seuil (% du plus haut)</Label>
              <Input
                id="threshold"
                type="number"
                min="1"
                max="100"
                value={filters.threshold_pct}
                onChange={(e) => handleFilterChange('threshold_pct', parseInt(e.target.value))}
                placeholder="50"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="sort">Trier par</Label>
              <Select 
                value={filters.sort_by} 
                onValueChange={(value) => handleFilterChange('sort_by', value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="pct_of_high">% du plus haut</SelectItem>
                  <SelectItem value="market_cap">Capitalisation</SelectItem>
                  <SelectItem value="current_price">Prix actuel</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Filtres avancés */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="market_cap">Capitalisation min. (USD)</Label>
              <Input
                id="market_cap"
                type="number"
                value={filters.min_market_cap_usd}
                onChange={(e) => handleFilterChange('min_market_cap_usd', e.target.value)}
                placeholder="ex: 1000000000"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="volume">Volume min. quotidien</Label>
              <Input
                id="volume"
                type="number"
                value={filters.min_volume}
                onChange={(e) => handleFilterChange('min_volume', e.target.value)}
                placeholder="ex: 100000"
              />
            </div>
          </div>

          {/* Bouton de recherche */}
          <Button 
            type="submit" 
            className="w-full" 
            disabled={isLoading || filters.indices.length === 0}
          >
            <Search className="h-4 w-4 mr-2" />
            {isLoading ? 'Recherche en cours...' : 'Lancer la recherche'}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}

export default SearchFilters

