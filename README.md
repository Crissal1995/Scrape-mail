# Scrape-mail
[![Linters](https://github.com/Crissal1995/Scrape-mail/actions/workflows/linters.yaml/badge.svg)](https://github.com/Crissal1995/auto_msrewards/actions/workflows/linters.yaml)
[![Tests](https://github.com/Crissal1995/Scrape-mail/actions/workflows/tests.yaml/badge.svg)](https://github.com/Crissal1995/auto_msrewards/actions/workflows/tests.yaml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


## Description
**Scrape-mail** is a tool created to easily and automatically download 
all the attachments of all the emails in a mailbox by simply launching it. 

It is also possible to set up filters, both on the subject of the email
and on the filename, in order to make the experience as immediate as possible.

## Usage

### Credentials
Create your `credentials.json` following the example file. 

If you cannot create it, it's also possible to use the tool interactively
by typing username and password.

### Python
Python version must be 3.7+.

You need to install the requirements with the command: 
```bash
python3 -m pip install -r requirements.txt
```

### Execution
Once you're done with configuration, you can execute Scrape-mail with the command:
```bash
python3 main.py
```

### Help
If you want to customize the experience, add filters and other things, you can
check the help of the tool with the command: 
```bash
python3 main.py --help
```
