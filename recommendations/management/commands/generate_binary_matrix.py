from django.core.management.base import BaseCommand
from products.models import BinaryMatrix
from recommendations.models import Result  # Assuming 'Result' is the model in the 'recommendations' app
import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules

class Command(BaseCommand):
    help = 'Generate results for Apriori algorithm'

    def handle(self, *args, **options):
        # Fetch binary matrix from the BinaryMatrix model
        binary_matrix_query = BinaryMatrix.objects.all()
        binary_matrix_data = list(binary_matrix_query.values())

        # Convert the binary matrix data to a DataFrame
        df = pd.DataFrame(binary_matrix_data)

        # Ensure 'id' is part of the DataFrame
        if 'id' in df.columns:
            # Extract product columns dynamically
            product_columns = ['Nike_Air_Jordan_1_Mid', 'Nike_Air_Jordan_2_Mid', 'Nike_Air_Jordan_3_Mid']

            # Apply Apriori algorithm
            frequent_itemsets = apriori(df[product_columns], min_support=0.01, use_colnames=True)

            # Generate association rules
            rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.2)

            # Save the association rules to the 'Result' model
            Result.objects.bulk_create([Result(
                antecedent=str(row['antecedents']),
                consequent=str(row['consequents']),
                support=row['support'],
                confidence=row['confidence']
            ) for _, row in rules.iterrows()])

            self.stdout.write(self.style.SUCCESS('Results generated successfully.'))
        else:
            print("Warning: 'id' not found in the DataFrame.")
