import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import os

# --- BAGIAN LOGIKA STEGANOGRAFI LSB ---

def char_to_binary(chars):
    """Mengubah string menjadi representasi biner."""
    return ''.join(format(ord(i), '08b') for i in chars)

def binary_to_char(binary):
    """Mengubah representasi biner kembali menjadi string."""
    chars = ""
    for i in range(0, len(binary), 8):
        byte = binary[i:i+8]
        if len(byte) == 8:
            chars += chr(int(byte, 2))
    return chars

def encode_image(image_path, secret_message):
    """Menyisipkan pesan rahasia ke dalam gambar."""
    try:
        img = Image.open(image_path, 'r').convert("RGB")
        width, height = img.size
        secret_message += "#####" 
        binary_secret_message = char_to_binary(secret_message)
        data_len = len(binary_secret_message)
        if data_len > width * height * 3:
            messagebox.showerror("Error", "Ukuran pesan terlalu besar untuk gambar ini!")
            return None
        data_index = 0
        new_img = img.copy()
        for y in range(height):
            for x in range(width):
                pixel = list(img.getpixel((x, y)))
                for i in range(3):
                    if data_index < data_len:
                        pixel[i] = int(format(pixel[i], '08b')[:-1] + binary_secret_message[data_index], 2)
                        data_index += 1
                new_img.putpixel((x, y), tuple(pixel))
                if data_index >= data_len:
                    return new_img 
        return new_img
    except FileNotFoundError:
        messagebox.showerror("Error", "File gambar tidak ditemukan.")
        return None
    except Exception as e:
        messagebox.showerror("Error", f"Terjadi kesalahan saat encoding: {e}")
        return None

def decode_image(image_path):
    """Mengekstrak pesan rahasia dari gambar."""
    try:
        img = Image.open(image_path, 'r')
        width, height = img.size
        binary_data = ""
        delimiter = "#####"
        for y in range(height):
            for x in range(width):
                pixel = img.getpixel((x, y))
                for i in range(3):
                    binary_data += format(pixel[i], '08b')[-1]
                    if len(binary_data) % 8 == 0:
                        decoded_chars = binary_to_char(binary_data)
                        if decoded_chars.endswith(delimiter):
                            return decoded_chars[:-len(delimiter)]
        return "Tidak ada pesan tersembunyi yang ditemukan atau delimiter rusak."
    except FileNotFoundError:
        messagebox.showerror("Error", "File gambar tidak ditemukan.")
        return None
    except Exception as e:
        messagebox.showerror("Error", f"Terjadi kesalahan saat decoding: {e}")
        return None

