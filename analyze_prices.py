import pandas as pd

def analyze_price_data(file_path):
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            parts = line.strip().split('|')
            if len(parts) == 3:
                ticker = parts[0]
                adjusted_close = float(parts[1])
                high = float(parts[2])
                
                if high != 0:
                    pct_from_high = ((adjusted_close - high) / high) * 100
                    data.append({
                        'ticker': ticker,
                        'adjusted_close': adjusted_close,
                        'high': high,
                        'pct_from_high': pct_from_high
                    })
    
    df = pd.DataFrame(data)
    
    print("\nDistribution des pourcentages de baisse par rapport au plus haut:")
    print(df['pct_from_high'].describe())
    
    print("\nTickers avec pct_from_high > -10% (proches du plus haut):")
    print(df[df['pct_from_high'] >= -10])
    
    print("\nTickers avec pct_from_high <= -10% et > -20%:")
    print(df[(df['pct_from_high'] < -10) & (df['pct_from_high'] >= -20)])
    
    print("\nTickers avec pct_from_high <= -20%:")
    print(df[df['pct_from_high'] < -20])

if __name__ == "__main__":
    analyze_price_data('price_data.txt')

