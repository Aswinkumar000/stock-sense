# PROVISIONAL SCHEMA - Member 3 (Delivery Orders and Internal Transfers)

This file documents assumptions made in the absence of Member 2's actual
database.py / models. Replace/reconcile once Member 2 pushes real code.

## Assumed: Product
- id (int, primary key)
- name (string)
- sku (string, unique)
- category (string)
- unit_of_measure (string)

## Assumed: Warehouse
- id (int, primary key)
- name (string)

## Assumed: Location
- id (int, primary key)
- name (string)
- warehouse_id (foreign key, references Warehouse.id)

## Assumed: StockQuantity (per product per location)
- id (int, primary key)
- product_id (foreign key, references Product.id)
- location_id (foreign key, references Location.id)
- quantity (float)

## My models (to be added in later steps)
- DeliveryOrder
- DeliveryOrderLine
- InternalTransfer
- InternalTransferLine
- StockMove (shared movement ledger, coordinate with Member 4)