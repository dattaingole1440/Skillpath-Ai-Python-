from fastapi import APIRouter
from fastapi.responses import FileResponse, Response
import os

router = APIRouter(tags=["PWA"])

@router.get("/manifest.json")
def get_manifest():
    manifest_path = os.path.abspath("app/static/manifest.json")
    if os.path.exists(manifest_path):
        return FileResponse(manifest_path, media_type="application/json")
    return Response(content='{"name":"SkillPath AI","short_name":"SkillPath","start_url":"/","display":"standalone"}', media_type="application/json")

@router.get("/sw.js")
def get_service_worker():
    sw_path = os.path.abspath("app/static/sw.js")
    if os.path.exists(sw_path):
        return FileResponse(sw_path, media_type="application/javascript")
    return Response(content='self.addEventListener("fetch", function(e){});', media_type="application/javascript")
