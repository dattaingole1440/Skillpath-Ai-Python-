import os
import uuid
import datetime
import qrcode
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from app.models.models import User, Career, Certificate

def generate_student_certificate(db: Session, student_id: int, career_id: int) -> Certificate:
    """
    Generates a personalized PDF certificate for a student who completed a career path.
    Saves the PDF and QR code files, stores the record in the database, and returns it.
    """
    # 1. Fetch Student & Career details
    student = db.query(User).filter(User.id == student_id).first()
    career = db.query(Career).filter(Career.id == career_id).first()
    
    if not student or not career:
        raise ValueError("Invalid student or career ID.")

    # Check if certificate already exists
    existing = db.query(Certificate).filter(
        Certificate.student_id == student_id,
        Certificate.career_id == career_id
    ).first()
    if existing:
        return existing

    # Create directories if they do not exist
    os.makedirs("app/static/uploads/certificates", exist_ok=True)
    os.makedirs("app/static/uploads/qrcodes", exist_ok=True)

    # 2. Generate unique Certificate Number
    date_str = datetime.date.today().strftime("%Y%m%d")
    unique_suffix = uuid.uuid4().hex[:6].upper()
    cert_number = f"SPAI-{date_str}-{unique_suffix}"

    # 3. Create Verification QR Code
    # In real deployment, change this to your public domain
    verify_url = f"http://127.0.0.1:8000/verify/certificate/{cert_number}"
    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(verify_url)
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_path = f"app/static/uploads/qrcodes/{cert_number}.png"
    qr_img.save(qr_path)

    # 4. Generate Certificate PDF using ReportLab
    pdf_path = f"app/static/uploads/certificates/{cert_number}.pdf"
    
    # Setup canvas (Landscape Letter size: 792 x 612 points)
    width, height = landscape(letter)
    c = canvas.Canvas(pdf_path, pagesize=landscape(letter))

    # --- Draw Elegant Background borders ---
    # Primary Dark Blue Border
    c.setStrokeColor(colors.HexColor("#0D6EFD")) # Bootstrap Blue
    c.setLineWidth(8)
    c.rect(20, 20, width - 40, height - 40)

    # Secondary Thin Gold/Orange Border
    c.setStrokeColor(colors.HexColor("#FFC107")) # Gold
    c.setLineWidth(2)
    c.rect(28, 28, width - 56, height - 56)

    # Accent corners
    c.setFillColor(colors.HexColor("#F8F9FA"))
    c.rect(34, 34, width - 68, height - 68, fill=True, stroke=False)

    # --- Title and Header Text ---
    c.setFillColor(colors.HexColor("#212529"))
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(width / 2.0, height - 120, "CERTIFICATE OF COMPLETION")

    c.setFillColor(colors.HexColor("#6C757D"))
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2.0, height - 160, "PROUDLY PRESENTED TO")

    # --- Student Name (Large Bold) ---
    c.setFillColor(colors.HexColor("#0D6EFD"))
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(width / 2.0, height - 230, student.name.upper())

    # --- Achievement Statement ---
    c.setFillColor(colors.HexColor("#212529"))
    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2.0, height - 280, "for successfully mastering all curriculum standards, hands-on projects,")
    c.drawCentredString(width / 2.0, height - 305, "and quiz evaluations to complete the specialized career track:")

    # --- Career Path Title ---
    c.setFillColor(colors.HexColor("#198754")) # Success Green
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2.0, height - 360, career.name)

    # --- Divider Line ---
    c.setStrokeColor(colors.HexColor("#E0E0E0"))
    c.setLineWidth(1)
    c.line(150, height - 400, width - 150, height - 400)

    # --- Footer Information (Verification, QR Code, Signatures) ---
    # Left side: Issue Date & Certificate Number
    c.setFillColor(colors.HexColor("#495057"))
    c.setFont("Helvetica", 10)
    c.drawString(70, 110, f"Date of Issue: {datetime.date.today().strftime('%B %d, %Y')}")
    c.drawString(70, 90, f"Certificate ID: {cert_number}")
    c.drawString(70, 70, "Verify validity via QR code scan.")

    # Middle: QR Code
    c.drawImage(qr_path, (width / 2.0) - 45, 60, width=90, height=90)
    c.setFont("Helvetica", 8)
    c.drawCentredString(width / 2.0, 50, "Scan to Verify")

    # Right side: Signature Placeholder
    c.setFont("Times-BoldItalic", 20)
    c.drawString(width - 250, 110, "SkillPath AI") # Digital Signature Text
    c.setStrokeColor(colors.HexColor("#495057"))
    c.setLineWidth(1)
    c.line(width - 270, 100, width - 70, 100) # Signature line
    c.setFont("Helvetica-Bold", 10)
    c.drawString(width - 210, 85, "Platform Director")

    # Save PDF Canvas
    c.showPage()
    c.save()

    # 5. Store record in database
    certificate = Certificate(
        student_id=student_id,
        career_id=career_id,
        certificate_number=cert_number,
        file_path=f"/static/uploads/certificates/{cert_number}.pdf",
        qr_code_path=f"/static/uploads/qrcodes/{cert_number}.png",
        signature_path=""
    )
    db.add(certificate)
    db.commit()
    db.refresh(certificate)

    return certificate
