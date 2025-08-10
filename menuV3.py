# -*- coding: utf-8 -*-
import tkinter as tk
from datetime import datetime
import json, os, re

# =========================
#  CONFIG
# =========================
RES_PATH = os.getenv("RES_PATH", "/home/pi/buanderie-reservation-main/reservations.json")
CODE_LEN = 4
ROOM_MIN, ROOM_MAX = 1, 54
ROOM_FORBIDDEN = {13}
STATUS_MS_OK = 15000     # 15s accès autorisé
STATUS_MS_FAIL = 3000    # 3s accès refusé

# Admin override (chambre + code)
ADMIN_ROOM = 69
ADMIN_CODE = "9632"

# =========================
#  TIMEZONE Europe/Paris (fallback local si pytz absent)
# =========================
try:
    import pytz
    TZ = pytz.timezone('Europe/Paris')
    def paris_now(): return datetime.now(TZ)
    def localize_paris(dt_naive): return TZ.localize(dt_naive)
except Exception:
    TZ = None
    def paris_now(): return datetime.now()
    def localize_paris(dt_naive): return dt_naive

# =========================
#  PARSE DATE/TIME
# =========================
def parse_iso_local(s):
    if not s: return None
    s = str(s).strip()
    for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S"):
        try:
            return localize_paris(datetime.strptime(s, fmt))
        except: pass
    return None

# =========================
#  DATA
# =========================
def load_reservations():
    if not os.path.exists(RES_PATH): return []
    try:
        with open(RES_PATH, "r") as f:
            data = json.load(f)
        out=[]
        for it in data:
            start = parse_iso_local(it.get("start"))
            end   = parse_iso_local(it.get("end"))
            code  = str(it.get("code","")).strip()
            title = str(it.get("title","")).strip()
            m = re.search(r'(\d+)', title)
            room = int(m.group(1)) if m else None
            if start and end and code and room is not None:
                it2 = dict(it)
                it2["_start_dt"]=start; it2["_end_dt"]=end; it2["_code"]=code; it2["_room"]=room
                out.append(it2)
        return out
    except:
        return []

# =========================
#  LOGIQUE D'ACCÈS
# =========================
def room_valid(n):
    return (ROOM_MIN <= n <= ROOM_MAX) and (n not in ROOM_FORBIDDEN)

def check_access(code_input, room_input):
    now = paris_now()
    all_res = load_reservations()
    room_res = [it for it in all_res if it["_room"] == room_input]
    active_all = [it for it in all_res if it["_start_dt"] <= now <= it["_end_dt"]]
    active_this_room = [it for it in room_res if it["_start_dt"] <= now <= it["_end_dt"]]
    active_other_room_same_code = [it for it in active_all if it["_room"] != room_input and it["_code"] == code_input]

    if active_this_room:
        for it in active_this_room:
            if it["_code"] == code_input:
                return (True, None, it)
        if active_other_room_same_code:
            return (False, "MAUVAISE CHAMBRE", None)
        return (False, "MAUVAIS CODE", None)

    if active_other_room_same_code:
        return (False, "MAUVAISE CHAMBRE", None)

    with_same_code_here = [it for it in room_res if it["_code"] == code_input]
    if not with_same_code_here:
        return (False, "MAUVAIS CODE", None)

    earliest = min(it["_start_dt"] for it in with_same_code_here)
    latest   = max(it["_end_dt"]   for it in with_same_code_here)
    if now < earliest: return (False, "VOUS ETES EN AVANCE", None)
    if now > latest:   return (False, "CRENEAU DEPASSE", None)
    return (False, "AUCUNE RESERVATION EN COURS", None)

# =========================
#  UI / Interactions
# =========================
def set_mode(new_mode):
    global input_mode, blink_on
    input_mode = new_mode
    btn_room.config(bg=MODE_ACTIVE_BG if input_mode=="ROOM" else MODE_IDLE_BG)
    btn_code.config(bg=MODE_ACTIVE_BG if input_mode=="CODE" else MODE_IDLE_BG)
    blink_on = False
    _apply_blink_styles()
    _schedule_blink()
    refresh_headers()

