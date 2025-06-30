import os
import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext, messagebox
import pathlib
from datetime import datetime
import json

class FolderStructurizeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FolderStructurize - Visualizador de Estrutura de Diretórios")
        self.root.geometry("900x600")
        self.setup_ui()

    def setup_ui(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Seletor de diretório
        dir_frame = ttk.Frame(frame)
        dir_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(dir_frame, text="Diretório:").pack(side=tk.LEFT)
        self.dir_entry = ttk.Entry(dir_frame, width=60)
        self.dir_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(dir_frame, text="Escolher", command=self.select_dir).pack(side=tk.LEFT)
        ttk.Button(dir_frame, text="Gerar", command=self.generate).pack(side=tk.LEFT, padx=5)
        ttk.Button(dir_frame, text="Salvar", command=self.save).pack(side=tk.LEFT)
        
        # Área de saída
        self.output = scrolledtext.ScrolledText(frame, font=("Consolas", 10), wrap=tk.NONE)
        self.output.pack(fill=tk.BOTH, expand=True)
        
    def select_dir(self):
        d = filedialog.askdirectory(title="Selecione o diretório")
        if d:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, d)

    def generate(self):
        path = self.dir_entry.get().strip()
        if not path or not os.path.isdir(path):
            messagebox.showerror("Erro", "Diretório inválido")
            return
        tree = self.build_tree(pathlib.Path(path))
        md = self.tree_to_markdown(tree)
        self.output.delete(1.0, tk.END)
        self.output.insert(tk.END, md)

    def save(self):
        content = self.output.get(1.0, tk.END).strip()
        if not content:
            messagebox.showerror("Erro", "Nada para salvar")
            return
        f = filedialog.asksaveasfilename(defaultextension=".md", filetypes=[("Markdown", "*.md"), ("Texto", "*.txt")])
        if f:
            with open(f, 'w', encoding='utf-8') as out:
                out.write(content)
            messagebox.showinfo("Salvo", f"Arquivo salvo em: {f}")

    def build_tree(self, path, prefix=""):
        tree = {"name": path.name, "type": "dir", "children": []}
        try:
            for entry in sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
                if entry.is_dir():
                    tree["children"].append(self.build_tree(entry, prefix + "    "))
                else:
                    tree["children"].append({"name": entry.name, "type": "file"})
        except Exception as e:
            tree["children"].append({"name": f"[Erro: {e}]", "type": "error"})
        return tree

    def tree_to_markdown(self, tree, prefix=""):
        lines = [f"# Estrutura de: {tree['name']}\n"]
        def walk(node, pre=""):
            if node["type"] == "dir":
                lines.append(f"{pre}📁 {node['name']}/")
                for c in node["children"]:
                    walk(c, pre + "    ")
            elif node["type"] == "file":
                lines.append(f"{pre}📄 {node['name']}")
            elif node["type"] == "error":
                lines.append(f"{pre}⚠️ {node['name']}")
        walk(tree)
        return "\n".join(lines)

def main():
    root = tk.Tk()
    app = FolderStructurizeApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 