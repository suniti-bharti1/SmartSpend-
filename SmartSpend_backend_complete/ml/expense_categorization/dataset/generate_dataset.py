"""
Generates a synthetic expense-categorization dataset with Indian merchants.
Output: expenses.csv (columns: description, category) in the same folder as this script.

Run from the SmartSpend root:
    python ml/expense_categorization/dataset/generate_dataset.py
"""
import os
import random

import pandas as pd

random.seed(42)

ROWS_PER_CATEGORY = 250

MERCHANTS = {
    "Food": [
        "Swiggy", "Zomato", "Dominos", "McDonalds", "KFC", "Starbucks", "Chaayos",
        "Haldirams", "Barbeque Nation", "Cafe Coffee Day", "Behrouz Biryani", "Faasos",
        "Pizza Hut", "Burger King", "Subway", "Wow Momo",
    ],
    "Groceries": [
        "BigBasket", "Blinkit", "Zepto", "DMart", "Reliance Fresh", "Swiggy Instamart",
        "More Supermarket", "Natures Basket", "JioMart", "Spencers", "Kirana Store",
        "Fresh Vegetables", "Milk Dairy",
    ],
    "Transport": [
        "Uber", "Ola Cabs", "Rapido", "Indian Oil", "HP Petrol Pump", "Bharat Petroleum",
        "FASTag Recharge", "Delhi Metro", "Namma Metro", "BluSmart", "Shell Petrol",
        "Auto Rickshaw", "Parking Fee",
    ],
    "Shopping": [
        "Amazon", "Flipkart", "Myntra", "Ajio", "Nykaa", "Decathlon", "Croma",
        "Reliance Digital", "Meesho", "Lifestyle Stores", "Westside", "Pantaloons",
        "Zara", "H&M", "Tata Cliq",
    ],
    "Bills & Utilities": [
        "Jio Recharge", "Airtel Postpaid", "Vi Prepaid", "BSNL Broadband", "Tata Power",
        "BESCOM Electricity", "Adani Electricity", "Indane Gas", "Tata Play DTH",
        "ACT Fibernet", "Water Bill", "Mahanagar Gas", "Airtel Xstream Fiber",
    ],
    "Entertainment": [
        "Netflix", "Spotify", "BookMyShow", "Hotstar", "Amazon Prime", "PVR Cinemas",
        "INOX", "Sony LIV", "YouTube Premium", "Steam Games", "Zee5", "Gaana Plus",
    ],
    "Health": [
        "Apollo Pharmacy", "PharmEasy", "Tata 1mg", "Practo", "Medplus", "Cult.fit",
        "Fortis Hospital", "Dr Lal PathLabs", "Netmeds", "Max Healthcare", "Dental Clinic",
        "Gym Membership",
    ],
    "Rent": [
        "House Rent", "Rent Payment", "PG Rent", "Flat Rent", "Monthly Rent",
        "Society Maintenance", "Rent to Landlord", "Room Rent", "NoBroker Rent",
        "Rent Ramesh", "Rent Suresh", "Rent Mrs Sharma",
    ],
    "Travel": [
        "IRCTC", "MakeMyTrip", "Goibibo", "IndiGo Airlines", "Air India", "RedBus",
        "OYO Rooms", "Cleartrip", "Booking.com", "Vistara", "EaseMyTrip", "Airbnb",
        "Treebo Hotels",
    ],
    "Other": [
        "ATM Withdrawal", "Cash Withdrawal", "Transfer to Friend", "Misc Payment",
        "Bank Charges", "LIC Premium", "Insurance Premium", "Cash Deposit",
        "Donation", "Mutual Fund SIP", "Loan EMI", "Credit Card Payment",
        "Sent to Self",
    ],
}

