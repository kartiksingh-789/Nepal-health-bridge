# 🇳🇵 🏥 ℕ𝕖𝕡𝕒𝕝 ℍ𝕖𝕒𝕝𝕥𝕙 𝔹𝕣𝕚𝕕𝕘𝕖 🏥 🇳🇵

[![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Operational-brightgreen?style=for-the-badge)](https://github.com/kartiksingh-789/Nepal-health-bridge)

---

## 🌟 **Overview**

**Nepal Health Bridge** is a comprehensive, multi-layered healthcare management ecosystem designed specifically to bridge the gap between patients, doctors, and hospitals in Nepal. It offers an integrated platform for medical consultations, appointment booking, medical history tracking, and a fully functional online pharmacy.

---

## ✨ **Core Modules**

### 🛌 **Patient Portal**
- **Smart Booking**: Seamless appointment scheduling with hospital, department, and doctor selection.
- **Medical Dashboard**: Track appointments, view current prescriptions, and access medical history.
- **Profile Management**: Maintain personal health records and contact information.
- **Direct Communication**: Easy contact with hospital administrations for inquiries.

### 👨‍⚕️ **Doctor Portal**
- **Live Schedule**: Real-time view of daily and upcoming appointments.
- **Digital Prescriptions**: Create and manage prescriptions directly through the dashboard.
- **Patient Statistics**: Quick access to patient details and medical backgrounds.
- **Profile Customization**: Update specializations and availability.

### 🏥 **Hospital Administration**
- **Resource Management**: Complete control over hospital departments and doctors (Add/Edit/Delete).
- **Appointment Control**: Manage, update, and track all bookings in real-time.
- **Reports & Billing**: Generate comprehensive reports and handle billing operations.
- **Inquiry Inbox**: Resolution-based tracking of patient queries.

### 🛒 **Integrated Pharmacy**
- **Medical Storefront**: Browse medical products with advanced filtering.
- **AJAX-Powered Cart**: Real-time cart management without page reloads.
- **Smart Wishlist**: Save essential items for later with a single click.
- **Order Tracking**: Comprehensive view of past and pending medicine orders.

---

## 🛠️ **Technology Stack**

| Technology | Usage |
| :--- | :--- |
| **Python 3.x** | Core Programming Language |
| **Django** | Robust Web Framework |
| **REST Framework** | API Architecture |
| **NumPy & Scikit-learn** | Backend Data/AI Analysis |
| **SQLite3** | Efficient Local Database |
| **HTML5 / CSS3 / JS** | Responsive & Dynamic UI |
| **AJAX / Fetch API** | Seamless Frontend Interactions |

---

## 🚀 **Installation & Setup**

Ensure you have Python installed. Follow these steps to get the project running locally:

### 1. Clone the Repository
```bash
git clone https://github.com/kartiksingh-789/Nepal-health-bridge.git
cd Nepal-health-bridge
```

### 2. Set Up Virtual Environment (Recommended)
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r nepal_health_bridge/requirements.txt
```

### 4. Database Migrations
```bash
cd nepal_health_bridge
python manage.py makemigrations
python manage.py migrate
```

### 5. Run the Server
```bash
python manage.py runserver
```

Open your browser and navigate to `http://127.0.0.1:8000/`.

---

## 📂 **Project Directory Structure**

```text
Nepal-health-bridge/
├── nepal_health_bridge/        # Core Django Project
│   ├── directory/             # Core Management (Patients/Doctors/Apps)
│   ├── pharmacy/              # Medical Store & E-commerce Logic
│   ├── nepal_health_bridge/   # Settings & Base URLs
│   ├── static/                # Global CSS/JS Assets
│   ├── media/                 # Uploaded Images & Prescriptions
│   ├── db.sqlite3             # Database
│   └── manage.py              # Execution Script
├── speed_up_animation.py      # Utility Scripts
└── README.md                  # Project Documentation
```

---

## 📜 **License**
This project is licensed under the MIT License.

## ✉️ **Contact**
**Developer:** Kartik Singh  
**GitHub:** [@kartiksingh-789](https://github.com/kartiksingh-789)

---
*Developed with ❤️ to improve healthcare accessibility in Nepal.*
