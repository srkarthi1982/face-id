from pydantic import BaseModel


class UserProfileUpdate(BaseModel):
    profile_id: int
    version: int
    first_name: str
    middle_name: str | None = None
    last_name: str
    date_of_birth: str | None


class UserProfileResponse(BaseModel):
    profile_id: int
    version: int
    first_name: str
    middle_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    mobile_no: str | None = None
    ext_no: str | None = None
    rank: str | None = None
    command: str | None = None
    qualification: str | None = None
