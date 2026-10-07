import socket
import struct
import math
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk


# ==============================
# SERVER SETTINGS
# ==============================

HOST = "127.0.0.1"
PORT = 5001

cover_image = None


# ==============================
# ENCRYPTION
# ==============================

def encrypt_message(message, key):
    """
    Simple XOR encryption.
    The same key is required at the server for decryption.
    """

    encrypted = ""

    for i, ch in enumerate(message):
        encrypted_char = chr(
            ord(ch) ^ ord(key[i % len(key)])
        )
        encrypted += encrypted_char

    return encrypted


# ==============================
# LSB STEGANOGRAPHY
# ==============================

def hide_message(image, message):
    """
    Hide the encrypted message inside the image
    using the Least Significant Bit (LSB).
    """

    # Convert encrypted message into bytes
    message_bytes = message.encode("utf-8")

    # Store message length in first 4 bytes
    data = struct.pack("!I", len(message_bytes)) + message_bytes

    # Convert bytes to bits
    bits = []

    for byte in data:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)

    # Check image capacity
    capacity = image.width * image.height * 3

    if len(bits) > capacity:
        raise ValueError(
            "Message is too large for this image."
        )

    stego = image.copy().convert("RGB")

    pixel_data = list(stego.getdata())

    bit_index = 0

    for i in range(len(pixel_data)):

        r, g, b = pixel_data[i]

        channels = [r, g, b]

        for j in range(3):

            if bit_index < len(bits):

                channels[j] = (
                    channels[j] & 254
                ) | bits[bit_index]

                bit_index += 1

        pixel_data[i] = tuple(channels)

        if bit_index >= len(bits):
            break

    stego.putdata(pixel_data)

    return stego


# ==============================
# PSNR
# ==============================

def calculate_psnr(original, stego):
    """
    Calculate PSNR between cover and stego image.
    """

    original = original.convert("RGB")
    stego = stego.convert("RGB")

    total_error = 0

    for p1, p2 in zip(
        original.getdata(),
        stego.getdata()
    ):

        for a, b in zip(p1, p2):
            total_error += (a - b) ** 2

    total_pixels = (
        original.width *
        original.height *
        3
    )

    mse = total_error / total_pixels

    if mse == 0:
        return float("inf")

    psnr = 10 * math.log10(
        (255 ** 2) / mse
    )

    return psnr


# ==============================
# SEND IMAGE TO SERVER
# ==============================

def send_file(sock, filename):

    with open(filename, "rb") as file:

        data = file.read()

    # Send image size first
    sock.sendall(
        struct.pack("!Q", len(data))
    )

    # Send image data
    sock.sendall(data)


# ==============================
# CREATE SCROLLABLE IMAGE AREA
# ==============================

def create_scrollable_image(parent):

    frame = tk.Frame(
        parent,
        bg="#1e1e1e"
    )

    canvas = tk.Canvas(
        frame,
        width=550,
        height=430,
        bg="black",
        highlightthickness=1,
        highlightbackground="#555555"
    )

    vertical_scrollbar = tk.Scrollbar(
        frame,
        orient=tk.VERTICAL,
        command=canvas.yview
    )

    horizontal_scrollbar = tk.Scrollbar(
        frame,
        orient=tk.HORIZONTAL,
        command=canvas.xview
    )

    canvas.configure(
        yscrollcommand=vertical_scrollbar.set,
        xscrollcommand=horizontal_scrollbar.set
    )

    canvas.grid(
        row=0,
        column=0,
        sticky="nsew"
    )

    vertical_scrollbar.grid(
        row=0,
        column=1,
        sticky="ns"
    )

    horizontal_scrollbar.grid(
        row=1,
        column=0,
        sticky="ew"
    )

    frame.grid_rowconfigure(
        0,
        weight=1
    )

    frame.grid_columnconfigure(
        0,
        weight=1
    )

    return frame, canvas


# ==============================
# DISPLAY IMAGE
# ==============================

def display_image(image, canvas):

    photo = ImageTk.PhotoImage(image)

    canvas.delete("all")

    canvas.create_image(
        0,
        0,
        anchor=tk.NW,
        image=photo
    )

    # Keep reference
    canvas.image = photo

    # IMPORTANT:
    # Keep image at ORIGINAL SIZE
    canvas.configure(
        scrollregion=(
            0,
            0,
            image.width,
            image.height
        )
    )


# ==============================
# SELECT COVER IMAGE
# ==============================

