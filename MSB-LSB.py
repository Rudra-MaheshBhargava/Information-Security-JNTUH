import numpy as np
from PIL import Image
import math


def calculate_psnr(original, processed):
    # Calculate Mean Squared Error (MSE)
    mse = np.mean(
        (original.astype(np.float64) -
         processed.astype(np.float64)) ** 2
    )

    # If images are identical
    if mse == 0:
        return float('inf'), mse

    # Maximum pixel value for an 8-bit image
    max_pixel = 255.0

    # Calculate PSNR
    psnr = 10 * math.log10((max_pixel ** 2) / mse)

    return psnr, mse


def manipulate_image_bits_interactive():

    print("--- RGB Image Bit Manipulation (MSB / LSB) ---")

    # 1. Take user inputs
    image_path = input(
        "Enter the path to the input RGB image (e.g., input.jpg): "
    ).strip() # Remove leading/trailing whitespace

    mode = input(
        "Choose manipulation mode - Type 'msb' or 'lsb': "
    ).strip().lower()

    if mode not in ['msb', 'lsb']:
        print("Error: Invalid mode selected. Please type either 'msb' or 'lsb'.")
        return

    try:
        bits = int(
            input("Enter the number of bits to manipulate (1 to 8): ").strip()
        )

        if not (1 <= bits <= 8):
            raise ValueError

    except ValueError:
        print("Error: Please enter a valid integer between 1 and 8.")
        return

    # 2. Load image
    try:
        img = Image.open(image_path).convert('RGB') # Convert to RGB to ensure consistency and avoid issues with images that may have an alpha channel or be in a different color mode.

    except FileNotFoundError:
        print(
            f"Error: The file '{image_path}' was not found. "
            "Check the path and try again."
        )
        return

    # Convert image to NumPy array
    img_array = np.array(img, dtype=np.uint8) # Use uint8 to represent pixel values in the range [0, 255]

    print(
        f"\nProcessing image " # this line is for printing the image dimensions and the selected mode and bits for manipulation.
        f"({img_array.shape[1]}x{img_array.shape[0]} pixels) " # this line prints the width and height of the image in pixels.
        f"using {mode.upper()} mode with {bits} bits..." # this line prints the selected mode (MSB or LSB) and the number of bits to manipulate.
    )

    # ==========================================================
    # 3. BIT MANIPULATION
    # ==========================================================

    if mode == 'lsb':

        # Create mask for selected LSB bits
        # Example:
        # bits = 1 -> 00000001
        # bits = 2 -> 00000011
        # bits = 3 -> 00000111
        mask = (1 << bits) - 1 # This line creates a mask that has the least significant 'bits' set to 1. For example, if bits=3, mask will be 00000111 in binary.

        # Flip the selected LSBs
        # 0 -> 1
        # 1 -> 0
        processed_array = img_array ^ mask # This line flips the least significant 'bits' of each pixel in the image. The XOR operation with the mask will invert the bits where the mask has 1s.

        output_filename = f"changed_image_lsb_{bits}bits.png" # This line defines the output filename for the processed image, indicating that it has been modified using LSB manipulation with the specified number of bits.

    else:  # MSB

        # Keep only the selected MSB bits
        shift = 8 - bits # This line calculates how many bits to shift to the right in order to isolate the most significant 'bits'. For example, if bits=3, shift will be 5, meaning we want to keep the top 3 bits and discard the lower 5 bits.

        mask = 0xFF ^ ((1 << shift) - 1) # This line creates a mask that has the most significant 'bits' set to 1 and the rest set to 0. For example, if bits=3, mask will be 11100000 in binary. oxff is a hexadecimal representation of 255, which is 11111111 in binary. The expression ((1 << shift) - 1) creates a mask for the lower bits, and XORing it with 0xFF inverts it to create the desired MSB mask.

        processed_array = img_array & mask # This line applies the mask to the original image array using a bitwise AND operation. This keeps only the most significant 'bits' of each pixel and sets the rest to 0.

        output_filename = f"changed_image_msb_{bits}bits.png"

    # ==========================================================
    # 4. CALCULATE MSE AND PSNR
    # ==========================================================

    psnr, mse = calculate_psnr(
        img_array,
        processed_array
    )

    # ==========================================================
    # 5. CONVERT ARRAY BACK TO IMAGE
    # ==========================================================

    processed_img = Image.fromarray( # This line converts the processed NumPy array back into a PIL Image object. The 'RGB' mode is specified to ensure that the image is treated as an RGB image, which is necessary for saving and displaying it correctly.
        processed_array, # The processed NumPy array containing the modified image data.
        'RGB' # Specifies that the image is in RGB mode, which means it has three color channels (Red, Green, Blue). This is important for correctly interpreting the pixel data when creating the image.
    )

    # ==========================================================
    # 6. SAVE IMAGE
    # ==========================================================

    processed_img.save(output_filename)

    # ==========================================================
    # 7. DISPLAY RESULTS
    # ==========================================================

    print("\n--------------------------------")
    print("IMAGE PROCESSING COMPLETE")
    print("--------------------------------")

    print(f"Mode       : {mode.upper()}")
    print(f"Bits       : {bits}")
    print(f"MSE        : {mse:.4f}")

    if math.isinf(psnr):
        print("PSNR       : Infinite (Images are identical)")
    else:
        print(f"PSNR       : {psnr:.2f} dB")

    print(f"Output file: {output_filename}")

    print("--------------------------------")

    # ==========================================================
    # 8. DISPLAY PROCESSED IMAGE
    # ==========================================================

    processed_img.show(
        title=f"Modified Image ({mode.upper()} - {bits} bits)"
    )


# ==============================================================
# MAIN PROGRAM
# ==============================================================

if __name__ == "__main__":
    manipulate_image_bits_interactive()