def refresh_headers():
    rv = room_var.get() if room_var.get() else "--"
    cv = code_var.get() if code_var.get() else "    "
    room_value.config(text=rv)
    code_value.config(text=cv.center(CODE_LEN, " "))

def on_digit(d):
    if input_mode=="ROOM":
        cur = room_var.get()
        if len(cur) >= 2: return
        nxt = cur + d
        try:
            n = int(nxt)
            if not (n == ADMIN_ROOM or room_valid(n)):
                return
            room_var.set(nxt)
            refresh_headers()
            if len(nxt) == 2:
                set_mode("CODE")
        except: pass
    else:
        cur = code_var.get()
        if len(cur) < CODE_LEN:
            code_var.set(cur + d)
            refresh_headers()

def on_backspace():
    if input_mode=="ROOM":
        room_var.set(room_var.get()[:-1])
    else:
        code_var.set(code_var.get()[:-1])
    refresh_headers()

def on_clear():
    if input_mode=="ROOM":
        room_var.set("")
    else:
        code_var.set("")
    refresh_headers()

# -------- Overlay plein écran --------
def show_overlay(msg, bg_color, ms):
    overlay_visible[0] = True
    container.grid_remove()
    overlay.config(bg=bg_color)
    overlay_label.config(text=msg, bg=bg_color)
    overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
    root.after(ms, hide_overlay)

def hide_overlay():
    overlay_visible[0] = False
    overlay.place_forget()
    container.grid()
    code_var.set("")
    refresh_headers()

def safe_write_valid(code, room):
    try:
        with open("/tmp/reservation_code.txt", "w") as f:
            f.write("room={};code={}".format(room, code))
    except: pass

def on_validate():
    if input_mode=="ROOM":
        rs = room_var.get()
        if not rs:
            show_overlay("ACCES REFUSE\nCHOISISSEZ CHAMBRE", FAIL_COLOR, STATUS_MS_FAIL); return
        try:
            rn = int(rs)
            if not (rn == ADMIN_ROOM or room_valid(rn)):
                show_overlay("ACCES REFUSE\nCHAMBRE INVALIDE", FAIL_COLOR, STATUS_MS_FAIL); return
        except:
            show_overlay("ACCES REFUSE\nCHAMBRE INVALIDE", FAIL_COLOR, STATUS_MS_FAIL); return
        set_mode("CODE"); return

    rs = room_var.get()
    if not rs:
        show_overlay("ACCES REFUSE\nCHOISISSEZ CHAMBRE", FAIL_COLOR, STATUS_MS_FAIL); return
    try:
        room_num = int(rs)
    except:
        show_overlay("ACCES REFUSE\nCHAMBRE INVALIDE", FAIL_COLOR, STATUS_MS_FAIL); return

    c = code_var.get().strip()
    if len(c) != CODE_LEN or not c.isdigit():
        show_overlay("ACCES REFUSE\nMAUVAIS CODE", FAIL_COLOR, STATUS_MS_FAIL); return

    if room_num == ADMIN_ROOM and c == ADMIN_CODE:
        safe_write_valid(c, room_num)
        show_overlay("ACCES AUTORISE\n(MODE ADMIN)", OK_COLOR, STATUS_MS_OK)
        return

    if not room_valid(room_num):
        show_overlay("ACCES REFUSE\nCHAMBRE INVALIDE", FAIL_COLOR, STATUS_MS_FAIL); return

    ok, reason, it = check_access(c, room_num)
    if ok:
        safe_write_valid(c, room_num)
        show_overlay("ACCES AUTORISE", OK_COLOR, STATUS_MS_OK)
    else:
        show_overlay("ACCES REFUSE\n{}".format(reason or ""), FAIL_COLOR, STATUS_MS_FAIL)

# =========================
#  Blink (clignotement du titre actif)
# =========================
blink_on = False
def _apply_blink_styles():
    active_lbl = room_title if input_mode=="ROOM" else code_title
    other_lbl  = code_title if input_mode=="ROOM" else room_title
    if blink_on:
        active_lbl.config(bg=BLINK_BG_ON, fg="white")
    else:
        active_lbl.config(bg=BLINK_BG_OFF, fg="white")
    other_lbl.config(bg=BG, fg=FG)

