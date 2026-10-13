# 📜 MODELING GOVERNANCE, ENGINEERING RULES & CODING STANDARDS
### *Sistem Prediksi Karhutla Indonesia (IndoWildfire-AI)*

Dokumen ini mendefinisikan aturan baku (*mandatory rules*), batasan metodologis, dan standar rekayasa perangkat lunak yang **wajib dipatuhi** oleh setiap pengembang, peneliti data, dan agen AI dalam mengembangkan model dan pipeline Karhutla.

---

## 🚫 1. Aturan Anti-Kebocoran Data (Zero-Leakage Temporal Rules)

### 🔴 ATURAN 1.1: Pengacakan Waktu (*Shuffling*) Dilarang Keras
* **Ketetapan:** Fungsi `train_test_split(..., shuffle=True)` atau `KFold(shuffle=True)` **DILARANG KERAS** digunakan pada dataset spatiotemporal.
* **Rasional Ilmiah:** Kebakaran hutan memiliki dependensi temporal yang sangat kuat (musim kemarau, fenomena El-Niño). Pengacakan baris akan membocorkan kondisi cuaca masa depan ke dalam data latih masa lalu (*lookahead bias*), menghasilkan evaluasi performa yang overoptimistis secara palsu.
* **Protokol Wajib:**
  ```python
  # BENAR: Pemisahan Berurutan Kronologis
  train_df = df[df['year'] <= 2022]
  val_df   = df[df['year'] == 2023]
  test_df  = df[df['year'].isin([2024, 2025])]
  live_df  = df[df['year'] == 2026]
  ```

### 🔴 ATURAN 1.2: Isolasi Fitur Spasial Tetangga (*Spatial Contiguity Lag*)
* **Ketetapan:** Fitur autokorelasi spasial sel sekitar (seperti `neighbor_fire_count`) **WAJIB** dihitung dari langkah waktu sebelumnya ($t-1$ atau $t-2$), bukan langkah waktu yang sama ($t$).
* **Rasional:** Menggunakan titik api tetangga pada bulan yang sama untuk memprediksi kebakaran bulan yang sama adalah kebocoran kontemporer (*contemporaneous leakage*).

### 🔴 ATURAN 1.3: Fitting Preprocessing Hanya pada Data Latih
* **Ketetapan:** Semua objek `StandardScaler`, `MinMaxScaler`, `OneHotEncoder`, dan `SimpleImputer` **HANYA BOLEH di-`fit()` pada training set**, kemudian di-`transform()` pada validation dan test set.
* **Pelanggaran:** Melakukan `.fit_transform()` pada seluruh dataframe sebelum pembagian data dikategorikan sebagai pelanggaran kritis.

---

## 📊 2. Aturan Integritas Metrik Evaluasi (Evaluation Integrity Rules)

### 🔴 ATURAN 2.1: Larangan Menggunakan Akurasi Standar (*Standard Accuracy Ban*)
* **Ketetapan:** Metrik akurasi standar (`accuracy_score`) **DILARANG** dijadikan metrik utama penentu keputusan pemilihan model.
* **Rasional:** Karena proporsi kejadian kebakaran adalah peristiwa langka (*rare event*, kelas positif $< 10\%$), model bodoh yang selalu memprediksi `0` (tidak ada api) akan menghasilkan akurasi $> 90\%$, namun gagal total menangkap bencana kebakaran aktual.

### 🟢 ATURAN 2.2: Metrik Wajib untuk Data Tidak Seimbang (*Imbalanced Metrics*)
Setiap eksperimen pemodelan wajib melaporkan hierarki 4 metrik berikut:
1. **PR-AUC (Precision-Recall AUC / Average Precision):** Metrik primer untuk mengukur trade-off precision vs recall tanpa bias dominasi true negative.
2. **Recall @ Top 20% Risk Ranking (Kapasitas Operasional):** Mengukur berapa persen kebakaran aktual yang berhasil ditangkap jika patroli Manggala Agni hanya mendatangi 20% sel berisiko tertinggi.
3. **Brier Score (Kalibrasi Probabilitas):** Memverifikasi bahwa nilai probabilitas yang dihasilkan model merepresentasikan frekuensi empiris sebenarnya (terkalibrasi, bukan sekadar skor acak).
4. **ROC-AUC:** Untuk mengukur kemampuan diskriminasi global sel aman vs berisiko.

