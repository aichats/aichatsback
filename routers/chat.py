import chat_v1
from fastapi import APIRouter

from .chat_v2 import get_chat_v2

router = APIRouter(tags=['chat'])

router.include_router(chat_v1.router)

router.get('/v2/{chat_id}')(get_chat_v2)
# cache = Cache(
#     maxsize=10000, ttl=deltaTime(min=20).total_seconds(),
# )


# release: using conversation retrieval chain for pdf support


# router.post('/')(create_v1)
# router.get('/{chat_id}')(get_chat_v1)
# router.put('/{chat_id}/upload')(upload_v1)
