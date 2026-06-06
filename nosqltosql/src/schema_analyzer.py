from src.type_inferencer import TypeInferencer

class ColumnSchema:
    def __init__(self, name: str, sql_type: str,
                 is_primary_key: bool = False,
                 is_foreign_key: bool = False,
                 references_table: str = None):
        self.name = name
        self.sql_type = sql_type
        self.is_primary_key = is_primary_key
        self.is_foreign_key = is_foreign_key
        self.references_table = references_table  

    def __repr__(self):
        flags = []
        if self.is_primary_key:
            flags.append("PK")
        if self.is_foreign_key:
            flags.append(f"FK->{self.references_table}")
        flag_str = f" [{', '.join(flags)}]" if flags else ""
        return f"{self.name}:{self.sql_type}{flag_str}"


class TableSchema:

    def __init__(self, name: str, parent_table: str = None):
        self.name = name
        self.parent_table = parent_table 
        self.columns = {}     
        self.rows = []       

        self.add_column(ColumnSchema(
            name="id_pk",
            sql_type=TypeInferencer.SQL_INTEGER,
            is_primary_key=True
        ))

        if parent_table:
            self.add_column(ColumnSchema(
                name=f"{parent_table}_fk",
                sql_type=TypeInferencer.SQL_INTEGER,
                is_foreign_key=True,
                references_table=parent_table
            ))

    def add_column(self, column: ColumnSchema):
        if column.name in self.columns:
            existing = self.columns[column.name]
            if existing.is_primary_key or existing.is_foreign_key:
                return
            new_type = TypeInferencer.promote(existing.sql_type, column.sql_type)
            existing.sql_type = new_type
        else:
            self.columns[column.name] = column

    def observe_value(self, column_name: str, value):
        inferred = TypeInferencer.infer(value)
        if column_name in self.columns:
            existing = self.columns[column_name]
            if not (existing.is_primary_key or existing.is_foreign_key):
                existing.sql_type = TypeInferencer.promote(existing.sql_type, inferred)
        else:
            self.add_column(ColumnSchema(name=column_name, sql_type=inferred))

    def finalize_types(self):
        for col in self.columns.values():
            col.sql_type = TypeInferencer.finalize(col.sql_type)

    def __repr__(self):
        cols = ", ".join(repr(c) for c in self.columns.values())
        parent = f" (parent: {self.parent_table})" if self.parent_table else ""
        return f"Table[{self.name}{parent}]: {cols} | {len(self.rows)} rows"

class SchemaAnalyzer:

    def __init__(self, root_table_name: str = "root"):
        self.root_table_name = root_table_name
        self.tables = {}  
        self._pk_counter = {} 

    def _get_or_create_table(self, name: str, parent: str = None) -> TableSchema:
        if name not in self.tables:
            self.tables[name] = TableSchema(name=name, parent_table=parent)
            self._pk_counter[name] = 0
        return self.tables[name]

    def _next_pk(self, table_name: str) -> int:
        self._pk_counter[table_name] += 1
        return self._pk_counter[table_name]

    def analyze(self, data):
        if isinstance(data, list):
            for item in data:
                self._process_object(item, self.root_table_name, parent_pk=None)
        elif isinstance(data, dict):
            self._process_object(data, self.root_table_name, parent_pk=None)
        else:
            table = self._get_or_create_table(self.root_table_name)
            table.observe_value("value", data)
            pk = self._next_pk(self.root_table_name)
            table.rows.append({"id_pk": pk, "value": data})

        for table in self.tables.values():
            table.finalize_types()

        return self.tables

    def _process_object(self, obj: dict, table_name: str, parent_pk):
        table = self._get_or_create_table(table_name,
                                          parent=self._find_parent_of(table_name))

        my_pk = self._next_pk(table_name)
        row = {"id_pk": my_pk}

        if parent_pk is not None and table.parent_table:
            row[f"{table.parent_table}_fk"] = parent_pk

        flat_columns = {}
        nested_arrays = []
        self._flatten(obj, prefix="", out_columns=flat_columns,
                      out_arrays=nested_arrays)

        for col_name, value in flat_columns.items():
            table.observe_value(col_name, value)
            row[col_name] = value

        table.rows.append(row)

        for key, array_value in nested_arrays:
            child_table_name = f"{table_name}_{key}"
            self._process_array(array_value, child_table_name,
                                parent_table=table_name, parent_pk=my_pk)
    def _flatten(self, obj: dict, prefix: str,
                 out_columns: dict, out_arrays: list):
        for key, value in obj.items():
            full_key = f"{prefix}_{key}" if prefix else key

            if isinstance(value, dict):
                self._flatten(value, prefix=full_key,
                              out_columns=out_columns, out_arrays=out_arrays)
            elif isinstance(value, list):
                out_arrays.append((full_key, value))
            else:
                out_columns[full_key] = value

    def _process_array(self, array_value: list, child_table_name: str,
                       parent_table: str, parent_pk):
        self._get_or_create_table(child_table_name, parent=parent_table)

        for element in array_value:
            if isinstance(element, dict):
                self._process_object(element, child_table_name, parent_pk=parent_pk)

            elif isinstance(element, list):
                grandchild_name = f"{child_table_name}_item"
                self._process_array(element, grandchild_name,
                                    parent_table=child_table_name,
                                    parent_pk=parent_pk)

            else:
                table = self.tables[child_table_name]
                my_pk = self._next_pk(child_table_name)
                row = {
                    "id_pk": my_pk,
                    f"{parent_table}_fk": parent_pk,
                    "value": element
                }
                table.observe_value("value", element)
                table.rows.append(row)

    def _find_parent_of(self, table_name: str):
        if table_name in self.tables:
            return self.tables[table_name].parent_table
        return None

    def print_schema(self):
        print("\n" + "=" * 70)
        print("SANAL ŞEMA")
        print("=" * 70)
        for table in self.tables.values():
            print(f"\n[TABLE] {table.name}"
                  + (f"  (parent: {table.parent_table})" if table.parent_table else ""))
            print("  Columns:")
            for col in table.columns.values():
                print(f"    - {col}")
            print(f"  Rows ({len(table.rows)}):")
            for r in table.rows:
                print(f"    {r}")