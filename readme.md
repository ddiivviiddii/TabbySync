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

### Security

Please note that `config.cfg` stores your WebDAV credentials in plain text format.

The data in `config.yaml` is encrypted by Tabby. Use a strong password for encryption and trust that no one can hack it :-)