import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib
import os

# ═══════════════════════════════════════════════════════════════
# SYMPTOM → SPECIALTY TRAINING DATA (Highly Expanded)
# ═══════════════════════════════════════════════════════════════

TRAINING_DATA = [
    # ── CARDIOLOGY (Heart & Circulation) ──
    ("chest pain", "Cardiology"),
    ("heart pain", "Cardiology"),
    ("chest tightness", "Cardiology"),
    ("shortness of breath chest", "Cardiology"),
    ("palpitations", "Cardiology"),
    ("irregular heartbeat", "Cardiology"),
    ("heart racing", "Cardiology"),
    ("chest pressure", "Cardiology"),
    ("heart attack symptoms", "Cardiology"),
    ("angina", "Cardiology"),
    ("heart failure", "Cardiology"),
    ("high blood pressure", "Cardiology"),
    ("low blood pressure", "Cardiology"),
    ("hypertension", "Cardiology"),
    ("swollen legs heart", "Cardiology"),
    ("fatigue and chest pain", "Cardiology"),
    ("dizziness and chest pain", "Cardiology"),
    ("cholesterol problems", "Cardiology"),
    ("arrhythmia", "Cardiology"),
    ("heart murmur", "Cardiology"),
    ("pulse racing", "Cardiology"),
    ("skipped heart beats", "Cardiology"),
    ("breathlessness when lying down", "Cardiology"),
    ("cyanosis bluish skin", "Cardiology"),
    ("chest pain radiating to arm", "Cardiology"),
    ("chest pain radiating to jaw", "Cardiology"),
    ("cold sweat and chest pressure", "Cardiology"),
    ("heart thumping", "Cardiology"),
    ("fainting while exercising", "Cardiology"),
    ("severe heart palpitations", "Cardiology"),
    ("belt around chest pain", "Cardiology"),
    ("weight on chest feeling", "Cardiology"),
    ("puffy ankles heart", "Cardiology"),
    ("difficulty breathing when lying down", "Cardiology"),
    ("sudden fainting episode", "Cardiology"),
    ("irregular heart rhythm", "Cardiology"),

    # ── OPHTHALMOLOGY (Eyes) ──
    ("eye pain", "Ophthalmology"),
    ("blurry vision", "Ophthalmology"),
    ("vision loss", "Ophthalmology"),
    ("eye redness", "Ophthalmology"),
    ("eye infection", "Ophthalmology"),
    ("double vision", "Ophthalmology"),
    ("eye itching", "Ophthalmology"),
    ("eye discharge", "Ophthalmology"),
    ("watery eyes", "Ophthalmology"),
    ("sensitivity to light", "Ophthalmology"),
    ("cataracts", "Ophthalmology"),
    ("glaucoma", "Ophthalmology"),
    ("dry eyes", "Ophthalmology"),
    ("floaters in vision", "Ophthalmology"),
    ("eye swelling", "Ophthalmology"),
    ("poor night vision", "Ophthalmology"),
    ("eye strain", "Ophthalmology"),
    ("conjunctivitis", "Ophthalmology"),
    ("stye in eye", "Ophthalmology"),
    ("seeing flashes of light", "Ophthalmology"),
    ("halo around lights", "Ophthalmology"),
    ("drooping eyelid", "Ophthalmology"),
    ("burning sensation eye", "Ophthalmology"),

    # ── ORTHOPEDICS (Bones & Joints) ──
    ("bone pain", "Orthopedics"),
    ("joint pain", "Orthopedics"),
    ("knee pain", "Orthopedics"),
    ("back pain", "Orthopedics"),
    ("lower back pain", "Orthopedics"),
    ("shoulder pain", "Orthopedics"),
    ("hip pain", "Orthopedics"),
    ("neck pain", "Orthopedics"),
    ("fracture", "Orthopedics"),
    ("broken bone", "Orthopedics"),
    ("swollen joint", "Orthopedics"),
    ("stiff joints", "Orthopedics"),
    ("arthritis", "Orthopedics"),
    ("muscle pain", "Orthopedics"),
    ("ankle pain", "Orthopedics"),
    ("wrist pain", "Orthopedics"),
    ("elbow pain", "Orthopedics"),
    ("foot pain", "Orthopedics"),
    ("spine pain", "Orthopedics"),
    ("difficulty walking", "Orthopedics"),
    ("sports injury", "Orthopedics"),
    ("ligament tear", "Orthopedics"),
    ("dislocated joint", "Orthopedics"),
    ("osteoporosis", "Orthopedics"),
    ("scoliosis", "Orthopedics"),
    ("sore muscles", "Orthopedics"),
    ("tendonitis", "Orthopedics"),
    ("sprained ankle", "Orthopedics"),
    ("osteoarthritis", "Orthopedics"),
    ("limited mobility", "Orthopedics"),
    ("bone fracture", "Orthopedics"),
    ("knee surgery", "Orthopedics"),
    ("joint replacement", "Orthopedics"),
    ("hip replacement", "Orthopedics"),

    # ── PEDIATRICS (Children) ──
    ("child fever", "Pediatrics"),
    ("baby not eating", "Pediatrics"),
    ("child cough", "Pediatrics"),
    ("infant crying", "Pediatrics"),
    ("child rash", "Pediatrics"),
    ("child vomiting", "Pediatrics"),
    ("child diarrhea", "Pediatrics"),
    ("newborn jaundice", "Pediatrics"),
    ("child growth problem", "Pediatrics"),
    ("vaccination", "Pediatrics"),
    ("child ear infection", "Pediatrics"),
    ("child not sleeping", "Pediatrics"),
    ("child weight loss", "Pediatrics"),
    ("child sore throat", "Pediatrics"),
    ("child breathing problem", "Pediatrics"),
    ("baby stomach pain", "Pediatrics"),
    ("child delayed development", "Pediatrics"),
    ("child allergies", "Pediatrics"),
    ("child headache", "Pediatrics"),
    ("adolescent health", "Pediatrics"),
    ("teething problems", "Pediatrics"),
    ("pediatric checkup", "Pediatrics"),
    ("baby colics", "Pediatrics"),

    # ── PSYCHIATRY (Mental Health) ──
    ("depression", "Psychiatry"),
    ("anxiety", "Psychiatry"),
    ("stress", "Psychiatry"),
    ("panic attack", "Psychiatry"),
    ("insomnia", "Psychiatry"),
    ("sleep problems", "Psychiatry"),
    ("mood swings", "Psychiatry"),
    ("mental health", "Psychiatry"),
    ("suicidal thoughts", "Psychiatry"),
    ("hallucinations", "Psychiatry"),
    ("paranoia", "Psychiatry"),
    ("bipolar disorder", "Psychiatry"),
    ("schizophrenia", "Psychiatry"),
    ("eating disorder", "Psychiatry"),
    ("obsessive thoughts", "Psychiatry"),
    ("phobia", "Psychiatry"),
    ("trauma", "Psychiatry"),
    ("addiction", "Psychiatry"),
    ("memory loss", "Psychiatry"),
    ("concentration problems", "Psychiatry"),
    ("feeling worthless", "Psychiatry"),
    ("social anxiety", "Psychiatry"),
    ("anger issues", "Psychiatry"),
    ("post traumatic stress", "Psychiatry"),
    ("dementia", "Psychiatry"),
    ("self harm", "Psychiatry"),
    ("excessive worry", "Psychiatry"),

    # ── DERMATOLOGY (Skin, Hair, Nails) ──
    ("skin rash", "Dermatology"),
    ("acne", "Dermatology"),
    ("skin itching", "Dermatology"),
    ("eczema", "Dermatology"),
    ("psoriasis", "Dermatology"),
    ("skin infection", "Dermatology"),
    ("hair loss", "Dermatology"),
    ("dandruff", "Dermatology"),
    ("skin allergy", "Dermatology"),
    ("hives", "Dermatology"),
    ("warts", "Dermatology"),
    ("moles", "Dermatology"),
    ("skin discoloration", "Dermatology"),
    ("fungal infection skin", "Dermatology"),
    ("dry skin", "Dermatology"),
    ("oily skin", "Dermatology"),
    ("skin peeling", "Dermatology"),
    ("nail infection", "Dermatology"),
    ("ringworm", "Dermatology"),
    ("sunburn", "Dermatology"),
    ("skin darkening", "Dermatology"),
    ("pimples", "Dermatology"),
    ("blisters", "Dermatology"),
    ("skin sores", "Dermatology"),
    ("vitiligo", "Dermatology"),
    ("skin cancer suspicion", "Dermatology"),
    ("excessive sweating", "Dermatology"),

    # ── DENTISTRY (Teeth & Gums) ──
    ("tooth pain", "Dentistry"),
    ("toothache", "Dentistry"),
    ("gum pain", "Dentistry"),
    ("tooth decay", "Dentistry"),
    ("bleeding gums", "Dentistry"),
    ("bad breath", "Dentistry"),
    ("mouth sores", "Dentistry"),
    ("jaw pain", "Dentistry"),
    ("broken tooth", "Dentistry"),
    ("tooth sensitivity", "Dentistry"),
    ("swollen gums", "Dentistry"),
    ("wisdom tooth", "Dentistry"),
    ("teeth grinding", "Dentistry"),
    ("mouth infection", "Dentistry"),
    ("dental cavity", "Dentistry"),
    ("loose tooth", "Dentistry"),
    ("missing tooth", "Dentistry"),
    ("teeth whitening", "Dentistry"),
    ("dry mouth", "Dentistry"),
    ("tongue pain", "Dentistry"),
    ("crooked teeth", "Dentistry"),
    ("orthodontic issues", "Dentistry"),

    # ── ENT / OTOLARYNGOLOGY (Ear, Nose, Throat) ──
    ("ear pain", "ENT"),
    ("hearing loss", "ENT"),
    ("ringing in ears", "ENT"),
    ("tinnitus", "ENT"),
    ("ear infection", "ENT"),
    ("nose bleed", "ENT"),
    ("sinus pain", "ENT"),
    ("blocked nose", "ENT"),
    ("sore throat ENT", "ENT"),
    ("difficulty swallowing", "ENT"),
    ("hoarse voice", "ENT"),
    ("dizziness ear", "ENT"),
    ("vertigo", "ENT"),
    ("snoring", "ENT"),
    ("nasal allergy", "ENT"),
    ("deviated septum", "ENT"),
    ("tonsillitis", "ENT"),
    ("ear wax buildup", "ENT"),

    # ── GASTROENTEROLOGY (Digestive System) ──
    ("stomach pain after eating", "Gastroenterology"),
    ("frequent acid reflux", "Gastroenterology"),
    ("bleeding while pooping", "Gastroenterology"),
    ("dark tarry stool", "Gastroenterology"),
    ("difficulty swallowing food", "Gastroenterology"),
    ("yellow eyes jaundice", "Gastroenterology"),
    ("unexplained loss of appetite", "Gastroenterology"),
    ("rectal bleeding", "Gastroenterology"),
    ("chronic constipation", "Gastroenterology"),
    ("pale colored stool", "Gastroenterology"),
    ("severe abdominal cramps", "Gastroenterology"),
    ("stomach pain", "Gastroenterology"),
    ("acid reflux", "Gastroenterology"),
    ("heartburn", "Gastroenterology"),
    ("bloating", "Gastroenterology"),
    ("gas and bloating", "Gastroenterology"),
    ("constipation gastro", "Gastroenterology"),
    ("diarrhea persistent", "Gastroenterology"),
    ("blood in stool", "Gastroenterology"),
    ("black stool", "Gastroenterology"),
    ("nausea and vomiting", "Gastroenterology"),
    ("indigestion gastro", "Gastroenterology"),
    ("jaundice", "Gastroenterology"),
    ("liver pain", "Gastroenterology"),
    ("gallbladder pain", "Gastroenterology"),
    ("loss of appetite gastro", "Gastroenterology"),
    ("difficulty digesting", "Gastroenterology"),
    ("irritable bowel", "Gastroenterology"),
    ("hemorrhoids", "Gastroenterology"),
    ("piles", "Gastroenterology"),

    # ── NEUROLOGY (Brain & Nervous System) ──
    ("severe headache", "Neurology"),
    ("migraine", "Neurology"),
    ("seizures", "Neurology"),
    ("epilepsy", "Neurology"),
    ("dizziness neurology", "Neurology"),
    ("numbness in limbs", "Neurology"),
    ("tingling sensation", "Neurology"),
    ("slurred speech", "Neurology"),
    ("weakness in one side of body", "Neurology"),
    ("stroke symptoms", "Neurology"),
    ("tremores", "Neurology"),
    ("shaking hands", "Neurology"),
    ("coordination problems", "Neurology"),
    ("forgetfulness", "Neurology"),
    ("confusion", "Neurology"),
    ("fainting neurology", "Neurology"),
    ("nerve pain", "Neurology"),
    ("loss of balance", "Neurology"),
    ("difficulty walking straight", "Neurology"),
    ("sudden vision change", "Neurology"),
    ("uncontrolled shaking", "Neurology"),
    ("memory issues", "Neurology"),
    ("brain fog severe", "Neurology"),
    ("pins and needles sensation", "Neurology"),
    ("drooping face", "Neurology"),
    ("sudden weakness in limbs", "Neurology"),
    ("slurred speech", "Neurology"),
    ("facial drooping", "Neurology"),
    ("numbness on one side of body", "Neurology"),
    ("worst headache of life", "Neurology"),
    ("seeing double vision", "Neurology"),
    ("inability to understand speech", "Neurology"),
    ("seizure episode", "Neurology"),
    ("shaking hands tremors", "Neurology"),
    ("burning sensation skin", "Neurology"),
    ("vertigo and spinning", "Neurology"),
    ("ringing in ears", "Neurology"),

    # ── GYNECOLOGY & OBSTETRICS (Women's Health) ──
    ("menstrual pain", "Gynecology"),
    ("irregular periods", "Gynecology"),
    ("heavy bleeding", "Gynecology"),
    ("pregnancy symptoms", "Gynecology"),
    ("morning sickness", "Gynecology"),
    ("pelvic pain", "Gynecology"),
    ("vaginal discharge", "Gynecology"),
    ("vaginal itching", "Gynecology"),
    ("breast pain", "Gynecology"),
    ("breast lump", "Gynecology"),
    ("menopause symptoms", "Gynecology"),
    ("infertility", "Gynecology"),
    ("pcos symptoms", "Gynecology"),
    ("ovarian pain", "Gynecology"),
    ("antenatal care", "Gynecology"),

    # ── UROLOGY (Urinary & Men's Health) ──
    ("painful urination", "Urology"),
    ("burning during urination", "Urology"),
    ("frequent urination night", "Urology"),
    ("blood in urine", "Urology"),
    ("kidney pain", "Urology"),
    ("kidney stone", "Urology"),
    ("prostate problems", "Urology"),
    ("difficulty starting urination", "Urology"),
    ("testicular pain", "Urology"),
    ("erectile dysfunction", "Urology"),
    ("urinary incontinence", "Urology"),
    ("bladder pain", "Urology"),
    ("pee hurts", "Urology"),
    ("hurts when i pee", "Urology"),
    ("blood in pee", "Urology"),
    ("peeing blood", "Urology"),
    ("uti urinary tract infection", "Urology"),
    ("dark urine", "Urology"),
    ("smelly urine", "Urology"),
    ("frequent peeing", "Urology"),

    # ── PULMONOLOGY (Lungs & Breathing) ──
    ("persistent cough pulmonology", "Pulmonology"),
    ("shortness of breath", "Pulmonology"),
    ("wheezing sound", "Pulmonology"),
    ("chronic mucus cough", "Pulmonology"),
    ("blood in cough", "Pulmonology"),
    ("whistling noise chest", "Pulmonology"),
    ("sharp chest pain when breathing", "Pulmonology"),
    ("tightness in chest respiratory", "Pulmonology"),
    ("bluish lips or nails", "Pulmonology"),
    ("frequent lung infections", "Pulmonology"),
    ("wheezing", "Pulmonology"),
    ("chest congestion", "Pulmonology"),
    ("coughing up blood", "Pulmonology"),
    ("asthma", "Pulmonology"),
    ("bronchitis", "Pulmonology"),
    ("pneumonia", "Pulmonology"),
    ("dry cough", "Pulmonology"),
    ("difficulty breathing", "Pulmonology"),
    ("lung infection", "Pulmonology"),
    ("sleep apnea", "Pulmonology"),

    # ── ENDOCRINOLOGY (Hormones & Diabetes) ──
    ("diabetes", "Endocrinology"),
    ("excessive thirst and urination", "Endocrinology"),
    ("blurred vision diabetes", "Endocrinology"),
    ("unexplained weight gain", "Endocrinology"),
    ("heat intolerance", "Endocrinology"),
    ("cold intolerance", "Endocrinology"),
    ("mood swings hormonal", "Endocrinology"),
    ("hair loss hormonal", "Endocrinology"),
    ("dry skin endocrine", "Endocrinology"),
    ("loss of sex drive", "Endocrinology"),
    ("sugar levels high", "Endocrinology"),
    ("high blood sugar", "Endocrinology"),
    ("excessive thirst", "Endocrinology"),
    ("unexplained weight loss", "Endocrinology"),
    ("thyroid swelling", "Endocrinology"),
    ("goiter", "Endocrinology"),
    ("excessive fatigue hormones", "Endocrinology"),
    ("feeling too cold or hot", "Endocrinology"),
    ("hormonal imbalance", "Endocrinology"),
    ("polycystic ovary", "Endocrinology"),
    ("low energy hormones", "Endocrinology"),

    # ── GENERAL PHYSICIAN (Common Ailments) ──
    ("fever", "General Physician"),
    ("cold", "General Physician"),
    ("cough", "General Physician"),
    ("headache", "General Physician"),
    ("body pain", "General Physician"),
    ("fatigue", "General Physician"),
    ("weakness", "General Physician"),
    ("nausea", "General Physician"),
    ("vomiting", "General Physician"),
    ("diarrhea", "General Physician"),
    ("stomach ache", "General Physician"),
    ("abdominal pain", "General Physician"),
    ("loss of appetite", "General Physician"),
    ("weight loss", "General Physician"),
    ("constipation", "General Physician"),
    ("indigestion", "General Physician"),
    ("sore throat", "General Physician"),
    ("runny nose", "General Physician"),
    ("flu", "General Physician"),
    ("infection common", "General Physician"),
    ("general checkup", "General Physician"),
    ("high fever", "General Physician"),
    ("body aches", "General Physician"),
    ("shivering", "General Physician"),

    # ── ONCOLOGY (Cancer) ──
    ("cancer", "Oncology"),
    ("tumor", "Oncology"),
    ("chemotherapy", "Oncology"),
    ("radiation therapy", "Oncology"),
    ("malignant growth", "Oncology"),
    ("unexplained weight loss", "Oncology"),
    ("lump in body", "Oncology"),
    ("abnormal biopsy", "Oncology"),
    ("new lump in breast", "Oncology"),
    ("rapid weight loss", "Oncology"),
    ("extreme fatigue and weight loss", "Oncology"),
    ("new skin growth", "Oncology"),
    ("changing mole", "Oncology"),
    ("night sweats and weight loss", "Oncology"),
    ("constant bloating and weight loss", "Oncology"),
    ("unusual bleeding", "Oncology"),
    ("chronic cough with weight loss", "Oncology"),
    ("swollen lymph nodes", "Oncology"),
    ("hard lump on neck", "Oncology"),
    ("hard lump on abdomen", "Oncology"),
    ("bone pain at night", "Oncology"),
    ("blood in cough oncology", "Oncology"),
    ("growth on skin cancer", "Oncology"),
    ("non healing ulcer", "Oncology"),
    ("unusual breast discharge", "Oncology"),
    ("persistent bloating oncology", "Oncology"),
    ("mouth ulcer not healing", "Oncology"),
    ("jaundice and weight loss", "Oncology"),
    ("unexplained bruising", "Oncology"),

    # ── NEPHROLOGY (Kidney) ──
    ("kidney disease", "Nephrology"),
    ("renal failure", "Nephrology"),
    ("dialysis", "Nephrology"),
    ("kidney function", "Nephrology"),
    ("protein in urine", "Nephrology"),
    ("puffy eyes in morning", "Nephrology"),
    ("foamy urine", "Nephrology"),
    ("foamy bubbles in urine", "Nephrology"),
    ("proteinuria", "Nephrology"),
    ("renal failure symptoms", "Nephrology"),
    ("kidney swelling", "Nephrology"),
    ("edema puffy eyes", "Nephrology"),
    ("swelling in face morning", "Nephrology"),
    ("decreased urine output", "Nephrology"),
    ("high creatinine levels", "Nephrology"),
    ("kidney stone pain renal", "Nephrology"),
    ("metallic taste kidneys", "Nephrology"),
    ("puffy lower eyelids", "Nephrology"),
    ("urine foamy kidney", "Nephrology"),
    ("chronic kidney failure", "Nephrology"),
    ("blood in urine nephro", "Nephrology"),

    # ── HEMATOLOGY (Blood) ──
    ("blood disorder", "Hematology"),
    ("anemia", "Hematology"),
    ("low iron blood", "Hematology"),
    ("clotting problem", "Hematology"),
    ("platelet count low", "Hematology"),
    ("bruising easily", "Hematology"),
    ("blood test abnormal", "Hematology"),

    # ── RHEUMATOLOGY (Autoimmune & Joints) ──
    ("rheumatoid arthritis", "Rheumatology"),
    ("autoimmune joint disease", "Rheumatology"),
    ("joint inflammation autoimmune", "Rheumatology"),
    ("lupus systemic", "Rheumatology"),
    ("chronic joint swelling autoimmune", "Rheumatology"),
    ("stiff joints morning", "Rheumatology"),
    ("vasculitis", "Rheumatology"),
    ("gout", "Rheumatology"),
    ("ankylosing spondylitis", "Rheumatology"),
    ("psoriatic arthritis", "Rheumatology"),
    ("connective tissue disease", "Rheumatology"),
    ("sjögren syndrome", "Rheumatology"),
    ("fibromyalgia chronic pain", "Rheumatology"),
    ("joint pain systemic", "Rheumatology"),
    ("autoimmune symptoms", "Rheumatology"),

    # ── INFECTIOUS DISEASE ──
    ("viral infection", "Infectious Disease"),
    ("bacterial infection", "Infectious Disease"),
    ("covid symptoms", "Infectious Disease"),
    ("malaria", "Infectious Disease"),
    ("typhoid", "Infectious Disease"),
    ("high contagious fever", "Infectious Disease"),
    ("chronic infection", "Infectious Disease"),

    # ── ALLERGY & IMMUNOLOGY ──
    ("allergic reaction", "Allergy & Immunology"),
    ("immune system deficiency", "Allergy & Immunology"),
    ("hypersensitivity", "Allergy & Immunology"),
    ("allergy asthma", "Allergy & Immunology"),
    ("anaphylaxis", "Allergy & Immunology"),

    # ── EMERGENCY MEDICINE ──
    ("emergency care", "Emergency Medicine"),
    ("er visit", "Emergency Medicine"),
    ("accident injury", "Emergency Medicine"),
    ("trauma case", "Emergency Medicine"),
    ("critical condition", "Emergency Medicine"),

    # ── FAMILY MEDICINE ──
    ("family doctor visit", "Family Medicine"),
    ("primary health care", "Family Medicine"),
    ("general family health", "Family Medicine"),

    # ── NEUROSURGERY ──
    ("brain surgery", "Neurosurgery"),
    ("spinal surgery", "Neurosurgery"),
    ("neurosurgeon consultation", "Neurosurgery"),

    # ── CARDIOTHORACIC SURGERY ──
    ("cardiac surgery", "Cardiothoracic Surgery"),
    ("heart surgery", "Cardiothoracic Surgery"),
    ("thoracic surgery", "Cardiothoracic Surgery"),

    # ── PLASTIC SURGERY ──
    ("plastic surgery", "Plastic Surgery"),
    ("cosmetic surgery", "Plastic Surgery"),
    ("reconstructive surgery", "Plastic Surgery"),

    # ── VASCULAR SURGERY ──
    ("vascular problems", "Vascular Surgery"),
    ("blood vessel surgery", "Vascular Surgery"),
    ("artery vein surgery", "Vascular Surgery"),

    # ── SPORTS MEDICINE ──
    ("sports injury", "Sports Medicine"),
    ("athlete muscle tear", "Sports Medicine"),
    ("ligament injury sports", "Sports Medicine"),

    # ── GERIATRICS ──
    ("elderly care", "Geriatrics"),
    ("senior health problems", "Geriatrics"),
    ("aging related disease", "Geriatrics"),

    # ── SLEEP MEDICINE ──
    ("sleep disorder", "Sleep Medicine"),
    ("insomnia", "Sleep Medicine"),
    ("sleep apnea", "Sleep Medicine"),

    # ── PAIN MANAGEMENT ──
    ("pain clinic", "Pain Management"),
    ("chronic pain relief", "Pain Management"),
    ("pain management therapy", "Pain Management"),

    # ── RADIOLOGY ──
    ("mri scan", "Radiology"),
    ("ct scan", "Radiology"),
    ("x-ray imaging", "Radiology"),

    # ── PATHOLOGY ──
    ("pathology lab test", "Pathology"),
    ("biopsy analysis", "Pathology"),
    ("blood test lab", "Pathology"),

    # ── PHYSIOTHERAPY ──
    ("physiotherapy session", "Physiotherapy"),
    ("physical therapy", "Physiotherapy"),
    ("muscle recovery exercise", "Physiotherapy"),

    # ── NUTRITION & DIETETICS ──
    ("dietitian advice", "Nutrition & Dietetics"),
    ("nutrition plan", "Nutrition & Dietetics"),
    ("weight loss diet", "Nutrition & Dietetics"),

    # ── REHABILITATION MEDICINE ──
    ("rehabilitation therapy", "Rehabilitation Medicine"),
    ("functional recovery", "Rehabilitation Medicine"),

    # ── SPEECH THERAPY ──
    ("speech disorder", "Speech Therapy"),
    ("communication difficulty therapy", "Speech Therapy"),

    # ── OCCUPATIONAL THERAPY ──
    ("occupational therapy recovery", "Occupational Therapy"),
    ("relearning daily tasks", "Occupational Therapy"),

    # ── CRITICAL CARE ──
    ("icu admission", "Critical Care"),
    ("life support", "Critical Care"),
    ("intensive care unit", "Critical Care"),
]

