from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'vehicle_maintenance_tracker'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Add template context processor
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

@app.context_processor
def inject_vehicles():
    if current_user.is_authenticated:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM vehicles WHERE user_id = %s', (current_user.id,))
        vehicles = cursor.fetchall()
        cursor.close()
        conn.close()
        # Convert each vehicle dictionary to a Vehicle object
        vehicle_objects = []
        for vehicle in vehicles:
            vehicle_objects.append({
                'id': vehicle['id'],
                'make': vehicle['make'],
                'model': vehicle['model'],
                'year': vehicle['year'],
                'license_plate': vehicle['license_plate']
            })
        return {'vehicles': vehicle_objects}
    return {'vehicles': []}

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, email, password_hash):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if user_data:
        return User(
            id=user_data['id'],
            username=user_data['username'],
            email=user_data['email'],
            password_hash=user_data['password_hash']
        )
    return None

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user_data and check_password_hash(user_data['password_hash'], password):
            user = User(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                password_hash=user_data['password_hash']
            )
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('auth/login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if username exists
        cursor.execute('SELECT id FROM users WHERE username = %s', (username,))
        if cursor.fetchone():
            flash('Username already exists')
            return redirect(url_for('signup'))
        
        # Check if email exists
        cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
        if cursor.fetchone():
            flash('Email already registered')
            return redirect(url_for('signup'))
        
        # Create new user
        password_hash = generate_password_hash(password)
        cursor.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)',
            (username, email, password_hash)
        )
        conn.commit()
        
        # Get the new user's ID
        user_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        user = User(id=user_id, username=username, email=email, password_hash=password_hash)
        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('auth/signup.html')

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get user's vehicles
    cursor.execute('SELECT * FROM vehicles WHERE user_id = %s', (current_user.id,))
    vehicles = cursor.fetchall()
    
    # Get upcoming maintenance
    cursor.execute('''
        SELECT mr.*, v.make, v.model, v.license_plate, st.name as service_type_name
        FROM maintenance_records mr
        JOIN vehicles v ON mr.vehicle_id = v.id
        JOIN service_types st ON mr.service_type_id = st.id
        WHERE v.user_id = %s AND mr.next_service_date >= CURDATE()
        ORDER BY mr.next_service_date
    ''', (current_user.id,))
    
    maintenance_records = cursor.fetchall()
    
    # Convert date strings to datetime objects and structure the data
    maintenance = {
        'due_soon': [],
        'upcoming': []
    }
    
    for record in maintenance_records:
        if record['next_service_date']:
            record['next_service_date'] = datetime.strptime(str(record['next_service_date']), '%Y-%m-%d').date()
            days_until = (record['next_service_date'] - datetime.now().date()).days
            
            # Structure the record
            structured_record = {
                'vehicle': {
                    'id': record['vehicle_id'],
                    'make': record['make'],
                    'model': record['model'],
                    'license_plate': record['license_plate']
                },
                'service_type': {
                    'name': record['service_type_name']
                },
                'next_service_date': record['next_service_date']
            }
            
            if days_until <= 7:
                maintenance['due_soon'].append(structured_record)
            else:
                maintenance['upcoming'].append(structured_record)
    
    cursor.close()
    conn.close()
    
    return render_template('dashboard/index.html', 
                         vehicles=vehicles,
                         maintenance=maintenance)

