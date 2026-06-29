# Menggunakan pondasi sistem operasi Linux + Python yang ringan
FROM python:3.10-slim

# Menentukan ruang kerja di dalam peti kemas
WORKDIR /app

# Menyalin daftar pustaka dan menginstalnya
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Menyalin seluruh kodingan Anda ke dalam peti kemas
COPY . .

# Membuka port 8000
EXPOSE 8000

# Perintah otomatis untuk menjalankan server saat peti kemas dihidupkan
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]