import pandas as pd
data = [
    {"Name": "MacBook Pro M3", "Category": "Electronics", "Cost": 30000000, "Price": 45000000, "Qty": 20, "Weight": 1.5},
    {"Name": "Sony WH-1000XM5", "Category": "Electronics", "Cost": 5000000, "Price": 8000000, "Qty": 50, "Weight": 0.3},
    {"Name": "Levi's 501 Jeans", "Category": "Fashion", "Cost": 800000, "Price": 1500000, "Qty": 100, "Weight": 0.6},
    {"Name": "Dyson Vacuum V15", "Category": "Home", "Cost": 12000000, "Price": 18000000, "Qty": 10, "Weight": 2.5},
    {"Name": "Industrial Drill", "Category": "Industrial", "Cost": 2000000, "Price": 3500000, "Qty": 30, "Weight": 4.0}
]

df = pd.DataFrame(data)
df.to_excel("inventory_sample_en.xlsx", index=False)

print("✅ Created 'inventory_sample_en.xlsx' successfully!")