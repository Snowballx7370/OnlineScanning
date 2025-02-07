import tkinter as tk
from tkinter import messagebox
import bcrypt


# Function to hash a password (for demonstration; typically done once and stored securely)
from config_test import *


# Function to verify a password
def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against the stored hash."""
    return bcrypt.checkpw(password.encode(), hashed_password.encode())


# Main application window
def main_program():
    """Main program logic."""
    root = tk.Tk()
    root.title("Main Program")

    label = tk.Label(root, text="Welcome to the main program!")
    label.pack(pady=20)

    root.mainloop()


# Function to handle login
def attempt_login():
    """Handle login attempt."""
    entered_password = password_entry.get()
    if verify_password(entered_password, stored_password_hash):
        messagebox.showinfo("Success", "Password correct! Proceeding to the main program.")
        login_window.destroy()
        main_program()
    else:
        messagebox.showerror("Error", "Incorrect password. Please try again.")


# Create a login window
def create_login_window():
    """Create and show the login window with centered positioning and colors."""
    global login_window, password_entry

    # Initialize the Tkinter window
    login_window = tk.Tk()
    login_window.title("Login")

    # Set the size of the window
    window_width = 300
    window_height = 150

    # Get the screen width and height
    screen_width = login_window.winfo_screenwidth()
    screen_height = login_window.winfo_screenheight()

    # Calculate the position to center the window
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)

    # Set the geometry of the window
    login_window.geometry(f'{window_width}x{window_height}+{x}+{y}')

    # Set the background color of the window
    login_window.configure(bg='lightblue')

    # Create and pack widgets with padding and color
    tk.Label(login_window, text="Enter password:", bg='lightblue', fg='darkblue').pack(pady=10)

    password_entry = tk.Entry(login_window, show='*', bg='white', fg='black')
    password_entry.pack(pady=10, padx=20)

    tk.Button(login_window, text="Login", command=attempt_login, bg='darkblue', fg='white').pack(pady=10)

    # Start the Tkinter event loop
    login_window.mainloop()


# Example usage
if __name__ == "__main__":
    # Hash a password for demonstration
    # In a real application, this hash should be stored securely and not hardcoded

    # Create and show the login window
    create_login_window()
