import os

base_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Nepal Health Bridge</title>
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    
    <style>
        :root {{
            --sidebar-bg: #2c3e50;
            --primary-color: #0056b3;
            --bg-light: #f4f7f6;
            --text-dark: #2c3e50;
            --hover-bg: rgba(255,255,255,0.05);
        }}

        body {{ font-family: 'Inter', sans-serif; background-color: var(--bg-light); color: var(--text-dark); }}
        .wrapper {{ display: flex; min-height: 100vh; }}
        #sidebar {{ width: 280px; background: var(--sidebar-bg); color: #fff; position: fixed; height: 100vh; z-index: 100; }}
        .sidebar-brand {{ padding: 30px 20px; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.1); }}
        .sidebar-brand i {{ font-size: 2rem; color: #fff; margin-bottom: 10px; }}
        .sidebar-brand h5 {{ font-weight: 700; margin: 0; letter-spacing: 0.5px;}}
        .nav-components {{ padding: 20px 0; }}
        .nav-components li a {{ padding: 15px 25px; display: flex; align-items: center; gap: 15px; color: rgba(255,255,255,0.7); text-decoration: none; transition: all 0.3s; border-left: 4px solid transparent; }}
        .nav-components li a:hover, .nav-components li.active a {{ color: #fff; background: var(--hover-bg); border-left-color: #fff; }}
        .logout-link {{ color: #ff6b6b !important; margin-top: auto;}}
        #content {{ flex: 1; margin-left: 280px; padding: 40px; }}
        .top-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 40px; }}
        .admin-profile {{ display: flex; align-items: center; gap: 15px; background: white; padding: 10px 20px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); font-weight: 600; }}
        .admin-profile i {{ color: var(--primary-color); font-size: 1.2rem; }}
        .dashboard-card {{ background: white; border-radius: 12px; padding: 60px 40px; text-align: center; box-shadow: 0 5px 20px rgba(0,0,0,0.05); margin-top: 50px; }}
        .dashboard-card i.main-icon {{ font-size: 4.5rem; color: var(--primary-color); margin-bottom: 25px; opacity: 0.9; }}
        .dashboard-card h3 {{ font-weight: 700; margin-bottom: 15px; color: var(--text-dark); }}
    </style>
</head>
<body>
    <div class="wrapper">
        <nav id="sidebar">
            <div class="sidebar-brand">
                <i class="fa-solid fa-hospital"></i>
                <h5>Hospital Admin</h5>
                <span class="badge bg-light text-dark rounded-pill mt-2">Kathmandu Central</span>
            </div>
            <ul class="list-unstyled nav-components">
                <li class="{active_main}">
                    <a href="{{% url 'hospital_admin_dashboard' %}}"><i class="fa-solid fa-chart-line"></i> Main Dashboard</a>
                </li>
                <li class="{active_appointments}"><a href="{{% url 'admin_manage_appointments' %}}"><i class="fa-solid fa-calendar-check"></i> Manage Appointments</a></li>
                <li class="{active_doctors}"><a href="{{% url 'admin_manage_doctors' %}}"><i class="fa-solid fa-user-doctor"></i> Add / Manage Doctors</a></li>
                <li class="{active_departments}"><a href="{{% url 'admin_manage_departments' %}}"><i class="fa-solid fa-sitemap"></i> Manage Departments</a></li>
                <li class="{active_contacts}"><a href="{{% url 'admin_patient_contacts' %}}"><i class="fa-solid fa-address-book"></i> Patient Contacts</a></li>
                <li class="{active_reports}"><a href="{{% url 'admin_reports_billing' %}}"><i class="fa-solid fa-file-invoice"></i> Reports & Billing</a></li>
                
                <li style="margin-top: 40px;">
                    <a href="{{% url 'hospital_login' %}}" class="logout-link"><i class="fa-solid fa-power-off"></i> Logout</a>
                </li>
            </ul>
        </nav>
        <div id="content">
            <div class="top-header">
                <div>
                    <h2 class="fw-bold mb-0">{title}</h2>
                    <p class="text-muted">Hospital operations management.</p>
                </div>
                <div class="admin-profile">
                    <i class="fa-solid fa-user-shield"></i>
                    <span>Admin User</span>
                </div>
            </div>

            <div class="dashboard-card mx-auto" style="max-width: 800px;">
                <i class="{icon} main-icon"></i>
                <h3>{title} Module</h3>
                <p class="text-muted mb-4 fs-5">This module is currently in active development. All UI components for {title} will be accessible here soon.</p>
                <a href="{{% url 'hospital_admin_dashboard' %}}" class="btn btn-primary px-4 py-2 mt-2 fw-semibold">Back to Main Dashboard</a>
            </div>
        </div>
    </div>
</body>
</html>
"""

pages = [
    ("Manage Appointments", "fa-solid fa-calendar-check", "active_appointments", "admin_manage_appointments.html"),
    ("Add / Manage Doctors", "fa-solid fa-user-doctor", "active_doctors", "admin_manage_doctors.html"),
    ("Manage Departments", "fa-solid fa-sitemap", "active_departments", "admin_manage_departments.html"),
    ("Patient Contacts", "fa-solid fa-address-book", "active_contacts", "admin_patient_contacts.html"),
    ("Reports & Billing", "fa-solid fa-file-invoice", "active_reports", "admin_reports_billing.html"),
]

for title, icon, active_key, filename in pages:
    kwargs = {
        "title": title,
        "icon": icon,
        "active_main": "",
        "active_appointments": "",
        "active_doctors": "",
        "active_departments": "",
        "active_contacts": "",
        "active_reports": "",
    }
    kwargs[active_key] = "active"
    content = base_html.format(**kwargs)
    filepath = os.path.join(r"d:\nepal_health_bridge\nepal_health_bridge\directory\templates\directory", filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
