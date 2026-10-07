import socket
import struct
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from io import BytesIO


# ==============================
# SERVER SETTINGS
# ==============================

HOST = "127.0.0.1"
PORT = 5001


# ==============================
# RECEIVE EXACT NUMBER OF BYTES
# ==============================

def receive_all(conn, size):

    data = b""

    while len(data) < size:

        packet = conn.recv(
            min(4096, size - len(data))
        )

        if not packet:
            raise ConnectionError(
                "Connection closed unexpectedly."
            )

        data += packet

    return data


# ==============================
# RECEIVE IMAGE
# ==============================

def receive_file(conn):

    # Receive image size
    size_data = receive_all(
        conn,
        8
    )

    size = struct.unpack(
        "!Q",
        size_data
    )[0]

    # Receive image
    image_data = receive_all(
        conn,
        size
    )

    return image_data


# ==============================
# EXTRACT MESSAGE USING LSB
# ==============================

def extract_message(image):

    image = image.convert("RGB")

    bits = []

    # Read LSB from every RGB channel
    for r, g, b in image.getdata():

        bits.append(r & 1)
        bits.append(g & 1)
        bits.append(b & 1)

    # --------------------------------
    # First 32 bits = message length
    # --------------------------------

    length_bits = bits[:32]

    message_length = 0

    for bit in length_bits:

        message_length = (
            (message_length << 1) | bit
        )

    # --------------------------------
    # Extract encrypted message
    # --------------------------------

    start = 32

    end = start + (
        message_length * 8
    )

    if end > len(bits):

        raise ValueError(
            "Invalid stego image or corrupted message."
        )

    message_bits = bits[
        start:end
    ]

    message_bytes = bytearray()

    # Convert bits back to bytes
    for i in range(
        0,
        len(message_bits),
        8
    ):

        byte = 0

        for bit in message_bits[
            i:i + 8
        ]:

            byte = (
                (byte << 1) | bit
            )

        message_bytes.append(byte)

    # Convert bytes to encrypted text
    encrypted_message = (
        bytes(message_bytes)
        .decode("utf-8")
    )

    return encrypted_message


# ==============================
# DECRYPT MESSAGE
# ==============================

def decrypt_message(
    encrypted_message,
    key
):

    decrypted = ""

    for i, ch in enumerate(
        encrypted_message
    ):

        decrypted_char = chr(
            ord(ch) ^
            ord(key[i % len(key)])
        )

        decrypted += decrypted_char

    return decrypted


# ============================================================
# SCROLLABLE IMAGE AREA
# ============================================================