# ═══════════════════════════════════════════════════════════════
# SPECIALTY → DEPARTMENT NAME MAPPING
# ═══════════════════════════════════════════════════════════════

SPECIALTY_DEPARTMENT_MAP = {
    "Cardiology":       ["Cardiology", "Cardio", "Heart"],
    "Ophthalmology":    ["Ophthalmology", "Eye", "Ophthal", "Optic"],
    "Orthopedics":      ["Orthopedics", "Orthopedic", "Ortho", "Bone", "Joint"],
    "Pediatrics":       ["Pediatrics", "Pediatric", "Child", "Children", "Infant"],
    "Psychiatry":       ["Psychiatry", "Mental Health", "Psychology", "Behavio"],
    "Dermatology":      ["Dermatology", "Skin", "Derma", "Hair"],
    "Dentistry":        ["Dentistry", "Dental", "Dentist", "Oral"],
    "ENT":              ["ENT", "Otolaryngology", "Ear", "Nose", "Throat"],
    "Gastroenterology": ["Gastroenterology", "Gastro", "Digestive", "Liver", "Stomach"],
    "Neurology":        ["Neurology", "Neuro", "Brain", "Nerve"],
    "Gynecology":       ["Gynecology", "Obstetrics", "Gynae", "OBS", "Women", "Maternity"],
    "Urology":          ["Urology", "Urinary", "Kidney", "Bladder"],
    "Pulmonology":      ["Pulmonology", "Chest", "Respiratory", "Lung"],
    "Endocrinology":    ["Endocrinology", "Endocrine", "Diabetes", "Thyroid", "Hormone"],
    "General Physician":["General", "OPD", "Medicine", "Internal", "Physician"],
    "Oncology":         ["Oncology", "Cancer", "Tumor", "Chemotherapy", "Radiation therapy"],
    "Nephrology":       ["Nephrology", "Kidney", "Renal", "Dialysis"],
    "Hematology":       ["Hematology", "Blood disorder", "Anemia", "Clotting", "Platelet"],
    "Rheumatology":     ["Rheumatology", "Arthritis", "Autoimmune", "Joint inflammation", "Lupus"],
    "Infectious Disease": ["Infectious", "Infection", "Virus", "Bacteria", "COVID", "Malaria", "Typhoid"],
    "Allergy & Immunology": ["Allergy", "Immune", "Immunology", "Hypersensitivity", "Asthma allergy"],
    "Emergency Medicine": ["Emergency", "ER", "Accident", "Trauma", "Critical care"],
    "Family Medicine":  ["Family doctor", "Primary care", "Family medicine", "General care"],
    "Neurosurgery":     ["Neurosurgery", "Brain surgery", "Spinal surgery", "Neuro surgery"],
    "Cardiothoracic Surgery": ["Cardiac surgery", "Heart surgery", "Thoracic surgery"],
    "Plastic Surgery":  ["Plastic surgery", "Cosmetic surgery", "Reconstructive surgery"],
    "Vascular Surgery": ["Vascular", "Blood vessel", "Artery", "Vein surgery"],
    "Sports Medicine":  ["Sports injury", "Athlete injury", "Muscle injury", "Ligament injury"],
    "Geriatrics":       ["Geriatrics", "Elderly care", "Senior health", "Aging diseases"],
    "Sleep Medicine":   ["Sleep disorder", "Insomnia", "Sleep apnea", "Sleep problems"],
    "Pain Management":  ["Pain clinic", "Chronic pain", "Pain management"],
    "Radiology":        ["Radiology", "MRI", "CT scan", "X-ray", "Imaging"],
    "Pathology":        ["Pathology", "Lab test", "Biopsy", "Blood test"],
    "Physiotherapy":    ["Physiotherapy", "Physical therapy", "Rehabilitation", "Muscle recovery"],
    "Nutrition & Dietetics": ["Dietitian", "Nutrition", "Diet", "Weight loss", "Obesity"],
    "Rehabilitation Medicine": ["Rehabilitation", "Recovery therapy", "Physical rehab"],
    "Speech Therapy":   ["Speech therapy", "Speech disorder", "Communication disorder"],
    "Occupational Therapy": ["Occupational therapy", "Functional recovery"],
    "Critical Care":    ["ICU", "Critical care", "Life support", "Intensive care"]
}

