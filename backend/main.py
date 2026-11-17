
from fastapi import FastAPI, Depends, HTTPException
from models import Product
from fastapi.middleware.cors import CORSMiddleware
from database import session, Base, engine
import database_models
from sqlalchemy.orm import Session

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Create database tables
Base.metadata.create_all(bind=engine)


@app.get("/")
def greet():
    return {"message": "Welcome to Vivgod"}


# Database dependency
def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()


# Initialize database with sample products
def init_db():
    db = session()
    try:
        count = db.query(database_models.Product).count()

        if count == 0:
            products = [
                database_models.Product(
                    id=1,
                    name="Product 1",
                    description="Description 1",
                    price=100.0,
                    quantity=10
                ),
                database_models.Product(
                    id=2,
                    name="Product 2",
                    description="Description 2",
                    price=200.0,
                    quantity=20
                ),
                database_models.Product(
                    id=3,
                    name="Product 3",
                    description="Description 3",
                    price=300.0,
                    quantity=30
                )
            ]

            db.add_all(products)
            db.commit()

    finally:
        db.close()


init_db()


# GET ALL PRODUCTS
@app.get("/products")
def get_all_products(db: Session = Depends(get_db)):
    return db.query(database_models.Product).all()


# GET PRODUCT BY ID
@app.get("/products/{product_id}")
def get_product_by_id(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(database_models.Product).filter(
        database_models.Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


# CREATE PRODUCT
@app.post("/products")
def create_product(
    product: Product,
    db: Session = Depends(get_db)
):
    new_product = database_models.Product(**product.model_dump())

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


# UPDATE PRODUCT
@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    updated_product: Product,
    db: Session = Depends(get_db)
):
    product = db.query(database_models.Product).filter(
        database_models.Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in updated_product.model_dump().items():
        if key != "id":
            setattr(product, key, value)

    db.commit()
    db.refresh(product)

    return product


# DELETE PRODUCT
@app.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(database_models.Product).filter(
        database_models.Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()

    return {"message": "Product deleted successfully"}
