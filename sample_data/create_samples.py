import pandas as pd
import numpy as np

N = 1000
np.random.seed(42)
data = {
    'PatientID': np.arange(1, N+1),
    'Age': np.random.choice(list(range(18, 100)) + [None], N, p=[0.01]*82 + [0.18]),
    'LabResult': np.random.normal(loc=5, scale=2, size=N)
}
# Introduce some missing values
mask = np.random.rand(N) < 0.1
for col in ['Age', 'LabResult']:
    arr = np.array(data[col], dtype=object)
    arr[mask] = None
    data[col] = arr

df = pd.DataFrame(data)
df.to_csv('sample_data/sample_epic.csv', index=False)
df.to_json('sample_data/sample_epic.json', orient='records', lines=False)
df.to_parquet('sample_data/sample_epic.parquet')
print('Sample files created in sample_data/.')
