import csv
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import re
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors
import fitz  # PyMuPDF

# === Load Model Embedding ===
model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

# Data PDF
pdf_chunks = []
pdf_embeddings = None
pdf_fitted = False
knn_pdf = NearestNeighbors(n_neighbors=5, metric='cosine')

# Path CSV
csv_path = "C:/Users/kals.corpora/Desktop/soal_jawaban.csv"

# Load data soal & jawaban
soal_jawaban = {}
soal_list = []
soal_embeddings = None
knn_csv = NearestNeighbors(n_neighbors=5, metric='cosine')

# Jawaban fallback kalau tidak ditemukan
fallback_jawaban = "Maaf, saya belum memiliki jawaban untuk pertanyaan itu. Silakan coba tanya hal lain ya."

# === FUNGSI LOAD CSV ===
def load_soal_jawaban():
    global soal_list, soal_embeddings
    try:
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            soal_list.clear()
            soal_jawaban.clear()
            for row in reader:
                soal_text = row['soal'].strip()
                jawaban_text = row['jawaban'].strip()
                soal_jawaban[soal_text.lower()] = jawaban_text
                soal_list.append(soal_text)
            
            if soal_list:
                soal_embeddings = model.encode(soal_list, convert_to_numpy=True)
                knn_csv.fit(soal_embeddings)
                print(f"[INFO] {len(soal_list)} soal dari CSV dimuat.")
    except FileNotFoundError:
        print("[WARNING] CSV belum ada, akan dibuat saat simpan data baru.")
    except Exception as e:
        print("Gagal load soal dari CSV:", e)

load_soal_jawaban()

# === FUNGSI LOAD PDF ===
def load_pdf():
    global pdf_chunks, pdf_embeddings, pdf_fitted, knn_pdf
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
        pdf_chunks = texts
        if pdf_chunks:
            pdf_embeddings = model.encode(pdf_chunks, convert_to_numpy=True)
            knn_pdf.fit(pdf_embeddings)
            pdf_fitted = True
            messagebox.showinfo("Sukses", "Materi dari PDF berhasil dimuat!")
        else:
            messagebox.showwarning("Kosong", "PDF tidak berisi teks yang dapat diproses.")
    except Exception as e:
        messagebox.showerror("Gagal", f"Gagal membaca PDF: {e}")

# === FUNGSI CEK KATA KUNCI ===
def keyword_overlap(q1, q2):
    words1 = set(re.findall(r'\w+', q1.lower()))
    words2 = set(re.findall(r'\w+', q2.lower()))
    if not words1 or not words2:
        return 0
    return len(words1 & words2) / len(words1)

# === FUNGSI CARI JAWABAN ===
def cari_jawaban(pertanyaan, top_k=5, th_semantic=0.6, th_keyword=0.5):
    pertanyaan_lower = pertanyaan.lower()

    if soal_list and soal_embeddings is not None:
        try:
            q_embedding = model.encode([pertanyaan], convert_to_numpy=True)
            distances, indices = knn_csv.kneighbors(q_embedding, n_neighbors=top_k)

            kandidat = []
            for dist, idx in zip(distances[0], indices[0]):
                soal_csv = soal_list[idx]
                jawaban_csv = soal_jawaban[soal_csv.lower()]
                semantic_score = 1 - dist
                keyword_score = keyword_overlap(pertanyaan, soal_csv)
                kandidat.append((soal_csv, jawaban_csv, semantic_score, keyword_score))
                print(f"[DEBUG] CSV - Soal: {soal_csv}, Semantic: {semantic_score:.3f}, Keyword: {keyword_score:.3f}")

            kandidat.sort(key=lambda x: (x[2] + x[3]) / 2, reverse=True)

            if kandidat and kandidat[0][2] >= th_semantic and kandidat[0][3] >= th_keyword:
                print(f"[DEBUG] Memilih jawaban CSV dengan skor {(kandidat[0][2] + kandidat[0][3])/2:.3f}")
                return kandidat[0][1]
        except Exception as e:
            print("[ERROR] Cari di CSV gagal:", e)

    if pdf_fitted and pdf_chunks:
        try:
            q_embedding = model.encode([pertanyaan], convert_to_numpy=True)
            distances, indices = knn_pdf.kneighbors(q_embedding, n_neighbors=top_k)

            kandidat = []
            for dist, idx in zip(distances[0], indices[0]):
                text_pdf = pdf_chunks[idx]
                semantic_score = 1 - dist
                keyword_score = keyword_overlap(pertanyaan, text_pdf)
                kandidat.append((text_pdf, semantic_score, keyword_score))
                print(f"[DEBUG] PDF - Text: {text_pdf[:30]}..., Semantic: {semantic_score:.3f}, Keyword: {keyword_score:.3f}")

            kandidat.sort(key=lambda x: (x[1] + x[2]) / 2, reverse=True)

            if kandidat and kandidat[0][1] >= th_semantic and kandidat[0][2] >= th_keyword:
                print(f"[DEBUG] Memilih jawaban PDF dengan skor {(kandidat[0][1] + kandidat[0][2])/2:.3f}")
                return f"(Dari PDF) {kandidat[0][0]}"
        except Exception as e:
            print("[ERROR] Cari di PDF gagal:", e)

    print("[DEBUG] Tidak ada jawaban cocok, menggunakan fallback.")
    return fallback_jawaban



