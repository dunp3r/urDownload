# GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
from tkinter import font
import yt_dlp
import sys
import os
import threading



def get_resource_path(relative_path):
    """Permite que funcione dentro del ejecutable"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

yt_dlp_path = get_resource_path("yt-dlp.exe")
ffmpeg_path = get_resource_path("ffmpeg.exe")

# Esto ayuda a encontrar los ejecutables en modo PyInstaller
def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)


# Ajustamos las opciones para yt-dlp
ffmpeg_path = get_resource_path("ffmpeg.exe")

# Ruta del ícono, compatible con PyInstaller
if hasattr(sys, '_MEIPASS'):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

icon_path = os.path.join(base_path, "assets", "you_icon.ico")


def download_video():
    url = entry_url.get()
    if not url:
        messagebox.showwarning("Advertencia", "Por favor, ingresa una URL válida.")
        return
    label_status.config(text="Descarga en proceso... Espere")
    root.update_idletasks()  # Forzar actualización visual inmediata

    
    save_path = filedialog.askdirectory()
    if not save_path:
        messagebox.showwarning("Advertencia", "Por favor, selecciona una carpeta de destino.")
        return

    ydl_opts = {
        'ffmpeg_location': ffmpeg_path,
        #'format': 'bv[ext=mp4][vcodec^=avc1]+ba[ext=m4a]/best[ext=mp4]/best',  # Descargar la mejor calidad de video y audio
        'format': 'bestvideo+bestaudio[ext=m4a]/best',
        'merge_output_format': 'mp4',
        'outtmpl': f'{save_path}/%(title)s.%(ext)s',  # Ruta y nombre del archivo de salida
        'merge_output_format': 'mp4',  # Formato de salida combinado (video + audio)
        'progress_hooks': [progress_hook],  # Llamar a la función hook de progreso
        'no_color': True, #
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        messagebox.showinfo("Éxito", f"Video descargado exitosamente en {save_path}.")
        label_status.config(text="Esperando acción...")
        progress_bar['value'] = 0  # (opcional) reinicia barra de progreso
        root.update_idletasks()
        entry_url.delete(0, tk.END)
        show_vlc_notice_once()
        
    except yt_dlp.DownloadError as e:
        messagebox.showerror("Error", f"No se pudo descargar el video: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo descargar el video: {e}")
        
def check_and_show_notice():
    flag_path = os.path.join(os.path.expanduser("~"), ".urdownload_vlc_notice")
    if not os.path.exists(flag_path):
        messagebox.showinfo(
            "Aviso de compatibilidad",
            "⚠️ Nota: Algunos reproductores como el de Windows no soportan códecs modernos como VP9 o AV1.\n"
            "📽️ Recomendamos usar VLC Media Player para evitar problemas de reproducción."
        )
        with open(flag_path, "w") as f:
            f.write("shown=True")

# FUNCION PARA ARREGLAR EL BUG DE VENTANA
def start_download_thread():
    # hilo separado para que la GUI no se congele
    thread = threading.Thread(target=download_video)
    thread.start()

# FUNCION PARA MOSTRAR EL MENSAJE UNA SOLA VEZ.
def show_vlc_notice_once():
    flag_path = os.path.join(os.path.expanduser("~"), ".urdownload_vlc_notice")
    if not os.path.exists(flag_path):
        messagebox.showinfo(
            "Aviso de compatibilidad",
            "El video se descargó correctamente en calidad máxima.\n\n"
            "⚠️ Nota: Algunos reproductores como el de Windows no soportan códecs modernos como VP9 o AV1.\n"
            "📽️ Recomendamos usar VLC Media Player para evitar problemas de reproducción."
        )
        with open(flag_path, "w") as f:
            f.write("shown=True")


def progress_hook(d):
    if d['status'] == 'downloading':
        # Obtener información sobre el progreso
        percent = d['_percent_str']
        downloaded = d['_downloaded_bytes_str']
        total = d['_total_bytes_str']
        speed = d['_speed_str']
        eta = d['_eta_str']
        
        # Actualizar el texto de la etiqueta con el progreso
        status = f"Descargando: {percent} ({downloaded} de {total}) a {speed}, ETA: {eta}"
        label_status.config(text=status)
        
        # Actualizar la barra de progreso
        progress = float(d['_percent_str'].replace('%', ''))
        progress_bar['value'] = progress
        
        # Actualizar la interfaz
        root.update_idletasks()

    elif d['status'] == 'finished':
        # Al finalizar la descarga
        label_status.config(text="Descarga completada.")
        progress_bar['value'] = 100  # Asegurar que la barra llegue al 100%
        root.update_idletasks()

# Configuración de la ventana principal
root = tk.Tk()
root.resizable(False, False)
root.title("urDownload")
root.iconbitmap(icon_path)
root.geometry("500x250")  # Ventana más grande para mayor comodidad
root.overrideredirect(False)
# Centrar ventana en pantalla
root.update_idletasks()
ancho_ventana = root.winfo_width()
alto_ventana = root.winfo_height()
pantalla_ancho = root.winfo_screenwidth()
pantalla_alto = root.winfo_screenheight()
x = (pantalla_ancho // 2) - (ancho_ventana // 2)
y = (pantalla_alto // 2) - (alto_ventana // 2)
root.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")


# Estilo de la ventana (negro grisáceo elegante)
color_fondo = "#1e1e1e"       # Fondo general (negro mate)
color_entrada = "#2b2b2b"     # Color del Entry (ligeramente más claro)
color_texto = "white"         # Blanco para contraste

root.config(bg=color_fondo)

# Estilo para el tema oscuro en ttk
style = ttk.Style()
style.theme_use('clam')
style.configure("TProgressbar", troughcolor=color_entrada, background="#4CAF50", bordercolor=color_fondo, lightcolor="#4CAF50", darkcolor="#4CAF50")

# Etiqueta de URL
label_url = tk.Label(root, text="Introduce la URL del video:", bg=color_fondo, fg=color_texto, font=("Segoe UI", 13))
label_url.pack(pady=10)

# Entrada de texto
entry_url = tk.Entry(root, width=50, font=("Segoe UI", 12), bg=color_entrada, fg=color_texto, insertbackground=color_texto, relief="solid", highlightcolor="white", highlightthickness=0.5)
entry_url.pack(pady=5)


# Barra de progreso
progress_bar = ttk.Progressbar(root, length=400, mode='determinate', maximum=100)
progress_bar.pack(pady=10)

# Etiqueta de estado
label_status = tk.Label(root, text="Esperando acción...", bg=color_fondo, fg=color_texto, font=("Segoe UI", 10))
label_status.pack(pady=4)

# Botón de descarga
download_button = tk.Button(
    root,
    text="DESCARGAR",
    command=start_download_thread,
    font=("Segoe UI Bold", 14),
    bg="#ef3e3e",  # Verde corporativo 3fe51a
    fg="black",
    activebackground="#388E3C",
    activeforeground="white",
    relief="raised",
    bd=1
)
download_button.pack(pady=20)

label_note = tk.Label(
    root,
    text="* Se Recomienda usar VLC para reproducir videos 4K correctamente.",
    bg=color_fondo,
    fg="#bbbbbb",
    font=("Segoe UI", 8)
)
label_note.pack(pady=2)


check_and_show_notice()


# Ejecutar la aplicación
root.mainloop()

