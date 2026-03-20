from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from grouping import assign_groups
from storage import clear_history, delete_record, load_history, save_result

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.post("/assign", response_class=HTMLResponse)
async def assign(
    request: Request,
    members: str = Form(""),
    mode: str = Form("group_size"),
    group_size: int = Form(2),
    num_groups: int = Form(2),
):
    names = [name.strip() for name in members.strip().splitlines() if name.strip()]

    if len(names) < 2:
        return HTMLResponse("<p><mark>2人以上のメンバーを入力してください</mark></p>")

    gs = group_size if mode == "group_size" else None
    ng = num_groups if mode == "num_groups" else None

    if gs is not None and gs >= len(names):
        return HTMLResponse("<p><mark>グループの人数はメンバー数より少なくしてください</mark></p>")
    if ng is not None and ng > len(names):
        return HTMLResponse("<p><mark>グループ数はメンバー数以下にしてください</mark></p>")

    history = load_history()
    groups = assign_groups(names, history, group_size=gs, num_groups=ng)
    save_result(names, groups, gs, ng)

    response = templates.TemplateResponse(request, "_result.html", {"groups": groups})
    response.headers["HX-Trigger"] = "historyUpdated"
    return response


@app.get("/history", response_class=HTMLResponse)
async def history(request: Request):
    records = list(reversed(load_history()))
    return templates.TemplateResponse(request, "_history.html", {"records": records})


@app.delete("/history", response_class=HTMLResponse)
async def clear_all_history(request: Request):
    clear_history()
    return templates.TemplateResponse(request, "_history.html", {"records": []})


@app.delete("/history/{record_id}", response_class=HTMLResponse)
async def delete_history(request: Request, record_id: str):
    delete_record(record_id)
    records = list(reversed(load_history()))
    return templates.TemplateResponse(request, "_history.html", {"records": records})
