import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.font import Font

#bizim yazdığımız sınıftan import ediyoruz
from src.json_loader import JsonLoader, JsonLoadError
from src.schema_analyzer import SchemaAnalyzer
from src.sql_generator import SqlGenerator
from src.database_manager import DatabaseManager, DatabaseError

DB_PATH = "output.db"

class Palette:
    BG_MAIN       = "#F0F4F8"   # Ana arka plan
    BG_PANEL      = "#FFFFFF"   # Panel arka planı
    BG_HEADER     = "#2C8282"   # Koyu mavi başlık
    BG_ROW_ALT    = "#EDF2F7"   # Çift satır vurgusu

    BTN_PRIMARY   = "#31A9CE"   # Dosya Seç
    BTN_PRIMARY_H = "#2C5282"   # Basık tuş
    BTN_SUCCESS   = "#38A169"   # Dönüştür
    BTN_SUCCESS_H = "#2F855A"
    BTN_DANGER    = "#E53E3E"   # Sıfırla
    BTN_DANGER_H  = "#C53030"
    BTN_DISABLED  = "#A0AEC0"   # Pasif buton

    TXT_DARK      = "#1A202C"
    TXT_MUTED     = "#4A5568"
    TXT_LIGHT     = "#FFFFFF"

    BORDER        = "#CBD5E0"
    SELECTION     = "#BEE3F8"

