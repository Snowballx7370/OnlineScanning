import csv
import ctypes
import pickle
import traceback

import gspread
import pandas as pd
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import re
import chromedriver_autoinstaller
from selenium.webdriver.common.by import By
from datetime import date
from datetime import timedelta
from datetime import datetime

import os
import random
import string
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials

import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import tkinter as tk
from tkinter import messagebox
import bcrypt
import logging
from logging.handlers import RotatingFileHandler

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/gmail.send']

from config import  *
chromedriver_autoinstaller.install()

# Configure logging
logger = logging.getLogger('long_running_app')
logger.setLevel(logging.INFO)

# Create a handler that writes log messages to a file with rotation
handler = RotatingFileHandler('online-scanning_LOGS.log', maxBytes=5*1024*1024, backupCount=10)  # 5MB per file, 10 backups
handler.setLevel(logging.INFO)

# Create a formatter and set it for the handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)

def fbsearch(keyword):

    url = keyword.split()
    post_url = 'https://www.facebook.com/search/posts?q='
    for i in range(len(url)):
        post_url += str(url[i] + '%20')
    post_url += '&filters=eyJyZWNlbnRfcG9zdHM6MCI6IntcIm5hbWVcIjpcInJlY2VudF9wb3N0c1wiLFwiYXJnc1wiOlwiXCJ9In0%3D'
    print(post_url)
    logger.info(post_url)
    return post_url

def login_to_facebook(username, password):
    LOGIN_URL = "https://www.facebook.com"
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(LOGIN_URL)
    time.sleep(2)
    email_ = driver.find_element(By.NAME, "email")
    pass_ = driver.find_element(By.NAME, "pass")
    email_.send_keys(username)
    time.sleep(1)
    pass_.send_keys(password)
    time.sleep(2)
    email_.submit()
    time.sleep(10)
    return driver

