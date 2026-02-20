SELECT
    enquiry_id,
    true_market_value,
    sale_price,
    won::int,
    actual_costs,
    gross_margin,
    date::date AS sale_date
FROM
    {{ source('raw', 'sales') }}
