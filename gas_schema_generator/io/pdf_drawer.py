from __future__ import annotations

from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

from ..core.config import ICON, PADDING
from ..core.model import DynamicParams, Selection, StaticConfig
from ..infra.l10n import get_pdf_label

Canvas = Any  # reportlab neturi tipų — laikom kaip Any


class Drawer:
    def __init__(self, c: Canvas) -> None:
        self.c = c
        self.page_w: float
        self.page_h: float
        self.page_w, self.page_h = A4

    def draw_box(self, x: float, y: float, size: float = ICON, label: str = "") -> None:
        self.c.rect(x, y, size, size)
        if label:
            self.c.setFont("Helvetica", 8)
            self.c.drawCentredString(x + size / 2, y + size + 4, label)

    def vline(self, x: float, y1: float, y2: float) -> None:
        self.c.line(x, y1, x, y2)

    def hline(self, x1: float, y: float, x2: float) -> None:
        self.c.line(x1, y, x2, y)

    def center_x(self, width: float) -> float:
        return float((self.page_w - width) / 2.0)

    def draw_schema(self, company: StaticConfig, dyn: DynamicParams, sel: Selection, out_path: str) -> None:
        self.c.setTitle(get_pdf_label("pdf_title", company.lang))
        margin = 25
        self.c.setFont("Helvetica-Bold", 12)
        self.c.drawCentredString(self.page_w / 2, self.page_h - margin, get_pdf_label("pdf_header", company.lang).format(P = f"{sel.pmax_kw:.3f}"))
        self.c.setFont("Helvetica", 9)
        self.c.drawCentredString(
            self.page_w / 2,
            self.page_h - margin - 14,
            f"{company.company_name} | {company.phone} | {company.email}",
        )

        y = self.page_h - 100
        center = self.page_w / 2

        # PS
        ps_x = center - ICON / 2
        ps_y = y
        self.draw_box(ps_x, ps_y, ICON, label=get_pdf_label("ps", company.lang))

        # GAS inner blocks
        inner_labels: list[str] = []
        if sel.direct_metering:
            inner_labels += [get_pdf_label("direct_meter", company.lang)]
            inner_labels += [get_pdf_label("main_breaker_fmt", company.lang).format(a=sel.main_breaker_a)]
        else:
            inner_labels += [get_pdf_label("mccb_fmt", company.lang).format(a=sel.main_breaker_a)]
            inner_labels += [get_pdf_label("ct_fmt", company.lang).format(a=sel.ct_rating_a)]
            inner_labels += [get_pdf_label("meas_terminals", company.lang)]
            inner_labels += [get_pdf_label("meter", company.lang)]
        for i in range(dyn.inverter_count):
            inner_labels.append(get_pdf_label("per_inverter_breaker", company.lang).format(n=i+1, a=sel.per_inv_breaker_a))

        cols = 2
        rows = (len(inner_labels) + cols - 1) // cols
        gas_w = cols * ICON + (cols - 1) * PADDING + 2 * PADDING
        gas_h = rows * ICON + (rows - 1) * PADDING + 2 * PADDING
        gas_x = self.center_x(gas_w)
        gas_y = ps_y - 120 - gas_h

        # GAS frame
        self.c.setStrokeColor(colors.black)
        self.c.rect(gas_x, gas_y, gas_w, gas_h)
        self.c.setFont("Helvetica-Bold", 10)
        self.c.drawCentredString(gas_x + gas_w / 2, gas_y + gas_h + 6, get_pdf_label("gas", company.lang))

        # 36×36 blocks inside GAS
        self.c.setFont("Helvetica", 8)
        for idx, label in enumerate(inner_labels):
            r = idx // cols
            ccol = idx % cols
            bx = gas_x + PADDING + ccol * (ICON + PADDING)
            by = gas_y + gas_h - PADDING - ICON - r * (ICON + PADDING)
            self.c.rect(bx, by, ICON, ICON)
            self.c.drawCentredString(bx + ICON / 2, by + ICON / 2 - 4, label)

        # PS → GAS
        self.vline(center, ps_y, gas_y + gas_h)

        # Inverters
        invs_y = gas_y - 120
        total_width = dyn.inverter_count * ICON + (dyn.inverter_count - 1) * PADDING
        start_x = center - total_width / 2
        centers: list[float] = []
        for i in range(dyn.inverter_count):
            x = start_x + i * (ICON + PADDING)
            self.c.rect(x, invs_y, ICON, ICON)
            self.c.setFont("Helvetica", 8)
            self.c.drawCentredString(x + ICON / 2, invs_y + ICON + 4, get_pdf_label("inv_n", company.lang).format(n=i+1))
            self.c.drawCentredString(x + ICON / 2, invs_y - 10, f"{dyn.inverter_powers_kw[i]} kW")
            centers.append(x + ICON / 2)

        if dyn.inverter_count == 1:
            self.vline(centers[0], invs_y + ICON, gas_y)
        else:
            bus_y = invs_y + ICON + 40
            self.hline(start_x, bus_y, start_x + total_width)
            for cx in centers:
                self.vline(cx, invs_y + ICON, bus_y)
            self.vline(center, bus_y, gas_y)

        # footer notes
        footer = get_pdf_label("footer_direct", company.lang) if sel.direct_metering else get_pdf_label("footer_ct", company.lang)
        self.c.setFont("Helvetica", 8)
        self.c.drawString (30, 40, footer)
        self.c.drawString(
            30, 28,
            get_pdf_label("footer_inv_breakers_fmt", company.lang).format(
                main_a=sel.main_breaker_a, per_a=sel.per_inv_breaker_a
            ),
        )
        if not sel.direct_metering and sel.ct_rating_a is not None:
            self.c.drawString(30, 16, get_pdf_label("footer_ct_rating_fmt", company.lang).format(ct_a=sel.ct_rating_a))
        self.c.showPage()
        self.c.save()
