from tkinter import filedialog, messagebox
import logging
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
        self.calendar.grid(row=7, column=1, columnspan=2, padx=10)
        self.time_entry.grid(row=7, column=3, padx=10)

        self.post_button.grid(row=8, column=1, pady=10)

        # Initialize logger
        logging.basicConfig(filename='twitter_poster.log', level=logging.ERROR)
        self.logger = logging.getLogger(__name__)

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

        try:
            self.validate_input(api_key, api_secret, access_token, access_secret,
                                message, description, image_path, datetime_str)
            post_datetime = self.parse_datetime(datetime_str)
            self.check_datetime(post_datetime)
            time_seconds = self.calculate_time_seconds(post_datetime)
            auth = self.get_auth(api_key, api_secret,
                                 access_token, access_secret)
            api = tweepy.API(auth)
            image_path_resized = self.resize_image(image_path)
            self.validate_tweet_content(message, description)
            self.tweet(api, message, description, image_path_resized)
            self.show_success_message(time_seconds)
        except Exception as e:
            self.handle_error(e)

    def validate_input(self, api_key, api_secret, access_token, access_secret,
                       message, description, image_path, datetime_str):
        if not all([api_key, api_secret, access_token, access_secret,
                    message, description, image_path, datetime_str]):
            raise ValueError("Please provide all required information.")

    def parse_datetime(self, datetime_str):
        try:
            return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            raise ValueError(
                "Please enter a valid date and time format (YYYY-MM-DD HH:MM:SS).")

    def check_datetime(self, post_datetime):
        current_datetime = datetime.now()
        if post_datetime < current_datetime:
            raise ValueError(
                "The specified date and time must be in the future.")

    def calculate_time_seconds(self, post_datetime):
        current_datetime = datetime.now()
        return (post_datetime - current_datetime).total_seconds()

    def get_auth(self, api_key, api_secret, access_token, access_secret):
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_secret)
        return auth

    def resize_image(self, image_path):
        try:
            image = Image.open(image_path)
            image = image.resize((500, 500), Image.ANTIALIAS)
            image_path_resized = "resized_image.png"
            image.save(image_path_resized)
            return image_path_resized
        except FileNotFoundError:
            raise FileNotFoundError("Image file not found.")
        except IOError:
            raise IOError("Error processing the image file.")

    def validate_tweet_content(self, message, description):
        if len(message) + len(description) > 280:
            raise ValueError(
                "The total length of the tweet message and description exceeds 280 characters.")

    def tweet(self, api, message, description, image_path_resized):
        try:
            tweet = f"{message}\n\nDescription: {description}"
            api.update_status(status=tweet, media_ids=[
                              api.media_upload(image_path_resized).media_id_string])
        except tweepy.TweepError as e:
            raise tweepy.TweepError(f"Tweet post failed: {e}")

    def show_success_message(self, time_seconds):
        # Provide visual feedback to the user
        messagebox.showinfo("Success", "Tweet posted successfully!")
        # Delay to allow the user to see the success message
        time.sleep(time_seconds)

    def handle_error(self, e):
        # Log the specific error details
        self.logger.error(f"An unexpected error occurred: {e}")
        # Display a detailed error message to the user
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = TwitterPoster(root)
    root.mainloop()
