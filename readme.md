## Simple credential synchronized for Tabby

This script uploads/downloads Tabby’s config.yaml to/from WebDAV storage. It also allows backing up the current configuration to local storage. The script features a GUI and can run on any system where Python is supported.


Usage:
- fill out config.cfg
- install required Python modules
- run

### Required Python modules

`requests`, `pytz`

### Configuration File (config.cfg)
The included config.cfg is configured for Windows. For macOS or Linux, you will need to rewrite the paths accordingly.

`webdav_url`

Point you server URL. The default is Yandex.Disk


`webdav_folder`

Full path to the WebDAV folder starting with `\`

`username` and `password`

WebDAV credentials

`path_to_file`

Path to Tabbys' config.yaml. In Windows it is `<YOUR_DISK>:\Users\<WINDOWS_USER_FOLDER>\AppData\Roaming\tabby\`

Replace `<YOUR_DISK>` and `<WINDOWS_USER_FOLDER>` with actual values.

`name_of_file`

Name of the Tabby configuration file. Currently, it is `config.yaml`

`destination_folder`

Path for local backup place for config.yaml. No versioning or additional backup features are included—it simply performs a copy operation.

### Runs script as application

You can run this script as standalone application without Python on the host.

Install `pyinstaller`:

`pip install pyinstaller`

Run from folder where the script is stored:

`pyinstaller --onefile --windowed --name TabbySync main.py`

Copy `TabbySync.exe` (for Windows application) to any folder for future use. Add `config.cfg` to this folder. Start of the application on Windows may be slow due possible antivirus check and start of PyInstaller engine.  



### Security

Please note that `config.cfg` stores your WebDAV credentials in plain text format.

The data in `config.yaml` is encrypted by Tabby. Use a strong password for encryption and trust that no one can hack it :-)