import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys

# Add parent directory to path to import indexer and searcher
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from indexer import CreateIndex, save_index, load_index
from searcher import Find, FindWordFile

class InvertedIndexApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Inverted Index - Chapter 6")
        self.geometry("1000x700")
        self.configure(bg="#1e1e2e")

        self.doc_table = {}
        self.term_table = {}
        self.current_dir = tk.StringVar(value=os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs"))
        self.stoplist_path = tk.StringVar(value=os.path.join(self.current_dir.get(), "stoplist.txt"))
        self.wordfile_path = tk.StringVar(value=os.path.join(self.current_dir.get(), "wordfile.txt"))

        self._build_ui()

    def _build_ui(self):
        # Apply dark theme styles
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", background="#313244", foreground="#cdd6f4", fieldbackground="#313244", borderwidth=0)
        style.map("Treeview", background=[("selected", "#45475a")])

        # Top Control Frame
        ctrl_frame = tk.LabelFrame(self, text="Cấu hình Index", bg="#1e1e2e", fg="#89b4fa", padx=10, pady=10)
        ctrl_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(ctrl_frame, text="Thư mục tài liệu:", bg="#1e1e2e", fg="#cdd6f4").grid(row=0, column=0, sticky=tk.W)
        tk.Entry(ctrl_frame, textvariable=self.current_dir, bg="#313244", fg="#cdd6f4", width=50).grid(row=0, column=1, padx=5)
        tk.Button(ctrl_frame, text="Chọn", command=self._browse_dir).grid(row=0, column=2, padx=5)

        tk.Label(ctrl_frame, text="File StopList:", bg="#1e1e2e", fg="#cdd6f4").grid(row=1, column=0, sticky=tk.W)
        tk.Entry(ctrl_frame, textvariable=self.stoplist_path, bg="#313244", fg="#cdd6f4", width=50).grid(row=1, column=1, padx=5)
        tk.Button(ctrl_frame, text="Chọn", command=self._browse_stoplist).grid(row=1, column=2, padx=5)

        tk.Button(ctrl_frame, text="🚀 Xây dựng Chỉ mục", bg="#a6e3a1", fg="#1e1e2e", font=("Helvetica", 10, "bold"), 
                  command=self._build_index).grid(row=0, column=3, rowspan=2, padx=20, sticky=tk.NSEW)

        # Main Content area (PanedWindow)
        main_pane = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg="#1e1e2e", sashwidth=4)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Left: Index Viewer
        left_frame = tk.Frame(main_pane, bg="#1e1e2e")
        main_pane.add(left_frame, minsize=400)
        
        tk.Label(left_frame, text="📚 Nội dung Chỉ mục (C-Words)", bg="#1e1e2e", fg="#cba6f7").pack()
        self.index_tree = ttk.Treeview(left_frame, columns=("Postings"), show="tree headings")
        self.index_tree.heading("#0", text="Từ khóa")
        self.index_tree.heading("Postings", text="Tài liệu : Tần suất")
        self.index_tree.pack(fill=tk.BOTH, expand=True)

        # Right: Search Panel
        right_frame = tk.Frame(main_pane, bg="#1e1e2e")
        main_pane.add(right_frame, minsize=400)

        search_ctrl = tk.LabelFrame(right_frame, text="Tìm kiếm Top-N", bg="#1e1e2e", fg="#f9e2af", padx=10, pady=10)
        search_ctrl.pack(fill=tk.X, pady=5)

        tk.Label(search_ctrl, text="Từ khóa:", bg="#1e1e2e", fg="#cdd6f4").grid(row=0, column=0, sticky=tk.W)
        self.search_entry = tk.Entry(search_ctrl, bg="#313244", fg="#cdd6f4")
        self.search_entry.grid(row=0, column=1, sticky=tk.EW)
        
        tk.Label(search_ctrl, text="N:", bg="#1e1e2e", fg="#cdd6f4").grid(row=0, column=2, padx=5)
        self.n_entry = tk.Entry(search_ctrl, bg="#313244", fg="#cdd6f4", width=5)
        self.n_entry.insert(0, "5")
        self.n_entry.grid(row=0, column=3)

        tk.Button(search_ctrl, text="Tìm kiếm (Từ)", bg="#f9e2af", fg="#1e1e2e", command=self._search).grid(row=0, column=4, padx=10, sticky=tk.EW)

        tk.Label(search_ctrl, text="WordFile:", bg="#1e1e2e", fg="#cdd6f4").grid(row=1, column=0, sticky=tk.W)
        tk.Entry(search_ctrl, textvariable=self.wordfile_path, bg="#313244", fg="#cdd6f4").grid(row=1, column=1, sticky=tk.EW)
        tk.Button(search_ctrl, text="Chọn", command=self._browse_wordfile).grid(row=1, column=2, padx=5)
        tk.Button(search_ctrl, text="Tìm kiếm (File)", bg="#fab387", fg="#1e1e2e", command=self._search_wordfile).grid(row=1, column=4, padx=10, pady=5, sticky=tk.EW)

        # Results area
        tk.Label(right_frame, text="🔍 Kết quả tìm kiếm", bg="#1e1e2e", fg="#f9e2af").pack(pady=(10, 0))
        self.results_tree = ttk.Treeview(right_frame, columns=("Score"), show="headings")
        self.results_tree.heading("Score", text="Điểm số (Tài liệu) - Double click để xem file")
        self.results_tree.pack(fill=tk.BOTH, expand=True)
        self.results_tree.bind("<Double-1>", self._on_tree_double_click)

        # Status Bar
        self.status_var = tk.StringVar(value="Sẵn sàng")
        tk.Label(self, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#313244", fg="#a6adc8").pack(side=tk.BOTTOM, fill=tk.X)

    def _browse_dir(self):
        d = filedialog.askdirectory()
        if d: self.current_dir.set(d)

    def _browse_stoplist(self):
        f = filedialog.askopenfilename(initialdir=self.current_dir.get())
        if f: self.stoplist_path.set(f)

    def _browse_wordfile(self):
        f = filedialog.askopenfilename(initialdir=self.current_dir.get())
        if f: self.wordfile_path.set(f)

    def _build_index(self):
        try:
            d = self.current_dir.get()
            s = self.stoplist_path.get()
            if not os.path.exists(d): raise Exception("Thư mục không tồn tại")
            
            self.doc_table, self.term_table = CreateIndex(d, s)
            
            # Update Index Tree
            for item in self.index_tree.get_children(): self.index_tree.delete(item)
            
            # DocTable as root nodes
            doc_root = self.index_tree.insert("", tk.END, text="DocTable", open=True)
            for doc_id, name in self.doc_table.items():
                self.index_tree.insert(doc_root, tk.END, text=f"[{doc_id}] {name}")
            
            term_root = self.index_tree.insert("", tk.END, text="TermTable", open=True)
            for term, postings in sorted(self.term_table.items()):
                p_str = ", ".join([f"doc{did}:{cnt}" for did, cnt in postings.items()])
                self.index_tree.insert(term_root, tk.END, text=term, values=(p_str,))
            
            self.status_var.set(f"✅ Đã xây dựng mục lục thành công từ {len(self.doc_table)} tài liệu.")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def _search(self):
        if not self.term_table:
            messagebox.showwarning("Lỗi", "Vui lòng xây dựng mục lục trước")
            return
        
        query = self.search_entry.get().strip()
        try:
            n = int(self.n_entry.get())
        except:
            n = 5
        
        # Clear previous
        for item in self.results_tree.get_children(): self.results_tree.delete(item)
        
        # We'll use a modified search logic to get results here since searcher.py prints to stdout
        # Instead, we can import the core logic or redirect output.
        # Let's assume we want to show the results in the Treeview.
        # I'll implement a simple score calculation here based on searcher.py logic
        
        scores = {}
        words = query.lower().split()
        for word in words:
            if word in self.term_table:
                for doc_id, count in self.term_table[word].items():
                    scores[doc_id] = scores.get(doc_id, 0) + count
        
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:n]
        
        if not sorted_results:
            self.status_var.set("Không tìm thấy kết quả.")
        else:
            for doc_id, score in sorted_results:
                doc_name = self.doc_table.get(doc_id, "Unknown")
                self.results_tree.insert("", tk.END, values=(f"{score} ({doc_name})",))
            self.status_var.set(f"Tìm thấy {len(sorted_results)} tài liệu.")

    def _search_wordfile(self):
        if not self.term_table:
            messagebox.showwarning("Lỗi", "Vui lòng xây dựng mục lục trước")
            return
        
        filepath = self.wordfile_path.get()
        if not os.path.exists(filepath):
            messagebox.showerror("Lỗi", f"File '{filepath}' không tồn tại.")
            return

        try:
            n = int(self.n_entry.get())
        except:
            n = 5
        
        # Clear previous
        for item in self.results_tree.get_children(): self.results_tree.delete(item)
        
        # Call the core searcher logic
        results = FindWordFile(filepath, n, self.doc_table, self.term_table)
        
        if not results:
            self.status_var.set("Không tìm thấy kết quả từ WordFile.")
        else:
            for score, doc_name in results:
                self.results_tree.insert("", tk.END, values=(f"{score} ({doc_name})",))
            self.status_var.set(f"Tìm thấy {len(results)} tài liệu từ WordFile.")

    def _on_tree_double_click(self, event):
        item = self.results_tree.selection()
        if not item: return
        
        val = self.results_tree.item(item, "values")[0]
        # Format is "score (filename)"
        import re
        match = re.search(r"\((.*?)\)", val)
        if match:
            filename = match.group(1)
            self._show_file_popup(filename)

    def _show_file_popup(self, filename):
        filepath = os.path.join(self.current_dir.get(), filename)
        if not os.path.exists(filepath):
            messagebox.showerror("Lỗi", f"Không tìm thấy file: {filepath}")
            return

        popup = tk.Toplevel(self)
        popup.title(f"Nội dung file: {filename}")
        popup.geometry("600x400")
        popup.configure(bg="#1e1e2e")

        from tkinter import scrolledtext
        txt = scrolledtext.ScrolledText(popup, bg="#1e1e2e", fg="#cdd6f4", insertbackground="white", font=("Consolas", 11))
        txt.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            txt.insert(tk.END, content)
            txt.configure(state=tk.DISABLED) # Read only
        except Exception as e:
            txt.insert(tk.END, f"Lỗi đọc file: {e}")

def run():
    app = InvertedIndexApp()
    app.mainloop()

if __name__ == "__main__":
    run()
