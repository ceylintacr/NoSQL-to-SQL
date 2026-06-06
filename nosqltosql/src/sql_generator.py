from src.schema_analyzer import TableSchema, ColumnSchema


class SqlGenerator:

    def __init__(self, tables: dict):
        self.tables = tables

    @staticmethod
    def _quote_ident(name: str) -> str:
        escaped = name.replace('"', '""')
        return f'"{escaped}"'

    @staticmethod
    def _format_value(value) -> str:
        if value is None:
            return "NULL"
        if isinstance(value, bool):
            return "1" if value else "0"
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, str):
            escaped = value.replace("'", "''")
            return f"'{escaped}'"
        return f"'{str(value).replace(chr(39), chr(39)*2)}'"

    def generate_create_statements(self) -> list:
        ordered_tables = self._topological_sort()
        statements = []
        for table in ordered_tables:
            statements.append(self._build_create_table(table))
        return statements

    def _build_create_table(self, table: TableSchema) -> str:
        """Tek bir tablo için CREATE TABLE cümlesi üretir."""
        lines = []
        column_defs = []
        foreign_keys = []

        for col in table.columns.values():
            col_def = self._build_column_def(col)
            column_defs.append(col_def)

            if col.is_foreign_key and col.references_table:
                fk_line = (
                    f'FOREIGN KEY ({self._quote_ident(col.name)}) '
                    f'REFERENCES {self._quote_ident(col.references_table)}'
                    f'("id_pk")'
                )
                foreign_keys.append(fk_line)

        all_lines = column_defs + foreign_keys
        body = ",\n    ".join(all_lines)

        sql = (
            f'CREATE TABLE IF NOT EXISTS {self._quote_ident(table.name)} (\n'
            f'    {body}\n'
            f');'
        )
        return sql

    def _build_column_def(self, col: ColumnSchema) -> str:
        parts = [self._quote_ident(col.name), col.sql_type]
        if col.is_primary_key:
            parts.append("PRIMARY KEY")
        return " ".join(parts)

    def generate_insert_statements(self) -> list:
        ordered_tables = self._topological_sort()
        statements = []
        for table in ordered_tables:
            for row in table.rows:
                statements.append(self._build_insert(table, row))
        return statements

    def _build_insert(self, table: TableSchema, row: dict) -> str:
        col_names = []
        values = []
        for col_name in table.columns.keys():
            if col_name in row:
                col_names.append(self._quote_ident(col_name))
                values.append(self._format_value(row[col_name]))

        cols_str = ", ".join(col_names)
        vals_str = ", ".join(values)
        return (
            f'INSERT INTO {self._quote_ident(table.name)} '
            f'({cols_str}) VALUES ({vals_str});'
        )

    def _topological_sort(self) -> list:
        remaining = dict(self.tables)
        ordered = []
        added_names = set()

        max_iters = len(remaining) ** 2 + 10
        iters = 0

        while remaining and iters < max_iters:
            iters += 1
            progress = False
            for name, table in list(remaining.items()):
                if table.parent_table is None or table.parent_table in added_names:
                    ordered.append(table)
                    added_names.add(name)
                    del remaining[name]
                    progress = True
            if not progress:
                for table in remaining.values():
                    ordered.append(table)
                break

        return ordered
    
    def print_all_sql(self):
        """Üretilen tüm SQL'i okunabilir formatta yazdırır."""
        print("\n" + "=" * 70)
        print("CREATE TABLE STATEMENTS")
        print("=" * 70)
        for sql in self.generate_create_statements():
            print(sql)
            print()

        print("=" * 70)
        print("INSERT INTO STATEMENTS")
        print("=" * 70)
        for sql in self.generate_insert_statements():
            print(sql)