# ═══════════════════════════════════════════════════════════════
# SPECIALTY ICONS & COLORS
# ═══════════════════════════════════════════════════════════════

SPECIALTY_META = {
    "Cardiology":        {"icon": "fa-heart-pulse",      "color": "#dc3545"},
    "Ophthalmology":     {"icon": "fa-eye",              "color": "#0056b3"},
    "Orthopedics":       {"icon": "fa-bone",             "color": "#fd7e14"},
    "Pediatrics":        {"icon": "fa-child",            "color": "#20c997"},
    "Psychiatry":        {"icon": "fa-brain",            "color": "#6f42c1"},
    "Dermatology":       {"icon": "fa-hand-dots",        "color": "#e91e8c"},
    "Dentistry":         {"icon": "fa-tooth",            "color": "#17a2b8"},
    "ENT":               {"icon": "fa-ear-listen",       "color": "#6610f2"},
    "Gastroenterology":  {"icon": "fa-notes-medical",    "color": "#8d6e63"},
    "Neurology":         {"icon": "fa-brain",            "color": "#2c3e50"},
    "Gynecology":        {"icon": "fa-venus",            "color": "#f06292"},
    "Urology":           {"icon": "fa-mars",             "color": "#4fc3f7"},
    "Pulmonology":       {"icon": "fa-lungs",            "color": "#aed581"},
    "Endocrinology":     {"icon": "fa-flask",            "color": "#ffd54f"},
    "General Physician": {"icon": "fa-stethoscope",      "color": "#2e8b57"},
    "Oncology":          {"icon": "fa-dna",              "color": "#9b59b6"},
    "Nephrology":        {"icon": "fa-vial",             "color": "#3498db"},
    "Hematology":        {"icon": "fa-droplet",          "color": "#c0392b"},
    "Rheumatology":      {"icon": "fa-joint",            "color": "#e67e22"},
    "Infectious Disease":{"icon": "fa-virus",            "color": "#27ae60"},
    "Allergy & Immunology":{"icon": "fa-shield-virus",    "color": "#2980b9"},
    "Emergency Medicine":{"icon": "fa-truck-medical",    "color": "#e74c3c"},
    "Family Medicine":   {"icon": "fa-house-user",       "color": "#16a085"},
    "Neurosurgery":      {"icon": "fa-brain",            "color": "#2c3e50"},
    "Cardiothoracic Surgery":{"icon": "fa-heart",        "color": "#c0392b"},
    "Plastic Surgery":   {"icon": "fa-sparkles",         "color": "#ff69b4"},
    "Vascular Surgery":  {"icon": "fa-droplet",          "color": "#e74c3c"},
    "Sports Medicine":   {"icon": "fa-person-running",   "color": "#2980b9"},
    "Geriatrics":        {"icon": "fa-person-cane",      "color": "#7f8c8d"},
    "Sleep Medicine":    {"icon": "fa-bed",              "color": "#2c3e50"},
    "Pain Management":   {"icon": "fa-syringe",          "color": "#e67e22"},
    "Radiology":         {"icon": "fa-x-ray",            "color": "#34495e"},
    "Pathology":         {"icon": "fa-microscope",       "color": "#8e44ad"},
    "Physiotherapy":     {"icon": "fa-person-walking",   "color": "#27ae60"},
    "Nutrition & Dietetics":{"icon": "fa-apple-whole",    "color": "#e67e22"},
    "Rehabilitation Medicine":{"icon": "fa-wheelchair",  "color": "#2980b9"},
    "Speech Therapy":    {"icon": "fa-comment-dots",     "color": "#3498db"},
    "Occupational Therapy":{"icon": "fa-briefcase-medical","color": "#16a085"},
    "Critical Care":     {"icon": "fa-hospital-user",    "color": "#c0392b"},
}

