rent = int(input("Enter your hostel/flat rent: "))
food = int(input("Enter total food cost: "))
electricity_units = int(input("Enter electricity units consumed: "))
charge_per_unit = int(input("Enter charge per unit: "))
persons = int(input("Enter number of persons living: "))
if persons <= 0:
    print("Number of persons must be greater than 0")
else:
    electricity_bill = electricity_units * charge_per_unit
    total_bill = rent + food + electricity_bill
    per_person = total_bill / persons
    print("\n----- BILL SUMMARY -----")
    print("Total Rent:", rent)
    print("Food Cost:", food)
    print("Electricity Bill:", electricity_bill)
    print("Total Bill:", total_bill)
    print("Each Person Pays:", round(per_person, 2))