@app.route('/vehicles/add', methods=['GET', 'POST'])
@login_required
def add_vehicle():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO vehicles (user_id, make, model, year, license_plate)
                VALUES (%s, %s, %s, %s, %s)
            ''', (
                current_user.id,
                request.form.get('make'),
                request.form.get('model'),
                request.form.get('year'),
                request.form.get('license_plate')
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Vehicle added successfully!', 'success')
            return redirect(url_for('dashboard'))
        except mysql.connector.Error as err:
            if err.errno == 1062:  # Duplicate entry error
                flash('A vehicle with this license plate already exists.', 'error')
            else:
                flash('An error occurred while adding the vehicle.', 'error')
    return render_template('vehicles/add.html')

@app.route('/vehicles/<int:vehicle_id>/maintenance/add', methods=['GET', 'POST'])
@login_required
def add_maintenance(vehicle_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Check if vehicle belongs to user
    cursor.execute('SELECT * FROM vehicles WHERE id = %s AND user_id = %s', 
                  (vehicle_id, current_user.id))
    vehicle = cursor.fetchone()
    
    if not vehicle:
        cursor.close()
        conn.close()
        flash('Vehicle not found or you do not have permission to access it.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            service_date = datetime.strptime(request.form.get('service_date'), '%Y-%m-%d')
            next_service_date = None
            
            # Get service type for interval calculation
            cursor.execute('SELECT * FROM service_types WHERE id = %s', 
                          (request.form.get('service_type'),))
            service_type = cursor.fetchone()
            
            if service_type and service_type['recommended_interval_months']:
                next_service_date = service_date + timedelta(days=30 * service_type['recommended_interval_months'])
            
            cursor.execute('''
                INSERT INTO maintenance_records 
                (vehicle_id, service_type_id, service_date, mileage, cost, notes, next_service_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (
                vehicle_id,
                request.form.get('service_type'),
                service_date,
                request.form.get('mileage'),
                request.form.get('cost'),
                request.form.get('notes'),
                next_service_date
            ))
            
            conn.commit()
            flash('Maintenance record added successfully!', 'success')
            return redirect(url_for('vehicle_details', vehicle_id=vehicle_id))
        except Exception as e:
            conn.rollback()
            flash('Error adding maintenance record. Please try again.', 'error')
            print(f"Error: {str(e)}")
    
    # Get service types for the form
    cursor.execute('SELECT * FROM service_types')
    service_types = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('maintenance/add.html', 
                         vehicle=vehicle, 
                         service_types=service_types)

