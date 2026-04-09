import pandas as pd

data = {
    'PatientID': [1, 2, 3, 4],
    'Age': [25, 30, None, 99],
    'LabResult': [4.2, 9.8, 0.1, None]
}
df = pd.DataFrame(data)
df.to_parquet('sample_epic.parquet')
print('sample_epic.parquet created.')
