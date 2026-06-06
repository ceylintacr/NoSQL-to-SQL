# 🔄 NoSQL to SQL Converter

Bu proje, karmaşık yapıdaki NoSQL (JSON) veri dosyalarını analiz ederek otomatik olarak ilişkisel SQL (SQLite3) veritabanı tablolarına dönüştüren kullanıcı dostu bir masaüstü uygulamasıdır.

## 🌟 Özellikler

- 📁 **JSON İçe Aktarma:** İç içe geçmiş (nested) veya düz JSON dosyalarını sorunsuz okuma.
- 🔍 **Şema Analizi:** JSON verisinin yapısını otomatik olarak çözümleme ve tablolar arası ilişkileri belirleme.
- 🧠 **Veri Tipi Çıkarımı (Type Inference):** JSON içerisindeki verileri analiz ederek en uygun SQL veri tiplerini (INTEGER, TEXT, REAL vb.) otomatik atama.
- ⚙️ **Dinamik SQL Üretimi:** Analiz edilen şemaya uygun `CREATE TABLE` ve `INSERT INTO` sorgularını dinamik olarak oluşturma.
- 🗄️ **SQLite Entegrasyonu:** Dönüştürülen verileri doğrudan bir `.db` dosyası olarak kaydetme.
- 🖥️ **Kullanıcı Dostu Arayüz (GUI):** Tüm işlemleri tek bir tıkla yapabileceğiniz, şık ve modern grafiksel arayüz.

## 📂 Proje Yapısı

Proje modüler bir mimariyle tasarlanmıştır:

```text
├── main.py                  # Uygulamayı başlatan ana dosya
├── src/                     # Kaynak kodlar
│   ├── gui.py               # Grafiksel kullanıcı arayüzü (Arayüz ve stillendirme)
│   ├── json_loader.py       # JSON dosyalarını okuma ve parse etme
│   ├── schema_analyzer.py   # JSON yapısını SQL mantığına (normalizasyon) göre analiz etme
│   ├── type_inferencer.py   # SQL veri tiplerini otomatik belirleme
│   ├── sql_generator.py     # SQL sorgularını oluşturma
│   └── database_manager.py  # SQLite3 veritabanı bağlantısı ve işlemleri
├── test_data/               # Test için örnek JSON dosyaları (Edge cases, nested vb.)
└── output.db                # Çıktı olarak üretilen örnek veritabanı dosyası
