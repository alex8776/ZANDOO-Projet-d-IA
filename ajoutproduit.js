let produitEnCours = null;

// 🔹 Ajouter un produit
document.getElementById("produitForm").addEventListener("submit", async function(event) {
    event.preventDefault();

    const produit = {
        libelle: document.getElementById("libelle").value,
        qualite: document.getElementById("qualite").value,
        prix: parseFloat(document.getElementById("prix").value),
        categorie: document.getElementById("categorie").value,
        stock: parseInt(document.getElementById("stock").value) || 0,
        imageProduit: document.getElementById("imageProduit").value,
        idVendeur: parseInt(document.getElementById("idVendeur").value)
    };

    try {
        const response = await fetch("http://127.0.0.1:8000/produits", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(produit)
        });

        if (!response.ok) {
            const error = await response.json();
            document.getElementById("message").textContent = "Erreur : " + error.detail;
            return;
        }

        const data = await response.json();
        document.getElementById("message").textContent = data.message;

        // Rafraîchir la liste des produits du vendeur
        chargerProduits(produit.idVendeur);

    } catch (err) {
        document.getElementById("message").textContent = "Erreur réseau : " + err;
    }
});

// 🔹 Charger les produits par vendeur
async function chargerProduits(idVendeur) {
    try {
        const response = await fetch(`http://127.0.0.1:8000/produits/vendeur/${idVendeur}`);
        const data = await response.json();

        const tbody = document.getElementById("produitsTable");
        tbody.innerHTML = "";

        data.produits.forEach(p => {
            const row = `<tr>
                <td>${p.idProduit}</td>
                <td>${p.libelle}</td>
                <td>${p.qualite || ""}</td>
                <td>${p.prix}</td>
                <td>${p.categorie || ""}</td>
                <td>${p.stock}</td>
                <td>${p.imageProduit ? `<img src="${p.imageProduit}" alt="image" width="50">` : ""}</td>
                <td>${p.idVendeur}</td>
                <td>
                    <button onclick="supprimerProduit(${p.idProduit}, ${p.idVendeur})">Supprimer</button>
                    <button onclick="ouvrirFormulaireModification(${p.idProduit}, ${p.idVendeur}, '${p.libelle}', '${p.qualite}', ${p.prix}, '${p.categorie}', ${p.stock}, '${p.imageProduit}')">Modifier</button>
                </td>
            </tr>`;
            tbody.innerHTML += row;
        });
    } catch (err) {
        document.getElementById("message").textContent = "Erreur lors du chargement des produits : " + err;
    }
}

// 🔹 Supprimer un produit
async function supprimerProduit(idProduit, idVendeur) {
    if (confirm("Voulez-vous vraiment supprimer ce produit ?")) {
        await fetch(`http://127.0.0.1:8000/produits/${idProduit}`, { method: "DELETE" });
        chargerProduits(idVendeur);
    }
}

// 🔹 Ouvrir le formulaire de modification avec les valeurs actuelles
function ouvrirFormulaireModification(idProduit, idVendeur, libelle, qualite, prix, categorie, stock, imageProduit) {
    produitEnCours = { idProduit, idVendeur };
    document.getElementById("editLibelle").value = libelle;
    document.getElementById("editQualite").value = qualite;
    document.getElementById("editPrix").value = prix;
    document.getElementById("editCategorie").value = categorie;
    document.getElementById("editStock").value = stock;
    document.getElementById("editImageProduit").value = imageProduit;
    document.getElementById("editForm").style.display = "block";
}

// 🔹 Valider la modification
async function validerModification() {
    const produit = {
        libelle: document.getElementById("editLibelle").value,
        qualite: document.getElementById("editQualite").value,
        prix: parseFloat(document.getElementById("editPrix").value),
        categorie: document.getElementById("editCategorie").value,
        stock: parseInt(document.getElementById("editStock").value),
        imageProduit: document.getElementById("editImageProduit").value,
        idVendeur: produitEnCours.idVendeur
    };

    await fetch(`http://127.0.0.1:8000/produits/${produitEnCours.idProduit}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(produit)
    });

    document.getElementById("editForm").style.display = "none";
    chargerProduits(produitEnCours.idVendeur);
}
