from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from datetime import date
from .models import Doctor, Department, Patient, Appointment, Prescription, Inquiry, HospitalAdmin, Hospital
from .symptom_classifier import predict_specialty
from django.views.decorators.cache import never_cache


# ═══════════════════════════════════════════════════════════════
# LANDING & PUBLIC
# ═══════════════════════════════════════════════════════════════

def landing_page(request):
    return render(request, "directory/landing.html")


def doctor_list(request):
    doctors = Doctor.objects.select_related("department").all()
    return render(request, "directory/doctor_list.html", {"doctors": doctors})


# ═══════════════════════════════════════════════════════════════
# HOSPITAL PORTAL — selects Admin or Doctor
# ═══════════════════════════════════════════════════════════════

def hospital_login(request):
    return render(request, "directory/hospital_portal.html")


# ═══════════════════════════════════════════════════════════════
# ADMIN AUTH
# ═══════════════════════════════════════════════════════════════

def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        if not username or not password:
            messages.error(request, "Please enter both username and password.")
        else:
            try:
                admin = HospitalAdmin.objects.get(username=username)
                if check_password(password, admin.password):
                    request.session["admin_id"]   = admin.id
                    request.session["admin_name"] = admin.full_name
                    request.session["admin_hospital_id"] = admin.hospital_id
                    return redirect("hospital_admin_dashboard")
                else:
                    messages.error(request, "Incorrect password.")
            except HospitalAdmin.DoesNotExist:
                messages.error(request, "No admin account found with this username.")

    storage = messages.get_messages(request)
    storage.used = True
    return render(request, "directory/admin_login.html")


def admin_logout(request):
    request.session.flush()
    return redirect("admin_login")


def admin_register(request):
    if request.method == "POST":
        full_name   = request.POST.get("full_name", "").strip()
        email       = request.POST.get("email", "").strip()
        username    = request.POST.get("username", "").strip()
        password    = request.POST.get("password", "").strip()
        hospital_id = request.POST.get("hospital_id")

        if not all([full_name, username, password, hospital_id]):
            messages.error(request, "Please fill in all required fields.")
        elif HospitalAdmin.objects.filter(username=username).exists():
            messages.error(request, "This username is already taken. Choose another.")
        else:
            try:
                hospital = get_object_or_404(Hospital, id=hospital_id)
                HospitalAdmin.objects.create(
                    hospital=hospital,
                    username=username,
                    password=password, # models.py auto-hashes on save
                    full_name=full_name,
                    email=email
                )
                messages.success(request, f"Admin account created for {hospital.name}! Please log in.")
                return redirect("admin_login")
            except Exception as e:
                messages.error(request, f"Registration failed: {str(e)}")

    hospitals = Hospital.objects.all().order_by("name")
    return render(request, "directory/admin_register.html", {"hospitals": hospitals})


# ═══════════════════════════════════════════════════════════════
# PATIENT AUTH
# ═══════════════════════════════════════════════════════════════

