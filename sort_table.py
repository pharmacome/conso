import sys

import pandas as pd

if __name__ == '__main__':
    df = pd.read_csv(sys.argv[1], sep='\t')
    df.sort_values(list(df.columns)).to_csv(sys.argv[1], sep='\t', index=False)
