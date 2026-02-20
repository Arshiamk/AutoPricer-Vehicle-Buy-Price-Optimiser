SELECT
    enquiry_id,
    vehicle_id,
    region_id,
    channel,
    damage_flag,
    damage_type,
    offer_price,
    date::date AS enquiry_date
FROM
    {{ source('raw', 'enquiries') }}
