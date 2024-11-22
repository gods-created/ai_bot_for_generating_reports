from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
import uvicorn

from validators import Data
from modules import SettingsAction
from middlewares import Error404Middleware

app = FastAPI(
    title='Editor',
    version='0.0.1',
    redoc_url=None,
    docs_url=None
)

app.mount('/static', StaticFiles(directory='static'), name='static')
templating = Jinja2Templates(directory='templates')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_headers=['*'],
    allow_methods=['*']
)

app.add_middleware(
    Error404Middleware
)

@app.get('/edit_data', tags=['No API'], name='Edit page data', response_class=HTMLResponse, status_code=200)
def _edit_page_data(request: Request, user_id: str = Query(...)):
    try:
        if not isinstance(user_id, str):
            raise ValueError('Некореткний ID користувача.')
        
        return templating.TemplateResponse(request=request, name='edit_page.html', context={'url': request.base_url, 'user_id': user_id})
    
    except (ValueError, Exception, ) as e:
        return HTMLResponse(content=str(e))
    
@app.post('/edit_data', tags=['API'], name='Edit data', response_class=JSONResponse, status_code=200)
async def _edit_data(request: Request, data: Data):
    try:
        json_data = data.to_json()
        async with SettingsAction() as module:
            response = await module._update_user(json_data)

        return JSONResponse(content=response)

    except (ValueError, Exception, ) as e:
        return HTMLResponse(content=str(e))
    
@app.get('/error404', tags=['No API', 'Errors'], name='Error 404', response_class=HTMLResponse, status_code=200)
def _error404(request: Request):
    try:        
        return templating.TemplateResponse(request=request, name='error404.html', context={})
    
    except (ValueError, Exception, ) as e:
        return HTMLResponse(content=str(e))
    
if __name__ == '__main__':
    uvicorn.run('server:app', host='0.0.0.0', port=8001, reload=True)