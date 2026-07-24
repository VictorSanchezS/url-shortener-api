import string

from sqlalchemy.orm import Session

from app import models

ALFABETO = string.digits + string.ascii_letters  # 0-9, a-z, A-Z (base62)


def _codificar_base62(numero: int) -> str:
    if numero == 0:
        return ALFABETO[0]
    resultado = []
    base = len(ALFABETO)
    while numero > 0:
        numero, residuo = divmod(numero, base)
        resultado.append(ALFABETO[residuo])
    return "".join(reversed(resultado))


def crear_url(db: Session, url_original: str) -> models.URL:
    nueva_url = models.URL(url_original=url_original, codigo_corto="")
    db.add(nueva_url)
    db.flush()  # asigna el ID sin hacer commit todavía

    # Usamos el ID autoincremental para generar un código corto único y determinístico
    nueva_url.codigo_corto = _codificar_base62(nueva_url.id)

    db.commit()
    db.refresh(nueva_url)
    return nueva_url


def obtener_url_por_codigo(db: Session, codigo_corto: str) -> models.URL | None:
    return db.query(models.URL).filter(models.URL.codigo_corto == codigo_corto).first()


def registrar_clic(db: Session, url: models.URL, ip_hash: str | None, user_agent: str | None, referrer: str | None):
    clic = models.Clic(url_id=url.id, ip_hash=ip_hash, user_agent=user_agent, referrer=referrer)
    url.clics_totales += 1
    db.add(clic)
    db.commit()


def eliminar_url(db: Session, url: models.URL):
    db.delete(url)
    db.commit()