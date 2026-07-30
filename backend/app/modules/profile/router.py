import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.core.permissions import PermissionCode
from app.core.response import ApiResponse, SuccessResponse, ok

from .models import Profile
from . import schemas as s


logger = logging.getLogger(__name__)

router = APIRouter()

# ---------------------------------------------------------------------------
# Profile Info
# ---------------------------------------------------------------------------
profile_router = APIRouter(prefix='/profile-info', tags=['Profile Info'])


def _generate_user_profile_response(profile: Profile) -> s.UserProfileResponse:
    return s.UserProfileResponse(
        profile_id=profile.id,
        version=profile.version,
        first_name=profile.first_name,
        middle_name=profile.middle_name,
        last_name=profile.last_name,
        email=profile.email,
        mobile_no=profile.mobile_no,
        ext_no=profile.ext_no,
        rank=profile.rank,
        command=profile.command,
        qualification=profile.qualification,
    )


@profile_router.get("/{user_id}", response_model=SuccessResponse[s.UserProfileResponse])
def get_profile(user_id: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    from app.modules.users.models import User
    user = db.execute(
        db.query(User).filter(User.username == user_id).statement
    ).scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    return ok(_generate_user_profile_response(user.profile))


@profile_router.put("/", response_model=ApiResponse)
async def update_profile(data: s.UserProfileUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    profile = db.get(Profile, data.profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    if profile.version != data.version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Resource was modified by another request. Reload and retry.")

    for f in ['first_name', 'middle_name', 'last_name', 'date_of_birth']:
        old = getattr(profile, f)
        new = getattr(data, f)
        if old != new:
            setattr(profile, f, new)

    db.commit()
    db.refresh(profile)

    return ApiResponse(success=True)


@profile_router.delete("/{profile_id}", response_model=ApiResponse)
def delete_profile(profile_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if not current_user.has_role('admin'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    profile = db.get(Profile, profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    user = profile.user
    db.delete(user)
    db.commit()
    return ApiResponse(success=True)


router.include_router(profile_router)
