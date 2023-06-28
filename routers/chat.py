from fastapi import APIRouter

from .chat_v1 import router as chatv1
from .chat_v2 import router as chatv2
from .chat_v3 import router as chatv3

router = APIRouter(tags=['chat'])

router.include_router(chatv2)

router.include_router(chatv1)

router.include_router(chatv3)

# cache = Cache(
#     maxsize=10000, ttl=deltaTime(min=20).total_seconds(),
# )


# release: using conversation retrieval chain for pdf support


# router.post('/')(create_v1)
# router.get('/{chat_id}')(get_chat_v1)
# router.put('/{chat_id}/upload')(upload_v1)
