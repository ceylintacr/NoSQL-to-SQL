import json
import os


class JsonLoadError(Exception):
    pass


class JsonLoader:

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data = None

    #json dosyasını okuyup döndürüyoruz.
    def load(self):
        #Dosya var mı?
        if not os.path.exists(self.file_path):
            raise JsonLoadError(f"Dosya bulunamadı: {self.file_path}")

        #Bir dosya mı?
        if not os.path.isfile(self.file_path):
            raise JsonLoadError(f"Verilen yol bir dosya değil: {self.file_path}")

        #Uzantı kontrolü
        if not self.file_path.lower().endswith(".json"):
            print(f"[UYARI] Dosya .json uzantılı değil: {self.file_path}")

        #Dosyayı oku ve parse et
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except json.JSONDecodeError as e:
            raise JsonLoadError(
                f"Geçersiz JSON formatı (satır {e.lineno}, sütun {e.colno}): {e.msg}"
            )
        except UnicodeDecodeError as e:
            raise JsonLoadError(f"Dosya UTF-8 olarak okunamadı: {e}")
        except OSError as e:
            raise JsonLoadError(f"Dosya okunurken sistem hatası: {e}")

        return self.data

    #şema analizer için nesne mi array mi onu alıyoruz.
    def get_root_type(self) -> str:
        if self.data is None:
            raise JsonLoadError("Önce load() metodunu çağırmalısınız.")

        if isinstance(self.data, dict):
            return "object"
        elif isinstance(self.data, list):
            return "array"
        else:
            return "primitive"

    #indentli şekilde yazdırma işlemi (alt alta olan verileri düzenliyoruz.)
    def pretty_print(self) -> str:
        if self.data is None:
            raise JsonLoadError("Önce load() metodunu çağırmalısınız.")

        return json.dumps(self.data, indent=2, ensure_ascii=False)