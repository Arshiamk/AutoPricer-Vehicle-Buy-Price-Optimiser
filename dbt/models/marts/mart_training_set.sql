WITH enquiries AS (
    SELECT * FROM {{ ref('stg_enquiries') }}
),
sales AS (
    SELECT * FROM {{ ref('stg_sales') }}
),
vehicles AS (
    SELECT * FROM {{ ref('stg_vehicles') }}
),
regions AS (
    SELECT * FROM {{ ref('stg_regions') }}
)

SELECT
    e.enquiry_id,
    e.vehicle_id,
    e.region_id,
    e.channel,
    e.damage_flag,
    e.damage_type,
    e.offer_price,
    e.enquiry_date,
    
    s.true_market_value,
    s.sale_price,
    COALESCE(s.won, 0) AS won,
    COALESCE(s.actual_costs, 0) AS actual_costs,
    COALESCE(s.gross_margin, 0) AS gross_margin,
    s.sale_date,
    
    v.make,
    v.model,
    v.year,
    v.mileage,
    v.fuel_type,
    v.body_type,
    
    r.region_name,
    r.country,
    r.risk_score
    
FROM enquiries e
LEFT JOIN sales s ON e.enquiry_id = s.enquiry_id
LEFT JOIN vehicles v ON e.vehicle_id = v.vehicle_id
LEFT JOIN regions r ON e.region_id = r.region_id