def patient_login(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        if not username or not password:
            messages.error(request, "Please enter both username and password.")
        else:
            try:
                patient = Patient.objects.get(username=username)
                if check_password(password, patient.password):
                    request.session["patient_id"]   = patient.id
                    request.session["patient_name"] = patient.full_name
                    return redirect("patient_dashboard")
                else:
                    messages.error(request, "Incorrect password. Please try again.")
            except Patient.DoesNotExist:
                messages.error(request, "No account found with this username.")

    storage = messages.get_messages(request)
    storage.used = True
    return render(request, "directory/patient_login.html")


def patient_logout(request):
    request.session.flush()
    return redirect("patient_login")


def patient_register(request):
    if request.method == "POST":
        step = int(request.POST.get("step", 1))
    else:
        # Clear registration session if 'clear' param is present
        if request.GET.get("clear") == "true":
            for key in list(request.session.keys()):
                if key.startswith("reg_"):
                    del request.session[key]
            return redirect("patient_register")
        step = int(request.GET.get("step", 1))

        for key, value in request.POST.items():
            if key not in ["csrfmiddlewaretoken", "step"]:
                request.session[f"reg_{key}"] = value

        if step < 4:
            return redirect(f"/patient/register/?step={step + 1}")

        try:
            Patient.objects.create(
                username            = request.session.get("reg_username"),
                email               = request.session.get("reg_email"),
                password            = make_password(request.session.get("reg_password")),
                primary_phone       = request.session.get("reg_primary_phone"),
                alternate_phone     = request.session.get("reg_alternate_phone", ""),
                full_name           = request.session.get("reg_full_name"),
                date_of_birth       = request.session.get("reg_date_of_birth"),
                gender              = request.session.get("reg_gender"),
                blood_group         = request.session.get("reg_blood_group"),
                nationality         = request.session.get("reg_nationality"),
                marital_status      = request.session.get("reg_marital_status"),
                country             = request.session.get("reg_country", "Nepal"),
                province            = request.session.get("reg_province"),
                district            = request.session.get("reg_district"),
                city                = request.session.get("reg_city"),
                ward_number         = request.session.get("reg_ward_number", ""),
                postal_code         = request.session.get("reg_postal_code", ""),
                full_address        = request.session.get("reg_full_address"),
                known_allergies     = request.session.get("reg_known_allergies", ""),
                chronic_conditions  = request.session.get("reg_chronic_conditions", ""),
                current_medications = request.session.get("reg_current_medications", ""),
                past_surgeries      = request.session.get("reg_past_surgeries", ""),
                has_disability      = request.session.get("reg_has_disability") == "on",
            )
            for key in list(request.session.keys()):
                if key.startswith("reg_"):
                    del request.session[key]

            messages.success(request, "Registration successful! Please log in.")
            return redirect("patient_login")

        except Exception as e:
            messages.error(request, f"Registration failed: {str(e)}")

    step = int(request.GET.get("step", 1))
    return render(request, "directory/patient_register.html", {
        "step": step,
        "reg_gender":         request.session.get("reg_gender", ""),
        "reg_blood_group":    request.session.get("reg_blood_group", ""),
        "reg_marital_status": request.session.get("reg_marital_status", ""),
        "reg_has_disability": request.session.get("reg_has_disability", ""),
    })


# ═══════════════════════════════════════════════════════════════
# PATIENT DASHBOARD
# ═══════════════════════════════════════════════════════════════

@never_cache
def patient_dashboard(request):
    if not request.session.get("patient_id"):
        return redirect("patient_login")

    patient_id = request.session["patient_id"]

    upcoming_count     = Appointment.objects.filter(patient_id=patient_id, status="upcoming").count()
    past_count         = Appointment.objects.filter(patient_id=patient_id, status="completed").count()
    prescription_count = Prescription.objects.filter(appointment__patient_id=patient_id).count()

    return render(request, "directory/patient_dashboard.html", {
        "patient_name":      request.session.get("patient_name", "Patient"),
        "upcoming_count":    upcoming_count,
        "past_count":        past_count,
        "prescription_count": prescription_count,
    })


@never_cache
def patient_my_appointments(request):
    if not request.session.get("patient_id"):
        return redirect("patient_login")

    patient_id = request.session["patient_id"]
    patient = get_object_or_404(Patient, id=patient_id)
    
    status_filter = request.GET.get("status")
    date_filter = request.GET.get("date")
    
    appointments = Appointment.objects.filter(patient_id=patient_id)
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    if date_filter:
        appointments = appointments.filter(appointment_date=date_filter)

    return render(request, "directory/my_appointments.html", {
        "appointments": appointments,
        "patient_name": request.session.get("patient_name", patient.full_name),
        "selected_status": status_filter,
        "selected_date": date_filter
    })


@never_cache
def patient_medical_history(request):
    if not request.session.get("patient_id"):
        return redirect("patient_login")
        
    patient_id = request.session["patient_id"]
    patient = get_object_or_404(Patient, id=patient_id)
    appointments = Appointment.objects.filter(patient_id=patient_id).select_related("doctor", "prescription")
    
    return render(request, "directory/patient_medical_history.html", {
        "patient": patient,
        "patient_name": request.session.get("patient_name", patient.full_name),
        "appointments": appointments
    })


@never_cache
def patient_profile(request):
    if not request.session.get("patient_id"):
        return redirect("patient_login")
        
    patient_id = request.session["patient_id"]
    patient = get_object_or_404(Patient, id=patient_id)
    
    return render(request, "directory/patient_profile.html", {
        "patient": patient,
        "patient_name": request.session.get("patient_name", patient.full_name)
    })

@never_cache
def coming_soon(request):
    """View to handle AI Symptom Analysis and display results."""
    query = request.GET.get("q", "").strip()
    results = []
    
    if query:
        # Get AI predictions
        results = predict_specialty(query)
        
        # For each result, find matching departments in the database
        for res in results:
            keywords = res["dept_keywords"]
            # Search for departments that match any of the keywords
            matching_depts = Department.objects.filter(status="active")
            from django.db.models import Q
            dept_query = Q()
            for kw in keywords:
                dept_query |= Q(name__icontains=kw)
            
            # Attaching matching departments to the result object
            res["matching_depts"] = matching_depts.filter(dept_query).select_related("hospital").distinct()

    return render(request, "directory/coming_soon.html", {
        "query": query,
        "results": results,
        "patient_name": request.session.get("patient_name", "Patient")
    })
        
# ═══════════════════════════════════════════════════════════════
# APPOINTMENT BOOKING FLOW
# ═══════════════════════════════════════════════════════════════

def select_hospital(request):
    # Determine distinct cities for the filter dropdown
    # We query the distinct locations from the Hospital model
    cities = Hospital.objects.values_list('location', flat=True).distinct().order_by('location')
    
    # Get the selected city from the GET parameters, if any
    selected_city = request.GET.get('city')
    
    if selected_city:
        hospitals = Hospital.objects.filter(location=selected_city)
    else:
        hospitals = Hospital.objects.all()
        
    context = {
        "hospitals": hospitals,
        "cities": cities,
        "selected_city": selected_city
    }
    return render(request, "directory/hospital_selection.html", context)


def select_department(request):
    hospital_id = request.GET.get("hospital_id") or request.session.get("booking_hospital_id")
    hospital = get_object_or_404(Hospital, id=hospital_id) if hospital_id else None

    if hospital_id:
        request.session["booking_hospital_id"] = hospital_id
    
    departments = Department.objects.filter(status="active")
    if hospital:
        departments = departments.filter(hospital=hospital)
        
    return render(request, "directory/department_selection.html", {
        "departments": departments,
        "hospital": hospital
    })


def select_doctor(request):
    department_id = request.GET.get("department_id") or request.GET.get("dept_id")
    department = get_object_or_404(Department, id=department_id) if department_id else None
    
    # If a department is provided directly (e.g. from AI analyzer), 
    # we must update the session's hospital to match that department's hospital.
    if department:
        request.session["booking_hospital_id"] = str(department.hospital.id)
        request.session["booking_department_id"] = str(department.id)
        request.session.modified = True

    hospital_id = request.session.get("booking_hospital_id")
    hospital = get_object_or_404(Hospital, id=hospital_id) if hospital_id else None
    
    doctors = Doctor.objects.filter(availability="available").select_related("department")
    if hospital:
        doctors = doctors.filter(hospital=hospital)
    if department_id:
        doctors = doctors.filter(department_id=department_id)
        
    return render(request, "directory/doctor_selection.html", {
        "doctors": doctors,
        "department": department,
        "hospital": hospital
    })


def medical_history(request):
    patient_id = request.session.get("patient_id")
    if not patient_id:
        from django.contrib import messages
        messages.error(request, "Please log in to book an appointment.")
        return redirect("patient_login")
        
    doctor_id = request.GET.get("doctor_id")
    if doctor_id:
        request.session["booking_doctor_id"] = doctor_id
        request.session.modified = True
        
    patient = get_object_or_404(Patient, id=patient_id)
    return render(request, "directory/medical_history.html", {"patient": patient})


def contact_info(request):
    if request.method == "POST":
        request.session["booking_phone"] = request.POST.get("phone")
        request.session["booking_alt_phone"] = request.POST.get("alt_phone")
        request.session["booking_address"] = request.POST.get("address", "")
        request.session["booking_appt_date"] = request.POST.get("appt_date")
        request.session["booking_appt_time"] = request.POST.get("appt_time")
        return redirect("payment_page")
        
    return render(request, "directory/contact_info.html")


def payment_page(request):
    doctor_id = request.session.get("booking_doctor_id")
    hospital_id = request.session.get("booking_hospital_id")
    patient_id = request.session.get("patient_id")
    
    if not doctor_id or not patient_id:
        print(f"DEBUG: Missing session data. doctor_id: {doctor_id}, patient_id: {patient_id}")
        return redirect("select_department")
        
    doctor = get_object_or_404(Doctor, id=doctor_id)
    hospital = get_object_or_404(Hospital, id=hospital_id) if hospital_id else None
    
    import datetime
    from django.utils import timezone
    
    # Generate appointment info from session or mock if empty
    appt_date_str = request.session.get("booking_appt_date")
    appt_time_str = request.session.get("booking_appt_time")
    
    if appt_date_str and appt_time_str:
        appt_date = datetime.datetime.strptime(appt_date_str, "%Y-%m-%d").date()
        appt_time = datetime.datetime.strptime(appt_time_str, "%H:%M").time()
    else:
        appt_date = timezone.now().date() + datetime.timedelta(days=1) # tomorrow
        appt_time = datetime.time(10, 30) # 10:30 AM
    
    if request.method == "POST":
        # Retrieve reason_for_visit from session (set during medical_history step)
        reason = request.session.get("booking_reason", "General Checkup")
        # Create appointment
        appointment = Appointment.objects.create(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_date=appt_date,
            appointment_time=appt_time,
            reason_for_visit=reason,
            status="upcoming",
            notes=f"Phone: {request.session.get('booking_phone', '')}, Address: {request.session.get('booking_address', '')}"
        )
        request.session["last_appointment_id"] = appointment.id
        request.session["last_hospital_name"] = hospital.name if hospital else "Nepal Health Bridge"
        # Clear booking session vars
        for key in ["booking_doctor_id", "booking_hospital_id", "booking_phone",
                    "booking_alt_phone", "booking_address", "booking_appt_date",
                    "booking_appt_time", "booking_reason"]:
            request.session.pop(key, None)
            
        return redirect("confirmation_page")
        
    context = {
        "doctor": doctor,
        "hospital": hospital,
        "appt_date": appt_date,
        "appt_time": appt_time,
        "total_amount": "850.00"
    }
    return render(request, "directory/payment.html", context)


def confirmation_page(request):
    appointment_id = request.session.get("last_appointment_id")
    hospital_name = request.session.get("last_hospital_name", "Nepal Health Bridge")
    appointment = None
    if appointment_id:
        appointment = Appointment.objects.select_related(
            "patient", "doctor", "doctor__department"
        ).filter(id=appointment_id).first()
    return render(request, "directory/appointment_confirmation.html", {
        "appointment": appointment,
        "hospital_name": hospital_name
    })


# ═══════════════════════════════════════════════════════════════
# DOCTOR AUTH & DASHBOARD
# ═══════════════════════════════════════════════════════════════

def doctor_login(request):
    if request.method == "POST":
        unique_id = request.POST.get("doctor_id", "").strip()
        password  = request.POST.get("password", "").strip()

        if not unique_id or not password:
            messages.error(request, "Please enter both ID and password.")
        else:
            try:
                doctor = Doctor.objects.get(unique_id=unique_id)
                if not doctor.password:
                    messages.error(request, "No password set. Contact admin.")
                elif check_password(password, doctor.password):
                    request.session["doctor_id"]   = doctor.id
                    request.session["doctor_name"] = doctor.full_name
                    return redirect("doctor_dashboard")
                else:
                    messages.error(request, "Incorrect password. Please try again.")
            except Doctor.DoesNotExist:
                messages.error(request, "No doctor found with this ID.")

    storage = messages.get_messages(request)
    storage.used = True
    return render(request, "directory/doctor_login.html")


def doctor_logout(request):
    request.session.flush()
    return redirect("doctor_login")


@never_cache
def doctor_dashboard(request):
    if not request.session.get("doctor_id"):
        return redirect("doctor_login")

    doctor = get_object_or_404(Doctor, id=request.session["doctor_id"])
    today  = date.today()

    today_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=today
    ).select_related("patient").order_by("appointment_time")

    return render(request, "directory/doctor_dashboard.html", {
        "doctor":             doctor,
        "today_appointments": today_appointments,
        "completed_count":    today_appointments.filter(status="completed").count(),
        "waiting_count":      today_appointments.filter(status="waiting").count(),
        "upcoming_count":     today_appointments.filter(status="upcoming").count(),
    })