EXTRA = {
    "Food": ["Chai Sutta Bar", "Chai Point", "Restaurant Bill", "Dinner", "Lunch", "Breakfast",
             "Cafe", "Bakery", "Biryani", "Street Food", "Ice Cream Parlour", "Juice Centre"],
    "Groceries": ["Groceries", "Vegetables", "Fruits", "Supermarket", "Provision Store",
                  "Grocery Order", "Fresh Mart"],
    "Transport": ["Ola ride", "Uber ride", "Cab fare", "Taxi", "Auto fare", "Petrol", "Diesel",
                  "Bus ticket", "Metro card recharge", "Toll", "Airport cab", "Ride to office"],
    "Shopping": ["Amazon order", "Flipkart order", "Clothes", "Shoes", "Electronics",
                 "Mobile accessories", "Online order", "Gift purchase", "Furniture"],
    "Bills & Utilities": ["Electricity bill", "Mobile recharge", "Broadband bill", "Gas bill",
                          "Water bill", "Postpaid bill", "DTH recharge", "Internet bill"],
    "Entertainment": ["Movie tickets", "Concert tickets", "Gaming", "OTT subscription",
                      "Music subscription", "Amusement Park"],
    "Health": ["Doctor consultation fee", "Doctor visit", "Clinic", "Medicines", "Lab test",
               "Hospital bill", "Dental checkup", "Eye checkup", "Health checkup"],
    "Rent": ["Monthly Rent", "Rent for March", "Rent transfer", "Rent advance", "Deposit rent"],
    "Travel": ["Flight ticket", "Train ticket", "Hotel booking", "Holiday package",
               "Bus booking", "Resort booking", "Visa fee"],
    "Personal Care": ["Salon", "Salon haircut", "Haircut", "Barber", "Spa", "Beauty Parlour",
                      "Urban Company", "Massage", "Grooming"],
    "Other": ["Paid to Rahul", "Paid to Amit", "Sent to Priya", "Transfer to Neha",
              "Paid to Rohan", "Monthly SIP", "SIP Investment", "Mutual Fund", "Zerodha", "Groww",
              "Monthly transfer", "Gift to friend"],
}

for _cat, _items in EXTRA.items():
    MERCHANTS.setdefault(_cat, []).extend(_items)

PREFIXES = ["", "", "UPI-", "UPI/", "POS ", "PAYTM*", "PhonePe ", "GPay ", "NEFT-", "IMPS-", "UPI/DR/"]
SUFFIXES = [
    "", "", "", " Mumbai", " Delhi", " Bangalore", " Pune", " Jaipur", " India",
    " Pvt Ltd", " Online", " Order", " Payment", " Txn",
]
BANK_HANDLES = ["@okhdfcbank", "@ybl", "@paytm", "@oksbi", "@icici", "@axl"]


def random_ref():
    return random.choice([
        "",
        f" {random.randint(100000, 99999999)}",
        f" Ref {random.randint(1000000, 999999999)}",
        f" #{random.randint(1000, 99999)}",
        f" {random.randint(10, 9999)}",
    ])


def random_case(text):
    return random.choice([text, text, text.upper(), text.lower()])


def make_description(merchant):
    desc = random.choice(PREFIXES) + random_case(merchant) + random.choice(SUFFIXES) + random_ref()
    if random.random() < 0.15:
        desc += random.choice(BANK_HANDLES)
    return desc.strip()


def generate():
    rows = []
    for category, merchants in MERCHANTS.items():
        seen = set()
        attempts = 0
        while len(seen) < ROWS_PER_CATEGORY and attempts < 20000:
            seen.add(make_description(random.choice(merchants)))
            attempts += 1
        rows.extend((desc, category) for desc in sorted(seen))

    df = pd.DataFrame(rows, columns=["description", "category"])
    return df.sample(frac=1, random_state=42).reset_index(drop=True)


if __name__ == "__main__":
    df = generate()
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "expenses.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved {len(df)} rows to {out_path}")
    print(df["category"].value_counts())
    print(df.head(10))
