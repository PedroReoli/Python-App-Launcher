import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk

# Variáveis globais
image = None
clone = None
mask = None
blur_intensity = 15  # Intensidade padrão
extreme_blur_intensity = 5  # Número de aplicações extras do blur
drawing = False


def open_image():
    """ Abre uma imagem e a exibe na tela """
    global image, clone, mask
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.jpeg")])
    if file_path:
        img_cv = cv2.imread(file_path)
        img_cv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(img_cv)
        clone = image.copy()
        mask = np.zeros((img_cv.shape[0], img_cv.shape[1]), dtype=np.uint8)
        update_preview()


def update_preview():
    """ Atualiza a imagem exibida no canvas """
    if image is not None:
        img_resized = image.resize((400, 300), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img_resized)
        canvas.create_image(0, 0, anchor="nw", image=img_tk)
        canvas.image = img_tk


def start_draw(event):
    """ Inicia o desenho da área de blur """
    global drawing
    drawing = True


def draw(event):
    """ Desenha com o cursor a área a ser borrada """
    if drawing and image:
        x, y = int(event.x * (image.width / 400)), int(event.y * (image.height / 300))
        
        # Criar área de desfoque
        cv2.circle(mask, (x, y), 15, 255, -1)
        temp = np.array(clone)
        
        # Aplicação contínua do desfoque
        for _ in range(extreme_blur_intensity):
            temp[mask > 0] = cv2.GaussianBlur(temp, (blur_intensity, blur_intensity), 0)[mask > 0]
        
        image.paste(Image.fromarray(temp))
        update_preview()


def stop_draw(event):
    """ Finaliza o desenho da área de blur """
    global drawing
    drawing = False


def save_image():
    """ Salva a imagem editada """
    file_path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                             filetypes=[("JPEG", "*.jpg"),
                                                        ("PNG", "*.png"),
                                                        ("All Files", "*.*")])
    if file_path and image:
        image.save(file_path)


def update_blur_intensity(val):
    """ Atualiza a intensidade do desfoque """
    global blur_intensity
    blur_intensity = max(5, int(val))  # Garante um mínimo


def update_extreme_blur(val):
    """ Define quantas vezes o blur será aplicado, para censura extrema """
    global extreme_blur_intensity
    extreme_blur_intensity = max(1, int(val))  # Garante um mínimo


# Criando a interface gráfica
root = tk.Tk()
root.title("Editor de Imagem - Blur Extremo")
root.geometry("500x550")
root.configure(bg="#2c3e50")

# Canvas para exibir imagem
canvas = tk.Canvas(root, width=400, height=300, bg="white")
canvas.pack(pady=10)

# Botão para abrir imagem
btn_open = ttk.Button(root, text="Abrir Imagem", command=open_image)
btn_open.pack(pady=5)

# Controle deslizante para intensidade do blur
tk.Label(root, text="Intensidade do Blur:", bg="#2c3e50", fg="white").pack()
slider = ttk.Scale(root, from_=5, to=50, orient="horizontal", command=update_blur_intensity)
slider.set(15)
slider.pack(pady=5)

# Controle deslizante para desfoque extremo (repetição do efeito)
tk.Label(root, text="Quantidade de Aplicações do Blur:", bg="#2c3e50", fg="white").pack()
slider_extreme = ttk.Scale(root, from_=1, to=10, orient="horizontal", command=update_extreme_blur)
slider_extreme.set(5)
slider_extreme.pack(pady=5)

# Botão para salvar a imagem
btn_save = ttk.Button(root, text="Salvar Imagem", command=save_image)
btn_save.pack(pady=5)

# Eventos do mouse para desenhar
canvas.bind("<ButtonPress-1>", start_draw)
canvas.bind("<B1-Motion>", draw)
canvas.bind("<ButtonRelease-1>", stop_draw)

root.mainloop()

# Fechar o navegador