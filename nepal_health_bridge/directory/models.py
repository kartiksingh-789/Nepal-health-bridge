from django.db import models
from django.contrib.auth.hashers import make_password


# ═══════════════════════════════════════════════════════════════
# HOSPITAL
# ═══════════════════════════════════════════════════════════════

class Hospital(models.Model):
    name = models.CharField(max_length=200, unique=True)
    location = models.CharField(max_length=255)
    image_url = models.URLField(max_length=500, blank=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=4.5)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


# ═══════════════════════════════════════════════════════════════
# DEPARTMENT
# ═══════════════════════════════════════════════════════════════

class Department(models.Model):

    STATUS_CHOICES = [
        ("active",   "Active"),
        ("inactive", "Inactive"),
    ]

    name       = models.CharField(max_length=200)
    hospital   = models.ForeignKey(
                     Hospital,
                     on_delete=models.CASCADE,
                     related_name="departments",
                     null=True, blank=True
                 )
    status     = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def total_doctors(self):
        return self.doctors.count()

    @property
    def head_doctor(self):
        doctor = self.doctors.filter(is_head=True).first()
        return doctor.full_name if doctor else "Not Assigned"


# ═══════════════════════════════════════════════════════════════
# DOCTOR
# ═══════════════════════════════════════════════════════════════

class Doctor(models.Model):

    AVAILABILITY_CHOICES = [
        ("available",   "Available"),
        ("unavailable", "Unavailable"),
        ("on_leave",    "On Leave"),
    ]

    unique_id    = models.CharField(max_length=20, unique=True, default="")
    hospital     = models.ForeignKey(
                       Hospital,
                       on_delete=models.CASCADE,
                       related_name="doctors",
                       null=True, blank=True
                   )
    full_name    = models.CharField(max_length=255, default="")
    specialty    = models.CharField(max_length=200, default="")
    availability = models.CharField(
                       max_length=15,
                       choices=AVAILABILITY_CHOICES,
                       default="available"
                   )
    department   = models.ForeignKey(
                       Department,
                       on_delete=models.SET_NULL,
                       null=True, blank=True,
                       related_name="doctors"
                   )
    is_head      = models.BooleanField(default=False)
    phone        = models.CharField(max_length=15, blank=True, default="")
    email        = models.EmailField(blank=True, default="")

    # ✅ NEW — doctor login password
    password     = models.CharField(max_length=255, blank=True, default="")

    created_at   = models.DateTimeField(auto_now_add=True, null=True)
    updated_at   = models.DateTimeField(auto_now=True,     null=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return f"{self.unique_id} - {self.full_name}"

    def save(self, *args, **kwargs):
        # ✅ Auto-hash password when saving
        if self.password and not self.password.startswith("pbkdf2_"):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)


# ═══════════════════════════════════════════════════════════════
# PATIENT
# ═══════════════════════════════════════════════════════════════