def patient_details(request):
    # 🔒 SECURITY: Only logged-in doctors may access this view
    if not request.session.get("doctor_id"):
        return redirect("doctor_login")

    appointment_id = request.GET.get("appointment_id")

    if not appointment_id:
        return redirect("doctor_dashboard")

    appointment = get_object_or_404(
        Appointment.objects.select_related("patient", "doctor"),
        id=appointment_id
    )

    # 🔒 Ensure this appointment belongs to the logged-in doctor
    if appointment.doctor_id != request.session["doctor_id"]:
        messages.error(request, "You are not authorised to view this appointment.")
        return redirect("doctor_dashboard")

    return render(request, "directory/doctor_patient_details.html", {
        "appointment": appointment,
        "patient":     appointment.patient,
    })


def prescription_page(request):
    if not request.session.get("doctor_id"):
        return redirect("doctor_login")

    appointment_id = request.GET.get("appointment_id")

    # ✅ If no appointment_id redirect to patient list
    if not appointment_id:
        messages.error(request, "Please select a patient first.")
        return redirect("doctor_patient_list")

    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == "POST":
        Prescription.objects.update_or_create(
            appointment=appointment,
            defaults={
                "diagnosis":    request.POST.get("diagnosis"),
                "medicines":    request.POST.get("medicines"),
                "instructions": request.POST.get("instructions", ""),
                "follow_up":    request.POST.get("follow_up") or None,
            }
        )
        messages.success(request, "Prescription saved successfully!")
        return redirect(f"/doctor/prescription/?appointment_id={appointment_id}")

    prescription = Prescription.objects.filter(appointment=appointment).first()
    return render(request, "directory/doctor_prescription.html", {
        "appointment":  appointment,
        "prescription": prescription,
    })


