from __future__ import annotations
import tkinter as tk
from tkinter import ttk, filedialog
from ..core.config import APP_NAME
from ..core.model import AppState, StaticConfig
from ..core.intents import Intent
from ..infra.store import Store
from ..core.reducer import reducer

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("720x560")
        self.resizable(False, False)

        self.store = Store(AppState(), reducer)
        self.store.subscribe(self.render)

        # UI scaffold
        self.notebook = ttk.Notebook(self)
        self.tab_dynamic = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_dynamic, text="Schema")
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.dynamic_wrapper = ttk.Frame(self.tab_dynamic)
        self.dynamic_wrapper.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        # top bar
        self.bar = ttk.Frame(self)
        self.bar.pack(fill=tk.X, padx=12, pady=8)
        self.btn_settings = ttk.Button(self.bar, text="Nustatymai", command=lambda: self.store.dispatch(Intent.OPEN_SETTINGS))
        self.btn_settings.pack(side=tk.LEFT)
        self.btn_generate = ttk.Button(self.bar, text="Išsaugoti PDF", command=lambda: self.store.dispatch(Intent.GENERATE))
        self.btn_generate.pack(side=tk.RIGHT)

        self.inv_count_var = tk.IntVar(value=1)
        self.power_vars: list[tk.StringVar] = []

        self.status = ttk.Label(self, text="", foreground="gray")
        self.status.pack(fill=tk.X, padx=12, pady=4)

        self.settings_win: tk.Toplevel | None = None

        self.store.dispatch(Intent.APP_START)

    def render(self, state: AppState):
        self.status.configure(text=state.ui.message)
        self.btn_generate.configure(state=(tk.NORMAL if state.ui.can_generate else tk.DISABLED))

        for w in self.dynamic_wrapper.winfo_children():
            w.destroy()
        row1 = ttk.Frame(self.dynamic_wrapper)
        row1.pack(fill=tk.X, pady=6)
        ttk.Label(row1, text="Inverterių skaičius (1..3)*", width=32).pack(side=tk.LEFT)
        spin = ttk.Spinbox(row1, from_=1, to=3, textvariable=self.inv_count_var, width=5,
                           command=lambda: self.store.dispatch(Intent.DYN_SET_COUNT, int(self.inv_count_var.get())))
        self.inv_count_var.set(state.dyn.inverter_count)
        spin.pack(side=tk.LEFT)

        powers_frame = ttk.Frame(self.dynamic_wrapper)
        powers_frame.pack(fill=tk.X, pady=8)
        self.power_vars = []
        for i in range(state.dyn.inverter_count):
            var = tk.StringVar(value=str(state.dyn.inverter_powers_kw[i]))
            self.power_vars.append(var)
            row = ttk.Frame(powers_frame)
            row.pack(fill=tk.X, pady=4)
            ttk.Label(row, text=f"Inverteris {i+1} galia (kW)*", width=32).pack(side=tk.LEFT)
            e = ttk.Entry(row, textvariable=var, width=10)
            e.pack(side=tk.LEFT)
            e.bind("<FocusOut>", lambda _e, idx=i, v=var: self.store.dispatch(Intent.DYN_SET_POWER, (idx, v.get())))
            ttk.Label(row, text="(5–150)").pack(side=tk.LEFT, padx=6)

        if state.ui.settings_open and self.settings_win is None:
            self.open_settings(state)
        if (not state.ui.settings_open) and self.settings_win is not None:
            try:
                self.settings_win.destroy()
            except Exception:
                pass
            self.settings_win = None

    def open_settings(self, state: AppState):
        self.settings_win = tk.Toplevel(self)
        self.settings_win.title("Programos nustatymai")
        self.settings_win.geometry("600x360")
        self.settings_win.transient(self)
        self.settings_win.grab_set()

        cfg = state.config or StaticConfig()
        v_company = tk.StringVar(value=cfg.company_name)
        v_phone = tk.StringVar(value=cfg.phone)
        v_email = tk.StringVar(value=cfg.email)
        v_out = tk.StringVar(value=cfg.output_dir)

        frm = ttk.Frame(self.settings_win)
        frm.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        def row(label, var, browse=False):
            r = ttk.Frame(frm); r.pack(fill=tk.X, pady=6)
            ttk.Label(r, text=label, width=28).pack(side=tk.LEFT)
            ent = ttk.Entry(r, textvariable=var); ent.pack(side=tk.LEFT, fill=tk.X, expand=True)
            if browse:
                ttk.Button(r, text="Pasirinkti…", command=lambda: self.pick_dir(var)).pack(side=tk.LEFT, padx=6)
            return ent

        row("Organizacijos pavadinimas*", v_company)
        row("Telefonas*", v_phone)
        row("El. paštas*", v_email)
        row("Išsaugojimo kelias*", v_out, browse=True)

        bar = ttk.Frame(self.settings_win); bar.pack(fill=tk.X, padx=16, pady=8)
        ttk.Button(bar, text="Atšaukti", command=lambda: self.store.dispatch(Intent.CLOSE_SETTINGS)).pack(side=tk.RIGHT, padx=6)
        def do_save():
            cfg2 = StaticConfig(v_company.get(), v_phone.get(), v_email.get(), v_out.get())
            self.store.dispatch(Intent.SETTINGS_EDIT, {
                "company_name": cfg2.company_name,
                "phone": cfg2.phone,
                "email": cfg2.email,
                "output_dir": cfg2.output_dir,
            })
            self.store.dispatch(Intent.SETTINGS_SAVE, cfg2)
        ttk.Button(bar, text="Išsaugoti", command=do_save).pack(side=tk.RIGHT)

    def pick_dir(self, var: tk.StringVar):
        d = filedialog.askdirectory()
        if d:
            var.set(d)

def main():
    app = App(); app.mainloop()