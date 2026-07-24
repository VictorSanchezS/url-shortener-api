import hashlib

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.redis_client import guardar_en_cache, obtener_de_cache, eliminar_de_cache

router = APIRouter()


@router.post("/urls", response_model=schemas.URLResponse, status_code=201)
def crear_url(payload: schemas.URLCreate, db: Session = Depends(get_db)):
    nueva_url = crud.crear_url(db, str(payload.url_original))
    guardar_en_cache(nueva_url.codigo_corto, nueva_url.url_original)
    return nueva_url


@router.get("/{codigo_corto}")
def redirigir(codigo_corto: str, request: Request, db: Session = Depends(get_db)):
    # 1. Intentamos servir desde cache (rápido, sin tocar Postgres)
    url_original = obtener_de_cache(codigo_corto)

    if url_original is None:
        # 2. Cache miss: buscamos en la base de datos
        url = crud.obtener_url_por_codigo(db, codigo_corto)
        if url is None:
            raise HTTPException(status_code=404, detail="Código no encontrado")
        url_original = url.url_original
        guardar_en_cache(codigo_corto, url_original)
    else:
        url = crud.obtener_url_por_codigo(db, codigo_corto)
        if url is None:
            raise HTTPException(status_code=404, detail="Código no encontrado")

    # Registramos el clic (para analytics), guardando la IP como hash por privacidad
    ip_hash = hashlib.sha256(request.client.host.encode()).hexdigest() if request.client else None
    crud.registrar_clic(
        db,
        url,
        ip_hash=ip_hash,
        user_agent=request.headers.get("user-agent"),
        referrer=request.headers.get("referer"),
    )

    return RedirectResponse(url=url_original, status_code=302)


@router.get("/urls/{codigo_corto}/stats", response_model=schemas.URLStats)
def obtener_stats(codigo_corto: str, db: Session = Depends(get_db)):
    url = crud.obtener_url_por_codigo(db, codigo_corto)
    if url is None:
        raise HTTPException(status_code=404, detail="Código no encontrado")

    ultimos_clics = [c.fecha for c in sorted(url.clics, key=lambda c: c.fecha, reverse=True)[:10]]

    return schemas.URLStats(
        codigo_corto=url.codigo_corto,
        url_original=url.url_original,
        clics_totales=url.clics_totales,
        ultimos_clics=ultimos_clics,
    )


@router.delete("/urls/{codigo_corto}", status_code=204)
def borrar_url(codigo_corto: str, db: Session = Depends(get_db)):
    url = crud.obtener_url_por_codigo(db, codigo_corto)
    if url is None:
        raise HTTPException(status_code=404, detail="Código no encontrado")

    crud.eliminar_url(db, url)
    eliminar_de_cache(codigo_corto)