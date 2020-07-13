from tkinter import font
import requests
import time
import sqlite3
import os
from pydub import AudioSegment
from tkinter import *
import threading


def audiorecorder(url, duration=30, file_name='myRadio.mp3'):

    footLabel.config(text='Record in process....')
    duration = int(duration)

    # make a folder with name download
    if not os.path.exists('Download'):
        os.mkdir('Download')

    # streaming
    start = time.time()
    r = requests.get(url, stream=True)
    with open('Download/'+file_name, 'wb') as f:
        for ch in r:
            elapsed = time.time() - start
            f.write(ch)
            if elapsed > duration:
                break

    # time to milliseconds
    endTime = duration * 1000

    # opening file and extracting segment
    song = AudioSegment.from_mp3('Download/'+file_name)
    extract = song[0:endTime]

    # Saving
    extract.export('Download/' + file_name, format="mp4")

    footLabel.config(text='Recording has ended')

    # save the information to Database
    db = sqlite3.connect('db_songs.sqlite')
    create_table(db)
    insert_songs_data(db, duration, file_name)
    print_table_data(db)


def create_table(db):
    c = db.cursor()
    c.execute('''
		CREATE TABLE IF NOT EXISTS log(
			id INTEGER PRIMARY KEY,
			name varchar(40),
			duration INTEGER
		);
	''')
    db.commit()


def insert_songs_data(db, duration=30, file_name='myRadio.mp3'):
    c = db.cursor()
    sql = '''
	INSERT INTO log(name, duration) VALUES (?, ?);
	'''
    c.execute(sql, (file_name, duration))
    db.commit()

def print_table_data(db):
    c = db.cursor()
    c.execute('SELECT * FROM log;')
    r = c.fetchall()

    for row in r:
        nr, name, duration = row
        listbox.insert(END, f'{"":2}{nr:3} {name:>20} {duration:15}')

def clear_fields():
    e1.delete(0, END)
    e2.delete(0, END)
    e3.delete(0, END)
    listbox.delete(0, END)
    footLabel.config(text='')

def recording_list():
    db = sqlite3.connect('db_songs.sqlite')
    create_table(db)
    print_table_data(db)


if __name__ == "__main__":
    root = Tk()
    root.iconbitmap('audio.ico')
    root.title("Audiorecorder")
    root.geometry("800x800")

    HeadImg = PhotoImage(file='audioicon.png')
    HeadLabel = Label(root, justify=CENTER, image=HeadImg).pack()
    frame = Frame(root, width=700, height=300, background='orange')
    font1 = font.Font(size=14)
    fontLabel = font.Font(size=13)
    # input field
    Label(frame, text="Link the podcast", bg="orange", font=font1).place(x=50, y=60)
    e1 = Entry(frame, width=70, borderwidth=2)
    e1.place(x=230, y=64)
    Label(frame, text="The duration", bg="orange", font=font1).place(x=50, y=120)
    e2 = Entry(frame, width=70, borderwidth=2)
    e2.place(x=230, y=124)
    Label(frame, text="The name of file", bg="orange", font=font1).place(x=50, y=180)
    e3 = Entry(frame, width=70, borderwidth=2)
    e3.place(x=230, y=184)
    # Buttons
    recButton = Button(frame, borderwidth=2, text='Clear', font=font1, width=9, height=2,
                       command=lambda: clear_fields())
    recButton.place(x=90, y=270)
    recButton = Button(frame, borderwidth=2, text='Recording list', font=font1, width=15, height=2,
                       command=lambda: recording_list())
    recButton.place(x=315, y=270)
    recButton = Button(frame, borderwidth=2, text='Record', font=font1, width=9, height=2, command=lambda: [
        (threading.Thread(target=audiorecorder, args=(e1.get(), e2.get(), e3.get(),)).start())])
    recButton.place(x=600, y=270)
    footLabel = Label(root, text="", font=fontLabel, fg='green', justify=LEFT)

    frame.pack(expand=TRUE, fill=BOTH)
    footLabel.pack()

    listbox = Listbox(root, width=100, borderwidth=2)
    listbox.place(x=50, y=560)

    root.mainloop()

   # url = "https://wdr-edge-10c2-dus-dtag-cdn.cast.addradio.de/wdr/1live/diggi/mp3/128/stream.mp3?ar-key=BcHBEcAgCATAYjLj0-FAAR8Woygl5JHqs_tOfCWmcwVGhVP1cie6sLrzgIo9mRFXdlMcIlskcF6mTTJO2u4"
