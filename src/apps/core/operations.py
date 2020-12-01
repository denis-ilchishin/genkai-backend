from django.contrib.postgres.signals import register_type_handlers
from django.db.migrations.operations.base import Operation


class ArrayValuesMaxSimilarity(Operation):
    reversible = True
    name = 'arr_sim'

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        if schema_editor.connection.vendor != 'postgresql':
            return

        schema_editor.execute(
            """
            create or replace function %s(arr text[], search_string text) returns float as $$
                declare
                    sim real = 0.00;
                    val text;
                begin
                    if array_length(arr, 1) < 1 
                    then 
                        return sim;
                    end if;

                    foreach val in array arr
                    loop
                        if sim < similarity(val, search_string) 
                        then
                            sim := similarity(val, search_string);
                        end if;
                    end loop;
                    return sim;
                end;
            $$ language plpgsql;
            """
            % schema_editor.quote_name(self.name)
        )

        register_type_handlers(schema_editor.connection)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        schema_editor.execute(
            "drop function %s(arr text[], search_string text)"
            % schema_editor.quote_name(self.name)
        )

    def describe(self):
        return "Creates function %s" % self.name
