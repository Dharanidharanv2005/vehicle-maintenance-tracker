from PIL import Image, ImageDraw, ImageFont
import os

def create_logo():
    # Create a new image with a white background
    width = 200
    height = 50
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)

    # Draw a blue rectangle for the background
    draw.rectangle([(0, 0), (width, height)], fill='#007bff')

    # Add text
    try:
        # Try to use a system font
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        # Fallback to default font
        font = ImageFont.load_default()

    # Draw the text
    text = "VMT"
    text_width = draw.textlength(text, font=font)
    text_position = ((width - text_width) // 2, (height - 24) // 2)
    draw.text(text_position, text, fill='white', font=font)

    # Create the images directory if it doesn't exist
    os.makedirs('static/images', exist_ok=True)

    # Save the image
    image.save('static/images/vehicle_logo.png', 'png')
    print("Logo created successfully!")

if __name__ == "__main__":
    create_logo() 