# ═══════════════════════════════════════════════════════════════
# HOSPITAL ADMIN DASHBOARD
# ═══════════════════════════════════════════════════════════════

@never_cache
def hospital_admin_dashboard(request):
    if not request.session.get("admin_id"):
        return redirect("admin_login")

    admin = get_object_or_404(HospitalAdmin, id=request.session["admin_id"])
    hospital = admin.hospital
    
    if not hospital:
        messages.error(request, "Your admin account is not linked to any hospital.")
        return redirect("admin_logout")

    today = date.today()
    return render(request, "directory/hospital_admin_dashboard.html", {
        "admin_name":         request.session.get("admin_name", "Admin User"),
        "total_doctors":      Doctor.objects.filter(hospital=hospital).count(),
        "total_departments":  Department.objects.filter(hospital=hospital).count(),
        # Patients are global, but we could count unique patients that have appointments at this hospital
        "total_patients":     Appointment.objects.filter(doctor__hospital=hospital).values('patient').distinct().count(),
        "today_appointments": Appointment.objects.filter(doctor__hospital=hospital, appointment_date=today).count(),
        "pending_count":      Appointment.objects.filter(
                                  doctor__hospital=hospital, appointment_date=today, status="waiting"
                              ).count(),
        "hospital_name":      hospital.name,
    })


# ═══════════════════════════════════════════════════════════════
# ADMIN — MANAGE APPOINTMENTS
# ═══════════════════════════════════════════════════════════════

# views.py

@never_cache
def admin_manage_appointments(request):
    if not request.session.get("admin_id"):
        return redirect("admin_login")

    admin = get_object_or_404(HospitalAdmin, id=request.session["admin_id"])
    hospital = admin.hospital
    
    today = date.today()

    # Base queryset — all appointments for this hospital's doctors
    all_qs = Appointment.objects.filter(doctor__hospital=hospital)

    appointments = all_qs.select_related(
        'patient', 'doctor', 'doctor__department'
    ).order_by('-appointment_date', 'appointment_time')

    search        = request.GET.get('search', '').strip()
    selected_date = request.GET.get('date', '')
    selected_dept = request.GET.get('department', '')

    if search:
        appointments = appointments.filter(patient__full_name__icontains=search)

    if selected_date:
        # User explicitly filtered by a specific date
        appointments = appointments.filter(appointment_date=selected_date)
    # If no date filter: show ALL appointments (no restriction)
    # so admins can always see what has been booked

    if selected_dept:
        appointments = appointments.filter(doctor__department__id=selected_dept)

    # ── Stat cards — counts from ALL patient records ──────────────────
    today_qs = all_qs.filter(appointment_date=today)

    return render(request, 'directory/admin_manage_appointments.html', {
        'appointments':       appointments,
        'filter_departments': Department.objects.filter(hospital=hospital).order_by('name'),
        'today':              today,
        'search':             search,
        'selected_date':      selected_date,
        'selected_dept':      selected_dept,
        # All-time counts (for the stat cards)
        'total_count':        all_qs.count(),
        'completed_count':    all_qs.filter(status='completed').count(),
        'waiting_count':      all_qs.filter(status='waiting').count(),
        'upcoming_count':     all_qs.filter(status='upcoming').count(),
        # Today-specific count (shown as a badge)
        'today_count':        today_qs.count(),
        'admin_name':         request.session.get("admin_name", "Admin User"),
        'hospital_name':      hospital.name if hospital else "Nepal Health Bridge",
    })

