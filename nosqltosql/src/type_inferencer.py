class TypeInferencer:
    SQL_INTEGER = "INTEGER"
    SQL_REAL = "REAL"
    SQL_TEXT = "TEXT"
    SQL_NULL = "NULL" 
    #verinin tipini belirlemek için tipleri define ettik.

    #iki farklı tip ile karşılaşınca hangisinin baskın olacağını belirlemek için sıra
    _TYPE_RANK = {
        SQL_NULL: 0,
        SQL_INTEGER: 1,
        SQL_REAL: 2,
        SQL_TEXT: 3,
    }

    #tipi belirliyoruz.
    @staticmethod
    def infer(value) -> str:
        if value is None:
            return TypeInferencer.SQL_NULL
        if isinstance(value, bool):
            return TypeInferencer.SQL_INTEGER
        if isinstance(value, int):
            return TypeInferencer.SQL_INTEGER
        if isinstance(value, float):
            return TypeInferencer.SQL_REAL
        if isinstance(value, str):
            return TypeInferencer.SQL_TEXT
        return TypeInferencer.SQL_TEXT

    #baskın olanı seçiyoruz
    @staticmethod
    def promote(type_a: str, type_b: str) -> str:
        rank_a = TypeInferencer._TYPE_RANK.get(type_a, 3)
        rank_b = TypeInferencer._TYPE_RANK.get(type_b, 3)

        if rank_a >= rank_b:
            return type_a
        return type_b

    #listenin tamamına bakıp tip belirliyoruz (baskınlığa göre)
    @staticmethod
    def infer_from_list(values: list) -> str:
        if not values:
            return TypeInferencer.SQL_NULL

        current_type = TypeInferencer.SQL_NULL
        for v in values:
            v_type = TypeInferencer.infer(v)
            current_type = TypeInferencer.promote(current_type, v_type)

        return current_type

    #son olarak sütunu oluştururken hangi tipi kullanacağımızı döndürür. NULL ise text döndürüyoruz!!
    @staticmethod
    def finalize(inferred_type: str) -> str:
        if inferred_type == TypeInferencer.SQL_NULL:
            return TypeInferencer.SQL_TEXT
        return inferred_type