@app.route('/maintenance/<int:record_id>/edit', methods=['GET', 'POST'])
@login_required
def update_maintenance(record_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get maintenance record and verify ownership
    cursor.execute('''
        SELECT mr.*, v.user_id
        FROM maintenance_records mr
        JOIN vehicles v ON mr.vehicle_id = v.id
        WHERE mr.id = %s
    ''', (record_id,))
    record = cursor.fetchone()
    
    if not record or record['user_id'] != current_user.id:
        cursor.close()
        conn.close()
        flash('Maintenance record not found or you do not have permission to edit it.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            service_date = datetime.strptime(request.form.get('service_date'), '%Y-%m-%d')
            next_service_date = None
            
            # Get service type for interval calculation
            cursor.execute('SELECT * FROM service_types WHERE id = %s', 
                          (request.form.get('service_type'),))
            service_type = cursor.fetchone()
            
            if service_type and service_type['recommended_interval_months']:
                next_service_date = service_date + timedelta(days=30 * service_type['recommended_interval_months'])
            
            cursor.execute('''
                UPDATE maintenance_records 
                SET service_type_id = %s,
                    service_date = %s,
                    mileage = %s,
                    cost = %s,
                    notes = %s,
                    next_service_date = %s
                WHERE id = %s
            ''', (
                request.form.get('service_type'),
                service_date,
                request.form.get('mileage'),
                request.form.get('cost'),
                request.form.get('notes'),
                next_service_date,
                record_id
            ))
            
            conn.commit()
            flash('Maintenance record updated successfully!', 'success')
            return redirect(url_for('vehicle_details', vehicle_id=record['vehicle_id']))
        except Exception as e:
            conn.rollback()
            flash('Error updating maintenance record. Please try again.', 'error')
            print(f"Error: {str(e)}")
    
    # Get service types for the form
    cursor.execute('SELECT * FROM service_types')
    service_types = cursor.fetchall()
    
    # Get vehicle details
    cursor.execute('SELECT * FROM vehicles WHERE id = %s', (record['vehicle_id'],))
    vehicle = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return render_template('maintenance/edit.html', 
                         record=record,
                         vehicle=vehicle,
                         service_types=service_types)

@app.route('/vehicles/<int:vehicle_id>')
@login_required
def vehicle_details(vehicle_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get vehicle details
    cursor.execute('SELECT * FROM vehicles WHERE id = %s AND user_id = %s', 
                  (vehicle_id, current_user.id))
    vehicle = cursor.fetchone()
    
    if not vehicle:
        cursor.close()
        conn.close()
        flash('Vehicle not found or you do not have permission to access it.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get maintenance records
    cursor.execute('''
        SELECT mr.*, st.name as service_type_name
        FROM maintenance_records mr
        LEFT JOIN service_types st ON mr.service_type_id = st.id
        WHERE mr.vehicle_id = %s
        ORDER BY mr.service_date DESC
    ''', (vehicle_id,))
    
    maintenance_records = cursor.fetchall()
    
    # Convert date strings to datetime objects and then to date objects for comparison
    for record in maintenance_records:
        if record['service_date']:
            record['service_date'] = datetime.strptime(str(record['service_date']), '%Y-%m-%d').date()
        if record['next_service_date']:
            record['next_service_date'] = datetime.strptime(str(record['next_service_date']), '%Y-%m-%d').date()
    
    cursor.close()
    conn.close()
    
    return render_template('vehicles/details.html', 
                         vehicle=vehicle, 
                         maintenance_records=maintenance_records)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/history')
@login_required
def maintenance_history():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('''
        SELECT mr.*, v.make, v.model, v.license_plate, st.name as service_type_name
        FROM maintenance_records mr
        JOIN vehicles v ON mr.vehicle_id = v.id
        JOIN service_types st ON mr.service_type_id = st.id
        WHERE v.user_id = %s
        ORDER BY mr.service_date DESC
    ''', (current_user.id,))
    
    maintenance_records = cursor.fetchall()
    
    # Convert date strings to datetime objects and structure the data
    structured_records = []
    
    for record in maintenance_records:
        if record['service_date']:
            record['service_date'] = datetime.strptime(str(record['service_date']), '%Y-%m-%d').date()
        if record['next_service_date']:
            record['next_service_date'] = datetime.strptime(str(record['next_service_date']), '%Y-%m-%d').date()
        
        # Structure the record
        structured_record = {
            'id': record['id'],
            'vehicle': {
                'id': record['vehicle_id'],
                'make': record['make'],
                'model': record['model'],
                'license_plate': record['license_plate']
            },
            'service_type': {
                'name': record['service_type_name']
            },
            'service_date': record['service_date'],
            'next_service_date': record['next_service_date'],
            'mileage': record['mileage'],
            'cost': record['cost'],
            'notes': record['notes']
        }
        
        structured_records.append(structured_record)
    
    # Calculate total cost
    total_cost = sum(record['cost'] or 0 for record in maintenance_records)
    
    cursor.close()
    conn.close()
    
    return render_template('maintenance/history.html', 
                         maintenance_records=structured_records,
                         total_cost=total_cost)

@app.route('/vehicles/<int:vehicle_id>/delete', methods=['POST'])
@login_required
def delete_vehicle(vehicle_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Check if vehicle belongs to user
    cursor.execute('SELECT * FROM vehicles WHERE id = %s AND user_id = %s', 
                  (vehicle_id, current_user.id))
    vehicle = cursor.fetchone()
    
    if not vehicle:
        cursor.close()
        conn.close()
        flash('Vehicle not found or you do not have permission to delete it.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        # Delete maintenance records first (due to foreign key constraint)
        cursor.execute('DELETE FROM maintenance_records WHERE vehicle_id = %s', (vehicle_id,))
        # Delete the vehicle
        cursor.execute('DELETE FROM vehicles WHERE id = %s', (vehicle_id,))
        conn.commit()
        flash('Vehicle and its maintenance records have been deleted successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash('Error deleting vehicle. Please try again.', 'error')
        print(f"Error: {str(e)}")
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True) 