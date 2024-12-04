import cv2
import tkinter as tk
from PIL import Image, ImageTk

def show_frame():
    ret, frame = cap.read()
    if ret:
        # Convert the frame to RGB format
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert the RGB frame to a PhotoImage
        img = ImageTk.PhotoImage(Image.fromarray(rgb_frame))

        # Update the label with the new image
        label.img = img
        label.config(image=img)
    else:
        print("Failed to capture frame.")

    # Schedule the next frame update
    window.after(10, show_frame)

# Create the main window
window = tk.Tk()
window.title("Webcam Viewer")

# Open the webcam
cap = cv2.VideoCapture(0)

# Check if the webcam opened successfully
if not cap.isOpened():
    print("Error: Could not open webcam.")
    window.destroy()
    exit()

# Create a label to display the frames
label = tk.Label(window)
label.pack()

# Schedule the first frame update
window.after(10, show_frame)

# Run the Tkinter main loop
window.mainloop()

# Release the webcam when the window is closed
cap.release()
cv2.destroyAllWindows()
