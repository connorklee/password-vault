import sqlite3
import hashlib
from tkinter import *
from tkinter.font import BOLD
from tkinter import simpledialog
from functools import partial

# database
with sqlite3.connect("passwordvault.db") as db:
    cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS masterpassword(
id INTEGER PRIMARY KEY,
password TEXT NOT NULL);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS vault(
id INTEGER PRIMARY KEY,
website TEXT NOT NULL,
username TEXT NOT NULL,
password TEXT NOT NULL);
""")

# POPUP


def popUp(text):
    answer = simpledialog.askstring("input string", text)
    return answer


# initiate window
window = Tk()

window.title("Password Vault")


def hashPassword(input):
    hash = hashlib.md5(input)
    hash = hash.hexdigest()

    return hash


def createScreen():
    window.geometry("350x200")

    home_lbl = Label(window, text="Create Master Password:")
    home_lbl.config(anchor=CENTER)
    home_lbl.pack()

    txt = Entry(window, width=20)
    txt.pack()
    txt.focus

    confirm_lbl = Label(window, text="Re-enter Password: ")
    confirm_lbl.pack()

    txt1 = Entry(window, width=20)
    txt1.pack()
    txt1.focus

    error_lbl = Label(window)
    error_lbl.pack()

    def savePassword():
        if txt.get() == txt1.get():
            hashedPassword = hashPassword(txt.get().encode('utf-8'))

            insert_password = """INSERT INTO masterpassword(password)
            VALUES(?)"""
            cursor.execute(insert_password, [(hashedPassword)])
            db.commit()

            for widget in window.winfo_children():
                widget.destroy()

            loginScreen()
        else:
            error_lbl.config(text="Passwords do not match!")

    btn = Button(window, text="Save", command=savePassword)
    btn.pack(pady=1)


def loginScreen():
    window.geometry("350x200")

    home_lbl = Label(window, text="Enter Master Password:")
    home_lbl.config(anchor=CENTER)
    home_lbl.pack()

    txt = Entry(window, width=20, show="*")
    txt.pack()
    txt.focus

    error_lbl = Label(window)
    error_lbl.pack()

    def getMasterPassword():
        checkHashedPassword = hashPassword(txt.get().encode('utf-8'))
        cursor.execute(
            "SELECT * FROM masterpassword WHERE id = 1 AND password = ?", [(checkHashedPassword)])
        return cursor.fetchall()

    def checkPassword():
        match = getMasterPassword()

        if match:
            passwordVault()
        else:
            txt.delete(0, 'end')
            error_lbl.config(text="Wrong Password. Try again.")

    btn = Button(window, text="Submit", command=checkPassword)
    btn.pack(pady=1)


def passwordVault():
    for widget in window.winfo_children():
        widget.destroy()

    def addEntry():
        text1 = "Website"
        text2 = "Username"
        text3 = "Password"

        website = popUp(text1)
        username = popUp(text2)
        password = popUp(text3)

        insert_fields = """INSERT INTO vault(website, username, password)
        VALUES(?, ?, ?)"""

        cursor.execute(insert_fields, (website, username, password))
        db.commit()

        passwordVault()

    def removeEntry(input):
        cursor.execute("DELETE FROM vault WHERE id = ?", (input,))
        db.commit()

        passwordVault()

    window.geometry("750x350")

    lbl = Label(window, text="Your Password Vault",
                font=("Futura", 16, "bold"))
    lbl.grid(column=1)

    btn = Button(window, text="+", command=addEntry)
    btn.grid(column=1, pady=5)

    lbl = Label(window, text="Website")
    lbl.grid(row=2, column=0, padx=80)
    lbl = Label(window, text="Username")
    lbl.grid(row=2, column=1, padx=80)
    lbl = Label(window, text="Password")
    lbl.grid(row=2, column=2, padx=80)

    cursor.execute("SELECT * FROM vault")
    if(cursor.fetchall() != None):
        i = 0
        while True:
            cursor.execute("SELECT * FROM vault")
            array = cursor.fetchall()

            lbl1 = Label(window, text=(array[i][1]), font=("Helvetica", 12))
            lbl1.grid(column=0, row=i+3)
            lbl1 = Label(window, text=(array[i][2]), font=("Helvetica", 12))
            lbl1.grid(column=1, row=i+3)
            lbl1 = Label(window, text=(array[i][3]), font=("Helvetica", 12))
            lbl1.grid(column=2, row=i+3)

            btn = Button(window, text="Delete",
                         command=partial(removeEntry, array[i][0]))
            btn.grid(column=3, row=i+3, pady=4)

            i = i+1

            cursor.execute("SELECT * FROM vault")
            if (len(cursor.fetchall()) <= i):
                break


cursor.execute("SELECT * FROM masterpassword")
if cursor.fetchall():
    loginScreen()
else:
    createScreen()
window.mainloop()
