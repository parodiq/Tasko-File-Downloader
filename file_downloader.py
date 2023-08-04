############################
# Tasko Download Manager   #
# program for download any #
# files from the           #
# internet, Developed      #
# by Aws Abbas             #
# For more information,    #
# visit:github.com/parodiq #
############################


import tkinter as tk
from tkinter import ttk
import requests
import threading
import os
import subprocess
import time
from tkinter import messagebox
from tkinter.simpledialog import Dialog
import json

class DeleteDialog(Dialog):
    def __init__(self, parent, file_name):
        self.file_name = file_name
        super().__init__(parent, title="Delete File")

    def body(self, master):
        tk.Label(master, text=f"Do you want to delete '{self.file_name}'?").pack()

    def buttonbox(self):
        box = tk.Frame(self)
        tk.Button(box, text="Delete from List and Disk", command=self.delete_from_disk, default=tk.ACTIVE).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(box, text="Delete from List Only", command=self.delete_from_list).pack(side=tk.LEFT, padx=5, pady=5)
        self.bind("<Return>", self.delete_from_disk)
        self.bind("<Escape>", self.cancel)
        box.pack()

    def apply(self):
        self.result = True

    def delete_from_list(self):
        self.result = False

    def delete_from_disk(self):
        self.result = True

class DownloadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Download Manager")
        
        root.configure(bg="#222222")
        root.option_add("*TButton*foreground", "white")
        root.option_add("*TButton*background", "#333333")
        root.option_add("*TButton*highlightBackground", "#333333")
        root.option_add("*TLabel*foreground", "white")
        root.option_add("*TLabel*background", "#222222")
        root.option_add("*TEntry*foreground", "white")
        root.option_add("*TEntry*background", "#333333")
        
        self.show_input_button = tk.Button(root, text='+', command=self.show_input_dialog)
        self.show_input_button.pack(pady=10)
        
        self.tree_columns = ("Name", "Size", "Location", "Download Time", "Progress")
        self.treeview = ttk.Treeview(root, columns=self.tree_columns, show="headings")
        for col in self.tree_columns:
            self.treeview.heading(col, text=col)
        self.treeview.pack(pady=10)

        self.treeview.column("Progress", width=100, anchor="center")

        self.delete_button = tk.Button(root, text="Delete", command=self.delete_selected, state=tk.DISABLED)
        self.delete_button.pack(pady=5)
        
        self.open_folder_button = tk.Button(root, text="Open File Folder", command=self.open_selected_file_folder, state=tk.DISABLED)
        self.open_folder_button.pack(pady=5)
        
        self.download_thread = None

        self.load_data()

    def create_menu(self):
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About", command=self.show_about)

    def show_about(self):
        about_text = (
            "Download Manager\n\n"
            "This program allows you to download files from the internet.\n"
            "Developed by Aws Abbas\n"
            "For more information, visit: github.com/parodiq"
        )
        messagebox.showinfo("About", about_text)

    def load_data(self):
        try:
            with open("data.json", "r") as file:
                data = json.load(file)
                for item in data:
                    self.treeview.insert("", "end", values=(item["Name"], item["Size"], item["Location"], item["Download Time"], item["Progress"]))
        except FileNotFoundError:
            pass

    def save_data(self):
        data = []
        for item in self.treeview.get_children():
            values = self.treeview.item(item, "values")
            data.append({
                "Name": values[0],
                "Size": values[1],
                "Location": values[2],
                "Download Time": values[3],
                "Progress": values[4]
            })

        with open("data.json", "w") as file:
            json.dump(data, file, indent=4)

    def show_input_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Download")
        
        self.url_label = tk.Label(dialog, text="Enter URL:")
        self.url_label.pack(pady=5)
        
        self.url_entry = tk.Entry(dialog, width=40)
        self.url_entry.pack(pady=5)
        
        self.start_button = tk.Button(dialog, text="Start Download", command=self.start_download)
        self.start_button.pack(pady=5)
        
        self.progress_bar = ttk.Progressbar(dialog, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(pady=10)
        
        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)

    def start_download(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a valid URL.")
            return
        
        self.progress_bar.pack(pady=10)
        self.download_thread = threading.Thread(target=self.download_file, args=(url,))
        self.download_thread.start()

    def download_file(self, url):
        try:
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            start_time = time.strftime("%Y-%m-%d %H:%M:%S")

            original_file_name = os.path.basename(url)
            file_name, file_extension = os.path.splitext(original_file_name)

            i = 1
            while os.path.exists(file_name + file_extension):
                file_name = f"{file_name}_{i}"
                i += 1

            full_file_name = file_name + file_extension

            with open(full_file_name, "wb") as f:
                for data in response.iter_content(chunk_size=1024):
                    downloaded_size += len(data)
                    f.write(data)
                    percentage = (downloaded_size / total_size) * 100
                    self.progress_bar['value'] = percentage
                    self.progress_bar.update()

            self.treeview.insert("", "end", values=(full_file_name, f"{total_size} bytes", os.path.abspath(full_file_name), start_time, f"{percentage:.2f}%"))

            self.save_data()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
    def delete_selected(self):
        selected_item = self.treeview.selection()
        if selected_item:
            selected_values = self.treeview.item(selected_item)['values']
            delete_dialog = DeleteDialog(self.root, selected_values[0])
            if delete_dialog.result is not None:
                if delete_dialog.result:
                    file_path = selected_values[2]
                    os.remove(file_path)
                    self.treeview.delete(selected_item)
                    self.delete_button.config(state=tk.DISABLED)
                else:
                    self.treeview.delete(selected_item)
                    self.delete_button.config(state=tk.DISABLED)

    def open_selected_file_folder(self):
        selected_item = self.treeview.selection()
        if selected_item:
            selected_values = self.treeview.item(selected_item)['values']
            file_folder = os.path.dirname(selected_values[2])
            if os.name == "nt":
                os.startfile(file_folder)
            elif os.name == "posix":
                subprocess.Popen(["xdg-open", file_folder])

    def on_treeview_select(self, event):
        selected_item = self.treeview.selection()
        if selected_item:
            self.delete_button.config(state=tk.NORMAL)
            self.open_folder_button.config(state=tk.NORMAL)
        else:
            self.delete_button.config(state=tk.DISABLED)
            self.open_folder_button.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = DownloadApp(root)
    app.treeview.bind("<<TreeviewSelect>>", app.on_treeview_select)
    app.create_menu()  
    root.mainloop()

if __name__ == "__main__":
    main()

############################
# Tasko Download Manager   #
# program for download any #
# files from the           #
# internet, Developed      #
# by Aws Abbas             #
# For more information,    #
# visit:github.com/parodiq #
############################
