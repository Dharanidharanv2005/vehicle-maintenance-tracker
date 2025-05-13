import os
import requests
from PIL import Image
from io import BytesIO

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def download_and_resize_image(url, save_path, size=None):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            if size:
                img = img.resize(size, Image.Resampling.LANCZOS)
            img.save(save_path, optimize=True, quality=85)
            print(f"Downloaded and saved: {save_path}")
            return True
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
    return False

def main():
    # Create necessary directories
    create_directory("static/images")
    create_directory("static/images/vehicles")
    create_directory("static/images/features")
    create_directory("static/images/logo")
    create_directory("static/images/hero")

    # Logo images
    logo_images = {
        "main_logo.png": {
            "url": "https://images.unsplash.com/photo-1581093458791-9d15482442f6",
            "size": (200, 200),
            "description": "Main Logo"
        },
        "favicon.ico": {
            "url": "https://images.unsplash.com/photo-1581093458791-9d15482442f6",
            "size": (32, 32),
            "description": "Favicon"
        }
    }

    # Hero background
    hero_images = {
        "hero-bg.jpg": {
            "url": "https://images.unsplash.com/photo-1581093458791-9d15482442f6",
            "size": (1920, 1080),
            "description": "Hero Background"
        }
    }

    # Vehicle images with their specifications
    vehicle_images = {
        "sedan.jpg": {
            "url": "https://images.unsplash.com/photo-1552519507-da3b142c6e3d",
            "size": (800, 600),
            "description": "Modern Sedan"
        },
        "suv.jpg": {
            "url": "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf",
            "size": (800, 600),
            "description": "Family SUV"
        },
        "truck.jpg": {
            "url": "https://images.unsplash.com/photo-1566576721346-d4a3b4eaeb55",
            "size": (800, 600),
            "description": "Commercial Truck"
        },
        "electric.jpg": {
            "url": "https://images.unsplash.com/photo-1619767886558-efdc25944de6",
            "size": (800, 600),
            "description": "Electric Vehicle"
        },
        "luxury.jpg": {
            "url": "https://images.unsplash.com/photo-1555215695-3004980ad54e",
            "size": (800, 600),
            "description": "Luxury Car"
        },
        "sports.jpg": {
            "url": "https://images.unsplash.com/photo-1525609004556-c46c7d6cf023",
            "size": (800, 600),
            "description": "Sports Car"
        },
        "hybrid.jpg": {
            "url": "https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8",
            "size": (800, 600),
            "description": "Hybrid Vehicle"
        },
        "compact.jpg": {
            "url": "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2",
            "size": (800, 600),
            "description": "Compact Car"
        },
        "luxury-sedan.jpg": {
            "url": "https://images.unsplash.com/photo-1555215695-3004980ad54e",
            "size": (800, 600),
            "description": "Luxury Sedan"
        },
        "sports-car.jpg": {
            "url": "https://images.unsplash.com/photo-1525609004556-c46c7d6cf023",
            "size": (800, 600),
            "description": "Sports Car"
        },
        "classic-car.jpg": {
            "url": "https://images.unsplash.com/photo-1581093458791-9d15482442f6",
            "size": (800, 600),
            "description": "Classic Car"
        },
        "electric-car.jpg": {
            "url": "https://images.unsplash.com/photo-1619767886558-efdc25944de6",
            "size": (800, 600),
            "description": "Electric Car"
        }
    }

    # Feature images
    feature_images = {
        "maintenance.jpg": {
            "url": "https://images.unsplash.com/photo-1583121274602-3e2820c69888",
            "size": (400, 300),
            "description": "Vehicle Maintenance"
        },
        "service.jpg": {
            "url": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158",
            "size": (400, 300),
            "description": "Service Center"
        },
        "parts.jpg": {
            "url": "https://images.unsplash.com/photo-1581093458791-9d15482442f6",
            "size": (400, 300),
            "description": "Auto Parts"
        },
        "diagnostic.jpg": {
            "url": "https://images.unsplash.com/photo-1581093458791-9d15482442f6",
            "size": (400, 300),
            "description": "Vehicle Diagnostics"
        },
        "repair.jpg": {
            "url": "https://images.unsplash.com/photo-1581093458791-9d15482442f6",
            "size": (400, 300),
            "description": "Auto Repair"
        },
        "service-reminders.jpg": {
            "url": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158",
            "size": (400, 300),
            "description": "Service Reminders"
        },
        "maintenance-tracking.jpg": {
            "url": "https://images.unsplash.com/photo-1583121274602-3e2820c69888",
            "size": (400, 300),
            "description": "Maintenance Tracking"
        },
        "vehicle-management.jpg": {
            "url": "https://images.unsplash.com/photo-1581093458791-9d15482442f6",
            "size": (400, 300),
            "description": "Vehicle Management"
        }
    }

    # Download logo images
    print("Downloading logo images...")
    for filename, specs in logo_images.items():
        save_path = os.path.join("static/images/logo", filename)
        download_and_resize_image(specs["url"], save_path, specs["size"])

    # Download hero images
    print("Downloading hero images...")
    for filename, specs in hero_images.items():
        save_path = os.path.join("static/images/hero", filename)
        download_and_resize_image(specs["url"], save_path, specs["size"])

    # Download vehicle images
    print("Downloading vehicle images...")
    for filename, specs in vehicle_images.items():
        save_path = os.path.join("static/images/vehicles", filename)
        download_and_resize_image(specs["url"], save_path, specs["size"])

    # Download feature images
    print("Downloading feature images...")
    for filename, specs in feature_images.items():
        save_path = os.path.join("static/images/features", filename)
        download_and_resize_image(specs["url"], save_path, specs["size"])

if __name__ == "__main__":
    main() 