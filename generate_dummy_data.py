import csv
from faker import Faker
import random
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()

# Define the number of rows you want to generate
num_rows = 10000  # You can increase this number as needed

# Define the CSV file name
csv_file = 'dummy_data.csv'

# Define the categories and corresponding keywords (for more realistic data)
categories = {
    'Groceries': ['Supermarket', 'Grocery Store', 'Market'],
    'Rent': ['Rent', 'Apartment', 'Housing'],
    'Utilities': ['Electricity', 'Water', 'Gas', 'Internet'],
    'Transport': ['Taxi', 'Bus', 'Train', 'Uber'],
    'Entertainment': ['Cinema', 'Concert', 'Theater', 'Netflix'],
    'Healthcare': ['Pharmacy', 'Doctor', 'Hospital'],
    'Food Delivery': ['UberEats', 'Deliveroo', 'GrubHub'],
    'Savings': ['Savings Account', 'Deposit'],
    'Clothing': ['Clothing Store', 'Fashion', 'Apparel'],
    'Restaurants': ['Restaurant', 'Cafe', 'Diner']
}

# Function to generate random transactions
def generate_transaction():
    category = random.choice(list(categories.keys()))
    description = random.choice(categories[category])
    amount = round(random.uniform(5.00, 200.00), 2)  # Random amount between 5 and 200
    date = fake.date_between(start_date='-2y', end_date='today')  # Random date in the last 2 years
    user_id = random.randint(1, 10)  # Assume 10 different users
    return [user_id, date, amount, category, description]

# Write to the CSV file
with open(csv_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['User ID', 'Date', 'Amount', 'Category', 'Description'])  # CSV header

    for _ in range(num_rows):
        writer.writerow(generate_transaction())

print(f'Dummy data generated and saved to {csv_file}')
