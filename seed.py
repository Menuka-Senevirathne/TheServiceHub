import os
from app import db, Appointment, Invoice, app

# Ensure the upload folder exists
UPLOAD_FOLDER = app.config.get('UPLOAD_FOLDER', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Optional: create dummy PDF files for invoices
dummy_pdf_path1 = os.path.join(UPLOAD_FOLDER, 'inv1.pdf')
dummy_pdf_path2 = os.path.join(UPLOAD_FOLDER, 'inv2.pdf')
for path in [dummy_pdf_path1, dummy_pdf_path2]:
    if not os.path.exists(path):
        with open(path, 'wb') as f:
            f.write(b'%PDF-1.4\n%Dummy PDF content\n%%EOF')

def seed_db():
    with app.app_context():
        db.create_all()

        # Skip seeding if data already exists
        if Appointment.query.first() or Invoice.query.first():
            print("Database already has data. Skipping seed.")
            return

        # ---------------- Sample Appointments ---------------- #
        sample_appointments = [
            Appointment(customer_id='001', vehicle_category='Car', job_description='Oil change'),
            Appointment(customer_id='002', vehicle_category='Bike', job_description='Brake repair'),
            Appointment(customer_id='003', vehicle_category='Truck', job_description='Engine check'),
            Appointment(customer_id='004', vehicle_category='Car', job_description='Tire rotation'),
            Appointment(customer_id='005', vehicle_category='Motorbike', job_description='Chain lubrication')
        ]

        # ---------------- Sample Invoices ---------------- #
        sample_invoices = [
            Invoice(branch_manager='Alice', branch='Colombo Central', total_cost='1500', filename='inv1.pdf', upload_path=dummy_pdf_path1),
            Invoice(branch_manager='Bob', branch='Kandy Branch', total_cost='2500', filename='inv2.pdf', upload_path=dummy_pdf_path2)
        ]

        # Insert into DB
        db.session.bulk_save_objects(sample_appointments + sample_invoices)
        db.session.commit()
        print("Sample data inserted successfully!")

if __name__ == "__main__":
    seed_db()
