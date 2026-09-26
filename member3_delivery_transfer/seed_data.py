from database import SessionLocal, engine, Base
import models

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Avoid duplicate seeding if run more than once
if db.query(models.Product).count() == 0:
    steel_rod = models.Product(name="Steel Rod", sku="SKU-STEEL-001", category="Raw Material", unit_of_measure="kg")
    chair = models.Product(name="Chair", sku="SKU-CHAIR-001", category="Finished Goods", unit_of_measure="unit")
    db.add_all([steel_rod, chair])
    db.commit()
    db.refresh(steel_rod)
    db.refresh(chair)

    main_warehouse = models.Warehouse(name="Main Warehouse")
    db.add(main_warehouse)
    db.commit()
    db.refresh(main_warehouse)

    main_store = models.Location(name="Main Store", warehouse_id=main_warehouse.id)
    production_rack = models.Location(name="Production Rack", warehouse_id=main_warehouse.id)
    db.add_all([main_store, production_rack])
    db.commit()
    db.refresh(main_store)
    db.refresh(production_rack)

    stock1 = models.StockQuantity(product_id=steel_rod.id, location_id=main_store.id, quantity=100.0)
    stock2 = models.StockQuantity(product_id=chair.id, location_id=main_store.id, quantity=100.0)
    db.add_all([stock1, stock2])
    db.commit()

    print("Seed data inserted:")
    print(f"  Product 'Steel Rod' id={steel_rod.id}, Product 'Chair' id={chair.id}")
    print(f"  Warehouse 'Main Warehouse' id={main_warehouse.id}")
    print(f"  Location 'Main Store' id={main_store.id}, 'Production Rack' id={production_rack.id}")
    print(f"  Stock: Steel Rod=100 at Main Store, Chair=100 at Main Store")
else:
    print("Products already exist -- skipping seed to avoid duplicates.")
    print("If you want a fresh start, delete stocksense_member3.db and rerun this script.")

db.close()