class Post_Scraper:
    """
    Post_Scraper class allows to scrape Facebook Posts based on search queries.
    """
    LOGIN_URL = "https://www.facebook.com"
    MBASIC_URL = "https://mbasic.facebook.com"

    def __init__(self, posts_url) -> None:
        # self.driver = webdriver.Chrome()
        self.posts_url = posts_url.replace("www", "mbasic")


    def login(self, username, password) -> None:
        """
        Login to a Facebook Account.

        Args:
            username (`str`)
                Facebook account username/email
            passward (`str`)
                Facebook account password
        """
        self.driver.get(self.LOGIN_URL)
        time.sleep(2)
        email_ = self.driver.find_element(By.NAME,"email")
        pass_ = self.driver.find_element(By.NAME,"pass")
        email_.send_keys(username)
        time.sleep(1)
        pass_.send_keys(password)
        time.sleep(2)
        email_.submit()
        time.sleep(10)


    def get_content(self, url=None):
        """
        parsing html from a web page.

        Args:
            url (`str`)
                web page url.
        Return:
            A beautiful soup object.
        """
        if url is None:
            url = self.posts_url
        self.driver.get(url)
        page_content = self.driver.page_source
        soup = BeautifulSoup(page_content, 'html.parser')
        return soup

    def clean_url(self, posts_urls_list):
        """
        Convert posts urls to mbasic facebook format.

        Args:
            posts_urls_list (`list[str]`)
        Return:
            A list of urls after applying the cleaning formula.
        """
        clean_posts_urls_list = [self.MBASIC_URL + url.replace("https://m.facebook.com", '').replace(self.MBASIC_URL, '') for url in posts_urls_list]
        return clean_posts_urls_list

    def clean_url_orig(self, orig_url):
        """
        Convert posts urls to original facebook format.

        Args:
            posts_urls_list (`list[str]`)
        Return:
            A list of urls after applying the cleaning formula.
        """
        clean_orig_urls_list = [self.LOGIN_URL + url.replace("https://m.facebook.com", '').replace(self.LOGIN_URL, '') for url in orig_url]
        return clean_orig_urls_list

    def get_more_posts(self, soup):
        time.sleep(random_time)
        """
        get more posts by going to the next page if exist.
        
        Args:
            soup (`bs4.BeautifulSoup object`):
                post html content.
        Return:
            A url (`str`) to get the next page.
        """
        if soup.find("div", id="see_more_pager") is not None:
            more_posts_url = soup.find("div", id="see_more_pager").find('a',href=True)['href']
        else:
            more_posts_url = None
        return more_posts_url

    def get_posts_info(self, soup, posts_urls_list=None, post_date_list=None, likes_list=None, orig_url=None, date_convert=None):
        """
        Extract the full stoy url, the post reactions and the publishing date.
        """

        if posts_urls_list is None:
            posts_urls_list = []
        if post_date_list is None:
            post_date_list = []
        if likes_list is None:
            likes_list = []
        if orig_url is None:
            orig_url = []
        if date_convert is None:
            date_convert = []

        while True:
            time.sleep(2)
            posts = soup.find_all("div", class_="by")
            # print(posts)
            for post in posts:
                like_span = post.find("span", id=re.compile("like_"))
                full_story_tag = post.find('a',href=re.compile("#footer_action_list"))
                if full_story_tag is None:
                    full_story_tag = post.find('a',href=re.compile("/story.php"))
                post_date_abbr = post.find("abbr")
                if full_story_tag:
                    full_story_href = full_story_tag["href"].replace("https://m.facebook.com", '').replace(self.MBASIC_URL, '')
                    posts_urls_list.append(full_story_href)
                    orig_url.append(full_story_href)
                    if post_date_abbr:
                        post_date = post_date_abbr.get_text()
                        post_date_list.append(post_date)
                    else:
                        post_date_list.append('None')

            more_posts_url = self.get_more_posts(soup)
            if more_posts_url:
                soup = self.get_content(more_posts_url)
            else:
                break
        posts_urls_list = self.clean_url(posts_urls_list)
        orig_url = self.clean_url_orig(orig_url)
        # print(orig_url)
        return posts_urls_list, post_date_list, likes_list, orig_url

    def get_profile(self, soup):
        """
        Get the creator profile.
        Args:
            soup (`bs4.BeautifulSoup object`)
        Return:
            A string containing the creator name.
            A string containing the profile url.
        """
        time.sleep(random_time)
        h3 = soup.find("h3")
        if h3 is not None:
            if h3.find('a') is not None:
                profile_name = h3.a.get_text()
                if h3.a.has_attr('href') :
                    h3_a_tag = h3.a['href']
                    h3_a_tag = h3_a_tag.replace("&__tn__=C-R",'')
                    profile_url = self.LOGIN_URL +  h3_a_tag
                else :
                    profile_url = "None"
        else :
            a_tag_actor = soup.find('a',class_="actor-link")
            if a_tag_actor is not None:
                profile_name = a_tag_actor.get_text()
                if a_tag_actor.has_attr('href'):
                    profile_url = self.LOGIN_URL + a_tag_actor['href']
                else:
                    profile_url = "None"
            else:
                profile_name="None"
                profile_url="None"

        return profile_name, profile_url

    def get_post_description(self, soup):
        """
        Extract the post descrtiption (text).
        """
        time.sleep(random_time)
        p=soup.findAll("p")
        if len(p) > 0:
            description_text =' '
            for item in p:
                description_text += item.get_text() + ' '
        else :
            description_text = ' '
            div_tag = soup.find('div',{'data-ft':'{"tn":"*s"}'})
            if div_tag is not None:
                description_text += div_tag.get_text()
            else:
                div_tag =soup.find('div',{'data-ft':'{"tn":",g"}'})
                if div_tag is not None:
                    description_text += div_tag.get_text().split(" · in Timeline")[0].replace('· Public','')
        return description_text

def get_keyword():
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file_loc, SCOPES)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(keyword_spreadsheet_id)
    worksheet = spreadsheet.worksheet(keyword_worksheet_name)
    keywords = worksheet.col_values(5)[1:]
    keyword_list.append(keywords)

    # try:
    #     df = pd.read_excel(keyword_file_loc)
    #
    #     # Access data in column E (assuming column E is the 5th column, index 4)
    #     column_E_data = df.iloc[:, 4]
    #
    #     for value in column_E_data:
    #         if pd.notna(value):  # Check if the cell is not empty
    #             keyword_list.append(re.sub(r"[^a-zA-Z0-9- ]", "", str(value)))
    #
    #     if not keyword_list:
    #         print('No data found.')
    #         return
    #
    #     # Now you have keyword_list containing the values from column E
    #     # You can use keyword_list as needed in your code
    #
    # except Exception as e:
    #     print(e)