# --- BAGIAN INTERFACE (GUI) ---

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Konfigurasi window utama
        self.title("🔒 LSB Steganography - Sistem Multimedia")
        self.geometry("1200x800")
        self.minsize(900, 700)
        
        # Set tema gelap yang 
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.encode_image_path = None
        self.decode_image_path = None
        
        # Konfigurasi grid utama
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header dengan gradient effect
        self.create_header()
        
        # Main content area
        self.create_main_content()
        
        # Footer
        self.create_footer()

    def create_header(self):
        """Membuat header"""
        self.header_frame = ctk.CTkFrame(self, height=80, corner_radius=0, 
                                        fg_color=["#1f538d", "#14375e"])
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.header_frame.grid_columnconfigure(1, weight=1)
        self.header_frame.grid_propagate(False)

        # Icon dan title
        self.title_container = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.title_container.grid(row=0, column=1, sticky="")
        
        self.title_label = ctk.CTkLabel(
            self.title_container, 
            text="🔐 LSB STEGANOGRAPHY",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="white"
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=10)
        
        self.subtitle_label = ctk.CTkLabel(
            self.title_container,
            text="Aplikasi Penyembunyian Pesan dalam Gambar",
            font=ctk.CTkFont(size=14),
            text_color=["#b8d4f0", "#a0c4ff"]
        )
        self.subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 10))

    def create_main_content(self):
        """Membuat area konten utama dengan scrollable frame"""
        # Scrollable frame sebagai container utama
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self, 
            corner_radius=15, 
            fg_color=["#f0f0f0", "#212121"],
            scrollbar_button_color=["#1f538d", "#14375e"],
            scrollbar_button_hover_color=["#2d5aa0", "#1e4574"]
        )
        self.scrollable_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Control tabs
        self.create_control_tabs()

    def create_control_tabs(self):
        """Membuat tab kontrol yang modern"""
        self.tab_view = ctk.CTkTabview(self.scrollable_frame, corner_radius=12, height=600)
        self.tab_view.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        # Custom tab styling
        self.tab_view.add("🔐 Encode Message")
        self.tab_view.add("🔓 Decode Message")
        
        # Encode tab
        self.create_encode_tab()
        
        # Decode tab
        self.create_decode_tab()

    def create_encode_tab(self):
        """Tab untuk encoding pesan"""
        encode_tab = self.tab_view.tab("🔐 Encode Message")
        encode_tab.grid_columnconfigure(0, weight=1)

        # Image preview area untuk encode
        self.create_encode_preview_area(encode_tab)
        
        # Step 1: Select image
        step1_frame = ctk.CTkFrame(encode_tab, corner_radius=10)
        step1_frame.grid(row=1, column=0, padx=20, pady=15, sticky="ew")
        step1_frame.grid_columnconfigure(1, weight=1)

        step1_label = ctk.CTkLabel(
            step1_frame,
            text="1️⃣ Pilih Gambar:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        step1_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")

        self.btn_open_encode = ctk.CTkButton(
            step1_frame,
            text="📁 Pilih Gambar",
            command=self.open_image_for_encode,
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=["#1f538d", "#14375e"],
            hover_color=["#2d5aa0", "#1e4574"]
        )
        self.btn_open_encode.grid(row=0, column=1, padx=15, pady=15, sticky="ew")

        # Step 2: Enter message
        step2_frame = ctk.CTkFrame(encode_tab, corner_radius=10)
        step2_frame.grid(row=2, column=0, padx=20, pady=15, sticky="ew")
        step2_frame.grid_columnconfigure(0, weight=1)

        step2_label = ctk.CTkLabel(
            step2_frame,
            text="2️⃣ Masukkan Pesan Rahasia:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        step2_label.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")

        self.secret_entry = ctk.CTkTextbox(
            step2_frame,
            height=100,
            corner_radius=8,
            font=ctk.CTkFont(size=14),
            border_width=2
        )
        self.secret_entry.grid(row=1, column=0, padx=15, pady=(5, 15), sticky="ew")

        # Step 3: Process
        self.btn_encode = ctk.CTkButton(
            encode_tab,
            text="🚀 Proses Encode & Simpan",
            command=self.encode_message,
            height=50,
            corner_radius=12,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=["#2d7d32", "#1b5e20"],
            hover_color=["#388e3c", "#2e7d32"]
        )
        self.btn_encode.grid(row=3, column=0, padx=20, pady=15)

    def create_encode_preview_area(self, parent):
        """Membuat area preview gambar untuk encode"""
        self.encode_preview_frame = ctk.CTkFrame(parent, corner_radius=12)
        self.encode_preview_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        self.encode_preview_frame.grid_columnconfigure((0, 1), weight=1)

        # Before image section
        self.before_section = ctk.CTkFrame(self.encode_preview_frame, corner_radius=10)
        self.before_section.grid(row=0, column=0, padx=10, pady=15, sticky="ew")
        self.before_section.grid_columnconfigure(0, weight=1)

        self.before_header = ctk.CTkFrame(self.before_section, height=40, corner_radius=8,
                                         fg_color=["#2b5797", "#1e3a5f"])
        self.before_header.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.before_header.grid_propagate(False)
        
        self.before_label = ctk.CTkLabel(
            self.before_header,
            text="📷 Gambar Asli",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        )
        self.before_label.pack(pady=10)

        self.before_image_panel = ctk.CTkLabel(
            self.before_section,
            text="🖼️\n\nPilih gambar untuk memulai",
            font=ctk.CTkFont(size=14),
            corner_radius=8,
            height=250,
            fg_color=["#e8e8e8", "#2b2b2b"],
            text_color=["#666666", "#cccccc"]
        )
        self.before_image_panel.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        # After image section
        self.after_section = ctk.CTkFrame(self.encode_preview_frame, corner_radius=10)
        self.after_section.grid(row=0, column=1, padx=10, pady=15, sticky="ew")
        self.after_section.grid_columnconfigure(0, weight=1)

        self.after_header = ctk.CTkFrame(self.after_section, height=40, corner_radius=8,
                                        fg_color=["#2d7d32", "#1b5e20"])
        self.after_header.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.after_header.grid_propagate(False)
        
        self.after_label = ctk.CTkLabel(
            self.after_header,
            text="🔒 Gambar Terenkripsi",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        )
        self.after_label.pack(pady=10)

        self.after_image_panel = ctk.CTkLabel(
            self.after_section,
            text="🎯\n\nHasil akan muncul di sini",
            font=ctk.CTkFont(size=14),
            corner_radius=8,
            height=250,
            fg_color=["#e8e8e8", "#2b2b2b"],
            text_color=["#666666", "#cccccc"]
        )
        self.after_image_panel.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

    def create_decode_tab(self):
        """Tab untuk decoding pesan"""
        decode_tab = self.tab_view.tab("🔓 Decode Message")
        decode_tab.grid_columnconfigure(0, weight=1)

        # Step 1: Select image with preview
        step1_frame = ctk.CTkFrame(decode_tab, corner_radius=10)
        step1_frame.grid(row=0, column=0, padx=20, pady=15, sticky="ew")
        step1_frame.grid_columnconfigure(1, weight=1)

        step1_label = ctk.CTkLabel(
            step1_frame,
            text="1️⃣ Pilih Gambar yang Mengandung Pesan:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        step1_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")

        self.btn_open_decode = ctk.CTkButton(
            step1_frame,
            text="📁 Pilih Gambar",
            command=self.open_image_for_decode,
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=["#d32f2f", "#b71c1c"],
            hover_color=["#e53935", "#c62828"]
        )
        self.btn_open_decode.grid(row=0, column=1, padx=15, pady=15, sticky="ew")

        # Image preview for decode
        preview_frame = ctk.CTkFrame(decode_tab, corner_radius=10)
        preview_frame.grid(row=1, column=0, padx=20, pady=15, sticky="ew")
        preview_frame.grid_columnconfigure(0, weight=1)

        preview_header = ctk.CTkFrame(preview_frame, height=40, corner_radius=8,
                                     fg_color=["#d32f2f", "#b71c1c"])
        preview_header.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        preview_header.grid_propagate(False)
        
        preview_label = ctk.CTkLabel(
            preview_header,
            text="🖼️ Gambar yang Akan Di-decode",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        )
        preview_label.pack(pady=10)

        self.decode_image_panel = ctk.CTkLabel(
            preview_frame,
            text="📁\n\nPilih gambar untuk melihat preview",
            font=ctk.CTkFont(size=14),
            corner_radius=8,
            height=250,
            fg_color=["#e8e8e8", "#2b2b2b"],
            text_color=["#666666", "#cccccc"]
        )
        self.decode_image_panel.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        # Step 2: Decode button
        self.btn_decode = ctk.CTkButton(
            decode_tab,
            text="🔍 Proses Decode",
            command=self.decode_message,
            height=50,
            corner_radius=12,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=["#f57c00", "#e65100"],
            hover_color=["#ff9800", "#ef6c00"]
        )
        self.btn_decode.grid(row=2, column=0, padx=20, pady=15)

        # Result area
        result_frame = ctk.CTkFrame(decode_tab, corner_radius=10)
        result_frame.grid(row=3, column=0, padx=20, pady=15, sticky="ew")
        result_frame.grid_columnconfigure(0, weight=1)

        self.decoded_message_label = ctk.CTkLabel(
            result_frame,
            text="📨 Pesan yang Ditemukan:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.decoded_message_label.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")

        self.decoded_message_text = ctk.CTkTextbox(
            result_frame,
            height=120,
            corner_radius=8,
            font=ctk.CTkFont(size=13),
            state="disabled"
        )
        self.decoded_message_text.grid(row=1, column=0, padx=15, pady=(5, 15), sticky="ew")

    def create_footer(self):
        """Membuat footer"""
        self.footer_frame = ctk.CTkFrame(self, height=40, corner_radius=0,
                                        fg_color=["#f5f5f5", "#1a1a1a"])
        self.footer_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        self.footer_frame.grid_propagate(False)

        self.footer_label = ctk.CTkLabel(
            self.footer_frame,
            text="© Kelompok 1 6C | UAS Sistem Multimedia",
            font=ctk.CTkFont(size=12),
            text_color=["#666666", "#cccccc"]
        )
        self.footer_label.pack(pady=12)

    def open_image_for_encode(self):
        """Buka gambar untuk encoding"""
        path = filedialog.askopenfilename(
            title="Pilih Gambar untuk Di-encode",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if path:
            self.encode_image_path = path
            self.display_image(self.encode_image_path, self.before_image_panel)
            self.after_image_panel.configure(image=None, text="🎯\n\nHasil akan muncul di sini")

    def open_image_for_decode(self):
        """Buka gambar untuk decoding"""
        path = filedialog.askopenfilename(
            title="Pilih Gambar untuk Di-decode",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if path:
            self.decode_image_path = path
            # Untuk decode, tampilkan gambar di panel khusus decode
            self.display_image(self.decode_image_path, self.decode_image_panel)
            self.decoded_message_text.configure(state="normal")
            self.decoded_message_text.delete("1.0", "end")
            self.decoded_message_text.insert("1.0", "Klik 'Proses Decode' untuk melihat pesan")
            self.decoded_message_text.configure(state="disabled")

    def display_image(self, path, panel):
        """Menampilkan gambar dengan ukuran yang sesuai"""
        try:
            img = Image.open(path)
            
            # Resize image untuk preview
            max_size = (300, 300)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Buat CTkImage
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, 
                                  size=(img.width, img.height))
            panel.configure(image=ctk_img, text="")
            panel.image = ctk_img
            
        except Exception as e:
            panel.configure(text=f"❌\n\nGagal memuat gambar:\n{str(e)[:50]}...")
            messagebox.showerror("Error", f"Gagal menampilkan gambar: {e}")

    def encode_message(self):
        """Proses encoding pesan"""
        if not self.encode_image_path:
            messagebox.showwarning("⚠️ Peringatan", "Silakan pilih gambar terlebih dahulu!")
            return
        
        secret = self.secret_entry.get("1.0", "end-1c").strip()
        if not secret:
            messagebox.showwarning("⚠️ Peringatan", "Pesan rahasia tidak boleh kosong!")
            return
        
        # Show progress
        self.btn_encode.configure(text="🔄 Processing...", state="disabled")
        self.update()
        
        new_img_obj = encode_image(self.encode_image_path, secret)
        
        if new_img_obj:
            filename = os.path.splitext(os.path.basename(self.encode_image_path))[0]
            save_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG file", "*.png")],
                initialfile=f"{filename}_encoded.png",
                title="💾 Simpan Gambar Hasil Encode"
            )
            
            if save_path:
                new_img_obj.save(save_path)
                self.display_image(save_path, self.after_image_panel)
                messagebox.showinfo("✅ Berhasil!", 
                                  f"Pesan berhasil disembunyikan!\n\nFile disimpan di:\n{save_path}")
        
        self.btn_encode.configure(text="🚀 Proses Encode & Simpan", state="normal")

    def decode_message(self):
        """Proses decoding pesan"""
        if not self.decode_image_path:
            messagebox.showwarning("⚠️ Peringatan", "Silakan pilih gambar yang ingin di-decode!")
            return
        
        # Show progress
        self.btn_decode.configure(text="🔄 Processing...", state="disabled")
        self.update()
        
        hidden_message = decode_image(self.decode_image_path)
        
        self.decoded_message_text.configure(state="normal")
        self.decoded_message_text.delete("1.0", "end")
        
        if hidden_message and hidden_message != "Tidak ada pesan tersembunyi yang ditemukan atau delimiter rusak.":
            self.decoded_message_text.insert("1.0", hidden_message)
            messagebox.showinfo("✅ Pesan Ditemukan!", 
                              f"Pesan berhasil diekstrak!\n\nPanjang pesan: {len(hidden_message)} karakter")
        else:
            self.decoded_message_text.insert("1.0", "❌ Tidak ada pesan tersembunyi yang ditemukan dalam gambar ini.")
            messagebox.showwarning("⚠️ Tidak Ditemukan", 
                                 "Tidak ada pesan tersembunyi yang ditemukan atau gambar tidak menggunakan metode LSB.")
        
        self.decoded_message_text.configure(state="disabled")
        self.btn_decode.configure(text="🔍 Proses Decode", state="normal")

if __name__ == "__main__":
    app = App()
    app.mainloop()