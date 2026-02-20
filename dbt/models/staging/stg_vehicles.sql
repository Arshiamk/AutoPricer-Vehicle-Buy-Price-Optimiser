SELECT
    vehicle_id,
    make,
    model,
    year,
    mileage,
    fuel_type,
    body_type
FROM
    {{ source('raw', 'vehicles') }}
