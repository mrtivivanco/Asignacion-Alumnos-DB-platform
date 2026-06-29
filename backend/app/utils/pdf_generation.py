from io import BytesIO
from textwrap import wrap

from faker import Faker
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def generate_fake_exam_pdf(exam_id: int, exam_name: str, fake: Faker) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle(f"Prueba {exam_id}")

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(72, 730, "PDF de prueba generado")

    pdf.setFont("Helvetica", 11)
    pdf.drawString(72, 700, f"ID de prueba: {exam_id}")
    pdf.drawString(72, 682, f"Nombre de la prueba: {exam_name}")
    pdf.drawString(72, 664, "Proposito: datos locales deterministas para probar MongoDB GridFS")

    y = 625
    for question_number in range(1, 7):
        question = f"{question_number}. {fake.sentence(nb_words=12)}"
        for line in wrap(question, width=88):
            pdf.drawString(72, y, line)
            y -= 18
        y -= 8

        if y < 100:
            pdf.showPage()
            pdf.setFont("Helvetica", 11)
            y = 730

    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return buffer.read()
