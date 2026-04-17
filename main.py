import sqlite3
import time
from functools import wraps
import datetime
import random

# ====================== DECORATOR ======================
def timer_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"[DECORATOR] {func.__name__} ishlashi: {end - start:.4f} soniya")
        return result
    return wrapper

# ====================== OOP CLASS ======================
class BankAccount:
    def __init__(self, account_holder):
        self._account_holder = account_holder
        self._balance = 0.0
        self._account_number = f"BA{random.randint(100000, 999999)}"
        self._create_db()

    @property
    def account_holder(self):
        return self._account_holder

    @account_holder.setter
    def account_holder(self, value):
        if len(str(value).strip()) < 3:
            raise ValueError("Ism kamida 3 harfdan iborat bo'lishi kerak!")
        self._account_holder = value
        print(f"Ism yangilandi: {value}")

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if value < 0:
            raise ValueError("Balans manfiy bo'lishi mumkin emas!")
        self._balance = value

    def _create_db(self):
        conn = sqlite3.connect("bank.db")
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            account_number TEXT,
            transaction_type TEXT,
            amount REAL,
            timestamp TEXT,
            balance_after REAL
        )''')
        conn.commit()
        conn.close()

    @timer_decorator
    def deposit(self, amount):
        if amount <= 0:
            print("Summa musbat bo'lishi kerak!")
            return
        self.balance += amount
        self._log_transaction("Deposit", amount)
        print(f"{amount} so'm kiritildi. Yangi balans: {self.balance} so'm")

    @timer_decorator
    def withdraw(self, amount):
        if amount <= 0:
            print("Summa musbat bo'lishi kerak!")
            return
        if amount > self.balance:
            print("Yetarli mablag' yo'q!")
            return
        self.balance -= amount
        self._log_transaction("Withdraw", amount)
        print(f"{amount} so'm yechildi. Yangi balans: {self.balance} so'm")

    def _log_transaction(self, trans_type, amount):
        conn = sqlite3.connect("bank.db")
        cursor = conn.cursor()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO transactions VALUES (NULL, ?, ?, ?, ?, ?)",
                       (self._account_number, trans_type, amount, now, self.balance))
        conn.commit()
        conn.close()

    @timer_decorator
    def show_history(self):
        conn = sqlite3.connect("bank.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions WHERE account_number = ? ORDER BY id DESC LIMIT 10",
                       (self._account_number,))
        rows = cursor.fetchall()
        conn.close()
        
        print(f"\n=== {self.account_holder} hisob tarixi ===")
        if not rows:
            print("Hozircha operatsiyalar yo'q.")
            return
        for row in rows:
            print(f"{row[4]} | {row[2]:<10} | {row[3]:>10} so'm | Balans: {row[5]} so'm")

    def info(self):
        print(f"\n=== Bank Hisobi Ma'lumotlari ===")
        print(f"Hisob raqami : {self._account_number}")
        print(f"Egasi         : {self.account_holder}")
        print(f"Balans        : {self.balance} so'm")

# ====================== MAIN ======================
if __name__ == "__main__":
    print("=== Python OOP Bank Tizimi ===\n")
    name = input("Ismingizni kiriting: ").strip()
    account = BankAccount(name)
    
    while True:
        print("\n1. Balansni ko'rish")
        print("2. Pul kiritish (Deposit)")
        print("3. Pul yechish (Withdraw)")
        print("4. Tarixni ko'rish")
        print("5. Ismni o'zgartirish")
        print("6. Chiqish")
        
        choice = input("\nTanlang (1-6): ").strip()
        
        if choice == "1":
            account.info()
        elif choice == "2":
            try:
                amt = float(input("Kiritiladigan summa: "))
                account.deposit(amt)
            except ValueError:
                print("Noto'g'ri summa!")
        elif choice == "3":
            try:
                amt = float(input("Yechildigan summa: "))
                account.withdraw(amt)
            except ValueError:
                print("Noto'g'ri summa!")
        elif choice == "4":
            account.show_history()
        elif choice == "5":
            new_name = input("Yangi ism: ").strip()
            try:
                account.account_holder = new_name
            except ValueError as e:
                print(e)
        elif choice == "6":
            print("Dastur tugatildi. Rahmat!")
            break
        else:
            print("Noto'g'ri tanlov!")
