from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import date
import mysql.connector
from typing import Optional

app = FastAPI(title="API Produits - projet_ia")

# 🔹 Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en production : préciser le domaine du front
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Fonction de connexion MySQL
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="projet_ia"
    )

# 🔹 Modèle de données
class Produit(BaseModel):
    libelle: str
    qualite: Optional[str] = None
    prix: float
    categorie: Optional[str] = None
    stock: Optional[int] = 0
    imageProduit: Optional[str] = None
    idVendeur: int

# 🔹 Ajouter un produit
@app.post("/produits", status_code=201)
def ajouter_produit(produit: Produit):
    if produit.prix <= 0:
        raise HTTPException(status_code=400, detail="Le prix doit être supérieur à 0")
    if produit.stock is not None and produit.stock < 0:
        raise HTTPException(status_code=400, detail="Le stock ne peut pas être négatif")

    sql = """
        INSERT INTO produit
        (libelle, qualite, prix, categorie, datePublication, stock, imageProduit, idVendeur)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        produit.libelle,
        produit.qualite,
        produit.prix,
        produit.categorie,
        date.today(),
        produit.stock,
        produit.imageProduit,
        produit.idVendeur
    )

    db = get_db_connection()
    try:
        cursor = db.cursor()
        cursor.execute(sql, values)
        db.commit()
        cursor.close()
        db.close()
    except mysql.connector.Error as err:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'insertion : {err.msg}")

    return {"message": "Produit ajouté avec succès", "produit": produit}

# 🔹 Lister tous les produits
@app.get("/produits")
def lister_produits():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM produit")
    produits = cursor.fetchall()
    cursor.close()
    db.close()
    return {"produits": produits}

# 🔹 Lister les produits par vendeur
@app.get("/produits/vendeur/{idVendeur}")
def produits_par_vendeur(idVendeur: int):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM produit WHERE idVendeur = %s", (idVendeur,))
    produits = cursor.fetchall()
    cursor.close()
    db.close()
    return {"produits": produits}

# 🔹 Supprimer un produit
@app.delete("/produits/{idProduit}")
def supprimer_produit(idProduit: int):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM produit WHERE idProduit = %s", (idProduit,))
        db.commit()
    except mysql.connector.Error as err:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression : {err.msg}")
    finally:
        cursor.close()
        db.close()
    return {"message": f"Produit {idProduit} supprimé avec succès"}

# 🔹 Modifier un produit
@app.put("/produits/{idProduit}")
def modifier_produit(idProduit: int, produit: Produit):
    db = get_db_connection()
    cursor = db.cursor()
    sql = """
        UPDATE produit
        SET libelle=%s, qualite=%s, prix=%s, categorie=%s, stock=%s, imageProduit=%s, idVendeur=%s
        WHERE idProduit=%s
    """
    values = (
        produit.libelle,
        produit.qualite,
        produit.prix,
        produit.categorie,
        produit.stock,
        produit.imageProduit,
        produit.idVendeur,
        idProduit
    )
    try:
        cursor.execute(sql, values)
        db.commit()
    except mysql.connector.Error as err:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la modification : {err.msg}")
    finally:
        cursor.close()
        db.close()
    return {"message": f"Produit {idProduit} modifié avec succès", "produit": produit}