def get_creds():
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file_loc, SCOPES)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(creds_spreadsheet_id)
    worksheet = spreadsheet.worksheet(creds_worksheet_name)
    platform = worksheet.col_values(2)[1:]
    user = worksheet.col_values(3)[1:]
    password = worksheet.col_values(4)[1:]
    status = worksheet.col_values(5)[1:]

    for values in zip(platform, user, password, status):
        cred_list.append(list(values))

def get_existing_descriptions():
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file_loc, SCOPES)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(write_spreadsheet_id)
    worksheet = spreadsheet.worksheet(write_worksheet_name)
    links = worksheet.col_values(11)[1:]
    names = worksheet.col_values(10)[1:]

    data = list(zip(links, names))
    existing_descriptions.append(data)
    # existing_descriptions.append(names)

def write_data():
    # get_existing_descriptions()
    # print(existing_descriptions)
    # if (seller_name,details) not in existing_descriptions:
    #     seller_name_list = [seller_name]

    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file_loc, SCOPES)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(write_spreadsheet_id)
    worksheet = spreadsheet.worksheet(write_worksheet_name)

    last_row = len(worksheet.col_values(1)) + 1
    update_range = f"A{last_row}:S{last_row + len(write_data_list) - 1}"
    worksheet.update(update_range, write_data_list)

        # data = [[str(unique), open, department, section, rpa, "Python", str(date_of_post), str(current_time), fb, ", ".join(seller_name_list), str(post_url), category, keyword, str(details),"No", "No", "No", section, section]]

        # try:
        #     service = build('sheets', 'v4', developerKey=API_KEY, credentials=creds)
        #
        #     range_name = "OS MAIN"  # Replace this with the sheet name and range you want to write to
        #     # Retrieve the current values in the sheet
        #     result = service.spreadsheets().values().get(spreadsheetId=write_spreadsheet_id, range=range_name).execute()
        #     values = result.get('values', [])
        #
        #     if not values:
        #         print('No data found.')
        #         return
        #
        #     # Calculate the next row to write to
        #     next_row = len(values) + 1
        #     # Prepare the data to write as a list of rows
        #     data = [[str(unique), open, department, section, rpa, "Python", str(date_of_post), str(current_time), fb, ", ".join(seller_name_list), str(post_url), category, keyword, str(details),"No", "No", "No", section, section]]
        #
        #     # Write the data to the sheet
        #     body = {'values': data}  # Pass data as a list of rows
        #     try:
        #         service.spreadsheets().values().append(
        #             spreadsheetId=write_spreadsheet_id,
        #             range=f"{range_name}!A{next_row}",
        #             valueInputOption='RAW',
        #             body=body,
        #         ).execute()
        #         print('Data successfully written to the sheet.')
        #     except HttpError as error:
        #         print(f'An error occurred: {error}')
        #
        # except HttpError as err:
        #     print(err)
    # else:
    #     print('Description already exists in Google Sheets. Skipping entry.')

def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_unique_string(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_unique_id(length, existing_strings):
    while True:
        new_string = "RPA-" + generate_unique_string(length)
        if new_string not in existing_strings:
            return new_string

def gen_unique_id(number_posts_max,existing_strings):

    for _ in range(number_posts_max):  # Generate 10 unique strings
        new_string = generate_unique_id(6, existing_strings)
        existing_strings.append(new_string)
        new_unique_id.append(new_string)
        print(new_string)
        logger.info(new_string)

def get_from_keywords_sheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file_loc, SCOPES)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(keyword_spreadsheet_id)
    worksheet = spreadsheet.worksheet(keyword_worksheet_name)
    department = worksheet.col_values(2)[1:]
    section = worksheet.col_values(3)[1:]
    category = worksheet.col_values(4)[1:]

    outer_department_list.append(department)
    outer_section_list.append(section)
    outer_category_list.append(category)


