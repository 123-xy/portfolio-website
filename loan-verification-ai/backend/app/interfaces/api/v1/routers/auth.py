from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.application.dto.auth import LoginCommand, RefreshCommand, RegisterCommand
from app.application.use_cases.auth.authenticate_user import AuthenticateUser
from app.application.use_cases.auth.logout_user import LogoutUser
from app.application.use_cases.auth.refresh_tokens import RefreshAccessToken
from app.application.use_cases.auth.register_user import RegisterUser
from app.interfaces.api.v1.deps.auth import (
    CurrentUser,
    client_context,
    get_authenticate_user,
    get_logout_user,
    get_refresh_access_token,
    get_register_user,
)
from app.interfaces.api.v1.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])

ClientCtx = Annotated[tuple[str | None, str | None], Depends(client_context)]


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new applicant account",
)
async def register(
    body: RegisterRequest,
    ctx: ClientCtx,
    use_case: Annotated[RegisterUser, Depends(get_register_user)],
) -> TokenResponse:
    user_agent, ip = ctx
    pair = await use_case.execute(
        RegisterCommand(email=body.email, full_name=body.full_name, password=body.password),
        user_agent=user_agent,
        ip_address=ip,
    )
    return TokenResponse(access_token=pair.access_token, refresh_token=pair.refresh_token)


@router.post("/login", response_model=TokenResponse, summary="Authenticate and receive tokens")
async def login(
    body: LoginRequest,
    ctx: ClientCtx,
    use_case: Annotated[AuthenticateUser, Depends(get_authenticate_user)],
) -> TokenResponse:
    user_agent, ip = ctx
    pair = await use_case.execute(
        LoginCommand(email=body.email, password=body.password, user_agent=user_agent, ip_address=ip)
    )
    return TokenResponse(access_token=pair.access_token, refresh_token=pair.refresh_token)


@router.post("/refresh", response_model=TokenResponse, summary="Rotate refresh token")
async def refresh(
    body: RefreshRequest,
    ctx: ClientCtx,
    use_case: Annotated[RefreshAccessToken, Depends(get_refresh_access_token)],
) -> TokenResponse:
    user_agent, ip = ctx
    pair = await use_case.execute(
        RefreshCommand(refresh_token=body.refresh_token, user_agent=user_agent, ip_address=ip)
    )
    return TokenResponse(access_token=pair.access_token, refresh_token=pair.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke a refresh token",
)
async def logout(
    body: LogoutRequest,
    use_case: Annotated[LogoutUser, Depends(get_logout_user)],
) -> None:
    await use_case.execute(RefreshCommand(refresh_token=body.refresh_token))


@router.get("/me", response_model=UserResponse, summary="Current authenticated user")
async def me(current_user: CurrentUser) -> UserResponse:
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
    )
