from app import db, Transaction, app
from datetime import datetime
import random

def generate_dummy_data():
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        # Define categories and some example descriptions
        categories = [
            'Food Delivery', 'Groceries', 'Healthcare', 'Entertainment', 'Transport', 
            'Utilities', 'Rent', 'Savings', 'Dining', 'Shopping', 'Travel', 'Gifts'
        ]
        descriptions = {
            'Food Delivery': ['Uber Eats', 'DoorDash', 'Grubhub'],
            'Groceries': ['Walmart', 'Kroger', 'Whole Foods', 'Trader Joe\'s'],
            'Healthcare': ['CVS Pharmacy', 'Walgreens', 'Doctor Visit', 'Dental'],
            'Entertainment': ['Netflix', 'Spotify', 'Movie Theater', 'Football Match', 'Concert'],
            'Transport': ['Uber', 'Lyft', 'Gas Station', 'Car Rental'],
            'Utilities': ['Electricity Bill', 'Water Bill', 'Internet Bill', 'Phone Bill'],
            'Rent': ['Monthly Rent', 'Home Insurance'],
            'Savings': ['Bank Deposit', 'Investment', 'Retirement Fund'],
            'Dining': ['Restaurant', 'Cafe', 'Bar'],
            'Shopping': ['Clothing Store', 'Electronics Store', 'Online Purchase'],
            'Travel': ['Airline', 'Hotel', 'Rental Car'],
            'Gifts': ['Gift Shop', 'Online Gifts']
        }

        # Generate a wide variety of transactions
        for i in range(300):
            category = random.choice(categories)
            description = random.choice(descriptions[category])
            transaction = Transaction(
                user_id=1,
                date=datetime(2023, random.randint(1, 12), random.randint(1, 28)),
                amount=random.uniform(-500, 1500),
                category=category,
                description=description
            )
            db.session.add(transaction)

        # Add specific transactions for football tickets and other notable transactions
        notable_transactions = [
            Transaction(user_id=1, date=datetime(2023, 5, 15), amount=-150.0, category='Entertainment', description='Football Match - Wigan Ath'),
            Transaction(user_id=1, date=datetime(2023, 6, 20), amount=-200.0, category='Entertainment', description='Football Match - MAN United'),
            Transaction(user_id=1, date=datetime(2023, 9, 10), amount=-120.0, category='Entertainment', description='Football Match - Arsenal'),
            Transaction(user_id=1, date=datetime(2023, 10, 12), amount=-100.0, category='Dining', description='Restaurant - Italian Bistro'),
            Transaction(user_id=1, date=datetime(2023, 11, 5), amount=-300.0, category='Travel', description='Airline - London to New York')
        ]
        
        for transaction in notable_transactions:
            db.session.add(transaction)

        db.session.commit()
        print("Extensive dummy data generated and saved to database")

if __name__ == '__main__':
    generate_dummy_data()

