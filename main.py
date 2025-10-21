import os
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import configparser
import pytz
import logging
import shutil

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

CONFIG_FILE = 'config.cfg'
CONFIG_PARSER = configparser.ConfigParser()

# Default configuration values
DEFAULT_CONFIG = {
    'webdav_url': 'https://webdav.yandex.ru/',
    'webdav_folder': '/Tabby',
    'username': '',
    'password': '',
    'path_to_file': '',
    'name_of_file': 'config.yaml',
    'destination_folder': ''
}


def load_config():
    config = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_FILE):
        CONFIG_PARSER.read(CONFIG_FILE)
        if 'WebDAV' in CONFIG_PARSER:
            config.update(CONFIG_PARSER['WebDAV'])
    return config


def save_config(config):
    CONFIG_PARSER['WebDAV'] = config
    with open(CONFIG_FILE, 'w') as configfile:
        CONFIG_PARSER.write(configfile)


# Load configuration
WEBDAV_CONFIG = load_config()
WEBDAV_URL = WEBDAV_CONFIG['webdav_url']
WEBDAV_FOLDER = WEBDAV_CONFIG['webdav_folder']
WEBDAV_USER = WEBDAV_CONFIG['username']
WEBDAV_PASSWORD = WEBDAV_CONFIG['password']
PATH_TO_FILE = WEBDAV_CONFIG['path_to_file']
NAME_OF_FILE = WEBDAV_CONFIG['name_of_file']
DESTINATION_FOLDER = WEBDAV_CONFIG['destination_folder']
PATH_TO_FILE_TO_SYNC = os.path.join(PATH_TO_FILE, NAME_OF_FILE)
WEBDAV_FILE = f'{WEBDAV_URL.rstrip("/")}/{WEBDAV_FOLDER.strip("/")}/{NAME_OF_FILE}'.strip('/')


def get_webdav_file_modification_date():
    try:
        response = requests.head(WEBDAV_FILE, auth=HTTPBasicAuth(WEBDAV_USER, WEBDAV_PASSWORD), timeout=10)
        if response.status_code == 200:
            return response.headers.get('Last-Modified')
        logging.warning(f"WebDAV HEAD request failed with status {response.status_code}")
        return None
    except requests.RequestException as e:
        logging.error(f"WebDAV connection error: {e}")
        return None


def get_local_file_modification_date():
    try:
        if os.path.exists(PATH_TO_FILE_TO_SYNC):
            local_mod_time = os.path.getmtime(PATH_TO_FILE_TO_SYNC)
            return datetime.fromtimestamp(local_mod_time).strftime('%Y-%m-%d %H:%M:%S')
        return None
    except OSError as e:
        logging.error(f"Error getting local file modification date: {e}")
        return None


def update_modification_dates(local_label, remote_label):
    global LAST_MODIFIED_REMOTE, LAST_MODIFIED_LOCAL

    # Get remote file date
    remote_mod_date_str = get_webdav_file_modification_date()
    if remote_mod_date_str:
        try:
            remote_mod_date = datetime.strptime(remote_mod_date_str, '%a, %d %b %Y %H:%M:%S %Z')
            original_tz = pytz.timezone('GMT')  # WebDAV typically uses GMT
            remote_mod_date = original_tz.localize(remote_mod_date)
            msk_tz = pytz.timezone('Europe/Moscow')
            remote_mod_date_msk = remote_mod_date.astimezone(msk_tz)
            LAST_MODIFIED_REMOTE = remote_mod_date_msk.strftime('%Y-%m-%d %H:%M:%S')
            logging.info(f"Remote file date: {LAST_MODIFIED_REMOTE}")
        except ValueError as e:
            logging.error(f"Error parsing remote date: {e}")
            LAST_MODIFIED_REMOTE = "Parse error"
    else:
        LAST_MODIFIED_REMOTE = "Unavailable"

    LAST_MODIFIED_LOCAL = get_local_file_modification_date() or "File not found"
    logging.info(f"Local file date: {LAST_MODIFIED_LOCAL}")

    local_label.config(text=f"Local file date: {LAST_MODIFIED_LOCAL}")
    remote_label.config(text=f"Remote file date: {LAST_MODIFIED_REMOTE}")


def sync_from_remote():
    try:
        response = requests.get(WEBDAV_FILE, auth=HTTPBasicAuth(WEBDAV_USER, WEBDAV_PASSWORD), timeout=30)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(PATH_TO_FILE_TO_SYNC), exist_ok=True)
            with open(PATH_TO_FILE_TO_SYNC, 'wb') as file:
                file.write(response.content)
            messagebox.showinfo("Sync", f"Downloaded {NAME_OF_FILE} from WebDAV.")
        else:
            messagebox.showerror("Sync", f"Failed to download {NAME_OF_FILE}. Status code: {response.status_code}")
    except Exception as e:
        messagebox.showerror("Sync", f"Error downloading file: {str(e)}")


def sync_to_remote():
    if not os.path.exists(PATH_TO_FILE_TO_SYNC):
        messagebox.showerror("Sync", f"Local file does not exist: {PATH_TO_FILE_TO_SYNC}")
        return

    try:
        with open(PATH_TO_FILE_TO_SYNC, 'rb') as file:
            response = requests.put(WEBDAV_FILE, data=file,
                                    auth=HTTPBasicAuth(WEBDAV_USER, WEBDAV_PASSWORD),
                                    timeout=30)
            if response.status_code in (200, 201, 204):
                messagebox.showinfo("Sync", f"Uploaded {NAME_OF_FILE} to WebDAV.")
            else:
                messagebox.showerror("Sync", f"Failed to upload {NAME_OF_FILE}. Status code: {response.status_code}")
    except Exception as e:
        messagebox.showerror("Sync", f"Error uploading file: {str(e)}")


