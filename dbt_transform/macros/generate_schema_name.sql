{% macro generate_schema_name(custom_schema_name, node) -%}
    {# 💡 If a custom schema is explicitly defined in dbt_project.yml (e.g., marts), use it directly without prefixes #}
    {%- if custom_schema_name is not none -%}
        {{ custom_schema_name | trim }}
    {%- else -%}
        {# 💡 Default back to the target schema defined in profiles.yml (STAGING) if no custom schema is provided #}
        {{ target.schema }}
    {%- endif -%}
{%- endmacro %}