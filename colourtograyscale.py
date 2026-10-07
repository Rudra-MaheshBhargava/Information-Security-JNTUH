import numpy as np
from PIL import Image

def convert_to_grayscale():
    print("--- Color Image to Grayscale Converter ---")
    
    # 1. Take user input for image path
    image_path = input("Enter the path to the input color image (e.g., input.jpg): ").strip()
    
    try:
        # 2. Load the image and convert to RGB
        img = Image.open(image_path).convert('RGB')
        img_array = np.array(img, dtype=np.float32) # Use float to prevent overflow during math
    except FileNotFoundError:
        print(f"Error: The file '{image_path}' was not found. Please check the path and try again.")
        return
        
    print(f"\nProcessing image: {img_array.shape[1]}x{img_array.shape[0]} pixels...")
    
    # 3. Separate RGB channels
    red = img_array[:, :, 0]
    green = img_array[:, :, 1]
    blue = img_array[:, :, 2]
    
    # 4. Apply the standard luminance formula
    # Y = 0.299*R + 0.587*G + 0.114*B
    grayscale_array = 0.299 * red + 0.587 * green + 0.114 * blue
    
    # Clip values to ensure they stay within valid 0-255 range and convert back to uint8
    grayscale_array = np.clip(grayscale_array, 0, 255).astype(np.uint8)
    
    # 5. Save and display the grayscale image
    output_filename = "grayscale_output.png"
    grayscale_img = Image.fromarray(grayscale_array, mode='L') # 'L' stands for luminance/grayscale
    grayscale_img.save(output_filename)
    
    print(f"Success! Grayscale image saved as: '{output_filename}'")
    
    # Automatically open/display the image window
    grayscale_img.show(title="Grayscale Converted Image")

if __name__ == "__main__":
    convert_to_grayscale()