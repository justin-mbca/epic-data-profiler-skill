import os
import tempfile
from skill.epic_data_profiler import profile_epic_data

def test_profile_epic_data_csv():
    # Create a temporary CSV file
    data = """PatientID,Age,LabResult\n1,25,4.2\n2,30,9.8\n3,,0.1\n4,99,\n"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='w') as f:
        f.write(data)
        file_path = f.name
    result = profile_epic_data(file_path)
    os.unlink(file_path)
    assert 'summary' in result
    assert 'PatientID' in result['summary']
    assert result['summary']['Age']['missing'] == 1
    assert result['summary']['LabResult']['missing'] == 1
    assert result['errors'] == []

def test_profile_epic_data_json():
    # Create a temporary JSON file
    data = '[{"PatientID": 1, "Age": 25, "LabResult": 4.2}, {"PatientID": 2, "Age": 30, "LabResult": 9.8}]'
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w') as f:
        f.write(data)
        file_path = f.name
    result = profile_epic_data(file_path)
    os.unlink(file_path)
    assert 'summary' in result
    assert 'PatientID' in result['summary']
    assert result['errors'] == []

def test_profile_epic_data_missing_file():
    result = profile_epic_data('nonexistent.csv')
    assert result['errors']

def test_profile_epic_data_missing_column():
    data = """PatientID,Age\n1,25\n2,30\n"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='w') as f:
        f.write(data)
        file_path = f.name
    result = profile_epic_data(file_path, columns_to_profile=['PatientID', 'LabResult'])
    os.unlink(file_path)
    assert 'Missing columns' in result['errors'][0]
    assert 'PatientID' in result['summary']
    assert 'LabResult' not in result['summary']

def test_profile_epic_data_parquet():
    import pandas as pd
    df = pd.DataFrame({
        'PatientID': [1, 2, 3],
        'Age': [25, 30, None],
        'LabResult': [4.2, 9.8, 0.1]
    })
    with tempfile.NamedTemporaryFile(delete=False, suffix='.parquet') as f:
        file_path = f.name
    df.to_parquet(file_path)
    result = profile_epic_data(file_path)
    os.unlink(file_path)
    assert 'summary' in result
    assert 'PatientID' in result['summary']
    assert result['summary']['Age']['missing'] == 1
    assert result['errors'] == []
