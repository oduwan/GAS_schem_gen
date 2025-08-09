from __future__ import annotations
"""PDF drawing utilities (ReportLab).

Coordinates: points (pt). Each visual block is 36x36 pt, per spec.
Vertical connections only; bus bar is used when >1 inverter.
"""
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.lib import colors
from ..core.config import ICON, PADDING

class Drawer:
    def __init__(self, c: pdfcanvas.Canvas):
        self.c = c
        self.page_w, self.page_h = A4

    def draw_box(self, x, y, size=ICON, label: str = ""):
        self.c.rect(x, y, size, size)
        if label:
            self.c.setFont("Helvetica", 8)
            self.c.drawCentredString(x + size/2, y + size + 4, label)

    def vline(self, x, y1, y2):
        self.c.line(x, y1, x, y2)

    def hline(self, x1, y, x2):
        self.c.line(x1, y, x2, y)

    def center_x(self, width):
        return (self.page_w - width) / 2

    def draw_schema(self, company, dyn, sel, out_path: str):
        self.c.setTitle("GAS schema")
        margin = 25
        self.c.setFont("Helvetica-Bold", 12)
        self.c.drawCentredString(self.page_w/2, self.page_h - margin, f"GAS schema (Pmax={sel.pmax_kw:.1f} kW)")
        self.c.setFont("Helvetica", 9)
        self.c.drawCentredString(self.page_w/2, self.page_h - margin - 14, f"{company.company_name} | {company.phone} | {company.email}")

        y = self.page_h - 100
        center = self.page_w / 2

        # PS
        ps_x = center - ICON/2
        ps_y = y
        self.draw_box(ps_x, ps_y, ICON, label="PS")

        # GAS inner blocks
        inner_labels: list[str] = []
        if sel.direct_metering:
            inner_labels += [f"Įv. automatas {sel.main_breaker_a} A", "Skaitiklis"]
        else:
            inner_labels += [f"MCCB {sel.main_breaker_a} A", f"TT {sel.ct_rating_a} A", "Mat. gnybtai", "Skaitiklis"]
        for i in range(dyn.inverter_count):
            inner_labels.append(f"Automatas {i+1}: {sel.per_inv_breaker_a} A")

        cols = 2
        rows = (len(inner_labels) + cols - 1) // cols
        gas_w = cols*ICON + (cols-1)*PADDING + 2*PADDING
        gas_h = rows*ICON + (rows-1)*PADDING + 2*PADDING
        gas_x = self.center_x(gas_w)
        gas_y = ps_y - 120 - gas_h

        # GAS frame
        self.c.setStrokeColor(colors.black)
        self.c.rect(gas_x, gas_y, gas_w, gas_h)
        self.c.setFont("Helvetica-Bold", 10)
        self.c.drawCentredString(gas_x + gas_w/2, gas_y + gas_h + 6, "GAS")

        # 36×36 blocks inside GAS
        self.c.setFont("Helvetica", 8)
        for idx, label in enumerate(inner_labels):
            r = idx // cols
            ccol = idx % cols
            bx = gas_x + PADDING + ccol*(ICON + PADDING)
            by = gas_y + gas_h - PADDING - ICON - r*(ICON + PADDING)
            self.c.rect(bx, by, ICON, ICON)
            self.c.drawCentredString(bx + ICON/2, by + ICON/2 - 4, label)

        # PS → GAS
        self.vline(center, ps_y, gas_y + gas_h)

        # Inverters
        invs_y = gas_y - 120
        total_width = dyn.inverter_count*ICON + (dyn.inverter_count-1)*PADDING
        start_x = center - total_width/2
        centers = []
        for i in range(dyn.inverter_count):
            x = start_x + i*(ICON + PADDING)
            self.c.rect(x, invs_y, ICON, ICON)
            self.c.setFont("Helvetica", 8)
            self.c.drawCentredString(x + ICON/2, invs_y + ICON + 4, f"KEITIKLIS {i+1}")
            self.c.drawCentredString(x + ICON/2, invs_y - 10, f"{dyn.inverter_powers_kw[i]} kW")
            centers.append(x + ICON/2)

        if dyn.inverter_count == 1:
            self.vline(centers[0], invs_y + ICON, gas_y)
        else:
            bus_y = invs_y + ICON + 40
            self.hline(start_x, bus_y, start_x + total_width)
            for cx in centers:
                self.vline(cx, invs_y + ICON, bus_y)
            self.vline(center, bus_y, gas_y)

        # footer notes
        self.c.setFont("Helvetica", 8)
        self.c.drawString(30, 40, f"Schema: {'Tiesioginis skaitiklis' if sel.direct_metering else 'Matavimo transformatoriai'}")
        self.c.drawString(30, 28, f"Įvado apsauga: {sel.main_breaker_a} A; Inverterių automatai: {sel.per_inv_breaker_a} A")
        if not sel.direct_metering:
            self.c.drawString(30, 16, f"TT nominalas: {sel.ct_rating_a} A")

        self.c.showPage(); self.c.save()