#programı burada oluşturuyoruz.
class ConverterApp:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("NoSQL'den SQL'e Dönüşüm Sistemi")
        self.root.geometry("1200x700")
        self.root.configure(bg=Palette.BG_MAIN)
        self.root.minsize(900, 550)

        self.current_file = None
        self.current_data = None
        self.db = DatabaseManager(DB_PATH)
        self.db.connect()

        self._apply_theme()

        self._build_header()
        self._build_toolbar()
        self._build_main_area()
        self._build_status_bar()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._refresh_db_view()

    #arayüzü oluşturduğumuz kısım
    def _apply_theme(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        self.font_title   = Font(family="Segoe UI", size=14, weight="bold")
        self.font_normal  = Font(family="Segoe UI", size=10)
        self.font_bold    = Font(family="Segoe UI", size=10, weight="bold")
        self.font_small   = Font(family="Segoe UI", size=9)

        style.configure("Panel.TLabelframe",
                        background=Palette.BG_PANEL,
                        borderwidth=1,
                        relief="solid",
                        bordercolor=Palette.BORDER)
        style.configure("Panel.TLabelframe.Label",
                        background=Palette.BG_PANEL,
                        foreground=Palette.BG_HEADER,
                        font=self.font_bold)

        style.configure("Main.TFrame", background=Palette.BG_MAIN)
        style.configure("Panel.TFrame", background=Palette.BG_PANEL)
        style.configure("Header.TFrame", background=Palette.BG_HEADER)
        style.configure("Toolbar.TFrame", background=Palette.BG_MAIN)

        style.configure("Header.TLabel",
                        background=Palette.BG_HEADER,
                        foreground=Palette.TXT_LIGHT,
                        font=self.font_title,
                        padding=12)
        style.configure("Toolbar.TLabel",
                        background=Palette.BG_MAIN,
                        foreground=Palette.TXT_MUTED,
                        font=self.font_normal)
        style.configure("ToolbarFile.TLabel",
                        background=Palette.BG_MAIN,
                        foreground=Palette.TXT_DARK,
                        font=self.font_bold)
        style.configure("Status.TLabel",
                        background=Palette.BG_HEADER,
                        foreground=Palette.TXT_LIGHT,
                        font=self.font_small,
                        padding=6)

        def make_button(name, bg, bg_hover):
            style.configure(name,
                            background=bg,
                            foreground=Palette.TXT_LIGHT,
                            font=self.font_bold,
                            padding=(14, 8),
                            borderwidth=0,
                            relief="flat",
                            focuscolor=bg)
            style.map(name,
                      background=[("active", bg_hover),
                                  ("disabled", Palette.BTN_DISABLED)],
                      foreground=[("disabled", "#E2E8F0")])

        make_button("Primary.TButton", Palette.BTN_PRIMARY, Palette.BTN_PRIMARY_H)
        make_button("Success.TButton", Palette.BTN_SUCCESS, Palette.BTN_SUCCESS_H)
        make_button("Danger.TButton",  Palette.BTN_DANGER,  Palette.BTN_DANGER_H)

        style.configure("Custom.TNotebook",
                        background=Palette.BG_PANEL,
                        borderwidth=0)
        style.configure("Custom.TNotebook.Tab",
                        background=Palette.BG_ROW_ALT,
                        foreground=Palette.TXT_MUTED,
                        padding=(14, 7),
                        font=self.font_normal,
                        borderwidth=0)
        style.map("Custom.TNotebook.Tab",
                  background=[("selected", Palette.BG_HEADER),
                              ("active",   Palette.BTN_PRIMARY)],
                  foreground=[("selected", Palette.TXT_LIGHT),
                              ("active",   Palette.TXT_LIGHT)])

        style.configure("Custom.Treeview",
                        background=Palette.BG_PANEL,
                        fieldbackground=Palette.BG_PANEL,
                        foreground=Palette.TXT_DARK,
                        rowheight=26,
                        font=self.font_normal,
                        borderwidth=0)
        style.configure("Custom.Treeview.Heading",
                        background=Palette.BG_HEADER,
                        foreground=Palette.TXT_LIGHT,
                        font=self.font_bold,
                        padding=6,
                        relief="flat")
        style.map("Custom.Treeview",
                  background=[("selected", Palette.SELECTION)],
                  foreground=[("selected", Palette.TXT_DARK)])
        style.map("Custom.Treeview.Heading",
                  background=[("active", Palette.BTN_PRIMARY)])

        style.configure("Custom.Vertical.TScrollbar",
                        background=Palette.BG_PANEL,
                        troughcolor=Palette.BG_MAIN,
                        bordercolor=Palette.BG_PANEL,
                        arrowcolor=Palette.TXT_MUTED)
        style.configure("Custom.Horizontal.TScrollbar",
                        background=Palette.BG_PANEL,
                        troughcolor=Palette.BG_MAIN,
                        bordercolor=Palette.BG_PANEL,
                        arrowcolor=Palette.TXT_MUTED)

        style.configure("TPanedwindow", background=Palette.BG_MAIN)
        style.configure("Sash", background=Palette.BORDER, gripcount=0)

    #başlıkları oluşturuyoruz
    def _build_header(self):
        header = ttk.Frame(self.root, style="Header.TFrame")
        header.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(header,
                  text="🗄  NoSQL → SQL Dönüşüm Sistemi",
                  style="Header.TLabel").pack(side=tk.LEFT, padx=8)

    #butonlarımızın oluduğu kısım
    def _build_toolbar(self):
        toolbar = ttk.Frame(self.root, style="Toolbar.TFrame", padding=10)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        self.btn_load = ttk.Button(
            toolbar, text="📂  Dosya Seç",
            style="Primary.TButton", command=self._on_load_file
        )
        self.btn_load.pack(side=tk.LEFT, padx=4)

        self.btn_convert = ttk.Button(
            toolbar, text="⚙  Dönüştür",
            style="Success.TButton", command=self._on_convert,
            state=tk.DISABLED
        )
        self.btn_convert.pack(side=tk.LEFT, padx=4)

        self.btn_reset = ttk.Button(
            toolbar, text="🗑  Sıfırla",
            style="Danger.TButton", command=self._on_reset
        )
        self.btn_reset.pack(side=tk.LEFT, padx=4)

        self.lbl_file = ttk.Label(
            toolbar,
            text="(Henüz dosya seçilmedi)",
            style="Toolbar.TLabel"
        )
        self.lbl_file.pack(side=tk.LEFT, padx=20)

    #arayüzü iki kısma bölüyoruz
    def _build_main_area(self):
        main = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=4)

        #burada kjson içeriği ağaç gibi gösteriliyor.
        left_frame = ttk.LabelFrame(main, text="  JSON İçeriği (Ağaç Görünümü)  ",
                                    style="Panel.TLabelframe", padding=6)
        main.add(left_frame, weight=1)

        self.json_tree = ttk.Treeview(left_frame, columns=("value",),
                                      show="tree headings",
                                      style="Custom.Treeview")
        self.json_tree.heading("#0", text="Anahtar / Yapı")
        self.json_tree.heading("value", text="Değer")
        self.json_tree.column("#0", width=260, anchor=tk.W)
        self.json_tree.column("value", width=220, anchor=tk.W)

        self.json_tree.tag_configure("odd",  background=Palette.BG_PANEL)
        self.json_tree.tag_configure("even", background=Palette.BG_ROW_ALT)

        json_scroll = ttk.Scrollbar(left_frame, orient=tk.VERTICAL,
                                    command=self.json_tree.yview,
                                    style="Custom.Vertical.TScrollbar")
        self.json_tree.configure(yscroll=json_scroll.set)
        self.json_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        json_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        #oluşturulan tablolar sağda gösteriliyor
        right_frame = ttk.LabelFrame(main, text="  Oluşturulan SQL Tabloları  ",
                                     style="Panel.TLabelframe", padding=6)
        main.add(right_frame, weight=2)

        self.tables_notebook = ttk.Notebook(right_frame, style="Custom.TNotebook")
        self.tables_notebook.pack(fill=tk.BOTH, expand=True)

    #alttaki durum çubuğu
    def _build_status_bar(self):
        self.status_var = tk.StringVar(value="Hazır.")
        status = ttk.Label(self.root, textvariable=self.status_var,
                           style="Status.TLabel", anchor=tk.W)
        status.pack(side=tk.BOTTOM, fill=tk.X)

    #dosya seçme işlemleri (hazır kütüphaneden kullandık)
    def _on_load_file(self):
        path = filedialog.askopenfilename(
            title="Bir JSON dosyası seçin",
            filetypes=[("JSON dosyaları", "*.json"), ("Tüm dosyalar", "*.*")]
        )
        if not path:
            return

        try:
            loader = JsonLoader(path)
            self.current_data = loader.load()
        except JsonLoadError as e:
            messagebox.showerror("JSON Yükleme Hatası", str(e))
            self.status_var.set("JSON yüklenemedi.")
            return

        self.current_file = path
        self.lbl_file.config(text=f"📄 {os.path.basename(path)}",
                             style="ToolbarFile.TLabel")
        self.btn_convert.config(state=tk.NORMAL)
        self.status_var.set(f"Yüklendi: {os.path.basename(path)}")

        self._populate_json_tree(self.current_data)

    #dönüştürme kısmı
    def _on_convert(self):
        if self.current_data is None:
            messagebox.showwarning("LÜTFEN", "Önce bir JSON dosyası yükleyin.")
            return

        try:
            self.db.drop_all_tables()
            analyzer = SchemaAnalyzer(root_table_name="root")#kendi şema analiz kodu
            analyzer.analyze(self.current_data)

            generator = SqlGenerator(analyzer.tables)#sqle çeviriyoruz
            creates = generator.generate_create_statements()
            inserts = generator.generate_insert_statements()

            self.db.execute_script(creates, inserts)

            self.status_var.set(
                f"✓  Dönüşüm tamamlandı: {len(analyzer.tables)} tablo, "
                f"{len(inserts)} satır eklendi."
            )
        except (JsonLoadError, DatabaseError) as e:
            messagebox.showerror("Dönüşüm Hatası", str(e))
            self.status_var.set("Dönüşüm başarısız.")
            return
        except Exception as e:
            messagebox.showerror("Beklenmeyen Hata", f"{type(e).__name__}: {e}")
            self.status_var.set("Dönüşüm başarısız.")
            return

        self._refresh_db_view()

    def _on_reset(self):
        confirm = messagebox.askyesno(
            "Sıfırlama Onayı",
            "Veritabanındaki TÜM tablolar silinecek. Emin misiniz?"
        )
        if not confirm:
            return

        try:
            self.db.drop_all_tables()
            self.status_var.set("Veritabanı sıfırlandı.")
        except DatabaseError as e:
            messagebox.showerror("Sıfırlama Hatası", str(e))
            return

        self._refresh_db_view()

    def _populate_json_tree(self, data):
        #eski verileri temizleyip sonra jsonı ekrana basıyoruz.
        for item in self.json_tree.get_children():
            self.json_tree.delete(item)

        self._row_counter = 0  # Çift/tek satır renkleri için
        self._insert_node(parent_id="", key="(root)", value=data)
        self._expand_all(self.json_tree)


    #Özyinelemeli olan fonksiyonumuz. Ağacı gezme algoritması
    def _insert_node(self, parent_id, key, value):
        tag = "even" if self._row_counter % 2 == 0 else "odd"
        self._row_counter += 1

        if isinstance(value, dict):
            node_id = self.json_tree.insert(
                parent_id, "end", text=str(key),
                values=(f"{{...}} ({len(value)} alan)",),
                tags=(tag,)
            )
            for k, v in value.items():
                self._insert_node(node_id, k, v)
        elif isinstance(value, list):
            node_id = self.json_tree.insert(
                parent_id, "end", text=str(key),
                values=(f"[...] ({len(value)} eleman)",),
                tags=(tag,)
            )
            for i, item in enumerate(value):
                self._insert_node(node_id, f"[{i}]", item)
        else:
            display = "null" if value is None else str(value)
            self.json_tree.insert(parent_id, "end", text=str(key),
                                  values=(display,),
                                  tags=(tag,))

    def _expand_all(self, tree, item=""):
        for child in tree.get_children(item):
            tree.item(child, open=True)
            self._expand_all(tree, child)

    def _refresh_db_view(self):
        for tab_id in self.tables_notebook.tabs():
            self.tables_notebook.forget(tab_id)

        try:
            table_names = self.db.list_tables()
        except DatabaseError as e:
            messagebox.showerror("Veritabanı Hatası", str(e))
            return

        if not table_names:
            empty_frame = ttk.Frame(self.tables_notebook, style="Panel.TFrame")
            tk.Label(empty_frame,
                     text="ℹ  Henüz tablo yok.\nBir JSON yükleyip 'Dönüştür' butonuna basın.",
                     bg=Palette.BG_PANEL,
                     fg=Palette.TXT_MUTED,
                     font=self.font_normal,
                     pady=40).pack(expand=True)
            self.tables_notebook.add(empty_frame, text="  —  ")
            return

        for table_name in table_names:
            self._add_table_tab(table_name)

    def _add_table_tab(self, table_name: str):
        frame = ttk.Frame(self.tables_notebook, style="Panel.TFrame")

        try:
            columns = self.db.get_table_columns(table_name)
            rows = self.db.fetch_table_rows(table_name)
        except DatabaseError as e:
            ttk.Label(frame, text=f"Hata: {e}",
                      background=Palette.BG_PANEL,
                      foreground=Palette.BTN_DANGER).pack()
            self.tables_notebook.add(frame, text=table_name)
            return

        tree = ttk.Treeview(frame, columns=columns, show="headings",
                            style="Custom.Treeview")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=130, anchor=tk.W)

        tree.tag_configure("odd",  background=Palette.BG_PANEL)
        tree.tag_configure("even", background=Palette.BG_ROW_ALT)

        for idx, row in enumerate(rows):
            display_row = tuple("NULL" if v is None else v for v in row)
            tag = "even" if idx % 2 == 0 else "odd"
            tree.insert("", "end", values=display_row, tags=(tag,))

        vsb = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview,
                            style="Custom.Vertical.TScrollbar")
        hsb = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=tree.xview,
                            style="Custom.Horizontal.TScrollbar")
        tree.configure(yscroll=vsb.set, xscroll=hsb.set)

        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        tab_label = f"  {table_name}  ({len(rows)})  "
        self.tables_notebook.add(frame, text=tab_label)

    def _on_close(self):
        try:
            self.db.close()
        except Exception:
            pass
        self.root.destroy()

def launch():
    root = tk.Tk()
    app = ConverterApp(root)
    root.mainloop()