def select_image():

    global cover_image

    filename = filedialog.askopenfilename(
        title="Select Cover Image",
        filetypes=[
            ("Image Files",
             "*.png *.jpg *.jpeg"),
            ("PNG Files", "*.png"),
            ("JPEG Files", "*.jpg *.jpeg")
        ]
    )

    if not filename:
        return

    try:

        cover_image = Image.open(
            filename
        ).convert("RGB")

        display_image(
            cover_image,
            cover_canvas
        )

        cover_size_label.config(
            text=f"Size: {cover_image.width} × "
                 f"{cover_image.height} pixels"
        )

        status_label.config(
            text="Cover image selected."
        )

    except Exception as e:

        messagebox.showerror(
            "Error",
            f"Could not open image:\n{e}"
        )


# ==============================
# ENCRYPT + HIDE + SEND
# ==============================

def encode_and_send():

    global cover_image

    # Check image
    if cover_image is None:

        messagebox.showwarning(
            "Missing Image",
            "Please select a cover image."
        )

        return

    # Get secret message
    message = message_entry.get()

    if not message:

        messagebox.showwarning(
            "Missing Message",
            "Please enter a secret message."
        )

        return

    # Get encryption key
    key = key_entry.get()

    if not key:

        messagebox.showwarning(
            "Missing Key",
            "Please enter an encryption key."
        )

        return

    try:

        # --------------------------------
        # STEP 1: ENCRYPT MESSAGE
        # --------------------------------

        encrypted_message = encrypt_message(
            message,
            key
        )

        # --------------------------------
        # STEP 2: HIDE ENCRYPTED MESSAGE
        # --------------------------------

        stego_image = hide_message(
            cover_image,
            encrypted_message
        )

        # --------------------------------
        # STEP 3: SAVE STEGO IMAGE
        # --------------------------------

        filename = "stego_image.png"

        stego_image.save(
            filename,
            "PNG"
        )

        # --------------------------------
        # STEP 4: DISPLAY STEGO IMAGE
        # --------------------------------

        display_image(
            stego_image,
            stego_canvas
        )

        stego_size_label.config(
            text=f"Size: {stego_image.width} × "
                 f"{stego_image.height} pixels"
        )

        # --------------------------------
        # STEP 5: CALCULATE PSNR
        # --------------------------------

        psnr = calculate_psnr(
            cover_image,
            stego_image
        )

        if math.isinf(psnr):

            psnr_text = "PSNR: ∞ dB"

        else:

            psnr_text = (
                f"PSNR: {psnr:.2f} dB"
            )

        psnr_label.config(
            text=psnr_text
        )

        # --------------------------------
        # STEP 6: SEND ONLY STEGO IMAGE
        # --------------------------------

        client = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        client.connect(
            (HOST, PORT)
        )

        send_file(
            client,
            filename
        )

        client.close()

        status_label.config(
            text="Stego image sent successfully to server."
        )

        messagebox.showinfo(
            "Success",
            "Message encrypted, hidden and sent successfully!"
        )

    except Exception as e:

        messagebox.showerror(
            "Error",
            str(e)
        )


# ============================================================
# MAIN WINDOW
# ============================================================

root = tk.Tk()

root.title(
    "LSB Image Steganography - Client"
)

root.configure(
    bg="#1e1e1e"
)

# ------------------------------------------------------------
# IMPORTANT:
# Main window gets a VERTICAL SCROLLBAR
# ------------------------------------------------------------

main_canvas = tk.Canvas(
    root,
    bg="#1e1e1e",
    highlightthickness=0
)

main_scrollbar = tk.Scrollbar(
    root,
    orient=tk.VERTICAL,
    command=main_canvas.yview
)

main_canvas.configure(
    yscrollcommand=main_scrollbar.set
)

main_scrollbar.pack(
    side=tk.RIGHT,
    fill=tk.Y
)

main_canvas.pack(
    side=tk.LEFT,
    fill=tk.BOTH,
    expand=True
)


# This frame contains the COMPLETE GUI
main_frame = tk.Frame(
    main_canvas,
    bg="#1e1e1e"
)

main_window = main_canvas.create_window(
    (0, 0),
    window=main_frame,
    anchor=tk.NW
)


# ------------------------------------------------------------
# Update scrollbar whenever content size changes
# ------------------------------------------------------------

def update_scroll_region(event=None):

    main_canvas.configure(
        scrollregion=main_canvas.bbox("all")
    )


main_frame.bind(
    "<Configure>",
    update_scroll_region
)


# ------------------------------------------------------------
# Make content width match window width
# ------------------------------------------------------------

def resize_main_frame(event):

    main_canvas.itemconfig(
        main_window,
        width=event.width
    )


main_canvas.bind(
    "<Configure>",
    resize_main_frame
)


# ------------------------------------------------------------
# Mouse wheel scrolling
# ------------------------------------------------------------

def mouse_wheel(event):

    main_canvas.yview_scroll(
        int(-1 * (event.delta / 120)),
        "units"
    )


root.bind_all(
    "<MouseWheel>",
    mouse_wheel
)