# === GUI ala The Amateurs (dark theme, bubble chat kiri kanan) ===
root = tk.Tk()
root.title("Amateur v 1.0")
root.configure(bg="#121212")
root.geometry("600x500")

# Frame chat log dengan scrollbar
chat_frame = tk.Frame(root, bg="#121212")
chat_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

chat_log = tk.Text(chat_frame, wrap=tk.WORD, state='disabled', bg="#1E1E1E", fg="#E0E0E0", font=("Segoe UI", 11))
chat_log.pack(fill=tk.BOTH, expand=True)

# Frame input di bawah
input_frame = tk.Frame(root, bg="#121212")
input_frame.pack(fill=tk.X, padx=10, pady=(0,10))

entry = tk.Entry(input_frame, font=("Segoe UI", 12), bg="#2C2C2C", fg="#FFFFFF", insertbackground='white')
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,10), pady=5)

def insert_message(who, msg):
    chat_log.configure(state='normal')

    # Sisipkan nama (rata kiri)
    tag_name = "name_tag"
    chat_log.insert(tk.END, f"\n{who}:\n", tag_name)

    # Sisipkan pesan, kalau user rata kanan, kalau bot rata kiri
    tag_msg = "msg_tag_user" if who == "kenan" else "msg_tag_bot"
    chat_log.insert(tk.END, msg + "\n", tag_msg)

    chat_log.configure(state='disabled')
    chat_log.see(tk.END)

def kirim():
    user_input = entry.get().strip()
    if not user_input:
        return
    insert_message("INQUILINE", user_input)
    entry.delete(0, tk.END)

    jawaban = cari_jawaban(user_input)
    if jawaban.startswith("(Dari PDF)"):
        insert_message("BOT", jawaban.replace("(Dari PDF) ", ""))
    else:
        insert_message("BOT", jawaban)

entry.bind("<Return>", lambda event: kirim())

# Setelah definisi chat_log, tambahkan konfigurasi tag:

chat_log.tag_configure("name_tag", foreground="#CCCCCC", font=("Segoe UI", 9, "bold"), justify="left")
chat_log.tag_configure("msg_tag_user", foreground="#A9D6FF", font=("Segoe UI", 11), justify="right", lmargin1=50, rmargin=10)
chat_log.tag_configure("msg_tag_bot", foreground="#E0E0E0", font=("Segoe UI", 11), justify="left", lmargin1=10, rmargin=50)

kirim_button = tk.Button(input_frame, text="Kirim", command=kirim, bg="#0078D7", fg="white", font=("Segoe UI", 10, "bold"))
kirim_button.pack(side=tk.RIGHT)

load_pdf_button = tk.Button(root, text="Load PDF", command=load_pdf, bg="#333333", fg="white", font=("Segoe UI", 10))
load_pdf_button.pack(padx=10, pady=(0,10), anchor="e")

root.mainloop()
