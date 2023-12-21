from logging import RootLogger
from tkinter import filedialog, messagebox
from typing import Self
import tweepy
from PIL import Image, ImageTk
import time
import os
import tkinter as tk
from datetime import datetime
from tkcalendar import Calendar, DateEntry


class TwitterPoster:
    def __init__(self, root):
        self.root = root
        self.root.title("Twitter Poster")

        self.api_key_label = tk.Label(root, text="API Key:")
        self.api_key_entry = tk.Entry(root)

        self.api_secret_label = tk.Label(root, text="API Secret:")
        self.api_secret_entry = tk.Entry(root, show="*")

        self.access_token_label = tk.Label(root, text="Access Token:")
        self.access_token_entry = tk.Entry(root)

        self.access_secret_label = tk.Label(root, text="Access Secret:")
        self.access_secret_entry = tk.Entry(root, show="*")

        self.message_label = tk.Label(root, text="Tweet Message:")
        self.message_entry = tk.Entry(root, width=40)

        self.description_label = tk.Label(root, text="Post Description:")
        self.description_entry = tk.Entry(root, width=40)

        self.image_path_label = tk.Label(root, text="Select Image:")
        self.image_path_entry = tk.Entry(root)
        self.browse_button = tk.Button(
            root, text="Browse", command=self.browse_image)

        self.datetime_label = tk.Label(root, text="Set Date and Time:")

        # Use DateEntry widget from tkcalendar for date input
        self.calendar = Calendar(root, selectmode='day', year=datetime.now(
        ).year, month=datetime.now().month, day=datetime.now().day)
        self.time_entry = DateEntry(
            root, width=12, background='darkblue', foreground='white', borderwidth=2)

        self.post_button = tk.Button(
            root, text="Post Tweet", command=self.post_tweet)

        # Layout
        self.api_key_label.grid(row=0, column=0, sticky="e")
        self.api_key_entry.grid(row=0, column=1, columnspan=2)

        self.api_secret_label.grid(row=1, column=0, sticky="e")
        self.api_secret_entry.grid(row=1, column=1, columnspan=2)

        self.access_token_label.grid(row=2, column=0, sticky="e")
        self.access_token_entry.grid(row=2, column=1, columnspan=2)

        self.access_secret_label.grid(row=3, column=0, sticky="e")
        self.access_secret_entry.grid(row=3, column=1, columnspan=2)

        self.message_label.grid(row=4, column=0, sticky="e")
        self.message_entry.grid(row=4, column=1, columnspan=2)

        self.description_label.grid(row=5, column=0, sticky="e")
        self.description_entry.grid(row=5, column=1, columnspan=2)

        self.image_path_label.grid(row=6, column=0, sticky="e")
        self.image_path_entry.grid(row=6, column=1, columnspan=2)
        self.browse_button.grid(row=6, column=3, pady=5, sticky="w")

        self.datetime_label.grid(row=7, column=0, sticky="e")

        # Adjust column and row for calendar and time_entry
        self.calendar.grid(row=7, column=1, columnspan=2, padx=10)
        self.time_entry.grid(row=7, column=3, padx=10)

        self.post_button.grid(row=8, column=1, pady=10)

    def browse_image(self):
        file_path = filedialog.askopenfilename()
        self.image_path_entry.delete(0, tk.END)
        self.image_path_entry.insert(0, file_path)

    def post_tweet(self):
        api_key = self.api_key_entry.get()
        api_secret = self.api_secret_entry.get()
        access_token = self.access_token_entry.get()
        access_secret = self.access_secret_entry.get()
        message = self.message_entry.get()
        description = self.description_entry.get()
        image_path = self.image_path_entry.get()

        selected_date = self.calendar.get_date()
        selected_time = self.time_entry.get()

        datetime_str = f"{selected_date} {selected_time}"

        if not all([api_key, api_secret, access_token, access_secret,
                    message, description, image_path, datetime_str]):
            messagebox.showerror(
                "Error", "Please provide all required information.")
            return

        try:
            # Convert the datetime string to a datetime object
            post_datetime = datetime.strptime(
                datetime_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            messagebox.showerror(
                "Error", "Please enter a valid date and time format (YYYY-MM-DD HH:MM:SS).")
            return

        current_datetime = datetime.now()

        if post_datetime < current_datetime:
            messagebox.showerror(
                "Error", "The specified date and time must be in the future.")
            return

        time_seconds = (post_datetime - current_datetime).total_seconds()

        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_secret)
        api = tweepy.API(auth)

        try:
            # Load image and resize
            image = Image.open(image_path)
            image = image.resize((500, 500), Image.ANTIALIAS)
            image_path_resized = "resized_image.png"
            image.save(image_path_resized)

            # Tweet
            tweet = f"{message}\n\nDescription: {description}"
            api.update_with_media(image_path_resized, status=tweet)
            print("Tweet posted successfully!")

            # Delay to allow the user to see the success message
            time.sleep(time_seconds)

        except tweepy.TweepError as e:
            messagebox.showerror("Error", f"Tweet post failed: {e}")
        finally:
            # Clean up resized image
            if os.path.exists(image_path_resized):
                os.remove(image_path_resized)


if __name__ == "__main__":
    root = tk.Tk()
    app = TwitterPoster(root)
    root.mainloop()