# ==============================
# TITLE
# ==============================

title_label = tk.Label(
    main_frame,
    text="LSB IMAGE STEGANOGRAPHY",
    font=("Arial", 28, "bold"),
    fg="white",
    bg="#1e1e1e"
)

title_label.pack(
    pady=(25, 10)
)


# ==============================
# CLIENT LABEL
# ==============================

client_label = tk.Label(
    main_frame,
    text="CLIENT",
    font=("Arial", 22),
    fg="white",
    bg="#1e1e1e"
)

client_label.pack(
    pady=10
)


# ==============================
# UPLOAD BUTTON
# ==============================

upload_button = tk.Button(
    main_frame,
    text="UPLOAD / SELECT IMAGE",
    font=("Arial", 16, "bold"),
    command=select_image,
    width=25,
    height=2
)

upload_button.pack(
    pady=10
)


# ==============================
# IMAGE AREA
# ==============================

images_frame = tk.Frame(
    main_frame,
    bg="#1e1e1e"
)

images_frame.pack(
    pady=10
)


# ------------------------------------------------------------
# COVER IMAGE
# ------------------------------------------------------------

cover_frame = tk.Frame(
    images_frame,
    bg="#1e1e1e"
)

cover_frame.grid(
    row=0,
    column=0,
    padx=20
)

cover_title = tk.Label(
    cover_frame,
    text="COVER IMAGE",
    font=("Arial", 20, "bold"),
    fg="white",
    bg="#1e1e1e"
)

cover_title.pack(
    pady=5
)

cover_image_frame, cover_canvas = (
    create_scrollable_image(
        cover_frame
    )
)

cover_image_frame.pack()

cover_size_label = tk.Label(
    cover_frame,
    text="Size: -- × -- pixels",
    font=("Arial", 14),
    fg="white",
    bg="#1e1e1e"
)

cover_size_label.pack(
    pady=8
)


# ------------------------------------------------------------
# STEGO IMAGE
# ------------------------------------------------------------

stego_frame = tk.Frame(
    images_frame,
    bg="#1e1e1e"
)

stego_frame.grid(
    row=0,
    column=1,
    padx=20
)

stego_title = tk.Label(
    stego_frame,
    text="STEGO IMAGE",
    font=("Arial", 20, "bold"),
    fg="white",
    bg="#1e1e1e"
)

stego_title.pack(
    pady=5
)

stego_image_frame, stego_canvas = (
    create_scrollable_image(
        stego_frame
    )
)

stego_image_frame.pack()

stego_size_label = tk.Label(
    stego_frame,
    text="Size: -- × -- pixels",
    font=("Arial", 14),
    fg="white",
    bg="#1e1e1e"
)

stego_size_label.pack(
    pady=8
)


# ==============================
# SECRET MESSAGE
# ==============================

message_title = tk.Label(
    main_frame,
    text="ENTER SECRET MESSAGE:",
    font=("Arial", 18, "bold"),
    fg="white",
    bg="#1e1e1e"
)

message_title.pack(
    pady=(25, 5)
)

message_entry = tk.Entry(
    main_frame,
    font=("Arial", 16),
    width=70
)

message_entry.pack(
    pady=5
)


# ==============================
# ENCRYPTION KEY
# ==============================

key_title = tk.Label(
    main_frame,
    text="ENTER ENCRYPTION KEY:",
    font=("Arial", 18, "bold"),
    fg="white",
    bg="#1e1e1e"
)

key_title.pack(
    pady=(15, 5)
)

key_entry = tk.Entry(
    main_frame,
    font=("Arial", 16),
    width=50,
    show="*"
)

key_entry.pack(
    pady=5
)


# ==============================
# ENCRYPT BUTTON
# ==============================

encrypt_button = tk.Button(
    main_frame,
    text="ENCRYPT → HIDE → SEND",
    font=("Arial", 18, "bold"),
    bg="#ffffff",
    fg="black",
    width=30,
    height=2,
    command=encode_and_send
)

encrypt_button.pack(
    pady=25
)


# ==============================
# PSNR
# ==============================

psnr_label = tk.Label(
    main_frame,
    text="PSNR: -- dB",
    font=("Arial", 18, "bold"),
    fg="white",
    bg="#1e1e1e"
)

psnr_label.pack(
    pady=10
)


# ==============================
# STATUS
# ==============================

status_label = tk.Label(
    main_frame,
    text="Please select a cover image.",
    font=("Arial", 14),
    fg="lightgray",
    bg="#1e1e1e"
)

status_label.pack(
    pady=(5, 30)
)


# ==============================
# WINDOW SIZE
# ==============================

root.geometry(
    "1500x900"
)

root.minsize(
    900,
    600
)


# ==============================
# START GUI
# ==============================

root.mainloop()