from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import text

from backend.app.database import engine

app = FastAPI(title="Field Fault Tracker API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/db-test")
def db_test():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM santraller"))
        count = result.scalar()

    return {
        "database": "connected",
        "santral_sayisi": count
    }


@app.get("/santraller")
def get_santraller():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT *
            FROM santraller
            ORDER BY id
        """))

        rows = result.mappings().all()

    return rows


class ArizaCreate(BaseModel):
    ekipman_id: int
    kategori_id: int
    tekniker_id: int
    baslik: str
    aciklama: str
    oncelik: str = "ORTA"


@app.post("/arizalar")
def create_ariza(ariza: ArizaCreate):

    with engine.connect() as conn:

        conn.execute(
            text("""
                INSERT INTO arizalar
                (
                    ekipman_id,
                    kategori_id,
                    tekniker_id,
                    baslik,
                    aciklama,
                    oncelik
                )
                VALUES
                (
                    :ekipman_id,
                    :kategori_id,
                    :tekniker_id,
                    :baslik,
                    :aciklama,
                    :oncelik
                )
            """),
            {
                "ekipman_id": ariza.ekipman_id,
                "kategori_id": ariza.kategori_id,
                "tekniker_id": ariza.tekniker_id,
                "baslik": ariza.baslik,
                "aciklama": ariza.aciklama,
                "oncelik": ariza.oncelik,
            }
        )

        conn.commit()

    return {
        "message": "Arıza oluşturuldu"
    }
@app.get("/arizalar")
def get_arizalar():

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT
                    a.id,
                    a.baslik,
                    a.aciklama,
                    a.durum,
                    a.oncelik,
                    a.olusturma_tarihi,
                    e.ad AS ekipman_adi,
                    t.ad_soyad AS tekniker_adi,
                    k.ad AS kategori_adi
                FROM arizalar a
                LEFT JOIN ekipmanlar e
                    ON a.ekipman_id = e.id
                LEFT JOIN teknikerler t
                    ON a.tekniker_id = t.id
                LEFT JOIN ariza_kategorileri k
                    ON a.kategori_id = k.id
                ORDER BY a.id DESC
            """)
        )

        rows = result.mappings().all()

    return rows