def _schedule_blink():
    global blink_on
    blink_on = not blink_on
    _apply_blink_styles()
    root.after(BLINK_MS, _schedule_blink)

# =========================
#  TK SETUP & LAYOUT (GRID propre)
# =========================
root = tk.Tk()
root.title("Reservation Code")
root.attributes("-fullscreen", True)
root.config(cursor="none")
root.focus_force()

W, H = root.winfo_screenwidth(), root.winfo_screenheight()

BG="#121212"; FG="#ffffff"
OK_COLOR="#145a32"; FAIL_COLOR="#922b21"
MODE_ACTIVE_BG="#005577"; MODE_IDLE_BG="#2b2b2b"
BTN_BG="#2b2b2b"; BTN_ACTIVE="#3a3a3a"
ERASE_BG="#8e4d12"; BACK_BG="#7a1f1f"

# Blink
BLINK_BG_ON  = "#0b3d2e"
BLINK_BG_OFF = "#145a32"
BLINK_MS     = 600

root.configure(bg=BG)

# Tailles ajustées (titres un peu plus petits, sans ":")
TITLE_FONT   = ("Arial", max(11, H//20), "bold")  # ↓ légèrement
VALUE_FONT   = ("Arial", max(12, H//14), "bold")
DISPLAY_FONT_STATUS = ("Arial", max(12, H//12), "bold")
btn_font = ("Arial", max(12, H//22), "bold")
btn_font_small = ("Arial", max(10, H//26), "bold")

# Container global -> GRID
container = tk.Frame(root, bg=BG)
container.grid(row=0, column=0, sticky="nsew")
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# Sub-grids
# Rows: 0=top (titres/valeurs), 1=bottom (barre + clavier), 2=spacer (pour remonter le clavier)
container.grid_rowconfigure(0, weight=0)
container.grid_rowconfigure(1, weight=0)
container.grid_rowconfigure(2, weight=1)  # spacer bas -> pousse tout vers le haut
container.grid_columnconfigure(0, weight=1)

# ---- TOP : deux titres + valeurs ----
top = tk.Frame(container, bg=BG)
top.grid(row=0, column=0, sticky="ew", padx=int(W*0.03), pady=(int(H*0.01), int(H*0.005)))

titles = tk.Frame(top, bg=BG)
titles.pack(side="top", fill="x")

room_title = tk.Label(titles, text="CHAMBRE", font=TITLE_FONT, fg=FG, bg=BG, padx=6, pady=2)
code_title = tk.Label(titles, text="CODE DE RÉSERVATION", font=TITLE_FONT, fg=FG, bg=BG, padx=6, pady=2)
room_title.pack(side="left", expand=True)
code_title.pack(side="right", expand=True)

values = tk.Frame(top, bg=BG)
values.pack(side="top", fill="x", pady=(int(H*0.004), 0))
room_value = tk.Label(values, text="--",   font=VALUE_FONT, fg=FG, bg=BG)
code_value = tk.Label(values, text="    ", font=VALUE_FONT, fg=FG, bg=BG)
room_value.pack(side="left", expand=True)
code_value.pack(side="right", expand=True)

# ---- BOTTOM : barre de mode + pavé ----
bottom = tk.Frame(container, bg=BG)
bottom.grid(row=1, column=0, sticky="ew", padx=int(W*0.03))

# Grid interne: 0=barre, 1=clavier
bottom.grid_rowconfigure(0, weight=0)
bottom.grid_rowconfigure(1, weight=0)
bottom.grid_columnconfigure(0, weight=1)

# Barre de mode (grosse, juste au-dessus du pavé)
mode_bar = tk.Frame(bottom, bg=BG)
mode_bar.grid(row=0, column=0, sticky="n", pady=(int(H*0.004), int(H*0.002)))

def make_touch_btn(parent, text, callback, bg, font):
    b = tk.Label(parent, text=text, bg=bg, fg="white", font=font, bd=0, relief="flat")
    def on_down(e): b.config(bg=BTN_ACTIVE)
    def on_up(e):
        b.config(bg=bg)
        x,y = e.x, e.y
        if 0 <= x <= b.winfo_width() and 0 <= y <= b.winfo_height():
            callback()
    def on_leave(e): b.config(bg=bg)
    b.bind("<ButtonPress-1>", on_down)
    b.bind("<ButtonRelease-1>", on_up)
    b.bind("<Leave>", on_leave)
    return b

btn_room = make_touch_btn(mode_bar, "SAISIR CHAMBRE", lambda: set_mode("ROOM"),
                          MODE_ACTIVE_BG, btn_font)
btn_code = make_touch_btn(mode_bar, "SAISIR CODE", lambda: set_mode("CODE"),
                          MODE_IDLE_BG, btn_font)
btn_room.pack(side="left", padx=int(W*0.02))
btn_code.pack(side="left", padx=int(W*0.02))

# Pavé numérique (remonté car spacer en bas prend le reste)
kb_wrap = tk.Frame(bottom, bg=BG)
kb_wrap.grid(row=1, column=0, sticky="n", pady=(int(H*0.004), 0))

kb = tk.Frame(kb_wrap, bg=BG)
kb.pack(fill="both", expand=True)

# Taille relative (large sur 2.8")
kb_width  = int(W * 0.94)
kb_height = int(H * 0.52)  # un peu plus haut pour le remonter
kb_wrap.configure(width=kb_width, height=kb_height)
kb_wrap.pack_propagate(False)

for c in range(4): kb.grid_columnconfigure(c, weight=1, uniform="cols")
for r in range(4): kb.grid_rowconfigure(r, weight=1, uniform="rows")

padx=max(2, W//200); pady=max(2, H//200)

def make_key(parent, label, ontap, bg, font):
    b = tk.Label(parent, text=label, bg=bg, fg="white", font=font, bd=0, relief="flat")
    def on_down(e): b.config(bg=BTN_ACTIVE)
    def on_up(e):
        b.config(bg=bg)
        x,y = e.x, e.y
        if 0 <= x <= b.winfo_width() and 0 <= y <= b.winfo_height():
            ontap()
    def on_leave(e): b.config(bg=bg)
    b.bind("<ButtonPress-1>", on_down)
    b.bind("<ButtonRelease-1>", on_up)
    b.bind("<Leave>", on_leave)
    b.grid_config = dict(sticky="nsew", padx=padx, pady=pady)
    return b

btn_font = ("Arial", max(12, H//22), "bold")
btn_font_small = ("Arial", max(10, H//26), "bold")

def add_key(r, c, text, cb, bg, font):
    w = make_key(kb, text, cb, bg, font)
    w.grid(row=r, column=c, **w.grid_config)

layout = [
    ("1","2","3","EFFACER"),
    ("4","5","6","SUPPR"),
    ("7","8","9","VALIDER"),
    ("", "0","", ""),
]

for r, row in enumerate(layout):
    for c, lab in enumerate(row):
        if lab == "":
            filler = tk.Label(kb, bg=BG)
            filler.grid(row=r, column=c, sticky="nsew", padx=padx, pady=pady)
            continue
        if lab.isdigit():
            add_key(r, c, lab, lambda x=lab: on_digit(x), BTN_BG, btn_font)
        elif lab == "EFFACER":
            add_key(r, c, lab, on_clear, ERASE_BG, btn_font_small)
        elif lab == "SUPPR":
            add_key(r, c, lab, on_backspace, BACK_BG, btn_font_small)
        elif lab == "VALIDER":
            add_key(r, c, lab, on_validate, OK_COLOR, btn_font_small)

# Spacer bas (prend tout le reste -> remonte visuellement la zone clavier)
bottom_spacer = tk.Frame(container, bg=BG, height=1)
bottom_spacer.grid(row=2, column=0, sticky="nsew")

# OVERLAY plein écran
overlay_visible = [False]
overlay = tk.Frame(root, bg="#000000")
overlay_label = tk.Label(overlay, text="", fg="white", bg="#000000",
                         font=DISPLAY_FONT_STATUS, justify="center")
overlay_label.pack(expand=True, fill="both")

# init
code_var = tk.StringVar(value="")
room_var = tk.StringVar(value="")
input_mode = "ROOM"
set_mode("ROOM")
refresh_headers()
root.bind("<Escape>", lambda e: root.destroy())
root.mainloop()
