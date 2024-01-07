# recommendations/apriori_util.py
from apyori import apriori
from products.models import BinaryMatrix  # Update the import based on your actual app structure

def get_transactions_data():
    # Query binary matrix data from the database and convert it to the required format
    binary_matrix_entries = BinaryMatrix.objects.all()

    # Assuming the columns are 'Nike_Air_Jordan_1_Mid', 'Nike_Air_Jordan_2_Mid', 'Nike_Air_Jordan_3_Mid'
    data = [
        [
            'Nike_Air_Jordan_1_Mid' if entry.Nike_Air_Jordan_1_Mid else '',
            'Nike_Air_Jordan_2_Mid' if entry.Nike_Air_Jordan_2_Mid else '',
            'Nike_Air_Jordan_3_Mid' if entry.Nike_Air_Jordan_3_Mid else '',
        ]
        for entry in binary_matrix_entries
    ]

    return data

def run_apriori():
    transactions_data = get_transactions_data()

    # Run Apriori algorithm
    results = list(apriori(transactions_data, min_support=0.2, min_confidence=0.5))

    return results