def create_scrollable_image(parent):

    frame = tk.Frame(
        parent,
        bg="#1e1e1e"
    )

    canvas = tk.Canvas(
        frame,
        width=700,
        height=500,
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

    return frame, canvas


# ============================================================
# DISPLAY IMAGE AT ORIGINAL SIZE
# ============================================================

def display_image(
    image,
    canvas
):

    photo = ImageTk.PhotoImage(
        image
    )

    canvas.delete("all")

    canvas.create_image(
        0,
        0,
        anchor=tk.NW,
        image=photo
    )

    # Keep image reference
    canvas.image = photo

    # Keep original image size
    canvas.configure(
        scrollregion=(
            0,
            0,
            image.width,
            image.height
        )
    )


# ============================================================
# DECRYPT BUTTON FUNCTION
# ============================================================

def decrypt_button_clicked():

    global received_image
    global encrypted_message

    if received_image is None:

        messagebox.showwarning(
            "No Image",
            "No stego image has been received."
        )

        return

    key = key_entry.get()

    if not key:

        messagebox.showwarning(
            "Missing Key",
            "Please enter the encryption key."
        )

        return

    try:

        # --------------------------------
        # Extract encrypted message
        # --------------------------------

        encrypted_message = extract_message(
            received_image
        )

        # --------------------------------
        # Decrypt message
        # --------------------------------

        hidden_message = decrypt_message(
            encrypted_message,
            key
        )

        # --------------------------------
        # Display hidden message
        # --------------------------------

        message_text.delete(
            "1.0",
            tk.END
        )

        message_text.insert(
            tk.END,
            hidden_message
        )

        status_label.config(
            text="Message extracted and decrypted successfully."
        )

    except Exception as e:

        messagebox.showerror(
            "Decryption Error",
            "Wrong key or invalid stego image."
        )

        status_label.config(
            text="Decryption failed."


        )


# ============================================================
# RECEIVE IMAGE FROM CLIENT
# ============================================================

def receive_image_from_client():

    global received_image

    try:

        # Create server socket
        server = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        server.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        server.bind(
            (HOST, PORT)
        )

        server.listen(1)

        status_label.config(
            text="Waiting for client..."
        )

        root.update()

        # Wait for client
        conn, address = server.accept()

        status_label.config(
            text="Client connected. Receiving stego image..."
        )

        root.update()

        # Receive image
        image_data = receive_file(
            conn
        )

        # Close connection
        conn.close()
        server.close()

        # Convert received bytes to image
        received_image = Image.open(
            BytesIO(image_data)
        ).convert("RGB")

        # Save received image
        received_image.save(
            "received_stego_image.png"
        )

        # Display image
        display_image(
            received_image,
            stego_canvas
        )

        # Display image size
        size_label.config(
            text=f"Size: {received_image.width} × "
                 f"{received_image.height} pixels"
        )

        status_label.config(
            text="Stego image received successfully. Enter the key."
        )

        # Enable key and decrypt button
        key_entry.config(
            state="normal"
        )

        decrypt_button.config(
            state="normal"
        )

    except Exception as e:

        messagebox.showerror(
            "Server Error",
            str(e)
        )

        status_label.config(
            text="Server error."


        )


# ============================================================
# MAIN WINDOW
# ============================================================

root = tk.Tk()

root.title(
    "LSB Image Steganography - Server"
)

root.configure(
    bg="#1e1e1e"
)


# ============================================================
# MAIN SCROLLABLE PAGE
# ============================================================

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

# Main scrollbar on RIGHT
main_scrollbar.pack(
    side=tk.RIGHT,
    fill=tk.Y
)

main_canvas.pack(
    side=tk.LEFT,
    fill=tk.BOTH,
    expand=True
)


# Frame containing all server content
main_frame = tk.Frame(
    main_canvas,
    bg="#1e1e1e"
)

main_window = main_canvas.create_window(
    (0, 0),
    window=main_frame,
    anchor=tk.NW
)


# ============================================================
# UPDATE SCROLL REGION
# ============================================================

def update_scroll_region(event=None):

    main_canvas.configure(
        scrollregion=main_canvas.bbox("all")
    )


main_frame.bind(
    "<Configure>",
    update_scroll_region
)


# ============================================================
# KEEP FRAME WIDTH SAME AS WINDOW
# ============================================================

def resize_main_frame(event):

    main_canvas.itemconfig(
        main_window,
        width=event.width
    )


main_canvas.bind(
    "<Configure>",
    resize_main_frame
)


# ============================================================
# MOUSE WHEEL SCROLL
# ============================================================

def mouse_wheel(event):

    main_canvas.yview_scroll(
        int(-1 * (event.delta / 120)),
        "units"
    )


root.bind_all(
    "<MouseWheel>",
    mouse_wheel
)


# ============================================================
# TITLE
# ============================================================

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


# ============================================================
# SERVER LABEL
# ============================================================

server_label = tk.Label(
    main_frame,
    text="SERVER",
    font=("Arial", 22),
    fg="white",
    bg="#1e1e1e"
)

server_label.pack(
    pady=10
)


# ============================================================
# STEGO IMAGE TITLE
# ============================================================

image_title = tk.Label(
    main_frame,
    text="RECEIVED STEGO IMAGE",
    font=("Arial", 20, "bold"),
    fg="white",
    bg="#1e1e1e"
)

image_title.pack(
    pady=10
)


# ============================================================
# STEGO IMAGE WITH SCROLLBARS
# ============================================================

stego_image_frame, stego_canvas = (
    create_scrollable_image(
        main_frame
    )
)

stego_image_frame.pack(
    pady=5
)


# ============================================================
# IMAGE SIZE
# ============================================================

size_label = tk.Label(
    main_frame,
    text="Size: -- × -- pixels",
    font=("Arial", 14),
    fg="white",
    bg="#1e1e1e"
)

size_label.pack(
    pady=10
)


# ============================================================
# ENCRYPTION KEY
# ============================================================

key_title = tk.Label(
    main_frame,
    text="ENTER DECRYPTION KEY:",
    font=("Arial", 18, "bold"),
    fg="white",
    bg="#1e1e1e"
)

key_title.pack(
    pady=(25, 5)
)


key_entry = tk.Entry(
    main_frame,
    font=("Arial", 16),
    width=50,
    show="*",
    state="disabled"
)

key_entry.pack(
    pady=5
)


# ============================================================
# DECRYPT BUTTON
# ============================================================

decrypt_button = tk.Button(
    main_frame,
    text="EXTRACT & DECRYPT MESSAGE",
    font=("Arial", 18, "bold"),
    bg="#ffffff",
    fg="black",
    width=32,
    height=2,
    command=decrypt_button_clicked,
    state="disabled"
)

decrypt_button.pack(
    pady=25
)


# ============================================================
# HIDDEN MESSAGE
# ============================================================

message_title = tk.Label(
    main_frame,
    text="HIDDEN MESSAGE:",
    font=("Arial", 18, "bold"),
    fg="white",
    bg="#1e1e1e"
)

message_title.pack(
    pady=(10, 5)
)


message_text = tk.Text(
    main_frame,
    font=("Arial", 16),
    width=60,
    height=5,
    wrap=tk.WORD
)

message_text.pack(
    pady=5
)


# ============================================================
# STATUS
# ============================================================

status_label = tk.Label(
    main_frame,
    text="Starting server...",
    font=("Arial", 14),
    fg="lightgray",
    bg="#1e1e1e"
)

status_label.pack(
    pady=(15, 30)
)


# ============================================================
# GLOBAL VARIABLES
# ============================================================

received_image = None
encrypted_message = None


# ============================================================
# WINDOW SIZE
# ============================================================

root.geometry(
    "1200x900"
)

root.minsize(
    800,
    600
)


# ============================================================
# START SERVER AFTER GUI LOADS
# ============================================================

root.after(
    500,
    receive_image_from_client
)


# ============================================================
# START GUI
# ============================================================

root.mainloop()