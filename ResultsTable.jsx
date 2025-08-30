import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Download, ArrowUpDown, TrendingDown } from 'lucide-react'

const ResultsTable = ({ results, isLoading, searchParams }) => {
  const [sortField, setSortField] = useState('pct_of_high')
  const [sortDirection, setSortDirection] = useState('asc')

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('asc')
    }
  }

  const sortedResults = [...results].sort((a, b) => {
    let aValue = a[sortField]
    let bValue = b[sortField]
    
    if (typeof aValue === 'string') {
      aValue = aValue.toLowerCase()
      bValue = bValue.toLowerCase()
    }
    
    if (sortDirection === 'asc') {
      return aValue > bValue ? 1 : -1
    } else {
      return aValue < bValue ? 1 : -1
    }
  })

  const formatCurrency = (value, currency = 'USD') => {
    if (!value) return 'N/A'
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 2
    }).format(value)
  }

  const formatMarketCap = (value) => {
    if (!value) return 'N/A'
    if (value >= 1e12) return `${(value / 1e12).toFixed(1)}T`
    if (value >= 1e9) return `${(value / 1e9).toFixed(1)}B`
    if (value >= 1e6) return `${(value / 1e6).toFixed(1)}M`
    return value.toLocaleString()
  }

  const formatVolume = (value) => {
    if (!value) return 'N/A'
    if (value >= 1e6) return `${(value / 1e6).toFixed(1)}M`
    if (value >= 1e3) return `${(value / 1e3).toFixed(1)}K`
    return value.toLocaleString()
  }

  const exportToCSV = () => {
    const headers = [
      'Ticker', 'Nom', 'Pays', 'Secteur', 'Prix Actuel', 'Devise',
      '% du Plus Haut', 'Plus Haut', 'Date Plus Haut', 'Capitalisation',
      'Volume Moyen 30j', 'Bourse'
    ]
    
    const csvContent = [
      headers.join(','),
      ...sortedResults.map(row => [
        row.ticker,
        `"${row.name}"`,
        row.country,
        `"${row.sector}"`,
        row.current_price,
        row.currency,
        row.pct_of_high,
        row.lookback_high,
        row.lookback_high_date,
        row.market_cap || '',
        row.avg_volume_30d,
        row.exchange
      ].join(','))
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `screening_results_${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const SortableHeader = ({ field, children }) => (
    <TableHead 
      className="cursor-pointer hover:bg-muted/50 select-none"
      onClick={() => handleSort(field)}
    >
      <div className="flex items-center gap-1">
        {children}
        <ArrowUpDown className="h-3 w-3" />
      </div>
    </TableHead>
  )

  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-8">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            <span className="ml-2">Recherche en cours...</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <TrendingDown className="h-5 w-5" />
            Résultats ({results.length} actions trouvées)
          </CardTitle>
          {results.length > 0 && (
            <Button onClick={exportToCSV} variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Exporter CSV
            </Button>
          )}
        </div>
        {searchParams && (
          <div className="flex flex-wrap gap-2 text-sm text-muted-foreground">
            <Badge variant="secondary">
              Indices: {searchParams.indices?.join(', ')}
            </Badge>
            <Badge variant="secondary">
              Période: {searchParams.lookback_years} ans
            </Badge>
            <Badge variant="secondary">
              Seuil: ≤ {searchParams.threshold_pct}%
            </Badge>
          </div>
        )}
      </CardHeader>
      <CardContent>
        {results.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            Aucun résultat trouvé avec les critères sélectionnés.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <SortableHeader field="ticker">Ticker</SortableHeader>
                  <SortableHeader field="name">Nom</SortableHeader>
                  <SortableHeader field="country">Pays</SortableHeader>
                  <SortableHeader field="sector">Secteur</SortableHeader>
                  <SortableHeader field="current_price">Prix</SortableHeader>
                  <SortableHeader field="pct_of_high">% Plus Haut</SortableHeader>
                  <SortableHeader field="lookback_high">Plus Haut</SortableHeader>
                  <SortableHeader field="lookback_high_date">Date</SortableHeader>
                  <SortableHeader field="market_cap">Market Cap</SortableHeader>
                  <SortableHeader field="avg_volume_30d">Volume 30j</SortableHeader>
                </TableRow>
              </TableHeader>
              <TableBody>
                {sortedResults.map((stock, index) => (
                  <TableRow key={`${stock.ticker}-${index}`}>
                    <TableCell className="font-medium">{stock.ticker}</TableCell>
                    <TableCell className="max-w-[200px] truncate" title={stock.name}>
                      {stock.name}
                    </TableCell>
                    <TableCell>{stock.country}</TableCell>
                    <TableCell className="max-w-[150px] truncate" title={stock.sector}>
                      {stock.sector}
                    </TableCell>
                    <TableCell>
                      {formatCurrency(stock.current_price, stock.currency)}
                    </TableCell>
                    <TableCell>
                      <Badge 
                        variant={stock.pct_of_high <= 30 ? "destructive" : 
                                stock.pct_of_high <= 50 ? "secondary" : "outline"}
                      >
                        {stock.pct_of_high}%
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {formatCurrency(stock.lookback_high, stock.currency)}
                    </TableCell>
                    <TableCell>{stock.lookback_high_date}</TableCell>
                    <TableCell>{formatMarketCap(stock.market_cap)}</TableCell>
                    <TableCell>{formatVolume(stock.avg_volume_30d)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default ResultsTable

