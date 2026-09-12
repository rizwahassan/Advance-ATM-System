import tkinter as tk
from tkinter import messagebox
from database import ATMDatabase
from face_auth import FaceAuthenticator
class ATMDashboard(tk.Toplevel):
    def __init__(self, parent, user_doc_id, user_data):
        super().__init__(parent)
        self.parent = parent
        self.user_doc_id = user_doc_id
        self.user_data = user_data
        
        self.title(f"ATM Dashboard - Welcome, {user_data.get('name', 'User')}")
        self.geometry("500x400")
        self.db = ATMDatabase(user_doc_id=user_doc_id)

        tk.Label(self, text=f"🏦 Welcome, {user_data.get('name', 'User')}", font=("Arial", 16, "bold")).pack(pady=15)
        
        tk.Button(self, text="Check Balance", width=25, font=("Arial", 12), command=self.check_balance).pack(pady=5)
        tk.Button(self, text="Deposit Money", width=25, font=("Arial", 12), command=self.deposit_money).pack(pady=5)
        tk.Button(self, text="Withdraw Money", width=25, font=("Arial", 12), command=self.withdraw_money).pack(pady=5)
        tk.Button(self, text="Change PIN", width=25, font=("Arial", 12), command=self.change_pin_window).pack(pady=5)

        tk.Button(self, text="Logout", width=15, bg="red", fg="white", font=("Arial", 10), command=self.logout).pack(pady=20)

    def logout(self):
        self.destroy()
        self.parent.deiconify()

    def check_balance(self):
        data = self.db.get_data()
        messagebox.showinfo("Balance", f"Current Balance: Rs. {data.get('balance', 0.0):,.2f}")

    def deposit_money(self):
        top = tk.Toplevel(self)
        top.title("Deposit")
        top.geometry("300x200")
        tk.Label(top, text="Enter Amount to Deposit:", font=("Arial", 10)).pack(pady=10)
        entry = tk.Entry(top, font=("Arial", 12))
        entry.pack(pady=5)

        def submit():
            try:
                amt = float(entry.get())
                if amt <= 0: raise ValueError()
                data = self.db.get_data()
                new_bal = data['balance'] + amt
                self.db.update_balance(new_bal, f"Deposited Rs. {amt:,.2f}")
                messagebox.showinfo("Success", f"Deposited Rs. {amt:,.2f} successfully!")
                top.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount.")

        tk.Button(top, text="Confirm Deposit", command=submit).pack(pady=10)

    def withdraw_money(self):
        top = tk.Toplevel(self)
        top.title("Withdraw")
        top.geometry("300x200")
        tk.Label(top, text="Enter Amount to Withdraw:", font=("Arial", 10)).pack(pady=10)
        entry = tk.Entry(top, font=("Arial", 12))
        entry.pack(pady=5)

        def submit():
            try:
                amt = float(entry.get())
                data = self.db.get_data()
                if amt <= 0 or amt > data['balance']:
                    raise ValueError()
                new_bal = data['balance'] - amt
                self.db.update_balance(new_bal, f"Withdrew Rs. {amt:,.2f}")
                messagebox.showinfo("Success", f"Withdrew Rs. {amt:,.2f} successfully!")
                top.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid amount or insufficient balance.")

        tk.Button(top, text="Confirm Withdrawal", command=submit).pack(pady=10)

    def change_pin_window(self):
        top = tk.Toplevel(self)
        top.title("Change PIN")
        top.geometry("300x250")
        tk.Label(top, text="New 4-Digit PIN:", font=("Arial", 10)).pack(pady=10)
        entry = tk.Entry(top, show="*", font=("Arial", 12))
        entry.pack(pady=5)

        def submit():
            npin = entry.get()
            if len(npin) == 4 and npin.isdigit():
                self.db.change_pin(npin)
                messagebox.showinfo("Success", "PIN changed successfully!")
                top.destroy()
            else:
                messagebox.showerror("Error", "PIN must be exactly 4 digits.")

        tk.Button(top, text="Update PIN", command=submit).pack(pady=10)


class CreateAccountWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Create New Account")
        self.geometry("400x350")
        self.db = ATMDatabase()
        self.face_auth = FaceAuthenticator()

        tk.Label(self, text="📝 Create New ATM Account", font=("Arial", 14, "bold")).pack(pady=15)

        tk.Label(self, text="Full Name:", font=("Arial", 10)).pack()
        self.name_entry = tk.Entry(self, font=("Arial", 11), width=25)
        self.name_entry.pack(pady=3)

        tk.Label(self, text="Create 4-Digit PIN:", font=("Arial", 10)).pack()
        self.pin_entry = tk.Entry(self, show="*", font=("Arial", 11), width=25)
        self.pin_entry.pack(pady=3)

        tk.Label(self, text="Initial Deposit Amount (Rs.):", font=("Arial", 10)).pack()
        self.bal_entry = tk.Entry(self, font=("Arial", 11), width=25)
        self.bal_entry.insert(0, "1000")
        self.bal_entry.pack(pady=3)

        self.face_var = tk.BooleanVar(value=True)
        self.face_check = tk.Checkbutton(self, text="Enable Face ID Authentication", variable=self.face_var, font=("Arial", 10))
        self.face_check.pack(pady=10)

        tk.Button(self, text="Register Account", bg="blue", fg="white", font=("Arial", 11, "bold"), command=self.register).pack(pady=10)

    def register(self):
        name = self.name_entry.get().strip()
        pin = self.pin_entry.get().strip()
        try:
            balance = float(self.bal_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid initial balance.")
            return

        if not name or len(pin) != 4 or not pin.isdigit():
            messagebox.showerror("Error", "Please enter a valid name and a 4-digit PIN.")
            return

        use_face = self.face_var.get()
        
        success, res, label_id = self.db.create_account(name, pin, balance, use_face)
        if not success:
            messagebox.showerror("Error", f"Failed to create account: {res}")
            return

        if use_face:
            messagebox.showinfo("Face Enrollment", "Next, we will capture your face for Face ID. Look straight at the camera.")
            face_success, face_msg = self.face_auth.register_new_face(label_id)
            if not face_success:
                messagebox.showwarning("Warning", f"Account created, but Face enrollment failed: {face_msg}")

        messagebox.showinfo("Success", f"Account created successfully for {name}!")
        self.destroy()
class ATMLoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure ATM System")
        self.root.geometry("400x320")
        self.db = ATMDatabase()
        self.face_auth = FaceAuthenticator()

        tk.Label(root, text="🏧 Secure ATM System", font=("Arial", 16, "bold")).pack(pady=20)

        tk.Label(root, text="Enter 4-Digit PIN:", font=("Arial", 11)).pack(pady=5)
        self.pin_entry = tk.Entry(root, show="*", font=("Arial", 14), justify="center")
        self.pin_entry.pack(pady=5)

        self.btn_login = tk.Button(root, text="Login to Account", bg="green", fg="white", font=("Arial", 12, "bold"), command=self.authenticate)
        self.btn_login.pack(pady=10)

        tk.Label(root, text="--- OR ---", font=("Arial", 10)).pack(pady=5)

        self.btn_create = tk.Button(root, text="Create New Account", bg="gray", fg="white", font=("Arial", 10), command=self.open_create_account)
        self.btn_create.pack(pady=5)

    def open_create_account(self):
        CreateAccountWindow(self.root)

    def authenticate(self):
        pin = self.pin_entry.get()
        if not pin:
            messagebox.showerror("Error", "Please enter your PIN.")
            return

        user_id, user_data = self.db.find_user_by_pin(pin)
        if not user_id:
            messagebox.showerror("Error", "Incorrect PIN or Account not found.")
            return

        if user_data.get("face_id_enabled", True):
            expected_label = user_data.get("face_label", 0)
            success, msg = self.face_auth.verify_face(expected_label=expected_label)
            if not success:
                messagebox.showerror("Access Denied", f"Face verification failed: {msg}")
                return

        messagebox.showinfo("Access Granted", f"Welcome back, {user_data.get('name')}!")
        self.root.withdraw()
        ATMDashboard(self.root, user_id, user_data)

if __name__ == "__main__":
    root = tk.Tk()
    app = ATMLoginApp(root)
    root.mainloop()
