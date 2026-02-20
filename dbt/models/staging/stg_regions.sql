SELECT
    region_id,
    name as region_name,
    country,
    risk_score
FROM
    {{ source('raw', 'regions') }}
