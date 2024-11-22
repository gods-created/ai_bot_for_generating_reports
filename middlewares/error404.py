from fastapi import Request
from fastapi.responses import RedirectResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware

class Error404Middleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if request.url.path.startswith("/static") or request.url.path == "/favicon.ico":
            return response
        
        if request.url.path == '/error404':
            return response
        
        if request.url.path == '/edit_data' and request.method == 'POST':
            return response
        
        if (
            request.method == 'GET' and 
            'edit_data' not in request.url.path
        ) or not request.query_params.get('user_id'):
            return RedirectResponse('/error404')

        return response