def get_unique_sheets():
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file_loc, SCOPES)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(write_spreadsheet_id)
    worksheet = spreadsheet.worksheet(write_worksheet_name)
    ids = worksheet.col_values(1)[1:]
    existing_strings.append(ids)
def display_on():
    global root
    print("Always On")
    ctypes.windll.kernel32.SetThreadExecutionState(0x80000002)

def upload_csv_to_gsheets():
    data = pd.read_csv(output_file_name, skiprows=1)
    url_values = data.iloc[:, 10]
    name_values = data.iloc[:, 9]
    get_existing_descriptions()
    inner_existing_descriptions = existing_descriptions[0]
    # print(len(url_values))
    # print(url_values)

    for i in range(len(url_values)):
        if (url_values[i], name_values[i]) not in inner_existing_descriptions:
            row_values = (data.iloc[i-1, 0], data.iloc[i-1, 1], data.iloc[i-1, 2], data.iloc[i-1, 3], data.iloc[i-1, 4], data.iloc[i-1, 5], data.iloc[i-1, 6], data.iloc[i-1, 7], data.iloc[i-1, 8], data.iloc[i-1, 9], data.iloc[i-1, 10], data.iloc[i-1, 11], data.iloc[i-1, 12], data.iloc[i-1, 13], data.iloc[i-1, 14], data.iloc[i-1, 15], data.iloc[i-1, 16], data.iloc[i-1, 17], data.iloc[i-1, 18])
            row_values = [str(value) for value in row_values]
    #         # row_list = row_values.tolist()
            write_data_list.append(row_values)
    #         print(row_values)
            print("Not existing csv")
            # logger.info("Not existing csv")
        else:
            print("Existing csv")
            # logger.info("Existing csv")
            df_existing = pd.read_csv(output_file_name)


            new_value = 'Appended'
            row_to_change = i
            column_to_change = 'Remarks'

            df_existing.at[row_to_change, column_to_change] = new_value

            df_existing.to_csv(output_file_name, index=False)
            print(f"Data updated in {output_file_name}")
            logger.info(f"Data updated in {output_file_name}")
    write_data()
    print(write_data_list)
    logger.info(write_data_list)