# ═══════════════════════════════════════════════════════════════
# TRAIN & SAVE MODEL
# ═══════════════════════════════════════════════════════════════

MODEL_PATH = os.path.join(os.path.dirname(__file__), "symptom_model.pkl")

def train_model():
    texts  = [item[0] for item in TRAINING_DATA]
    labels = [item[1] for item in TRAINING_DATA]

    model = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), lowercase=True)),
        ("clf",   MultinomialNB(alpha=0.1)),
    ])
    model.fit(texts, labels)
    joblib.dump(model, MODEL_PATH)
    return model

def load_model():
    if os.path.exists(MODEL_PATH):
        try:
            return joblib.load(MODEL_PATH)
        except:
            return train_model()
    return train_model()

# ═══════════════════════════════════════════════════════════════
# PREDICT SPECIALTY FROM SYMPTOMS
# ═══════════════════════════════════════════════════════════════

def predict_specialty(symptom_text):
    model = load_model()
    symptom_text = symptom_text.lower().strip()

    # Get predictions with probabilities
    try:
        proba   = model.predict_proba([symptom_text])[0]
        classes = model.classes_
        top3_idx = np.argsort(proba)[::-1][:3]

        results = []
        for idx in top3_idx:
            specialty = classes[idx]
            confidence = round(proba[idx] * 100, 1)
            if confidence > 5:  # Only include if > 5% confidence
                meta = SPECIALTY_META.get(specialty, {"icon": "fa-stethoscope", "color": "#0056b3"})
                results.append({
                    "specialty":  specialty,
                    "confidence": confidence,
                    "icon":       meta["icon"],
                    "color":      meta["color"],
                    "dept_keywords": SPECIALTY_DEPARTMENT_MAP.get(specialty, [specialty]),
                })
        return results
    except:
        return []

# Force retraining if file is missing
if not os.path.exists(MODEL_PATH):
    train_model()