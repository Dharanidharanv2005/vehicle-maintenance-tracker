-- Create database
CREATE DATABASE IF NOT EXISTS vehicle_maintenance_tracker;
USE vehicle_maintenance_tracker;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Vehicles table
CREATE TABLE IF NOT EXISTS vehicles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    make VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    year INT NOT NULL,
    license_plate VARCHAR(20) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Service types table
CREATE TABLE IF NOT EXISTS service_types (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    recommended_interval_months INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Maintenance records table
CREATE TABLE IF NOT EXISTS maintenance_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    vehicle_id INT NOT NULL,
    service_type_id INT NOT NULL,
    service_date DATE NOT NULL,
    mileage INT NOT NULL,
    cost DECIMAL(10,2),
    notes TEXT,
    next_service_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE,
    FOREIGN KEY (service_type_id) REFERENCES service_types(id)
);

-- Insert default service types
INSERT INTO service_types (name, description, recommended_interval_months) VALUES
('Oil Change', 'Regular engine oil and filter change', 3),
('Tire Rotation', 'Rotate and balance tires', 6),
('Brake Service', 'Inspect and service brake system', 12),
('Air Filter', 'Replace engine air filter', 12),
('Battery Check', 'Inspect and test battery', 6),
('Transmission Service', 'Transmission fluid change and inspection', 24),
('Coolant Flush', 'Replace engine coolant', 24),
('Spark Plugs', 'Replace spark plugs', 36); 