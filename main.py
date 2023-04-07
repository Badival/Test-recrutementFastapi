from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from tortoise.contrib.fastapi import register_tortoise, HTTPNotFoundError
from tortoise.exceptions import DoesNotExist
from tortoise import fields
from tortoise.models import Model
from pydantic import BaseModel

# définir le modèle pour les entreprises
class Company(BaseModel):
    name: str
    address: str
    capital: float
    status: str
    contact_person_name: str
    contact_person_email: str
    contact_person_phone: str

# définir le modèle de base de données pour les entreprises
class CompanyDB(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    address = fields.CharField(max_length=255)
    capital = fields.FloatField()
    status = fields.CharField(max_length=255)
    contact_person_name = fields.CharField(max_length=255)
    contact_person_email = fields.CharField(max_length=255)
    contact_person_phone = fields.CharField(max_length=255)

    class Meta:
        table = "companies"

class Message(BaseModel):
    message: str

# initialiser FastAPI
app = FastAPI()

# définir la sécurité pour l'API
security = HTTPBasic()

# définir la fonction d'authentification basique
async def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = "admin"
    correct_password = "admin"
    if credentials.username != correct_username or credentials.password != correct_password:
        raise HTTPException(
            status_code=401,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True

# définir les endpoints pour CRUD des entreprises

# créer une entreprise
@app.post("/companies", response_model=Message)
async def create_company(company: Company, current_user: bool = Depends(get_current_user)):
    company_db = await CompanyDB.create(**company.dict())
    await company_db.save()
    return Message(message="Company créée")

# récupérer une entreprise par ID
@app.get("/companies/{company_id}")
async def get_company(company_id: int, current_user: bool = Depends(get_current_user)):
    try:
        return await CompanyDB.get(id=company_id)
    except DoesNotExist:
        raise HTTPNotFoundError(f"Entreprise avec l'ID {company_id} n'existe pas")

# mettre à jour une entreprise par ID
@app.put("/companies/{company_id}", response_model=Message)
async def update_company(company_id: int, company: Company, current_user: bool = Depends(get_current_user)):
    await CompanyDB.filter(id=company_id).update(**company.dict())
    await CompanyDB.get(id=company_id)
    return Message(message="Company modifiée")

# supprimer une entreprise par ID
@app.delete("/companies/{company_id}")
async def delete_company(company_id: int, current_user: bool = Depends(get_current_user)):
    deleted_count = await CompanyDB.filter(id=company_id).delete()
    if not deleted_count:
        raise HTTPNotFoundError(f"Entreprise avec l'ID {company_id} n'existe pas")
    return {"message": f"Entreprise avec l'ID {company_id} a été supprimé avec succès"}
   
# récupérer toutes les entreprises avec pagination
@app.get("/companies")
async def get_companies(page: int = 1, per_page: int = 10, current_user: bool = Depends(get_current_user)):
    offset = (page - 1) * per_page
    companies = await CompanyDB.all().offset(offset).limit(per_page)

    # retourner les entreprises paginées
    return {
        "page": page,
        "per_page": per_page,
        "companies": companies,
    }

register_tortoise(
app,
db_url="sqlite://dbTortoise.sqlite3",
modules={"models": ["main"]},
generate_schemas=True,
)