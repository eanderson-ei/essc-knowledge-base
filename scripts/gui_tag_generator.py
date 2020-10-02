import tkinter as tk
from tkinter import filedialog, Text, font
import os
from tika import parser
from text_rank import TextRank4Keyword
from text_summary import summarize
from graph_database import update_tags

# instantiate app
root = tk.Tk()
root.title('Keyword Tagging System')
root.iconbitmap('assets/icon.ico')
gill_sans = font.Font(family='Gill Sans MT', size=10)

# allow for processing of multiple files at once
files = []

# user open files
def file_opener():
    global f
    # remove any files already printed to the screen
    for widget in file_frame.winfo_children():
        widget.destroy()
    
    # open at the last directory or the current directory if new
    if len(files) > 0:
        initialdir = os.path.dirname(files[-1])
    else:
        initialdir = os.getcwd()
        
    # save full path of selected file and append to files list
    filename = filedialog.askopenfilename(initialdir=initialdir,
                                          title='Select File',
                                          filetypes=[('extension', '.pdf .txt')])
    if filename not in files and filename:
        files.append(filename)
    
    # add filename to the screen
    for f in files:
        # label = tk.Label(file_frame, text=os.path.basename(f))
        label = tk.Text(file_frame, wrap=tk.WORD,
                        padx=10, pady=10, font=gill_sans)
        label.insert(tk.INSERT, os.path.basename(f))
        label.pack()


# run tag generator and summarizer
def run_app():
    # make keywords global in scope
    global keywords

    # remove any keywords already printed to the screen
    for widget in text_frame.winfo_children():
        widget.destroy()
    
    # break out if files is empty
    if len(files) == 0:
        return None

    # parse pdfs and combine text into single string
    combined_text = ''
    for f in files:
        _, file_extension = os.path.splitext(f)
        if file_extension == '.txt':
            with open(f, encoding="utf8") as reader:
                text = reader.read()
            text = text.replace('\n', ' ')
        elif file_extension == '.pdf':
            raw = parser.from_file(f)
            text = raw['content']
            text = text.replace('\n', '')
        else:
            print("Incorrect file extension")
        
        combined_text += text
        
    # get keywords
    tr4w = TextRank4Keyword()
    tr4w.analyze(combined_text, window_size=8, lower=False)
    keywords = tr4w.get_keywords(30)
    
    # summarize
    summary = summarize(combined_text)
    
    # print to screen
    # label1 = tk.Label(summary_frame, text=summary, wraplength=500)  # summary
    if summary:
        label1 = tk.Text(summary_frame, wrap=tk.WORD,
                        padx=10, pady=10, font=gill_sans)
        label1.insert(tk.INSERT, summary)
        label1.pack()
    else:
        print(f"No summary available for {os.path.basename(f)}")
    
    # label2 = tk.Label(text_frame, text='\n'.join(keywords))  # keywords
    if keywords:
        label2 = tk.Text(text_frame, wrap=tk.WORD,
                        padx=10, pady=10, font=gill_sans)
        label2.insert(tk.INSERT, '\n'.join(keywords))
        label2.pack()
    else:
        print(f"No keywords available for {os.path.basename(f)}")


# save to database
def save_to_database():
    update_tags(os.path.basename(f), keywords)
    print(f"Save successful: {os.path.basename(f)}")


# start over
def clear_all():
    for widget in text_frame.winfo_children():
        widget.destroy()
        
    for widget in summary_frame.winfo_children():
        widget.destroy()
    
    for widget in file_frame.winfo_children():
        widget.destroy()
    
    global files 
    files = []

# canvas governs app size on screen (or use root.geometry("700x700"))
canvas = tk.Canvas(root, height=700, width=700, bg="#263D42")
canvas.grid(row=0, column=0, columnspan=4)

# frame allows mutliple 'frames' within canvas
tk.Label(canvas, text="Files Uploaded", bg="#263D42", fg="white")\
    .place(x=.1*700,y=.1*700-20)
file_frame = tk.Frame(root, bg='lightgrey')
file_frame.place(relwidth=0.8, relheight=0.1, relx=0.1, rely=0.1)

tk.Label(canvas, text="Summary", bg="#263D42", fg="white")\
    .place(x=.1*700,y=.25*700-14)
summary_frame = tk.Frame(root, bg='white')
summary_frame.place(relwidth=0.8, relheight=0.2, relx=0.1, rely=0.25)
scrollbar = tk.Scrollbar(summary_frame)

tk.Label(canvas, text="Keywords", bg="#263D42", fg="white")\
    .place(x=.1*700,y=.5*700-7)
text_frame = tk.Frame(root, bg='white')
text_frame.place(relwidth=0.8, relheight=0.4, relx=0.1, rely=0.5)

# button to open a file
open_file = tk.Button(root, text='Open File', padx=10, pady=5,
                      fg='white', bg="#263D42", command=file_opener)
open_file.grid(row=3, column=0)  # register button

# button to generate tag cloud
run_apps = tk.Button(root, text='Run', padx=10, pady=5,
                      fg='white', bg="#263D42", command=run_app)
run_apps.grid(row=3, column=1)

# button to save to database
save = tk.Button(root, text='Save', padx=10, pady=5,
                      fg='white', bg="green", command=save_to_database)
save.grid(row=3, column=2)

# clear results
clear = tk.Button(root, text='Clear', padx=10, pady=5,
                  fg='white', bg='red', command=clear_all)
clear.grid(row=3, column=3)

# run app
root.mainloop()