import sqlite3
import os

#veritabani hatalarini ayiklama:
class DatabaseError(Exception):
    pass

#veritabani islerimlerinin hepsi burada:
class DatabaseManager:

    def __init__(self, db_path: str = "output.db"): #sinif olusturulunca otomatik acilir
        self.db_path = db_path #veritabani dosyasinin yolu
        self.conn = None

    def connect(self): #veritabanina baglanir
        try:#hata olusursa diye deniyoruz
            self.conn = sqlite3.connect(self.db_path)#sqlite dosyasina bagliyoruz
            self.conn.execute("PRAGMA foreign_keys = ON;")#foreign key default olarak kapali onu elle aciyoruz
        except sqlite3.Error as e:
            raise DatabaseError(f"Veritabanına bağlanılamadı: {e}")#hata olursa exception yapiyrz

    def close(self):#baglanti varsa baglantiyi kapatiyoruz
        if self.conn:
            self.conn.close()
            self.conn = None

    def _ensure_connected(self):#baglanti yoksa otomatik baglanir
        if self.conn is None:
            self.connect()

    def execute_script(self, create_statements: list, insert_statements: list):
        #tabloları olusturma ve veri ekleme
        self._ensure_connected()
        cursor = self.conn.cursor()#sql komutlari bu sekilde gonderir

        try:
            cursor.execute("BEGIN;")

            for sql in create_statements:#create table komutu
                cursor.execute(sql)

            for sql in insert_statements:#veri ekleme islemi
                cursor.execute(sql)

            self.conn.commit()#degisiklikleri kalici yapiyor

        except sqlite3.Error as e:#calisirken hata olursa degisiklikler geri alinir
            self.conn.rollback()
            raise DatabaseError(
                f"SQL calistirilirken hata olustu, tum degisiklikler geri alindi: {e}"
            )

    def list_tables(self) -> list:#tablolari listeler
        self._ensure_connected()
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master "#tablolar indexler viewlar burada tutulur
            "WHERE type='table' AND name NOT LIKE 'sqlite_%' "#sqlitein kendi tablolarini gizler
            #sadece bizim tablolarimizi gorunur hale getirir
            "ORDER BY name;"
        )
        return [row[0] for row in cursor.fetchall()]

    def get_table_columns(self, table_name: str) -> list:
        self._ensure_connected()
        cursor = self.conn.cursor()
        safe_name = table_name.replace('"', '""')
        cursor.execute(f'PRAGMA table_info("{safe_name}");')
        return [row[1] for row in cursor.fetchall()]

    def fetch_table_rows(self, table_name: str) -> list:
        self._ensure_connected()
        cursor = self.conn.cursor()
        safe_name = table_name.replace('"', '""')
        cursor.execute(f'SELECT * FROM "{safe_name}";')
        return cursor.fetchall()

    def drop_all_tables(self):
        self._ensure_connected()
        cursor = self.conn.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys = OFF;") #tablolar birbirine bagli olabilecegi icin kapatiyoruz
            tables = self.list_tables()
            cursor.execute("BEGIN;")
            for t in tables:
                safe_name = t.replace('"', '""')
                cursor.execute(f'DROP TABLE IF EXISTS "{safe_name}";')
            self.conn.commit()
            cursor.execute("PRAGMA foreign_keys = ON;")
        except sqlite3.Error as e:
            self.conn.rollback()
            raise DatabaseError(f"Tablolar silinirken hata olustu: {e}")

    def print_all_tables(self):
        tables = self.list_tables()
        if not tables:
            print("(Veritabani bos)")
            return

        for t in tables:
            cols = self.get_table_columns(t)
            rows = self.fetch_table_rows(t)
            print(f"\n[TABLE] {t}")
            print("  Columns: " + ", ".join(cols))
            print(f"  Rows ({len(rows)}):")
            for r in rows:
                print(f"    {r}")