def appointment_update_status(request, pk, status):
    if not request.session.get("admin_id"):
        return redirect("admin_login")
    if request.method == 'POST':
        appointment = get_object_or_404(Appointment, pk=pk)
        appointment.status = status
        appointment.save()
        messages.success(request, f'Appointment marked as {status}.')
    return redirect('admin_manage_appointments')


@never_cache
def admin_appointment_detail(request, pk):
    """Admin-only view: full appointment details including patient info & prescription."""
    # 🔒 SECURITY: Only logged-in hospital admins may access this view
    if not request.session.get("admin_id"):
        return redirect("admin_login")

    admin = get_object_or_404(HospitalAdmin, id=request.session["admin_id"])
    hospital = admin.hospital

    # 🔒 Scope to this admin's hospital — prevents cross-hospital snooping
    appointment = get_object_or_404(
        Appointment.objects.select_related(
            "patient", "doctor", "doctor__department"
        ),
        pk=pk,
        doctor__hospital=hospital
    )

    prescription = Prescription.objects.filter(appointment=appointment).first()

    return render(request, "directory/admin_appointment_detail.html", {
        "appointment":  appointment,
        "prescription": prescription,
        "hospital_name": hospital.name,
        "admin_name":    request.session.get("admin_name", "Admin User"),
    })

# ═══════════════════════════════════════════════════════════════
# ADMIN — MANAGE DOCTORS
# ═══════════════════════════════════════════════════════════════

@never_cache
def admin_manage_doctors(request):
    if not request.session.get("admin_id"):
        return redirect("admin_login")
        
    admin = get_object_or_404(HospitalAdmin, id=request.session["admin_id"])
    hospital = admin.hospital
    
    doctors     = Doctor.objects.filter(hospital=hospital).select_related("department").all().order_by("full_name")
    departments = Department.objects.filter(hospital=hospital, status="active")
    return render(request, "directory/admin_manage_doctors.html", {
        "doctors":     doctors,
        "departments": departments,
        "hospital_name": hospital.name if hospital else "Nepal Health Bridge",
    })


def doctor_add(request):
    if not request.session.get("admin_id"):
        return redirect("admin_login")
        
    admin = get_object_or_404(HospitalAdmin, id=request.session["admin_id"])
    hospital = admin.hospital
    
    if request.method == "POST":
        try:
            Doctor.objects.create(
                hospital     = hospital,
                unique_id    = request.POST["unique_id"],
                full_name    = request.POST["full_name"],
                specialty    = request.POST["specialty"],
                department   = get_object_or_404(Department, id=request.POST["department"], hospital=hospital),
                availability = request.POST.get("availability", "available"),
                is_head      = request.POST.get("is_head") == "on",
                phone        = request.POST.get("phone", ""),
                email        = request.POST.get("email", ""),
                password     = request.POST.get("password", ""),
            )
            messages.success(request, "Doctor added successfully!")
        except Exception as e:
            messages.error(request, f"Error adding doctor: {str(e)}")
    return redirect("admin_manage_doctors")


def doctor_edit(request, pk):
    if not request.session.get("admin_id"):
        return redirect("admin_login")
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == "POST":
        try:
            doctor.unique_id    = request.POST["unique_id"]
            doctor.full_name    = request.POST["full_name"]
            doctor.specialty    = request.POST["specialty"]
            doctor.department   = get_object_or_404(Department, id=request.POST["department"])
            doctor.availability = request.POST.get("availability", "available")
            doctor.is_head      = request.POST.get("is_head") == "on"
            new_password = request.POST.get("password", "").strip()
            if new_password:
                doctor.password = new_password
            doctor.save()
            messages.success(request, "Doctor updated successfully!")
        except Exception as e:
            messages.error(request, f"Error updating doctor: {str(e)}")
    return redirect("admin_manage_doctors")


def doctor_delete(request, pk):
    if not request.session.get("admin_id"):
        return redirect("admin_login")
    doctor = get_object_or_404(Doctor, pk=pk)
    name   = doctor.full_name
    doctor.delete()
    messages.success(request, f"Dr. {name} has been removed.")
    return redirect("admin_manage_doctors")


# ═══════════════════════════════════════════════════════════════
# ADMIN — MANAGE DEPARTMENTS
# ═══════════════════════════════════════════════════════════════