---

## 🌲 3. Batasan Domain Fisika Gambut & Iklim (Domain Physics Constraints)

### 🟢 ATURAN 3.1: Prioritas Fitur Gambut & Kelembapan Tanah
* **Ketetapan:** Fitur tutupan kubah gambut (`peat_fraction`) dan kelembapan volumetrik tanah lapisan akar (`soil_moisture`) **TIDAK BOLEH DIHILANGKAN** dari seleksi fitur (*feature selection*).
* **Fisika Kebakaran:** Lebih dari 95% emisi jelaga dan kebakaran membara bawah tanah (*smoldering*) terjadi pada gambut dalam. Kelembapan tanah $< 0.25 \, \text{m}^3/\text{m}^3$ dan kelembapan relatif $< 65\%$ merupakan batas kritis penentu pembakaran gambut (*tipping point*).

### 🟢 ATURAN 3.2: Penanganan Nilai Ekstrem Curah Hujan
* Curah hujan tidak boleh dinormalisasi secara simetris biasa; gunakan transformasi logaritmik $\log(1 + \text{precipitation})$ atau akumulasi defisit kekeringan berturut-turut (*consecutive dry days / CDD*).

---

## 🔐 4. Aturan Keamanan, Kredensial & Manajemen Data (Security & Data Governance)

### 🔴 ATURAN 4.1: Larangan Keras Hardcoding Kredensial & Kunci API
* **Ketetapan:** API Key (NASA FIRMS `MAP_KEY`, Hugging Face Access Token `hf_...`, GitHub Token `ghp_...`) **DILARANG KERAS** ditulis langsung ke dalam berkas kode sumber (*scripts, notebooks, configs*).
* **Standar Implementasi:** Wajib dibaca melalui *Environment Variables* atau file `.env` yang terisolasi:
  ```python
  nasa_api_key = os.getenv("NASA_FIRMS_MAP_KEY", "")
  ```

### 🔴 ATURAN 4.2: Manajemen Berkas Besar & Git LFS
* Berkas biner model (`.pkl`, `.joblib`, `.pth`) dan dataset biner berukuran $> 50 \text{ MB}$ **WAJIB** dimasukkan ke dalam `.gitignore` atau dikelola melalui Git LFS. Repositori GitHub utama tidak boleh membengkak oleh file dump biner.

### 🟢 ATURAN 4.3: Kepatuhan Atribusi Data Pihak Ketiga
Setiap publikasi ilmiah, visualisasi dashboard, dan laporan analitis wajib mencantumkan sumber resmi:
* **NASA FIRMS:** *"NASA Earth Observing System Data and Information System (EOSDIS) / LANCE FIRMS"*.
* **ERA5 Reanalysis:** *"ECMWF ERA5-Land Reanalysis data via Open-Meteo"*.
* **SiPongi+:** *"Kementerian Lingkungan Hidup dan Kehutanan (KLHK) Republik Indonesia"*.
* **Indonesian Wildfire Panel:** *"Indonesian Wildfire Panel Dataset (2012–2025), CC BY 4.0"*.

---

## 💻 5. Standar Rekayasa Kode (Software Engineering & Reproducibility)

1. **Deterministik & Reproduktif:** Semua generator angka acak wajib mengunci seed eksplisit (`random_state=42`, `np.random.seed(42)`).
2. **Ketik Anotasi (*Type Hinting*):** Semua fungsi dan metode di modul `src/` wajib menyertakan anotasi tipe data Python (`typing.Dict`, `typing.Optional`, `typing.Tuple`).
3. **Penyimpanan Format Kolom:** Semua data keluaran tabular perantara wajib disimpan dalam format **Apache Parquet (Snappy Compressed)** untuk menjamin kecepatan I/O dan penghematan memori RAM.
4. **Validasi Skema Runtime:** Data input dari live stream 2026 wajib lolos validasi model `Pydantic` sebelum disuntikkan ke mesin inferensi model.
