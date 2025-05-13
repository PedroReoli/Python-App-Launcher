import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
import pandas as pd
import webbrowser
import os
import json
import threading
from PIL import Image, ImageTk

# Importações para Google Sheets (opcionais, só serão usadas se o usuário tiver as credenciais)
try:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

# Configuração do CustomTkinter
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Cores personalizadas
PRIMARY_COLOR = "#56239f"
SECONDARY_COLOR = "#ff7200"
WHITE_COLOR = "#ffffff"

class EstadosApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuração da janela principal
        self.title("Gerenciador de Combinações de Estados")
        self.geometry("1200x800")
        self.configure(fg_color=WHITE_COLOR)
        
        # Lista de estados brasileiros
        self.estados = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", 
                        "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", 
                        "RS", "RO", "RR", "SC", "SP", "SE", "TO"]
        
        # Dicionário para armazenar os valores
        self.valores = {}
        for origem in self.estados:
            for destino in self.estados:
                self.valores[f"{origem}-{destino}"] = ""
        
        self.create_widgets()
        
    def create_widgets(self):
        # Frame principal
        main_frame = ctk.CTkFrame(self, fg_color=WHITE_COLOR, corner_radius=0)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame, 
            text="Gerenciador de Combinações de Estados", 
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=PRIMARY_COLOR
        )
        title_label.pack(pady=(0, 20))
        
        # Frame para os botões de ação
        button_frame = ctk.CTkFrame(main_frame, fg_color=WHITE_COLOR)
        button_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Botões de ação
        save_button = ctk.CTkButton(
            button_frame, 
            text="Salvar Dados", 
            command=self.save_data,
            fg_color=PRIMARY_COLOR,
            hover_color=SECONDARY_COLOR
        )
        save_button.pack(side=tk.LEFT, padx=5)
        
        load_button = ctk.CTkButton(
            button_frame, 
            text="Carregar Dados", 
            command=self.load_data,
            fg_color=PRIMARY_COLOR,
            hover_color=SECONDARY_COLOR
        )
        load_button.pack(side=tk.LEFT, padx=5)
        
        export_csv_button = ctk.CTkButton(
            button_frame, 
            text="Exportar CSV", 
            command=self.export_to_csv,
            fg_color=PRIMARY_COLOR,
            hover_color=SECONDARY_COLOR
        )
        export_csv_button.pack(side=tk.LEFT, padx=5)
        
        export_sheets_button = ctk.CTkButton(
            button_frame, 
            text="Exportar para Google Sheets", 
            command=self.export_to_sheets,
            fg_color=SECONDARY_COLOR,
            hover_color=PRIMARY_COLOR
        )
        export_sheets_button.pack(side=tk.LEFT, padx=5)
        
        # Frame para a seleção de estados
        selection_frame = ctk.CTkFrame(main_frame, fg_color=WHITE_COLOR)
        selection_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Comboboxes para seleção de estados
        origem_label = ctk.CTkLabel(selection_frame, text="Estado de Origem:", text_color=PRIMARY_COLOR)
        origem_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.origem_var = tk.StringVar()
        self.origem_combobox = ctk.CTkComboBox(
            selection_frame, 
            values=self.estados,
            variable=self.origem_var,
            width=100,
            border_color=PRIMARY_COLOR,
            button_color=PRIMARY_COLOR,
            dropdown_hover_color=SECONDARY_COLOR
        )
        self.origem_combobox.pack(side=tk.LEFT, padx=(0, 20))
        self.origem_combobox.set(self.estados[0])
        
        destino_label = ctk.CTkLabel(selection_frame, text="Estado de Destino:", text_color=PRIMARY_COLOR)
        destino_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.destino_var = tk.StringVar()
        self.destino_combobox = ctk.CTkComboBox(
            selection_frame, 
            values=self.estados,
            variable=self.destino_var,
            width=100,
            border_color=PRIMARY_COLOR,
            button_color=PRIMARY_COLOR,
            dropdown_hover_color=SECONDARY_COLOR
        )
        self.destino_combobox.pack(side=tk.LEFT, padx=(0, 20))
        self.destino_combobox.set(self.estados[0])
        
        view_button = ctk.CTkButton(
            selection_frame, 
            text="Visualizar Combinação", 
            command=self.view_combination,
            fg_color=PRIMARY_COLOR,
            hover_color=SECONDARY_COLOR
        )
        view_button.pack(side=tk.LEFT, padx=5)
        
        # Frame para a tabela
        table_frame = ctk.CTkFrame(main_frame, fg_color=WHITE_COLOR)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Criar canvas para permitir rolagem
        canvas = tk.Canvas(table_frame, bg=WHITE_COLOR, highlightthickness=0)
        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient="horizontal", command=canvas.xview)
        
        # Configurar o canvas
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Posicionar scrollbars e canvas
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame dentro do canvas para conter a tabela
        self.table_inner_frame = tk.Frame(canvas, bg=WHITE_COLOR)
        canvas.create_window((0, 0), window=self.table_inner_frame, anchor="nw")
        
        # Criar a tabela de estados
        self.create_table()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Pronto para uso")
        status_bar = ctk.CTkLabel(
            self, 
            textvariable=self.status_var,
            text_color=PRIMARY_COLOR,
            fg_color="#f0f0f0",
            corner_radius=0
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_table(self):
        # Limpar a tabela existente
        for widget in self.table_inner_frame.winfo_children():
            widget.destroy()
        
        # Criar cabeçalhos
        tk.Label(
            self.table_inner_frame, 
            text="", 
            width=5, 
            bg=PRIMARY_COLOR, 
            fg=WHITE_COLOR,
            relief=tk.RAISED,
            padx=5,
            pady=5
        ).grid(row=0, column=0, sticky="nsew")
        
        for col, estado in enumerate(self.estados, 1):
            tk.Label(
                self.table_inner_frame, 
                text=estado, 
                width=5, 
                bg=PRIMARY_COLOR, 
                fg=WHITE_COLOR,
                relief=tk.RAISED,
                padx=5,
                pady=5
            ).grid(row=0, column=col, sticky="nsew")
        
        # Criar linhas
        for row, origem in enumerate(self.estados, 1):
            tk.Label(
                self.table_inner_frame, 
                text=origem, 
                width=5, 
                bg=PRIMARY_COLOR, 
                fg=WHITE_COLOR,
                relief=tk.RAISED,
                padx=5,
                pady=5
            ).grid(row=row, column=0, sticky="nsew")
            
            for col, destino in enumerate(self.estados, 1):
                key = f"{origem}-{destino}"
                
                # Criar um frame para conter o entry e o botão
                cell_frame = tk.Frame(self.table_inner_frame, bg=WHITE_COLOR)
                cell_frame.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)
                
                # Entry para o valor
                entry = tk.Entry(
                    cell_frame, 
                    width=8,
                    relief=tk.SOLID,
                    borderwidth=1
                )
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                # Preencher com valor existente, se houver
                if key in self.valores and self.valores[key]:
                    entry.insert(0, self.valores[key])
                
                # Associar a entrada ao dicionário
                entry.bind("<FocusOut>", lambda e, k=key, ent=entry: self.update_value(k, ent.get()))
                
                # Botão para abrir em nova guia
                open_button = tk.Button(
                    cell_frame, 
                    text="→",
                    bg=SECONDARY_COLOR,
                    fg=WHITE_COLOR,
                    relief=tk.RAISED,
                    borderwidth=1,
                    command=lambda o=origem, d=destino: self.open_combination(o, d)
                )
                open_button.pack(side=tk.RIGHT)
    
    def update_value(self, key, value):
        self.valores[key] = value
        self.status_var.set(f"Valor atualizado: {key} = {value}")
    
    def open_combination(self, origem, destino):
        # Aqui você pode definir a URL para abrir
        # Por exemplo, pode ser uma página que mostra detalhes dessa combinação
        url = f"https://example.com/estados?origem={origem}&destino={destino}"
        webbrowser.open_new_tab(url)
        self.status_var.set(f"Abrindo combinação {origem}-{destino} em nova guia")
    
    def view_combination(self):
        origem = self.origem_var.get()
        destino = self.destino_var.get()
        key = f"{origem}-{destino}"
        
        if key in self.valores:
            valor = self.valores[key] if self.valores[key] else "Não definido"
            messagebox.showinfo("Combinação", f"{origem}-{destino} = {valor}")
        else:
            messagebox.showinfo("Combinação", f"Combinação {origem}-{destino} não encontrada")
    
    def save_data(self):
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile="estados_valores.json"
            )
            
            if not file_path:  # Se o usuário cancelar
                return
                
            with open(file_path, 'w') as f:
                json.dump(self.valores, f)
            self.status_var.set(f"Dados salvos em {file_path}")
            messagebox.showinfo("Sucesso", f"Dados salvos com sucesso em {file_path}")
        except Exception as e:
            self.status_var.set(f"Erro ao salvar dados: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao salvar dados: {str(e)}")
    
    def load_data(self):
        try:
            file_path = filedialog.askopenfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if not file_path:  # Se o usuário cancelar
                return
                
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    self.valores = json.load(f)
                self.create_table()  # Recriar a tabela com os novos valores
                self.status_var.set(f"Dados carregados de {file_path}")
                messagebox.showinfo("Sucesso", f"Dados carregados com sucesso de {file_path}")
            else:
                self.status_var.set(f"Arquivo {file_path} não encontrado")
                messagebox.showwarning("Aviso", f"Arquivo {file_path} não encontrado")
        except Exception as e:
            self.status_var.set(f"Erro ao carregar dados: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao carregar dados: {str(e)}")
    
    def export_to_csv(self):
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile="estados_export.csv"
            )
            
            if not file_path:  # Se o usuário cancelar
                return
                
            # Criar um DataFrame pandas com os dados
            data = []
            for origem in self.estados:
                row = [origem]
                for destino in self.estados:
                    key = f"{origem}-{destino}"
                    row.append(self.valores.get(key, ""))
                data.append(row)
            
            # Criar o DataFrame
            columns = ["Estado"] + self.estados
            df = pd.DataFrame(data, columns=columns)
            
            # Salvar como CSV
            df.to_csv(file_path, index=False)
            
            self.status_var.set(f"Dados exportados para {file_path}")
            messagebox.showinfo("Sucesso", f"Dados exportados com sucesso para {file_path}")
        except Exception as e:
            self.status_var.set(f"Erro ao exportar dados: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao exportar dados: {str(e)}")
    
    def export_to_sheets(self):
        if not GSPREAD_AVAILABLE:
            messagebox.showwarning(
                "Dependências Faltando", 
                "As bibliotecas gspread e oauth2client não estão instaladas.\n"
                "Instale-as usando: pip install gspread oauth2client"
            )
            return
            
        try:
            # Primeiro, exportar para CSV como backup
            csv_file = "estados_export_temp.csv"
            
            # Criar um DataFrame pandas com os dados
            data = []
            for origem in self.estados:
                row = [origem]
                for destino in self.estados:
                    key = f"{origem}-{destino}"
                    row.append(self.valores.get(key, ""))
                data.append(row)
            
            # Criar o DataFrame
            columns = ["Estado"] + self.estados
            df = pd.DataFrame(data, columns=columns)
            
            # Salvar temporariamente como CSV
            df.to_csv(csv_file, index=False)
            
            # Pedir o arquivo de credenciais
            credentials_file = filedialog.askopenfilename(
                title="Selecione o arquivo de credenciais do Google Cloud",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if not credentials_file:  # Se o usuário cancelar
                # Mostrar instruções para exportação manual
                msg = (
                    "Para exportar manualmente para o Google Sheets:\n\n"
                    f"1. Um arquivo CSV foi gerado: {csv_file}\n"
                    "2. Abra o Google Sheets e crie uma nova planilha\n"
                    "3. Vá para Arquivo > Importar > Fazer upload\n"
                    "4. Selecione o arquivo CSV gerado"
                )
                messagebox.showinfo("Exportar para Google Sheets", msg)
                webbrowser.open_new_tab("https://sheets.google.com")
                return
                
            # Iniciar a exportação em uma thread separada para não bloquear a UI
            self.status_var.set("Exportando para o Google Sheets...")
            threading.Thread(
                target=self._export_to_sheets_thread, 
                args=(credentials_file, csv_file)
            ).start()
            
        except Exception as e:
            self.status_var.set(f"Erro ao exportar dados: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao exportar dados: {str(e)}")
    
    def _export_to_sheets_thread(self, credentials_file, csv_file):
        try:
            # Configurar as credenciais
            SCOPE = ["https://spreadsheets.google.com/feeds", 
                    "https://www.googleapis.com/auth/spreadsheets", 
                    "https://www.googleapis.com/auth/drive"]
            
            credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, SCOPE)
            client = gspread.authorize(credentials)
            
            # Criar uma nova planilha
            sheet_name = "Combinações de Estados"
            try:
                spreadsheet = client.open(sheet_name)
                # Se a planilha já existe, usar a primeira página
                sheet = spreadsheet.get_worksheet(0)
            except gspread.SpreadsheetNotFound:
                # Se a planilha não existe, criar uma nova
                spreadsheet = client.create(sheet_name)
                sheet = spreadsheet.get_worksheet(0)
            
            # Limpar a planilha
            sheet.clear()
            
            # Preencher o cabeçalho
            header = [""] + self.estados
            sheet.update('A1', [header])
            
            # Preencher os dados
            for i, origem in enumerate(self.estados):
                row = [origem]
                for destino in self.estados:
                    key = f"{origem}-{destino}"
                    valor = self.valores.get(key, "")
                    row.append(valor)
                
                # Atualizar a linha (índice+2 porque o cabeçalho é linha 1 e o índice começa em 0)
                sheet.update(f'A{i+2}', [row])
            
            # Formatar o cabeçalho
            sheet.format('A1:AA1', {
                "backgroundColor": {
                    "red": 0.337,
                    "green": 0.137,
                    "blue": 0.624
                },
                "textFormat": {
                    "foregroundColor": {
                        "red": 1.0,
                        "green": 1.0,
                        "blue": 1.0
                    },
                    "bold": True
                }
            })
            
            # Formatar a primeira coluna
            sheet.format(f'A1:A{len(self.estados)+1}', {
                "backgroundColor": {
                    "red": 0.337,
                    "green": 0.137,
                    "blue": 0.624
                },
                "textFormat": {
                    "foregroundColor": {
                        "red": 1.0,
                        "green": 1.0,
                        "blue": 1.0
                    },
                    "bold": True
                }
            })
            
            # Atualizar a UI na thread principal
            self.after(0, lambda: self.status_var.set(f"Planilha exportada com sucesso!"))
            self.after(0, lambda: messagebox.showinfo(
                "Sucesso", 
                f"Planilha '{sheet_name}' criada e preenchida com sucesso!\nURL: {spreadsheet.url}"
            ))
            self.after(0, lambda: webbrowser.open_new_tab(spreadsheet.url))
            
        except Exception as e:
            # Atualizar a UI na thread principal
            self.after(0, lambda: self.status_var.set(f"Erro ao exportar para o Google Sheets: {str(e)}"))
            self.after(0, lambda: messagebox.showerror(
                "Erro", 
                f"Erro ao exportar para o Google Sheets: {str(e)}"
            ))

def main():
    app = EstadosApp()
    app.mainloop()

if __name__ == "__main__":
    main()