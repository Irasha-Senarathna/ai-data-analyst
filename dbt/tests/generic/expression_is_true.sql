{#- Fails (or warns) for every row where the SQL expression is not true.
    Written here instead of using dbt_utils so the project needs no `dbt deps`. -#}
{% test expression_is_true(model, expression) %}
    select *
    from {{ model }}
    where not ({{ expression }})
{% endtest %}