@never_cache
def admin_manage_departments(request):
    if not request.session.get("admin_id"):
        return redirect("admin_login")
        
    admin = get_object_or_404(HospitalAdmin, id=request.session["admin_id"])
    hospital = admin.hospital
    
    departments = Department.objects.filter(hospital=hospital).order_by("name")
    doctors     = Doctor.objects.filter(hospital=hospital, availability="available").order_by("full_name")
    return render(request, "directory/admin_manage_departments.html", {
        "departments": departments,
        "doctors":     doctors,
        "hospital_name": hospital.name if hospital else "Nepal Health Bridge",
    })


def department_add(request):
    if not request.session.get("admin_id"):
        return redirect("admin_login")
        
    admin = get_object_or_404(HospitalAdmin, id=request.session["admin_id"])
    hospital = admin.hospital
    
    if request.method == "POST":
        try:
            dept = Department.objects.create(
                hospital = hospital,
                name   = request.POST["name"],
                status = request.POST.get("status", "active"),
            )
            head_doctor_id = request.POST.get("head_doctor_id")
            if head_doctor_id:
                Doctor.objects.filter(id=head_doctor_id, hospital=hospital).update(
                    is_head=True, department=dept
                )
            messages.success(request, f"'{dept.name}' department added successfully!")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    return redirect("admin_manage_departments")


def department_edit(request, pk):
    if not request.session.get("admin_id"):
        return redirect("admin_login")
    dept = get_object_or_404(Department, pk=pk)
    if request.method == "POST":
        try:
            dept.name   = request.POST["name"]
            dept.status = request.POST.get("status", "active")
            dept.save()
            
            # Handle head doctor assignment
            head_doctor_id = request.POST.get("head_doctor_id")
            # First, remove head status from any existing doctors in this department
            Doctor.objects.filter(department=dept, is_head=True).update(is_head=False)
            
            if head_doctor_id:
                Doctor.objects.filter(id=head_doctor_id).update(
                    is_head=True, department=dept
                )
            messages.success(request, f"'{dept.name}' updated successfully!")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    return redirect("admin_manage_departments")


def department_delete(request, pk):
    if not request.session.get("admin_id"):
        return redirect("admin_login")
    dept = get_object_or_404(Department, pk=pk)
    name = dept.name
    dept.delete()
    messages.success(request, f"'{name}' department deleted.")
    return redirect("admin_manage_departments")


# ═══════════════════════════════════════════════════════════════
# ADMIN — INBOX / PATIENT CONTACTS
# ═══════════════════════════════════════════════════════════════

@never_cache
def admin_patient_contacts(request):
    if not request.session.get("admin_id"):
        return redirect("admin_login")

    admin = get_object_or_404(HospitalAdmin, id=request.session["admin_id"])
    hospital = admin.hospital

    search    = request.GET.get("search", "")
    
    # Filter inquiries ONLY for this hospital, or those explicitly marked for this hospital (or if global/null it shouldn't show up here if every hospital demands separation)
    # Actually, we should only show inquiries that belong to this hospital
    inquiries = Inquiry.objects.filter(hospital=hospital).order_by("-created_at")

    if search:
        inquiries = inquiries.filter(name__icontains=search)  | \
                    inquiries.filter(email__icontains=search)  | \
                    inquiries.filter(message__icontains=search)

    return render(request, "directory/admin_patient_contacts.html", {
        "inquiries":      inquiries,
        "search":         search,
        "new_count":      Inquiry.objects.filter(hospital=hospital, status="new").count(),
        "read_count":     Inquiry.objects.filter(hospital=hospital, status="read").count(),
        "resolved_count": Inquiry.objects.filter(hospital=hospital, status="resolved").count(),
        "hospital_name":  hospital.name if hospital else "Nepal Health Bridge",
        "admin_name":     request.session.get("admin_name", "Admin User"),
    })


def inquiry_mark_read(request, pk):
    if not request.session.get("admin_id"):
        return redirect("admin_login")
    inquiry = get_object_or_404(Inquiry, pk=pk)
    inquiry.status = "read"
    inquiry.save()
    messages.success(request, "Inquiry marked as read.")
    return redirect("admin_patient_contacts")


def inquiry_mark_resolved(request, pk):
    if not request.session.get("admin_id"):
        return redirect("admin_login")
    inquiry = get_object_or_404(Inquiry, pk=pk)
    inquiry.status = "resolved"
    inquiry.save()
    messages.success(request, "Inquiry marked as resolved.")
    return redirect("admin_patient_contacts")


# ═══════════════════════════════════════════════════════════════
# ADMIN — PATIENT CONTACT DIRECTORY
# ═══════════════════════════════════════════════════════════════

@never_cache
def admin_patient_directory(request):
    """Shows registered patient contact details (phone, address, etc.)"""
    if not request.session.get("admin_id"):
        return redirect("admin_login")

    admin = get_object_or_404(HospitalAdmin, id=request.session["admin_id"])
    hospital = admin.hospital

    # All patients who have at least one appointment at this hospital
    patient_ids = Appointment.objects.filter(
        doctor__hospital=hospital
    ).values_list('patient_id', flat=True).distinct()

    patients = Patient.objects.filter(id__in=patient_ids).order_by('full_name')

    search = request.GET.get('search', '').strip()
    if search:
        patients = patients.filter(
            full_name__icontains=search
        ) | patients.filter(
            email__icontains=search
        ) | patients.filter(
            primary_phone__icontains=search
        )

    return render(request, "directory/admin_patient_directory.html", {
        "patients":                   patients,
        "search":                     search,
        "total_patients":             patients.count(),
        "patients_with_appointments": patient_ids.count(),
        "patients_with_phone":        patients.exclude(primary_phone="").count(),
        "hospital_name":              hospital.name if hospital else "Nepal Health Bridge",
        "admin_name":                 request.session.get("admin_name", "Admin User"),
    })


