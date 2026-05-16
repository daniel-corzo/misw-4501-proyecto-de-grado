import { jsPDF } from 'jspdf';
import type { ReporteIngresosResponse } from '../../../core/services/booking.service';

export function generateRevenuePdf(data: ReporteIngresosResponse, lang: string): void {
  const isEs = lang === 'es';

  const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const margin = 15;
  const contentWidth = pageWidth - margin * 2;

  const BLUE: [number, number, number] = [30, 80, 180];
  const DARK: [number, number, number] = [30, 30, 30];
  const GRAY: [number, number, number] = [100, 100, 100];
  const LIGHT_BG: [number, number, number] = [240, 245, 255];
  const TABLE_HEADER_BG: [number, number, number] = [30, 80, 180];
  const ROW_ALT_BG: [number, number, number] = [247, 250, 255];
  const TOTAL_ROW_BG: [number, number, number] = [220, 230, 250];
  const FOOTER_BORDER: [number, number, number] = [200, 200, 200];

  const monthNames = isEs
    ? ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
    : ['January','February','March','April','May','June','July','August','September','October','November','December'];

  const formatCurrency = (amount: number): string =>
    '$' + new Intl.NumberFormat(isEs ? 'es-CO' : 'en-US').format(amount);

  const formatDate = (d: Date): string =>
    new Intl.DateTimeFormat(isEs ? 'es-CO' : 'en-US', {
      year: 'numeric', month: 'long', day: 'numeric',
    }).format(d);

  const footerHeight = 10;
  const usableBottom = pageHeight - footerHeight - 5;

  let y = margin;

  const drawFooter = (pageNum: number, totalPages: number): void => {
    const fy = pageHeight - footerHeight;
    doc.setDrawColor(...FOOTER_BORDER);
    doc.setLineWidth(0.3);
    doc.line(margin, fy, pageWidth - margin, fy);
    doc.setFontSize(8);
    doc.setTextColor(...GRAY);
    const leftText  = isEs ? 'TravelHub — Confidencial' : 'TravelHub — Confidential';
    const rightText = isEs ? `Página ${pageNum} de ${totalPages}` : `Page ${pageNum} of ${totalPages}`;
    doc.text(leftText, margin, fy + 5);
    doc.text(rightText, pageWidth - margin, fy + 5, { align: 'right' });
  };

  // ── Header ───────────────────────────────────────────────────────────────
  doc.setFontSize(22);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(...BLUE);
  doc.text('TravelHub', margin, y);
  y += 8;

  doc.setFontSize(16);
  doc.setTextColor(...DARK);
  doc.text(isEs ? 'Reporte de Ingresos' : 'Income Report', margin, y);
  y += 7;

  doc.setFontSize(11);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(...GRAY);
  if (data.nombre_hotel) {
    doc.text(data.nombre_hotel, margin, y);
    y += 6;
  }
  doc.text((isEs ? 'Generado el: ' : 'Generated on: ') + formatDate(new Date()), margin, y);
  y += 5;

  doc.setDrawColor(...BLUE);
  doc.setLineWidth(0.5);
  doc.line(margin, y, pageWidth - margin, y);
  y += 8;

  // ── Summary boxes ────────────────────────────────────────────────────────
  const boxH = 18;
  const boxW = (contentWidth - 5) / 2;

  doc.setFillColor(...LIGHT_BG);
  doc.roundedRect(margin, y, boxW, boxH, 3, 3, 'F');
  doc.setFontSize(8);
  doc.setTextColor(...GRAY);
  doc.setFont('helvetica', 'normal');
  doc.text(isEs ? 'Total Ingresos' : 'Total Income', margin + 4, y + 5);
  doc.setFontSize(13);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(...DARK);
  doc.text(formatCurrency(data.total_general), margin + 4, y + 13);

  const box2X = margin + boxW + 5;
  doc.setFillColor(...LIGHT_BG);
  doc.roundedRect(box2X, y, boxW, boxH, 3, 3, 'F');
  doc.setFontSize(8);
  doc.setTextColor(...GRAY);
  doc.setFont('helvetica', 'normal');
  doc.text(isEs ? 'Total Pagos' : 'Total Payments', box2X + 4, y + 5);
  doc.setFontSize(13);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(...DARK);
  doc.text(String(data.total_pagos), box2X + 4, y + 13);

  y += boxH + 10;

  // ── Table ────────────────────────────────────────────────────────────────
  const colWidths: [number, number, number, number] = [20, 40, 45, 0];
  colWidths[3] = contentWidth - colWidths[0] - colWidths[1] - colWidths[2];
  const colHeaders = isEs
    ? ['Año', 'Mes', 'Pagos Realizados', 'Ingresos Totales']
    : ['Year', 'Month', 'Payments', 'Total Income'];
  const rowH = 8;
  const cellPad = 3;

  let currentPage = 1;

  const drawTableHeader = (): void => {
    doc.setFillColor(...TABLE_HEADER_BG);
    doc.rect(margin, y, contentWidth, rowH, 'F');
    doc.setFontSize(9);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(255, 255, 255);
    let cx = margin;
    for (let i = 0; i < colHeaders.length; i++) {
      const align = i >= 2 ? 'right' : 'left';
      const tx = align === 'right' ? cx + colWidths[i] - cellPad : cx + cellPad;
      doc.text(colHeaders[i], tx, y + 5.5, { align });
      cx += colWidths[i];
    }
    y += rowH;
  };

  drawTableHeader();

  for (let i = 0; i < data.ingresos_por_mes.length; i++) {
    if (y + rowH > usableBottom) {
      drawFooter(currentPage, 1);
      doc.addPage();
      currentPage++;
      y = margin;
      drawTableHeader();
    }

    const row = data.ingresos_por_mes[i];
    if (i % 2 === 1) {
      doc.setFillColor(...ROW_ALT_BG);
      doc.rect(margin, y, contentWidth, rowH, 'F');
    }

    doc.setFontSize(9);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...DARK);

    const cells = [
      String(row.anio),
      monthNames[row.mes - 1] ?? String(row.mes),
      String(row.total_pagos),
      formatCurrency(row.ingresos_totales),
    ];

    let cx = margin;
    for (let j = 0; j < cells.length; j++) {
      const align = j >= 2 ? 'right' : 'left';
      const tx = align === 'right' ? cx + colWidths[j] - cellPad : cx + cellPad;
      doc.text(cells[j], tx, y + 5.5, { align });
      cx += colWidths[j];
    }
    y += rowH;
  }

  // ── Total row ────────────────────────────────────────────────────────────
  if (y + rowH > usableBottom) {
    drawFooter(currentPage, 1);
    doc.addPage();
    currentPage++;
    y = margin;
  }
  doc.setFillColor(...TOTAL_ROW_BG);
  doc.rect(margin, y, contentWidth, rowH, 'F');
  doc.setFontSize(9);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(...DARK);
  doc.text(isEs ? 'Total General' : 'Grand Total', margin + contentWidth / 2, y + 5.5, { align: 'center' });
  const totalCells = ['', '', String(data.total_pagos), formatCurrency(data.total_general)];
  let cx = margin;
  for (let j = 0; j < totalCells.length; j++) {
    if (totalCells[j]) {
      const align = j >= 2 ? 'right' : 'left';
      const tx = align === 'right' ? cx + colWidths[j] - cellPad : cx + cellPad;
      doc.text(totalCells[j], tx, y + 5.5, { align });
    }
    cx += colWidths[j];
  }
  y += rowH;

  // ── Footers on all pages ─────────────────────────────────────────────────
  const totalPagesRef = doc.internal.pages.length - 1;
  for (let p = 1; p <= totalPagesRef; p++) {
    doc.setPage(p);
    drawFooter(p, totalPagesRef);
  }

  doc.save(isEs ? 'reporte-ingresos.pdf' : 'income-report.pdf');
}
