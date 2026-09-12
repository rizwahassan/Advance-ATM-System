# 🏧 Biometric ATM System with Face Recognition & Firestore

A desktop ATM application built with Python, Tkinter, OpenCV, and Firebase Firestore. Features dual-factor authentication using a 4-digit PIN and facial recognition (LBPH Face Recognizer).

## 📌 Features
* **Dual-Factor Authentication:** Log in with a 4-digit PIN + live face verification.
* **Face Enrollment:** Captures facial samples via webcam using OpenCV and trains an LBPH model.
* **Firestore Cloud Storage:** Stores accounts, PINs, balances, and transaction history in Firebase.
* **ATM Dashboard:**
  * Check account balance
  * Deposit & withdraw funds
  * Update 4-digit PIN

## 📁 Project Structure
* `main_app.py` - Tkinter GUI application (Login, Registration, Dashboard)
* `database.py` - Firestore database connector & user data management
* `face_auth.py` - OpenCV face detection, model training, and verification
