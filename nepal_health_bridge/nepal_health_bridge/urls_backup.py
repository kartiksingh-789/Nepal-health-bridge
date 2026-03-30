from django.contrib import admin
from django.urls import path, include          # ← include added
from django.conf import settings
from django.conf.urls.static import static
from directory import views

urlpatterns = [
    path("admin/", admin.site.urls),

    # ──────────────────────────────────────────────
    # 🆕 PHARMACY — all pharmacy URLs under /pharmacy/
    # ──────────────────────────────────────────────
    path("pharmacy/", include("pharmacy.urls")),

    # ──────────────────────────────────────────────
    # LANDING & PUBLIC
    # ──────────────────────────────────────────────
    path("", views.landing_page, name="landing"),
    path("doctors/", views.doctor_list, name="doctor_list"),

    # ──────────────────────────────────────────────
    # PATIENT AUTH
    # ──────────────────────────────────────────────
    path("patient/login/",     views.patient_login,    name="patient_login"),
    path("patient/logout/",    views.patient_logout,   name="patient_logout"),
    path("patient/register/",  views.patient_register, name="patient_register"),

    # ──────────────────────────────────────────────
    # PATIENT DASHBOARD
    # ──────────────────────────────────────────────
    path("patient/dashboard/",          views.patient_dashboard,         name="patient_dashboard"),
    path("patient/appointments/",       views.patient_my_appointments,   name="patient_my_appointments"),
    path("patient/medical-history/",    views.patient_medical_history,   name="patient_medical_history"),
    path("patient/profile/",            views.patient_profile,           name="patient_profile"),
    path("patient/prescription/<int:appointment_id>/", views.patient_view_prescription, name="patient_view_prescription"),
    path("patient/coming-soon/",        views.coming_soon,               name="patient_coming_soon"),

    # ──────────────────────────────────────────────
    # APPOINTMENT BOOKING FLOW
    # ──────────────────────────────────────────────
    path("patient/select-hospital/",            views.select_hospital,   name="select_hospital"),
    path("patient/select-department/",          views.select_department, name="select_department"),
    path("patient/select-doctor/",              views.select_doctor,     name="select_doctor"),
    path("patient/booking-medical-history/",    views.medical_history,   name="medical_history"),
    path("patient/contact-info/",               views.contact_info,      name="contact_info"),
    path("patient/payment/",                    views.payment_page,      name="payment_page"),
    path("patient/confirmation/",               views.confirmation_page, name="confirmation_page"),

    # ──────────────────────────────────────────────
    # HOSPITAL & ADMIN LOGIN
    # ──────────────────────────────────────────────
    path("hospital/portal/",         views.hospital_login,    name="hospital_login"),
    path("hospital/admin-login/",    views.admin_login,       name="admin_login"),
    path("hospital/admin-register/", views.admin_register,    name="admin_register"),
    path("hospital/admin-logout/",   views.admin_logout,      name="admin_logout"),

    # ──────────────────────────────────────────────
    # DOCTOR AUTH & DASHBOARD
    # ──────────────────────────────────────────────
    path("hospital/doctor-login/",   views.doctor_login,      name="doctor_login"),
    path("hospital/doctor-logout/",  views.doctor_logout,     name="doctor_logout"),
    path("doctor/dashboard/",        views.doctor_dashboard,  name="doctor_dashboard"),
    path("doctor/patient-details/",  views.patient_details,   name="patient_details"),
    path("doctor/prescription/",     views.prescription_page, name="prescription_page"),
    path("doctor/patients/",         views.doctor_patient_list,              name="doctor_patient_list"),
    path("doctor/write-prescription/", views.doctor_write_prescription_list, name="doctor_write_prescription_list"),
    path("doctor/schedule/",         views.doctor_schedule,   name="doctor_schedule"),
    path("doctor/appointments/<int:pk>/close/", views.doctor_close_appointment, name="doctor_close_appointment"),
    path("doctor/profile/",          views.doctor_profile,    name="doctor_profile"),

    # ──────────────────────────────────────────────
    # HOSPITAL ADMIN DASHBOARD
    # ──────────────────────────────────────────────
    path("hospital/admin-dashboard/", views.hospital_admin_dashboard, name="hospital_admin_dashboard"),

    # ──────────────────────────────────────────────
    # ADMIN — APPOINTMENTS
    # ──────────────────────────────────────────────
    path("hospital/admin/appointments/",                          views.admin_manage_appointments, name="admin_manage_appointments"),
    path("hospital/admin/appointments/<int:pk>/status/<str:status>/", views.appointment_update_status, name="appointment_update_status"),
    path("hospital/admin/appointments/<int:pk>/detail/",          views.admin_appointment_detail,  name="admin_appointment_detail"),

    # ──────────────────────────────────────────────
    # ADMIN — DOCTORS
    # ──────────────────────────────────────────────
    path("hospital/admin/doctors/",              views.admin_manage_doctors, name="admin_manage_doctors"),
    path("hospital/admin/doctors/add/",          views.doctor_add,           name="doctor_add"),
    path("hospital/admin/doctors/edit/<int:pk>/",   views.doctor_edit,       name="doctor_edit"),
    path("hospital/admin/doctors/delete/<int:pk>/", views.doctor_delete,     name="doctor_delete"),

    # ──────────────────────────────────────────────
    # ADMIN — DEPARTMENTS
    # ──────────────────────────────────────────────
    path("hospital/admin/departments/",              views.admin_manage_departments, name="admin_manage_departments"),
    path("hospital/admin/departments/add/",          views.department_add,           name="department_add"),
    path("hospital/admin/departments/edit/<int:pk>/",   views.department_edit,       name="department_edit"),
    path("hospital/admin/departments/delete/<int:pk>/", views.department_delete,     name="department_delete"),

    # ──────────────────────────────────────────────
    # ADMIN — INBOX / CONTACTS
    # ──────────────────────────────────────────────
    path("hospital/admin/contacts/",                  views.admin_patient_contacts,  name="admin_patient_contacts"),
    path("hospital/admin/contacts/<int:pk>/read/",    views.inquiry_mark_read,       name="inquiry_mark_read"),
    path("hospital/admin/contacts/<int:pk>/resolved/", views.inquiry_mark_resolved,  name="inquiry_mark_resolved"),
    path("hospital/admin/patient-directory/",         views.admin_patient_directory, name="admin_patient_directory"),

    # ──────────────────────────────────────────────
    # ADMIN — REPORTS & BILLING
    # ──────────────────────────────────────────────
    path("hospital/admin/reports/", views.admin_reports_billing, name="admin_reports_billing"),

] + static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT) \
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)