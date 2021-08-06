{%- if cookiecutter.use_qgis_plugin_tools|lower != "n" -%}
{%- include 'plugin_templates/plugin_with_submodule.py' -%}
{%- else -%}
{%- include 'plugin_templates/plugin_without_submodule.py' -%}
{%- endif -%}
