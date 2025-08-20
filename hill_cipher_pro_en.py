import tkinter as tk
from tkinter import scrolledtext, messagebox, font
import numpy as np
import math
import sys

class HillCipherProApp:
    """
    A comprehensive Hill Cipher GUI tool with dual-mode support (row/column vectors)
    and detailed calculation logs. This is an all-English version for maximum compatibility.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Professional Hill Cipher Tool")
        self.root.geometry("800x700")

        # --- Simplified Font Setup for English UI ---
        self.default_font = font.Font(family="Arial", size=10)
        self.header_font = font.Font(family="Arial", size=11, weight="bold")
        self.log_font = font.Font(family="Courier New", size=10)

        # --- UI Layout ---
        main_frame = tk.Frame(root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self._create_info_frame(main_frame)
        self._create_key_frame(main_frame)
        self._create_io_frame(main_frame)
        self._create_button_frame(main_frame)
        self._create_log_frame(main_frame)
        
        self.status_label = tk.Label(main_frame, text="Ready. Please configure the key and enter text.", bd=1, relief=tk.SUNKEN, anchor=tk.W, font=self.default_font)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

    def _create_info_frame(self, parent):
        info_frame = tk.LabelFrame(parent, text="Important Notes", padx=10, pady=10, font=self.header_font)
        info_frame.pack(fill=tk.X, pady=5)
        info_text = (
            "1. The key matrix must be a square N×N matrix.\n"
            "2. The matrix determinant (det) must be coprime with 26 (i.e., gcd(det, 26) = 1).\n"
            "3. Select the correct vector orientation used for the calculation."
        )
        tk.Label(info_frame, text=info_text, justify=tk.LEFT, font=self.default_font).pack(anchor="w")

    def _create_key_frame(self, parent):
        key_frame = tk.LabelFrame(parent, text="Key & Calculation Settings", padx=10, pady=10, font=self.header_font)
        key_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(key_frame, text="Key Matrix Elements (space-separated):", font=self.default_font).grid(row=0, column=0, sticky="w", padx=5)
        self.key_entry = tk.Entry(key_frame, width=40, font=self.default_font)
        self.key_entry.grid(row=0, column=1, sticky="ew", padx=5)
        self.key_entry.insert(0, "11 8 3 7")
        
        self.vector_mode = tk.StringVar(value="row")
        tk.Label(key_frame, text="Vector Orientation:", font=self.default_font).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        row_radio = tk.Radiobutton(key_frame, text="Row Vector (C = P × K)", variable=self.vector_mode, value="row", font=self.default_font)
        row_radio.grid(row=1, column=1, sticky="w")
        col_radio = tk.Radiobutton(key_frame, text="Column Vector (C = K × P)", variable=self.vector_mode, value="column", font=self.default_font)
        col_radio.grid(row=2, column=1, sticky="w")
        key_frame.columnconfigure(1, weight=1)

    def _create_io_frame(self, parent):
        io_frame = tk.Frame(parent)
        io_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        io_frame.columnconfigure(0, weight=1)
        io_frame.columnconfigure(1, weight=1)

        pt_frame = tk.LabelFrame(io_frame, text="Plaintext", padx=5, pady=5, font=self.header_font)
        pt_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.plaintext_area = scrolledtext.ScrolledText(pt_frame, height=6, wrap=tk.WORD, font=self.default_font)
        self.plaintext_area.pack(fill=tk.BOTH, expand=True)
        self.plaintext_area.insert(tk.END, "ACT")

        ct_frame = tk.LabelFrame(io_frame, text="Ciphertext", padx=5, pady=5, font=self.header_font)
        ct_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        self.ciphertext_area = scrolledtext.ScrolledText(ct_frame, height=6, wrap=tk.WORD, font=self.default_font)
        self.ciphertext_area.pack(fill=tk.BOTH, expand=True)

    def _create_button_frame(self, parent):
        button_frame = tk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=5)
        
        self.encrypt_button = tk.Button(button_frame, text="Encrypt ↓", command=lambda: self.process_action('encrypt'), font=self.default_font)
        self.encrypt_button.pack(side=tk.LEFT, expand=True, padx=5, ipady=5)
        
        self.decrypt_button = tk.Button(button_frame, text="Decrypt ↑", command=lambda: self.process_action('decrypt'), font=self.default_font)
        self.decrypt_button.pack(side=tk.LEFT, expand=True, padx=5, ipady=5)
        
        self.clear_button = tk.Button(button_frame, text="Clear", command=self.clear_all, font=self.default_font)
        self.clear_button.pack(side=tk.RIGHT, expand=True, padx=5, ipady=5)

    def _create_log_frame(self, parent):
        log_frame = tk.LabelFrame(parent, text="Calculation Log", padx=10, pady=5, font=self.header_font)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.log_area = scrolledtext.ScrolledText(log_frame, height=8, wrap=tk.WORD, state='disabled', font=self.log_font)
        self.log_area.pack(fill=tk.BOTH, expand=True)

    def log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def clear_all(self):
        self.plaintext_area.delete("1.0", tk.END)
        self.ciphertext_area.delete("1.0", tk.END)
        self.log_area.config(state='normal')
        self.log_area.delete("1.0", tk.END)
        self.log_area.config(state='disabled')
        self.status_label.config(text="All fields cleared.")

    def _str_to_key_matrix(self, key_str):
        try:
            nums = [int(n) for n in key_str.split()]
            size = int(math.sqrt(len(nums)))
            if size * size != len(nums):
                messagebox.showerror("Key Error", "The number of elements in the key must be a perfect square (e.g., 4, 9, 16).")
                return None
            return np.array(nums).reshape(size, size)
        except ValueError:
            messagebox.showerror("Key Error", "The key must contain only numbers and spaces.")
            return None

    def _mod_inverse_num(self, a, m):
        a = a % m
        try:
            return pow(a, -1, m)
        except ValueError:
            return None

    def _get_key_inverse(self, key_matrix):
        det = int(round(np.linalg.det(key_matrix)))
        self.log(f"Calculating determinant det(K) = {det}")
        det_inv = self._mod_inverse_num(det, 26)
        if det_inv is None:
            self.log(f"Error: Determinant {det} is not coprime with 26, gcd({det}, 26) != 1.")
            messagebox.showerror("Key Not Invertible", f"The matrix determinant is {det}, which is not coprime with 26. This key cannot be used for decryption.")
            return None
        self.log(f"Calculating modular multiplicative inverse: ({det}^-1) mod 26 = {det_inv}")
        adjugate_matrix = np.round(np.linalg.inv(key_matrix) * det).astype(int)
        inverse_matrix = (det_inv * adjugate_matrix) % 26
        self.log(f"Calculated Inverse Matrix K⁻¹ (mod 26):\n{inverse_matrix}")
        return inverse_matrix

    def process_action(self, mode):
        self.log_area.config(state='normal')
        self.log_area.delete("1.0", tk.END)
        self.log_area.config(state='disabled')
        
        key_matrix = self._str_to_key_matrix(self.key_entry.get())
        if key_matrix is None: return
        
        vector_mode = self.vector_mode.get()
        self.log(f"--- Starting {mode.capitalize()} Process ---")
        self.log(f"Mode: {'Row Vector (P × K)' if vector_mode == 'row' else 'Column Vector (K × P)'}")
        self.log(f"Original Key Matrix K:\n{key_matrix}")
        
        if mode == 'encrypt':
            text = self.plaintext_area.get("1.0", tk.END)
            matrix_to_use = key_matrix
        else: # decrypt
            text = self.ciphertext_area.get("1.0", tk.END)
            matrix_to_use = self._get_key_inverse(key_matrix)
            if matrix_to_use is None: 
                self.status_label.config(text="Decryption failed: Key is not invertible.")
                return

        processed_text = ''.join(filter(str.isalpha, text)).upper()
        m = matrix_to_use.shape[0]

        if len(processed_text) % m != 0:
            padding_needed = m - (len(processed_text) % m)
            processed_text += 'A' * padding_needed
            self.log(f"Text has been padded: {processed_text}")

        result_text = ""
        for i in range(0, len(processed_text), m):
            chunk = processed_text[i:i+m]
            vec = np.array([ord(char) - ord('A') for char in chunk])
            
            if vector_mode == 'row':
                result_vec = (vec @ matrix_to_use) % 26
            else: # column
                result_vec = (matrix_to_use @ vec.T) % 26
            
            result_text += ''.join([chr(int(num) + ord('A')) for num in result_vec])

        if mode == 'encrypt':
            self.ciphertext_area.delete("1.0", tk.END)
            self.ciphertext_area.insert("1.0", result_text)
        else:
            self.plaintext_area.delete("1.0", tk.END)
            self.plaintext_area.insert("1.0", result_text)
            
        self.log("--- Process Finished ---")
        self.status_label.config(text=f"{mode.capitalize()} complete.")


if __name__ == "__main__":
    try:
        import numpy
    except ImportError:
        print("Error: The 'numpy' library is required.")
        print("Please run in your terminal: pip install numpy")
        exit()
        
    root = tk.Tk()
    app = HillCipherProApp(root)
    root.mainloop()