def update_suspended(suspend, status):
    # get_existing_descriptions()
    # print(existing_descriptions)
    # if (seller_name,details) not in existing_descriptions:
    #     seller_name_list = [seller_name]

    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file_loc, SCOPES)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(creds_spreadsheet_id)
    worksheet = spreadsheet.worksheet(creds_worksheet_name)

    # last_row = len(worksheet.col_values(1)) + 1
    # update_range = f"A{last_row}:S{last_row + len(write_data_list) - 1}"
    update_range = f"E{suspend}"
    worksheet.update(update_range, status)

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against the stored hash."""
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

def attempt_login():
    """Handle login attempt."""
    entered_password = password_entry.get()
    if verify_password(entered_password, stored_password_hash):
        messagebox.showinfo("Success", "Password correct! Proceeding to the main program.")
        login_window.destroy()
    else:
        messagebox.showerror("Error", "Incorrect password. Please try again.")

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
if __name__ == "__main__":
    create_login_window()
    run = 0
    while run < 1:
        run = 1
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file_loc, SCOPES)

        keyword_list = []
        cred_list = []
        creds_fb_email = []
        creds_fb_password = []
        outer_department_list = []
        outer_section_list = []
        outer_category_list = []
        existing_strings = []
        existing_descriptions = []

        get_keyword()
        print(keyword_list)
        logger.info(keyword_list)
        get_creds()
        # print(cred_list)
        get_from_keywords_sheet()
        # print(department_list)
        # driver = login_to_facebook(creds_fb[0], creds_fb[1])
        facebook_emails = [user[1] for user in cred_list if user[0] == 'Facebook' and user[3] == 'Active']
        facebook_passwords = [user[2] for user in cred_list if user[0] == 'Facebook' and user[3] == 'Active']
        # print(facebook_emails)
        inner_keyword_list = keyword_list[0]
        department_list = outer_department_list[0]
        section_list = outer_section_list[0]
        category_list = outer_category_list[0]
        # print(inner_keyword_list)
        # print(len(inner_keyword_list))
        x = 0
        skip = 0
        # while iteration < 2:
        while x < len(inner_keyword_list):
            while True:
                from config import number_posts_max

                display_on()
                try:
                    active_facebook_entries = [user for user in cred_list if
                                               user[0] == 'Facebook' and user[3] == 'Active']
                    user = active_facebook_entries[x % len(active_facebook_entries)]

                    # print(x)
                    # print("Skip" + str(skip))
                    write_data_list = []
                    index = (x + skip) % len(facebook_emails)
                    current_email_index = (x + skip) % len(facebook_emails)
                    current_email = facebook_emails[current_email_index]
                    current_password_index = (x + skip) % len(facebook_passwords)
                    current_password = facebook_passwords[current_password_index]
                    # current_password = facebook_passwords[x + skip % len(facebook_passwords)]
                    # print("current " + str(current_email) + " " + str(current_password))
                    driver = login_to_facebook(current_email, current_password)
                    try:
                        driver.find_element(By.XPATH, '//div[@class="fsl fwb fcb" and text()="Wrong Credentials"]')
                        print("Wrong creds")
                        logger.info("Wrong creds")
                        status = "Wrong credentials"
                        update_suspended(index + 2, status)
                        skip = skip + 1
                        driver.close()
                        continue

                    except NoSuchElementException:
                        random_time = 3

                        time.sleep(5)
                        scraper = Post_Scraper(fbsearch(inner_keyword_list[x]))
                        scraper.driver = driver
                        soup = scraper.get_content()
                        # print(soup)
                        posts_urls_list, post_date_list, likes_list, orig_url = scraper.get_posts_info(soup)
                        print(f">>> Number of Posts Available: {len(posts_urls_list)}")
                        logger.info(f">>> Number of Posts Available: {len(posts_urls_list)}")
                        print(f"number_posts_max: {number_posts_max}")
                        logger.info(f"number_posts_max: {number_posts_max}")

                        profile_names_list, profile_urls_list, descriptions_list, who_commented_list, comments_list = [], [], [], [], []
                        if number_posts_max > len(posts_urls_list):
                            number_posts_max = len(posts_urls_list)
                        get_unique_sheets()
                        convert_date = []
                        new_unique_id = []
                        gen_unique_id(number_posts_max, existing_strings)
                        for i in range(number_posts_max):
                            # print("true")
                            time.sleep(3)
                            post_url = posts_urls_list[i]
                            post_soup = scraper.get_content(post_url)
                            time.sleep(3)
                            profile_name, profile_url = scraper.get_profile(post_soup)
                            profile_names_list.append(profile_name)
                            profile_urls_list.append(profile_url)
                            descriptions_list.append(scraper.get_post_description(post_soup))
                            # Convert date of post
                            date_text = post_date_list[i]
                            split_date_text = date_text.split()
                            print(split_date_text)
                            logger.info(split_date_text)

                            today = date.today()
                            now = datetime.now()
                            # current_time = now.strftime("%d-%m-%Y %H:%M")
                            current_time = now.strftime("%m/%d/%Y %H:%M:%S")
                            this_month = today.strftime('%B')
                            yesterday = today - timedelta(days=1)
                            none = 'None'

                            if split_date_text[0] == 'Yesterday':
                                try:
                                    time_post = split_date_text[2]
                                    yesterday = yesterday.strftime("%m/%d/%Y")
                                    time_post = time_post.strftime("%H:%M:%S")
                                    time_post_datetime = datetime.strptime(time_post, "%H:%M:%S")
                                    formatted_time = time_post_datetime.strftime("%H:%M:%S")
                                    concat_date_time = str(yesterday) + " " + str(formatted_time)
                                    convert_date.append(concat_date_time)
                                except:
                                    convert_date.append(none)

                            elif len(split_date_text) > 2 and split_date_text[1] in ['January', 'February', 'March',
                                                                                     'April', 'May', 'June', 'July',
                                                                                     'August', 'September', 'October',
                                                                                     'November', 'December']:
                                if split_date_text[3].isdigit():
                                    year_num = datetime.strptime(split_date_text[3], '%Y').year
                                else:
                                    year_num = today.year
                                month_num = datetime.strptime(split_date_text[1], '%B').month
                                date_num = datetime.strptime(split_date_text[0], '%d').day

                                date_append = datetime(year_num, month_num, date_num).date()
                                if split_date_text[3] == "at":
                                    time_post = split_date_text[4]
                                else:
                                    time_post = split_date_text[3]
                                date_append = date_append.strftime("%m/%d/%Y")
                                time_post = time_post.strftime("%H:%M:%S")
                                time_post_datetime = datetime.strptime(time_post, "%H:%M:%S")
                                formatted_time = time_post_datetime.strftime("%H:%M:%S")
                                concat_date_time = str(date_append) + " " + str(time_post)
                                convert_date.append(concat_date_time)

                            elif len(split_date_text) > 2 and split_date_text[0] in ['January', 'February', 'March',
                                                                                     'April', 'May', 'June', 'July',
                                                                                     'August', 'September', 'October',
                                                                                     'November', 'December']:
                                month_num = datetime.strptime(split_date_text[0], '%B').month
                                # date_num = datetime.strptime(split_date_text[1], '%d').day
                                date_num = datetime.strptime(split_date_text[1].replace(',', ''), '%d').day
                                if split_date_text[2].isdigit():
                                    year_num = datetime.strptime(split_date_text[2], '%Y').year
                                else:
                                    year_num = today.year
                                date_append = datetime(year_num, month_num, date_num).date()
                                if len(split_date_text) == 6:
                                    concat_time = split_date_text[4] + split_date_text[5]
                                else:
                                    concat_time = split_date_text[3] + split_date_text[4]
                                time_post = datetime.strptime(concat_time, '%I:%M%p')
                                time_post_convert = time_post.strftime('%H:%M:%S')
                                date_append = date_append.strftime("%m/%d/%Y")
                                concat_date_time = str(date_append) + " " + str(time_post_convert)

                                convert_date.append(concat_date_time)

                            elif len(split_date_text) >= 2 and any(
                                    [split_date_text[1] == 'hr', split_date_text[1] == 'hrs',
                                     split_date_text[1] == 'min', split_date_text[1] == 'mins']):
                                if split_date_text[1] == 'hrs' or split_date_text[1] == 'hr':
                                    sub_hours = timedelta(hours=int(split_date_text[0]))
                                    time_post = now - sub_hours
                                else:
                                    sub_minutes = timedelta(minutes=int(split_date_text[0]))
                                    time_post = now - sub_minutes

                                adjust_date = time_post.date()
                                time_post_convert = time_post.strftime('%H:%M:%S')
                                adjust_date = adjust_date.strftime("%m/%d/%Y")
                                concat_date_time = str(adjust_date) + " " + str(time_post_convert)
                                convert_date.append(concat_date_time)
                            else:
                                convert_date.append(none)
                            match = re.search(r'story_fbid=([A-Za-z0-9]+)&id=([A-Za-z0-9]+)', orig_url[i])

                            if match:
                                story_fbid = match.group(1)
                                id_value = match.group(2)

                                # Create a shorter Facebook URL
                                short_url = f"https://www.facebook.com/{id_value}/posts/{story_fbid}"

                                print(short_url)
                                logger.info(short_url)
                            else:
                                print("Unable to extract the required parameters from the URL.")
                                logger.info("Unable to extract the required parameters from the URL.")
                                short_url = "None"

                            # print(inner_existing_descriptions)
                            if profile_names_list[i] == 'None':
                                print("NONE!!")
                                skip = skip + 1
                                status = "Suspended"
                                update_suspended(index + 2, status)
                                break
                            else:

                                print("----------------------------------")
                                logger.info("----------------------------------")
                                print(short_url)
                                logger.info(short_url)
                                print(post_date_list[i])
                                logger.info(post_date_list[i])
                                print(f"post {i + 1} successfully scraped")
                                logger.info(f"post {i + 1} successfully scraped")
                                print(inner_keyword_list[x])
                                logger.info(inner_keyword_list[x])
                                print(convert_date[i])
                                logger.info(convert_date[i])
                                fb = 'Facebook'
                                rpa = 'RPA'
                                open = 'OPEN'
                                python = 'Python'

                                get_existing_descriptions()
                                inner_existing_descriptions = existing_descriptions[0]
                                if (short_url, profile_names_list[i]) not in inner_existing_descriptions:
                                    print("Not existing")
                                    if convert_date[i] != 'None':
                                        converted_date = datetime.strptime(convert_date[i], "%m/%d/%Y %H:%M:%S")
                                        difference = now - converted_date
                                        diff_in_days = difference.days
                                        days_in_month = 30
                                        # print("diff:" + str(diff_in_days))
                                        if (diff_in_days < days_in_month):
                                            print("New Data")
                                            data_to_append = (
                                                new_unique_id[i], open, department_list[x], section_list[x], rpa,
                                                python,
                                                convert_date[i], current_time, fb, profile_names_list[i], short_url,
                                                category_list[x], inner_keyword_list[x], " ", "No", "No", "No",
                                                section_list[x], section_list[x])
                                            print(data_to_append)
                                            write_data_list.append(data_to_append)
                                            data_to_append_csv = [(new_unique_id[i], open, department_list[x],
                                                                   section_list[x], rpa, python, convert_date[i],
                                                                   current_time, fb, profile_names_list[i], short_url,
                                                                   category_list[x], inner_keyword_list[x], " ", "No",
                                                                   "No", "No", section_list[x], section_list[x], " ")]

                                            column_names = ["Unique ID", "OS Status", "Department", "Section", "Source",
                                                            "OS By", "Date of Post", "Monitoring Date", "Site Source",
                                                            "Post Owner", "Link URL", "Keyword Category", "Keyword",
                                                            "Details of Assessment", "With Disposition?", "Case Close?",
                                                            "VPN Related?", "HandledBy", "HandledBy Section", "Remarks"]
                                            # Check if the Excel file already exists
                                            if os.path.exists(output_file_name):
                                                # Append data to the existing Excel file

                                                df_existing = pd.read_csv(output_file_name)
                                                df_new_data = pd.DataFrame(data_to_append_csv, columns=column_names)
                                                df_combined = pd.concat([df_existing, df_new_data], ignore_index=True)
                                                df_combined.to_csv(output_file_name, index=False)
                                                print(f"Data appended to {output_file_name}")
                                                logger.info(f"Data appended to {output_file_name}")
                                            else:
                                                # Create a new Excel file and save the data
                                                df = pd.DataFrame(data_to_append_csv, columns=column_names)
                                                df.to_csv(output_file_name, index=False)
                                                print(f"New CSV file {output_file_name} created with data")
                                                logger.info(f"New CSV file {output_file_name} created with data")
                                        else:
                                            print("Post is more than 1 month")
                                else:
                                    print('Description already exists in Google Sheets. Skipping entry.')
                        if x == len(inner_keyword_list):
                            break
                        else:
                            x = x + 1
                            # print(write_data_list)
                        # data_to_append = (new_unique_id[i],department_list[x], section_list[x], category_list[x],fb,rpa,open,inner_keyword_list[x],this_month, current_time, convert_date[i], profile_names_list[i], descriptions_list[i],orig_url[i])
                        # skip = skip + 1
                        write_data()
                        write_data_list = []
                        existing_descriptions = []
                        print(len(profile_names_list), len(descriptions_list), len(profile_urls_list))
                        # driver.close()

                        if skip == len(facebook_emails):
                            skip = 0
                        scraper.driver.close()
                except Exception as e:
                    print(f"An error occurred: {e}")
                    logger.error(f"An error occurred: {e}")
                    if x == len(inner_keyword_list):
                        break
                    else:
                        x = x + 1

        upload_csv_to_gsheets()
        run = 0
        x = 0

    # except Exception as e:
    #     # Handle exceptions and send email notification
    #     exception_info = traceback.format_exc()
    #     # log_info = "Logs:\n"
    #     # log_info += str(post_date_list) + "\n" + str(convert_date)
    #     # error_message = f"Error occurred: {str(e)}"
    #     # error_message = f"Error occurred:\n{exception_info}\n\n{log_info}"
    #     error_message = f"Error occurred:\n{exception_info}"
    #     print(error_message)
    #     send_email("Code Exception Notification", error_message)