import tkinter as tk
from tkinter import scrolledtext, messagebox, font
import numpy as np
import math
import sys # 导入sys库以检测操作系统

class HillCipherProApp:
    """
    一个完备的希尔密码图形化工具，支持行向量和列向量两种模式，
    并提供详细的计算日志和跨平台中文显示支持。
    """
    def __init__(self, root):
        self.root = root
        self.root.title("专业希尔密码工具 (Professional Hill Cipher Tool)")
        self.root.geometry("800x700")

        # --- 核心改动：设置支持中文的字体 ---
        self._setup_fonts()

        # --- UI 布局 (现在所有组件都会使用新设置的字体) ---
        main_frame = tk.Frame(root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self._create_info_frame(main_frame)
        self._create_key_frame(main_frame)
        self._create_io_frame(main_frame)
        self._create_button_frame(main_frame)
        self._create_log_frame(main_frame)
        
        self.status_label = tk.Label(main_frame, text="准备就绪。请配置密钥并输入文本。", bd=1, relief=tk.SUNKEN, anchor=tk.W, font=self.default_font)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

    def _setup_fonts(self):
        """
        检测操作系统并设置合适的、支持中文的字体。
        """
        os_type = sys.platform
        
        # 为不同操作系统定义首选字体列表
        if os_type == "win32": # Windows
            default_family = "Microsoft YaHei UI"
            log_family = "Consolas"
        elif os_type == "darwin": # macOS
            default_family = "PingFang SC"
            log_family = "Monaco"
        else: # Linux and others
            # 尝试常见的Linux中文字体
            default_family = "WenQuanYi Micro Hei"
            log_family = "Monospace"
        
        try:
            # 尝试应用字体
            font.nametofont("TkDefaultFont").config(family=default_family, size=10)
            font.nametofont("TkTextFont").config(family=default_family, size=10)
            self.default_font = font.Font(family=default_family, size=10)
            self.header_font = font.Font(family=default_family, size=11, weight="bold")
            self.log_font = font.Font(family=log_family, size=10)
        except tk.TclError:
            # 如果首选字体不存在，则退回到通用字体（可能不支持中文）
            print(f"警告：未找到推荐字体 '{default_family}'。界面可能无法正常显示中文。")
            self.default_font = font.Font(family="Arial", size=10)
            self.header_font = font.Font(family="Arial", size=11, weight="bold")
            self.log_font = font.Font(family="Courier New", size=10)

    # ... 以下是创建UI组件的方法，已确保它们都使用了新字体 ...
    
    def _create_info_frame(self, parent):
        info_frame = tk.LabelFrame(parent, text="注意事项", padx=10, pady=10, font=self.header_font)
        info_frame.pack(fill=tk.X, pady=5)
        info_text = (
            "1. 密钥矩阵必须是 N×N 的方阵。\n"
            "2. 矩阵的行列式(det)与26必须互质 (即 gcd(det, 26) = 1)，否则无法解密。\n"
            "3. 本工具支持两种计算约定，请务必选择正确的向量方向。"
        )
        tk.Label(info_frame, text=info_text, justify=tk.LEFT, font=self.default_font).pack(anchor="w")

    def _create_key_frame(self, parent):
        key_frame = tk.LabelFrame(parent, text="密钥与计算设置", padx=10, pady=10, font=self.header_font)
        key_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(key_frame, text="密钥矩阵元素 (空格分隔):", font=self.default_font).grid(row=0, column=0, sticky="w", padx=5)
        self.key_entry = tk.Entry(key_frame, width=40, font=self.default_font)
        self.key_entry.grid(row=0, column=1, sticky="ew", padx=5)
        self.key_entry.insert(0, "11 8 3 7")
        
        self.vector_mode = tk.StringVar(value="row")
        tk.Label(key_frame, text="向量方向:", font=self.default_font).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        row_radio = tk.Radiobutton(key_frame, text="行向量 (P' = P × K)", variable=self.vector_mode, value="row", font=self.default_font)
        row_radio.grid(row=1, column=1, sticky="w")
        col_radio = tk.Radiobutton(key_frame, text="列向量 (P' = K × P)", variable=self.vector_mode, value="column", font=self.default_font)
        col_radio.grid(row=2, column=1, sticky="w")
        key_frame.columnconfigure(1, weight=1)

    def _create_io_frame(self, parent):
        io_frame = tk.Frame(parent)
        io_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        io_frame.columnconfigure(0, weight=1)
        io_frame.columnconfigure(1, weight=1)

        pt_frame = tk.LabelFrame(io_frame, text="明文 (Plaintext)", padx=5, pady=5, font=self.header_font)
        pt_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.plaintext_area = scrolledtext.ScrolledText(pt_frame, height=6, wrap=tk.WORD, font=self.default_font)
        self.plaintext_area.pack(fill=tk.BOTH, expand=True)
        self.plaintext_area.insert(tk.END, "ACT")

        ct_frame = tk.LabelFrame(io_frame, text="密文 (Ciphertext)", padx=5, pady=5, font=self.header_font)
        ct_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        self.ciphertext_area = scrolledtext.ScrolledText(ct_frame, height=6, wrap=tk.WORD, font=self.default_font)
        self.ciphertext_area.pack(fill=tk.BOTH, expand=True)

    def _create_button_frame(self, parent):
        button_frame = tk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=5)
        
        self.encrypt_button = tk.Button(button_frame, text="加密 (Encrypt) ↓", command=lambda: self.process_action('encrypt'), font=self.default_font)
        self.encrypt_button.pack(side=tk.LEFT, expand=True, padx=5, ipady=5)
        
        self.decrypt_button = tk.Button(button_frame, text="解密 (Decrypt) ↑", command=lambda: self.process_action('decrypt'), font=self.default_font)
        self.decrypt_button.pack(side=tk.LEFT, expand=True, padx=5, ipady=5)
        
        self.clear_button = tk.Button(button_frame, text="清空 (Clear)", command=self.clear_all, font=self.default_font)
        self.clear_button.pack(side=tk.RIGHT, expand=True, padx=5, ipady=5)

    def _create_log_frame(self, parent):
        log_frame = tk.LabelFrame(parent, text="计算日志", padx=10, pady=5, font=self.header_font)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.log_area = scrolledtext.ScrolledText(log_frame, height=8, wrap=tk.WORD, state='disabled', font=self.log_font)
        self.log_area.pack(fill=tk.BOTH, expand=True)
        
    # ... 后端逻辑和处理函数部分与之前相同，此处省略 ...
    # ... 您可以将之前代码中从 def log(self, message): 开始到结尾的部分直接复制到这里 ...

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
        self.status_label.config(text="已清空。")

    def _str_to_key_matrix(self, key_str):
        try:
            nums = [int(n) for n in key_str.split()]
            size = int(math.sqrt(len(nums)))
            if size * size != len(nums):
                messagebox.showerror("密钥错误", "密钥元素个数必须是完全平方数 (例如 4, 9, 16)。")
                return None
            return np.array(nums).reshape(size, size)
        except ValueError:
            messagebox.showerror("密钥错误", "密钥只能包含数字和空格。")
            return None

    def _mod_inverse_num(self, a, m):
        a = a % m
        try:
            return pow(a, -1, m)
        except ValueError:
            return None

    def _get_key_inverse(self, key_matrix):
        det = int(round(np.linalg.det(key_matrix)))
        self.log(f"计算行列式 det(K) = {det}")
        det_inv = self._mod_inverse_num(det, 26)
        if det_inv is None:
            self.log(f"错误: 行列式 {det} 与 26 不互质，gcd({det}, 26) != 1。")
            messagebox.showerror("密钥不可逆", f"矩阵行列式为 {det}，与26不互质，该密钥无法用于解密！")
            return None
        self.log(f"计算行列式的模26乘法逆元: ({det}^-1) mod 26 = {det_inv}")
        adjugate_matrix = np.round(np.linalg.inv(key_matrix) * det).astype(int)
        inverse_matrix = (det_inv * adjugate_matrix) % 26
        self.log(f"计算得到逆矩阵 K⁻¹ (mod 26):\n{inverse_matrix}")
        return inverse_matrix

    def process_action(self, mode):
        self.log_area.config(state='normal')
        self.log_area.delete("1.0", tk.END)
        self.log_area.config(state='disabled')
        key_matrix = self._str_to_key_matrix(self.key_entry.get())
        if key_matrix is None: return
        vector_mode = self.vector_mode.get()
        self.log(f"--- 开始 {mode.capitalize()} 过程 ---")
        self.log(f"模式: {'行向量 (P × K)' if vector_mode == 'row' else '列向量 (K × P)'}")
        self.log(f"原始密钥矩阵 K:\n{key_matrix}")
        if mode == 'encrypt':
            text = self.plaintext_area.get("1.0", tk.END)
            matrix_to_use = key_matrix
        else:
            text = self.ciphertext_area.get("1.0", tk.END)
            matrix_to_use = self._get_key_inverse(key_matrix)
            if matrix_to_use is None: 
                self.status_label.config(text="解密失败: 密钥不可逆。")
                return
        processed_text = ''.join(filter(str.isalpha, text)).upper()
        m = matrix_to_use.shape[0]
        if len(processed_text) % m != 0:
            padding_needed = m - (len(processed_text) % m)
            processed_text += 'A' * padding_needed
            self.log(f"文本已填充: {processed_text}")
        result_text = ""
        for i in range(0, len(processed_text), m):
            chunk = processed_text[i:i+m]
            vec = np.array([ord(char) - ord('A') for char in chunk])
            if vector_mode == 'row':
                result_vec = (vec @ matrix_to_use) % 26
            else:
                result_vec = (matrix_to_use @ vec.T) % 26
            result_text += ''.join([chr(int(num) + ord('A')) for num in result_vec])
        if mode == 'encrypt':
            self.ciphertext_area.delete("1.0", tk.END)
            self.ciphertext_area.insert("1.0", result_text)
        else:
            self.plaintext_area.delete("1.0", tk.END)
            self.plaintext_area.insert("1.0", result_text)
        self.log("--- 过程结束 ---")
        self.status_label.config(text=f"{mode.capitalize()} 完成。")

if __name__ == "__main__":
    try:
        import numpy
    except ImportError:
        print("错误：需要安装 numpy 库。")
        print("请在终端运行: pip install numpy")
        exit()
    root = tk.Tk()
    app = HillCipherProApp(root)
    root.mainloop()