class Patient(models.Model):

    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
    ]

    BLOOD_GROUP_CHOICES = [
        ("A+",  "A+"),  ("A-",  "A-"),
        ("B+",  "B+"),  ("B-",  "B-"),
        ("O+",  "O+"),  ("O-",  "O-"),
        ("AB+", "AB+"), ("AB-", "AB-"),
    ]

    MARITAL_STATUS_CHOICES = [
        ("single",   "Single"),
        ("married",  "Married"),
        ("divorced", "Divorced"),
        ("widowed",  "Widowed"),
    ]

    # ── Step 1: Account Info ───────────────────────────────────
    username        = models.CharField(max_length=150, unique=True)
    email           = models.EmailField(unique=True)
    password        = models.CharField(max_length=255)
    primary_phone   = models.CharField(max_length=15)
    alternate_phone = models.CharField(max_length=15, blank=True)

    # ── Step 2: Personal Info ──────────────────────────────────
    full_name      = models.CharField(max_length=255)
    date_of_birth  = models.DateField(null=True, blank=True)
    gender         = models.CharField(max_length=1,  choices=GENDER_CHOICES,         blank=True)
    blood_group    = models.CharField(max_length=3,  choices=BLOOD_GROUP_CHOICES,    blank=True)
    nationality    = models.CharField(max_length=100, blank=True)
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES, blank=True)

    # ── Step 3: Address Info ───────────────────────────────────
    country      = models.CharField(max_length=100, default="Nepal")
    province     = models.CharField(max_length=100, blank=True)
    district     = models.CharField(max_length=100, blank=True)
    city         = models.CharField(max_length=100, blank=True)
    ward_number  = models.CharField(max_length=10,  blank=True)
    postal_code  = models.CharField(max_length=10,  blank=True)
    full_address = models.TextField(blank=True)

    # ── Step 4: Medical Info ───────────────────────────────────
    known_allergies     = models.TextField(blank=True)
    chronic_conditions  = models.TextField(blank=True)
    current_medications = models.TextField(blank=True)
    past_surgeries      = models.TextField(blank=True)
    has_disability      = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    def save(self, *args, **kwargs):
        # Auto-hash password only if not already hashed
        if self.password and not self.password.startswith("pbkdf2_"):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)


# ═══════════════════════════════════════════════════════════════
# APPOINTMENT
# ═══════════════════════════════════════════════════════════════

class Appointment(models.Model):

    STATUS_CHOICES = [
        ("upcoming",  "Upcoming"),
        ("waiting",   "Waiting"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    patient          = models.ForeignKey(
                           Patient,
                           on_delete=models.CASCADE,
                           related_name="appointments"
                       )
    doctor           = models.ForeignKey(
                           Doctor,
                           on_delete=models.CASCADE,
                           related_name="appointments"
                       )
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason_for_visit = models.CharField(max_length=255)
    status           = models.CharField(
                           max_length=10,
                           choices=STATUS_CHOICES,
                           default="upcoming"
                       )
    notes            = models.TextField(blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["appointment_date", "appointment_time"]

    def __str__(self):
        return f"{self.patient.full_name} -> Dr.{self.doctor.full_name} on {self.appointment_date}"


# ═══════════════════════════════════════════════════════════════
# PRESCRIPTION
# ═══════════════════════════════════════════════════════════════

class Prescription(models.Model):

    appointment  = models.OneToOneField(
                       Appointment,
                       on_delete=models.CASCADE,
                       related_name="prescription"
                   )
    diagnosis    = models.TextField()
    medicines    = models.TextField()
    instructions = models.TextField(blank=True)
    follow_up    = models.DateField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription for {self.appointment.patient.full_name}"


# ═══════════════════════════════════════════════════════════════
# INQUIRY  (Inbox / Patient Contacts)
# ═══════════════════════════════════════════════════════════════

class Inquiry(models.Model):

    STATUS_CHOICES = [
        ("new",      "New"),
        ("read",     "Read"),
        ("resolved", "Resolved"),
    ]

    hospital   = models.ForeignKey(
                     Hospital,
                     on_delete=models.CASCADE,
                     related_name="inquiries",
                     null=True, blank=True
                 )
    name       = models.CharField(max_length=255)
    email      = models.EmailField()
    phone      = models.CharField(max_length=15)
    message    = models.TextField()
    status     = models.CharField(max_length=10, choices=STATUS_CHOICES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Inquiries"

    def __str__(self):
        return f"{self.name} - {self.email}"
    
    # ═══════════════════════════════════════════════════════════════
# HOSPITAL ADMIN
# ═══════════════════════════════════════════════════════════════

class HospitalAdmin(models.Model):
    hospital   = models.ForeignKey(
                     Hospital,
                     on_delete=models.CASCADE,
                     related_name="admins",
                     null=True, blank=True
                 )
    username   = models.CharField(max_length=150, unique=True)
    password   = models.CharField(max_length=255)
    full_name  = models.CharField(max_length=255)
    email      = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        # Auto-hash password
        if self.password and not self.password.startswith("pbkdf2_"):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)


        