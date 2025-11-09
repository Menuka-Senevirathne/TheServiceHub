import os
from datetime import datetime
from flask import Flask, request, jsonify, abort, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)

# -------------------- CONFIG -------------------- #
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///theservicehub.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -------------------- MODELS -------------------- #
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(100), nullable=False)
    vehicle_category = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    branch_manager = db.Column(db.String(100), nullable=False)
    branch = db.Column(db.String(200), nullable=False)
    total_cost = db.Column(db.String(300), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    upload_path = db.Column(db.String(300), nullable=False)
    status = db.Column(db.String(50), default='draft')
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

# -------------------- UTILITIES -------------------- #
def error_response(message, code):
    return jsonify({'error': message}), code

# -------------------- ROUTES -------------------- #

@app.route('/')
def index():
    return jsonify({'message': 'The Service Hub backend is running'}), 200


# -------------------- APPOINTMENTS -------------------- #

# Create new appointment
@app.route('/appointments', methods=['POST'])
def create_appointment():
    data = request.get_json()
    if not data:
        return error_response('Request body must be JSON', 400)
    
    required = ['customer_id', 'vehicle_category', 'job_description']
    if not all(k in data for k in required):
        return error_response('Missing required fields: customer_id, vehicle_category, job_description', 400)

    appointment = Appointment(
        customer_id=data['customer_id'],
        vehicle_category=data['vehicle_category'],
        job_description=data['job_description']
    )
    db.session.add(appointment)
    db.session.commit()

    return jsonify({
        'message': 'Appointment created successfully',
        'appointment': {
            'id': appointment.id,
            'status': appointment.status,
            'links': {
                'self': url_for('get_appointment', appointment_id=appointment.id, _external=True)
            }
        }
    }), 201


# Get all appointments
@app.route('/appointments', methods=['GET'])
def get_appointments():
    customer_id = request.args.get('customer_id')
    query = Appointment.query
    if customer_id:
        query = query.filter_by(customer_id=customer_id)
    appointments = query.all()

    return jsonify([
        {
            'id': a.id,
            'customer_id': a.customer_id,
            'vehicle_category': a.vehicle_category,
            'job_description': a.job_description,
            'status': a.status,
            'created_at': a.created_at.strftime('%Y-%m-%d %H:%M')
        } for a in appointments
    ]), 200


# Get single appointment
@app.route('/appointments/<int:appointment_id>', methods=['GET'])
def get_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    return jsonify({
        'id': appointment.id,
        'customer_id': appointment.customer_id,
        'vehicle_category': appointment.vehicle_category,
        'job_description': appointment.job_description,
        'status': appointment.status,
        'created_at': appointment.created_at.strftime('%Y-%m-%d %H:%M')
    }), 200


# Update appointment status (PATCH — admin action)
@app.route('/appointments/<int:appointment_id>', methods=['PATCH'])
def update_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    data = request.get_json()

    if not data or 'status' not in data:
        return error_response('Missing status field in request body', 400)

    # Allowed statuses
    allowed_statuses = {'scheduled', 'rejected'}
    new_status = data['status'].lower()

    if new_status not in allowed_statuses:
        return error_response(f"Invalid status. Allowed values are: {', '.join(allowed_statuses)}", 400)

    appointment.status = new_status
    db.session.commit()
    return jsonify({'message': 'Status updated successfully', 'status': appointment.status}), 200



# -------------------- INVOICES -------------------- #

# Upload new invoice
@app.route('/invoices', methods=['POST'])
def upload_invoice():
    if 'upload_file' not in request.files:
        return error_response('No file part in request', 400)

    file = request.files['upload_file']
    branch_manager = request.form.get('branch_manager')
    branch = request.form.get('branch')
    total_cost = request.form.get('total_cost')

    # Validation
    if not file or file.filename == '':
        return error_response('No file selected', 400)
    if not branch_manager or not branch or not total_cost:
        return error_response('Missing required fields: branch_manager, branch, or total_cost', 400)
    if not file.filename.lower().endswith('.pdf'):
        return error_response('Only PDF files are allowed', 400)

    # Save file
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Create invoice
    invoice = Invoice(
        branch_manager=branch_manager,
        branch=branch,
        total_cost=total_cost,
        filename=filename,
        upload_path=filepath,
        status='darfted'  
    )
    db.session.add(invoice)
    db.session.commit()

    # Return JSON response
    return jsonify({
        'message': 'Invoice uploaded successfully',
        'invoice': {
            'id': invoice.id,
            'filename': invoice.filename,
            'status': invoice.status,
            'links': {
                'self': url_for('get_invoice', invoice_id=invoice.id, _external=True)
            }
        }
    }), 201


@app.route('/invoices/<int:invoice_id>', methods=['PATCH'])
def update_invoice_status(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    data = request.get_json()
    
    if not data or 'status' not in data:
        return jsonify({'error': 'Missing status field'}), 400
    
    new_status = data['status'].lower()
    if new_status not in ['approved', 'rejected']:
        return jsonify({'error': 'Invalid status. Allowed values: approved, rejected'}), 400

    invoice.status = new_status
    db.session.commit()

    return jsonify({
        'message': f'Invoice status updated to {new_status}',
        'invoice_id': invoice.id,
        'status': invoice.status
    }), 200

# Get all invoices
@app.route('/invoices', methods=['GET'])
def get_invoices():
    invoices = Invoice.query.all()
    return jsonify([
        {
            'id': inv.id,
            'branch_manager': inv.branch_manager,
            'branch': inv.branch,
            'total_cost': inv.total_cost,
            'filename': inv.filename,
            'uploaded_at': inv.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
        } for inv in invoices
    ]), 200


# Get single invoice
@app.route('/invoices/<int:invoice_id>', methods=['GET'])
def get_invoice(invoice_id):
    inv = Invoice.query.get_or_404(invoice_id)
    return jsonify({
        'id': inv.id,
        'branch_manager': inv.branch_manager,
        'branch': inv.branch,
        'total_cost': inv.total_cost,
        'filename': inv.filename,
        'uploaded_at': inv.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
    }), 200


# -------------------- MAIN -------------------- #
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
