import csv
import tkinter as tk
from tkinter import filedialog, messagebox
# ==import pdfplumber
import difflib
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors
import numpy as np
import fitz  # PyMuPDF


# === Load Model Embedding ===
model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

# === Data Struktur Embedding ===
pdf_chunks = []
pdf_embeddings = None
pdf_fitted = False
knn = NearestNeighbors(n_neighbors=1, metric='cosine')

# Path ke file soal jawaban
csv_path = "C:/Users/kals.corpora/Desktop/soal_jawaban.csv"

# Cek permission file CSV
try:
    with open(csv_path, "a", newline='', encoding='utf-8') as f:
        f.write("")
    print("File CSV bisa ditulis.")
except Exception as e:
    print("Error saat membuka file CSV:", e)

# Load soal dan jawaban dari CSV
soal_jawaban = {}
def load_soal_jawaban():
    try:
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                soal_jawaban[row['soal'].strip().lower()] = row['jawaban'].strip()
    except Exception as e:
        print("Gagal load soal dari CSV:", e)

load_soal_jawaban()

# Fungsi memuat dan proses isi PDF
def load_pdf():
    global materi_text, pdf_chunks, pdf_embeddings, pdf_fitted, knn
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if not file_path:
        return
    try:
        texts = []
        with fitz.open(file_path) as pdf:
            for page in pdf:
                text = page.get_text()
                if text:
                    lines = [line.strip() for line in text.splitlines() if line.strip()]
                    texts.extend(lines)
        pdf_chunks = texts  # <-- simpan sebagai chunks untuk pencarian
        if pdf_chunks:
            pdf_embeddings = model.encode(pdf_chunks, convert_to_numpy=True)
            knn.fit(pdf_embeddings)
            pdf_fitted = True
            messagebox.showinfo("Sukses", "Materi dari PDF berhasil dimuat dan diproses!")
        else:
            messagebox.showwarning("Kosong", "PDF tidak berisi teks yang dapat diproses.")
    except Exception as e:
        messagebox.showerror("Gagal", f"Gagal membaca PDF: {e}")

# Fungsi cari jawaban pintar
def cari_jawaban(pertanyaan):
    pertanyaan = pertanyaan.lower()
    
    # --- Cek dari CSV ---
    soal_list = list(soal_jawaban.keys())
    match = difflib.get_close_matches(pertanyaan, soal_list, n=1, cutoff=0.6)
    if match:
        print("[DEBUG] Jawaban diambil dari CSV:", match[0])
        return soal_jawaban[match[0]]

    # --- Cek dari PDF dengan vector search ---
    if pdf_fitted and model and knn and pdf_chunks:
        try:
            q_embedding = model.encode([pertanyaan], convert_to_numpy=True)
            distance, index = knn.kneighbors(q_embedding, n_neighbors=1)
            print("[DEBUG] PDF cosine distance:", distance[0][0])

            if distance[0][0] < 0.4:  # threshold kemiripan
                print("[DEBUG] Jawaban diambil dari PDF, index:", index[0][0])
                return f"(Dari PDF) {pdf_chunks[index[0][0]]}"
            else:
                print("[DEBUG] Jarak terlalu jauh, tidak diambil dari PDF.")
        except Exception as e:
            print("[ERROR] Gagal memproses PDF vector search:", e)
    else:
        print("[DEBUG] PDF belum diproses atau model belum siap.")

    # --- Tidak ditemukan ---
    print("[DEBUG] Jawaban tidak ditemukan.")
    return None

# Fungsi menyimpan pelajaran baru
def simpan_pelajaran(soal_baru, jawaban_baru):
    try:
        with open(csv_path, "a", newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([soal_baru.strip(), jawaban_baru.strip()])
        soal_jawaban[soal_baru.strip().lower()] = jawaban_baru.strip()
    except Exception as e:
        messagebox.showerror("Gagal Simpan", f"Gagal menyimpan jawaban baru: {e}")

# === GUI ===
root = tk.Tk()
root.title("Z4yn K3nan - Chatbot Edukasi Pintar")

chat_log = tk.Text(root, height=20, width=60)
chat_log.pack(padx=10, pady=10)

entry = tk.Entry(root, width=50)
entry.pack(side=tk.LEFT, padx=(10, 0), pady=(0, 10))

kirim_button = tk.Button(root, text="Kirim")
kirim_button.pack(side=tk.LEFT, padx=(5, 0), pady=(0, 10))

load_pdf_button = tk.Button(root, text="Load PDF", command=load_pdf)
load_pdf_button.pack(side=tk.LEFT, padx=(5, 10), pady=(0, 10))

belajar_mode = False
last_question = ""

def kirim():
    global belajar_mode, last_question
    user_input = entry.get().strip()
    if not user_input:
        return
    chat_log.insert(tk.END, "kenan: " + user_input + "\n")
    entry.delete(0, tk.END)

    if belajar_mode:
        simpan_pelajaran(last_question, user_input)
        chat_log.insert(tk.END, "Papah: Terima kasih! Saya sudah belajar jawaban baru.\n\n")
        belajar_mode = False
        last_question = ""
    else:
        jawaban = cari_jawaban(user_input)
        if jawaban:
            if jawaban.startswith("(Dari PDF)"):
                chat_log.insert(tk.END, "papa (belajar dari PDF): " + jawaban.replace("(Dari PDF) ", "") + "\n\n")
            else:
                chat_log.insert(tk.END, "papa (dari CSV): " + jawaban + "\n\n")
        else:
            chat_log.insert(tk.END, "papa: Maaf, saya belum tahu jawaban untuk pertanyaan itu.\n")
            chat_log.insert(tk.END, "papa: Tolong bantu saya jawab ya, agar saya bisa belajar!\n\n")
            belajar_mode = True
            last_question = user_input

kirim_button.config(command=kirim)

root.mainloop()
