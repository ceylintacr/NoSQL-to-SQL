# 🔄 NoSQL to SQL Dinamik Dönüştürücü Motoru

Bu proje, yapısı ve derinliği önceden bilinmeyen karmaşık NoSQL (JSON) verilerini çalışma zamanında (runtime) analiz ederek, otonom bir şekilde normalize edilmiş ilişkisel SQL veritabanlarına dönüştüren dinamik bir dönüştürücü motorudur. 

Sabit (hardcoded) bir yapıya bağlı kalmadan, esnek ve şemasız (schema-less) veri modellerini katı kurallı SQL şemalarına çevirmek için gelişmiş algoritmik çözümleme (parsing) yöntemleri kullanır.

## 🌟 Temel Özellikler

- **Dinamik Şema Çözümleme:** Derinliği veya içerdiği alanlar önceden bilinmeyen JSON dosyalarını okuyarak veri tiplerini (metin, sayı, boolean, obje, dizi) otomatik algılar.
- **Otomatik Düzleştirme (Flattening):** İç içe geçmiş alt objeleri (nested objects) SQL yapısına uygun hale getirmek için ebeveyn-çocuk anahtarlarını birleştirerek (örn: `adres_sehir`, `adres_ilce`) düzleştirir.
- **Akıllı Dizi (Array) Yönetimi:** JSON içindeki dizileri tespit ettiğinde işlemi durdurur, bu verileri ana tabloya sıkıştırmak yerine otomatik olarak **yeni alt tablolar (child tables)** oluşturur.
- **Otomatik İlişki Kurma:** Ana tablolar ile alt tablolar arasında veri bütünlüğünü sağlamak için dinamik olarak **Primary Key** ve **Foreign Key** (1:N - Bire Çok) bağlantıları kurar.
- **Jenerik SQL Yürütme:** Sanal tablo taslaklarını gerçek zamanlı olarak `CREATE TABLE` ve `INSERT INTO` sorgularına dönüştürüp SQLite veritabanında çalıştırır.

## 🧠 Normalizasyon Standartları
Proje motoru, veritabanı oluştururken ilişkisel veritabanı tasarım standartlarını (Normal Formlar) otonom olarak uygular:
* **1NF (Birinci Normal Form):** Diziler (array) tespit edildiğinde atomik veri kuralını sağlamak için veriler alt tablolara ayrıştırılır ve her eleman yeni bir satır olarak işlenir.
* **2NF (İkinci Normal Form):** Üretilen her tabloya otomatik bir Birincil Anahtar (Primary Key) atanır ve verilerin anahtara tam bağımlılığı sağlanır.
* **3NF (Üçüncü Normal Form):** 5-6 katman derinliğe kadar inebilen verilerde geçişli bağımlılıklar (transitive dependency) tespit edilir ve veri tekrarını önlemek için hiyerarşik Foreign Key yapılarıyla alt tablolara bölünür.

## 🖥️ Kullanıcı Arayüzü (GUI) Modülleri

Sistem, dönüşüm işlemlerini kolaylaştıran modern bir masaüstü arayüzüne sahiptir:
* **Hiyerarşik Ağaç Görünümü (Tree View):** Sisteme yüklenen karmaşık JSON dosyasının hiyerarşisi, okunabilir bir ağaç yapısında veya formatlı metin (pretty-print) olarak kullanıcıya sunulur.
* **DataGrid Gösterimi:** Dönüşüm tamamlandıktan sonra, arka planda dinamik olarak üretilen SQL tabloları ve içerikleri arayüz üzerinden incelenebilir.
* **Sistem Sıfırlama (Reset):** Yeni bir JSON test etmek için mevcut veritabanındaki tüm tabloları silen (`DROP TABLE`) ve ortamı temizleyen tek tıkla sıfırlama özelliği bulunur.

## 📂 Mimari Akış ve Çalışma Prensibi

1. **Parsing (Veri Okuma):** JSON dosyasının belleğe alınması ve anahtar-değer ilişkilerinin çıkarılması.
2. **Tablo Tasarımı:** Basit veri tiplerinin sütunlaştırılması ve alt objelerin (nested) düzleştirilmesi.
3. **İlişki Kurulumu:** Dizilerin ayrıştırılıp alt tabloların ve Foreign Key bağlantılarının oluşturulması.
4. **Execution (Yürütme):** Sorguların dinamik olarak üretilmesi ve `.db` dosyasına verilerin yazılması.

## 🚀 Kurulum ve Kullanım

1. **Projeyi Klonlayın:**
   ```bash
   git clone [https://github.com/KULLANICI_ADIN/PROJE_ADIN.git](https://github.com/KULLANICI_ADIN/PROJE_ADIN.git)
