from django.contrib import admin
from django.contrib.auth.hashers import make_password
from .models import Hospital, Department, Doctor, Patient, Appointment, Prescription, Inquiry, HospitalAdmin

@admin.register(Hospital)
class HospitalModelAdmin(admin.ModelAdmin):
    list_display  = ["name", "location", "rating", "created_at"]
    search_fields = ["name", "location"]

@admin.register(HospitalAdmin)
class HospitalAdminAdmin(admin.ModelAdmin):
    list_display  = ["username", "full_name", "email", "created_at"]
    search_fields = ["username", "full_name"]

    def save_model(self, request, obj, form, change):
        if obj.password and not obj.password.startswith("pbkdf2_"):
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display  = ["name", "head_doctor", "total_doctors", "status", "created_at"]
    list_filter   = ["status"]
    search_fields = ["name"]


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display  = ["unique_id", "full_name", "specialty", "department", "availability", "is_head"]
    list_filter   = ["availability", "department", "is_head"]
    search_fields = ["full_name", "unique_id", "specialty"]

    # ✅ Auto-hash password when saving via admin panel
    def save_model(self, request, obj, form, change):
        if obj.password and not obj.password.startswith("pbkdf2_"):
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display  = ["full_name", "email", "primary_phone", "blood_group", "city", "created_at"]
    list_filter   = ["gender", "blood_group", "has_disability"]
    search_fields = ["full_name", "email", "primary_phone"]

    # ✅ Auto-hash password when saving via admin panel
    def save_model(self, request, obj, form, change):
        if obj.password and not obj.password.startswith("pbkdf2_"):
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display  = ["patient", "doctor", "appointment_date", "appointment_time", "status"]
    list_filter   = ["status", "appointment_date"]
    search_fields = ["patient__full_name", "doctor__full_name", "reason_for_visit"]


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display  = ["appointment", "diagnosis", "follow_up", "created_at"]
    search_fields = ["appointment__patient__full_name", "diagnosis"]


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display  = ["name", "email", "phone", "status", "created_at"]
    list_filter   = ["status"]
    search_fields = ["name", "email", "message"]