# ═══════════════════════════════════════════════════════════════
# ADMIN — REPORTS & BILLING
# ═══════════════════════════════════════════════════════════════

@never_cache
def admin_reports_billing(request):
    if not request.session.get("admin_id"):
        return redirect("admin_login")
        
    admin = get_object_or_404(HospitalAdmin, id=request.session["admin_id"])
    hospital = admin.hospital

    today        = date.today()
    appointments = Appointment.objects.filter(doctor__hospital=hospital).select_related(
        "patient", "doctor"
    ).order_by("-appointment_date")

    return render(request, "directory/admin_reports_billing.html", {
        "appointments":       appointments,
        "total_appointments": appointments.count(),
        "completed_today":    appointments.filter(
                                  appointment_date=today,
                                  status="completed"
                              ).count(),
        "hospital_name": hospital.name if hospital else "Nepal Health Bridge",
    })

# ═══════════════════════════════════════════════════════════════
#patient my appointments
# ═══════════════════════════════════════════════════════════════
def patient_my_appointments(request):
    if not request.session.get("patient_id"):
        return redirect("patient_login")

    patient_id      = request.session["patient_id"]
    selected_status = request.GET.get("status", "")
    selected_date   = request.GET.get("date", "")

    appointments = Appointment.objects.select_related(
        "doctor", "doctor__department"
    ).filter(patient_id=patient_id).order_by("-appointment_date", "appointment_time")

    if selected_status:
        appointments = appointments.filter(status=selected_status)

    if selected_date:
        try:
            appointments = appointments.filter(appointment_date=selected_date)
        except Exception:
            selected_date = ""  # ✅ ignore invalid date, show all

    return render(request, "directory/my_appointments.html", {
        "patient_name":    request.session.get("patient_name", "Patient"),
        "appointments":    appointments,
        "selected_status": selected_status,
        "selected_date":   selected_date,
    })

#----------------------------------------
# PATIENT MEDICAL HISTORY
#----------------------------------------



def patient_medical_history(request):
    if not request.session.get("patient_id"):
        return redirect("patient_login")

    patient_id = request.session["patient_id"]
    patient    = Patient.objects.get(id=patient_id)

    past_appointments = Appointment.objects.select_related(
        "doctor", "doctor__department", "prescription"
    ).filter(
        patient_id=patient_id,
        status__in=["completed", "cancelled"]
    ).order_by("-appointment_date")

    return render(request, "directory/patient_medical_history.html", {
        "patient_name":      request.session.get("patient_name", "Patient"),
        "patient":           patient,
        "past_appointments": past_appointments,
    })

@never_cache
def patient_view_prescription(request, appointment_id):
    if not request.session.get("patient_id"):
        return redirect("patient_login")
    
    appointment = get_object_or_404(
        Appointment.objects.select_related("doctor", "doctor__hospital", "patient"), 
        id=appointment_id, 
        patient_id=request.session["patient_id"]
    )
    prescription = get_object_or_404(Prescription, appointment=appointment)
    
    return render(request, "directory/patient_view_prescription.html", {
        "appointment": appointment,
        "prescription": prescription,
        "patient_name": request.session.get("patient_name", "Patient")
    })

# ═══════════════════════════════════════════════════════════════
# PATIENT PROFILE
# ═══════════════════════════════════════════════════════════════
def patient_profile(request):
    if not request.session.get("patient_id"):
        return redirect("patient_login")

    patient = Patient.objects.get(id=request.session["patient_id"])

    if request.method == "POST":
        patient.full_name         = request.POST.get("full_name", "").strip()
        patient.email             = request.POST.get("email", "").strip()
        patient.primary_phone     = request.POST.get("primary_phone", "").strip()
        patient.alternate_phone   = request.POST.get("alternate_phone", "").strip()
        patient.date_of_birth     = request.POST.get("date_of_birth") or None
        patient.gender            = request.POST.get("gender", "")
        patient.blood_group       = request.POST.get("blood_group", "")
        patient.country           = request.POST.get("country", "").strip()
        patient.province          = request.POST.get("province", "").strip()
        patient.district          = request.POST.get("district", "").strip()
        patient.city              = request.POST.get("city", "").strip()
        patient.ward_number       = request.POST.get("ward_number", "").strip()
        patient.postal_code       = request.POST.get("postal_code", "").strip()
        patient.full_address      = request.POST.get("full_address", "").strip()
        patient.known_allergies   = request.POST.get("known_allergies", "").strip()
        patient.chronic_conditions= request.POST.get("chronic_conditions", "").strip()
        patient.current_medications=request.POST.get("current_medications", "").strip()
        patient.past_surgeries    = request.POST.get("past_surgeries", "").strip()

        new_password = request.POST.get("new_password", "").strip()
        if new_password:
            patient.password = new_password

        patient.save()

        # ✅ Update session name if changed
        request.session["patient_name"] = patient.full_name
        messages.success(request, "Profile updated successfully!")
        return redirect("patient_profile")

    return render(request, "directory/patient_profile.html", {
        "patient": patient,
    })


