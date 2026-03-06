import pandas as pd
from analysis_module import calculate_growth

df = pd.read_csv("data/cleaned_data.csv")

result = calculate_growth(df)

print(result.sort_values("growth_percent", ascending=False))