def configure_webdav_options():
    global WEBDAV_CONFIG, WEBDAV_URL, WEBDAV_FOLDER, WEBDAV_USER, WEBDAV_PASSWORD
    global PATH_TO_FILE, NAME_OF_FILE, DESTINATION_FOLDER, PATH_TO_FILE_TO_SYNC, WEBDAV_FILE

    current_config = {
        'webdav_url': WEBDAV_URL,
        'webdav_folder': WEBDAV_FOLDER,
        'username': WEBDAV_USER,
        'password': WEBDAV_PASSWORD,
        'path_to_file': PATH_TO_FILE,
        'name_of_file': NAME_OF_FILE,
        'destination_folder': DESTINATION_FOLDER
    }

    config_window = tk.Toplevel()
    config_window.title("Configure WebDAV Options")
    config_window.geometry("400x230")

    entries = {}
    row = 0
    for key, value in current_config.items():
        tk.Label(config_window, text=key.replace('_', ' ').title()).grid(row=row, column=0, sticky='w', padx=5, pady=2)
        entry = tk.Entry(config_window, width=40)
        entry.grid(row=row, column=1, padx=5, pady=2)
        entry.insert(0, value)
        entries[key] = entry
        row += 1

    def save_and_close():
        WEBDAV_CONFIG.update({key: entry.get() for key, entry in entries.items()})
        WEBDAV_URL = WEBDAV_CONFIG['webdav_url']
        WEBDAV_FOLDER = WEBDAV_CONFIG['webdav_folder']
        WEBDAV_USER = WEBDAV_CONFIG['username']
        WEBDAV_PASSWORD = WEBDAV_CONFIG['password']
        PATH_TO_FILE = WEBDAV_CONFIG['path_to_file']
        NAME_OF_FILE = WEBDAV_CONFIG['name_of_file']
        DESTINATION_FOLDER = WEBDAV_CONFIG['destination_folder']

        global PATH_TO_FILE_TO_SYNC, WEBDAV_FILE
        PATH_TO_FILE_TO_SYNC = os.path.join(PATH_TO_FILE, NAME_OF_FILE)
        WEBDAV_FILE = f'{WEBDAV_URL.rstrip("/")}/{WEBDAV_FOLDER.strip("/")}/{NAME_OF_FILE}'.strip('/')

        save_config(WEBDAV_CONFIG)
        config_window.destroy()
        messagebox.showinfo("Config", "Configuration saved successfully!")

    tk.Button(config_window, text="Save", command=save_and_close).grid(row=row, column=1, pady=10)


def check_webdav_connection():
    logging.info("Checking WebDAV connection...")
    logging.info(f"WebDAV URL: {WEBDAV_URL}")
    logging.info(f"WebDAV Folder: {WEBDAV_FOLDER}")
    logging.info(f"Username: {WEBDAV_USER}")

    try:
        response = requests.head(WEBDAV_URL, auth=HTTPBasicAuth(WEBDAV_USER, WEBDAV_PASSWORD), timeout=10)
        logging.info(f"Status code: {response.status_code}")
        if response.status_code == 200:
            return True, "Connected to WebDAV server"
        else:
            return False, f"Status code: {response.status_code}"
    except requests.RequestException as e:
        return False, str(e)


def update_webdav_status_label(webdav_status_label):
    webdav_status, webdav_message = check_webdav_connection()
    if not webdav_status:
        messagebox.showerror("WebDAV Connection", f"Failed to connect to WebDAV server. {webdav_message}")
        webdav_status_label.config(text="WebDAV не аллё!", fg="red")
    else:
        webdav_status_label.config(text="WebDAV подключен", fg="green")


def copy_file_to_folder():
    if not os.path.exists(PATH_TO_FILE_TO_SYNC):
        messagebox.showerror("Error", f"Source file does not exist: {PATH_TO_FILE_TO_SYNC}")
        return

    if not os.path.exists(DESTINATION_FOLDER):
        messagebox.showerror("Error", f"Destination folder does not exist: {DESTINATION_FOLDER}")
        return

    destination_path = os.path.join(DESTINATION_FOLDER, NAME_OF_FILE)
    try:
        shutil.copy2(PATH_TO_FILE_TO_SYNC, destination_path)  # copy2 preserves metadata
        messagebox.showinfo("Copy File", f"File copied to {destination_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to copy file: {str(e)}")


def create_gui():
    root = tk.Tk()
    root.title("WebDAV-One-File-Sync")
    root.geometry("320x320")

    # Status labels
    webdav_status_label = tk.Label(root, text="Checking WebDAV connection...")
    webdav_status_label.pack(pady=5)

    local_label = tk.Label(root, text="Local file date: Checking...")
    local_label.pack(pady=5)

    remote_label = tk.Label(root, text="Remote file date: Checking...")
    remote_label.pack(pady=5)

    # Update status on startup
    update_webdav_status_label(webdav_status_label)
    update_modification_dates(local_label, remote_label)

    # Buttons
    tk.Button(root, text="Sync from remote", command=sync_from_remote).pack(pady=5)
    tk.Button(root, text="Sync to remote", command=sync_to_remote).pack(pady=5)
    tk.Button(root, text="Recheck", command=lambda: update_modification_dates(local_label, remote_label)).pack(pady=5)
    tk.Button(root, text="Configure WebDAV Options", command=configure_webdav_options).pack(pady=5)
    tk.Button(root, text="Check WebDAV Connection",
              command=lambda: update_webdav_status_label(webdav_status_label)).pack(pady=5)
    tk.Button(root, text="Copy File to Folder", command=copy_file_to_folder).pack(pady=5)

    root.mainloop()


if __name__ == '__main__':
    create_gui()