# ═══════════════════════════════════════════════════════════════
# DOCTOR DASHBOARD & APPOINTMENT MANAGEMENT
# ═══════════════════════════════════════════════════════════════
from datetime import date

def doctor_dashboard(request):
    if not request.session.get("doctor_id"):
        return redirect("doctor_login")

    doctor_id = request.session["doctor_id"]
    doctor    = Doctor.objects.get(id=doctor_id)
    today     = date.today()

    appointments = Appointment.objects.select_related(
        "patient"
    ).filter(
        doctor_id=doctor_id,
        appointment_date=today
    ).order_by("appointment_time")

    return render(request, "directory/doctor_dashboard.html", {
        "doctor":       doctor,
        "appointments": appointments,
        "total_today":  appointments.count(),
    })

    # ═══════════════════════════════════════════════════════════════
    # my schedule
    # ═══════════════════════════════════════════════════════════════
from itertools import groupby
from datetime import date

@never_cache
def doctor_schedule(request):
    if not request.session.get("doctor_id"):
        return redirect("doctor_login")

    doctor_id       = request.session["doctor_id"]
    doctor          = Doctor.objects.get(id=doctor_id)
    today           = date.today()
    selected_status = request.GET.get("status", "")

    appointments = Appointment.objects.select_related(
        "patient"
    ).filter(
        doctor_id=doctor_id,
        appointment_date__gte=today
    ).order_by("appointment_date", "appointment_time")

    if selected_status:
        appointments = appointments.filter(status=selected_status)

    # ✅ Group by date
    grouped = {}
    for appt in appointments:
        key = appt.appointment_date
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(appt)

    return render(request, "directory/doctor_schedule.html", {
        "doctor":               doctor,
        "grouped_appointments": grouped,
        "today":                today,
        "selected_status":      selected_status,
        "total_count":          appointments.count(),
    })

# ═══════════════════════════════════════════════════════════════
# DOCTOR — PATIENT DETAILS 
# ═══════════════════════════════════════════════════════════════
@never_cache
def doctor_patient_list(request):
    if not request.session.get("doctor_id"):
        return redirect("doctor_login")

    doctor = get_object_or_404(Doctor, id=request.session["doctor_id"])
    search = request.GET.get("search", "")

    appointments = Appointment.objects.filter(
        doctor=doctor
    ).select_related("patient").order_by("-appointment_date")

    if search:
        appointments = appointments.filter(
            patient__full_name__icontains=search
        )

    return render(request, "directory/doctor_patient_list.html", {
        "doctor":          doctor,
        "appointments":    appointments,
        "search":          search,
        "total_patients":  appointments.values("patient").distinct().count(),
        "completed_count": appointments.filter(status="completed").count(),
        "waiting_count":   appointments.filter(status="waiting").count(),
        "upcoming_count":  appointments.filter(status="upcoming").count(),
        "mode":            "patient_list"
    })

@never_cache
def doctor_write_prescription_list(request):
    if not request.session.get("doctor_id"):
        return redirect("doctor_login")

    doctor = get_object_or_404(Doctor, id=request.session["doctor_id"])
    search = request.GET.get("search", "")

    # For prescribing, we might want to focus on waiting/upcoming appointments
    appointments = Appointment.objects.filter(
        doctor=doctor
    ).select_related("patient").order_by("-appointment_date")

    if search:
        appointments = appointments.filter(
            patient__full_name__icontains=search
        )

    return render(request, "directory/doctor_patient_list.html", {
        "doctor":          doctor,
        "appointments":    appointments,
        "search":          search,
        "total_patients":  appointments.values("patient").distinct().count(),
        "completed_count": appointments.filter(status="completed").count(),
        "waiting_count":   appointments.filter(status="waiting").count(),
        "upcoming_count":  appointments.filter(status="upcoming").count(),
        "mode":            "write_prescription"
    })


def doctor_close_appointment(request, pk):
    if not request.session.get("doctor_id"):
        return redirect("doctor_login")
        
    if request.method == "POST":
        appointment = get_object_or_404(Appointment, pk=pk)
        
        # Ensure that only the assigned doctor can close this file
        if appointment.doctor.id != request.session["doctor_id"]:
            messages.error(request, "You are not authorized to close this appointment.")
            return redirect("doctor_dashboard")
            
        appointment.status = "completed"
        appointment.save()
        messages.success(request, f"File for {appointment.patient.full_name} has been closed successfully.")
        
    return redirect("doctor_dashboard")


@never_cache
def doctor_profile(request):
    if not request.session.get("doctor_id"):
        return redirect("doctor_login")

    doctor = Doctor.objects.get(id=request.session["doctor_id"])

    if request.method == "POST":
        doctor.email = request.POST.get("email", "").strip()
        doctor.phone = request.POST.get("phone", "").strip()

        new_password = request.POST.get("new_password", "").strip()
        if new_password:
            doctor.password = new_password

        doctor.save()
        
        # Update session name just in case
        request.session["doctor_name"] = f"Dr. {doctor.full_name}"
        messages.success(request, "Profile and password updated successfully!")
        return redirect("doctor_profile")

    return render(request, "directory/doctor_profile.html", {
        "doctor": doctor,
    })


