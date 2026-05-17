import { jsPDF } from 'jspdf';
import type { ReporteOcupacionResponse } from '../../../core/services/booking.service';

export function generateOccupationPdf(data: ReporteOcupacionResponse, lang: string): void {
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

  const formatPct = (v: number): string => v.toFixed(2) + '%';

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
  doc.text(isEs ? 'Reporte de Ocupación' : 'Occupation Report', margin, y);
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
  if (data.fecha_registro) {
    const regLabel = isEs ? 'Hotel registrado desde: ' : 'Hotel registered on: ';
    doc.text(regLabel + formatDate(new Date(data.fecha_registro)), margin, y);
    y += 5;
  }

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
  doc.text(isEs ? 'Total Habitaciones' : 'Total Rooms', margin + 4, y + 5);
  doc.setFontSize(13);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(...DARK);
  doc.text(String(data.total_habitaciones), margin + 4, y + 13);

  const box2X = margin + boxW + 5;
  doc.setFillColor(...LIGHT_BG);
  doc.roundedRect(box2X, y, boxW, boxH, 3, 3, 'F');
  doc.setFontSize(8);
  doc.setTextColor(...GRAY);
  doc.setFont('helvetica', 'normal');
  doc.text(isEs ? 'Tasa de Ocupación Global' : 'Global Occupation Rate', box2X + 4, y + 5);
  doc.setFontSize(13);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(...DARK);
  doc.text(formatPct(data.tasa_ocupacion_global), box2X + 4, y + 13);

  y += boxH + 10;

  // ── Table 1: por mes ──────────────────────────────────────────────────────
  doc.setFontSize(11);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(...DARK);
  doc.text(isEs ? 'Ocupación por Mes' : 'Occupation by Month', margin, y);
  y += 6;

  const colMes: [number, number, number, number, number] = [18, 38, 35, 35, 0];
  colMes[4] = contentWidth - colMes[0] - colMes[1] - colMes[2] - colMes[3];
  const headersMes = isEs
    ? ['Año', 'Mes', 'Noches Ocup.', 'Noches Disp.', '% Ocup.']
    : ['Year', 'Month', 'Occupied N.', 'Avail. N.', '% Occup.'];
  const rowH = 8;
  const cellPad = 3;

  const drawMesHeader = (): void => {
    doc.setFillColor(...TABLE_HEADER_BG);
    doc.rect(margin, y, contentWidth, rowH, 'F');
    doc.setFontSize(8);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(255, 255, 255);
    let cx = margin;
    for (let i = 0; i < headersMes.length; i++) {
      const align = i >= 2 ? 'right' : 'left';
      const tx = align === 'right' ? cx + colMes[i] - cellPad : cx + cellPad;
      doc.text(headersMes[i], tx, y + 5.5, { align });
      cx += colMes[i];
    }
    y += rowH;
  };

  drawMesHeader();

  let totalOcupMes = 0;
  let totalDispMes = 0;

  for (let i = 0; i < data.ocupacion_por_mes.length; i++) {
    if (y + rowH > usableBottom) {
      doc.addPage();
      y = margin;
      drawMesHeader();
    }
    const row = data.ocupacion_por_mes[i];
    totalOcupMes += row.noches_ocupadas;
    totalDispMes += row.noches_disponibles;

    if (i % 2 === 1) {
      doc.setFillColor(...ROW_ALT_BG);
      doc.rect(margin, y, contentWidth, rowH, 'F');
    }
    doc.setFontSize(8);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...DARK);

    const cells = [
      String(row.anio),
      monthNames[row.mes - 1] ?? String(row.mes),
      String(row.noches_ocupadas),
      String(row.noches_disponibles),
      formatPct(row.tasa_ocupacion),
    ];
    let cx = margin;
    for (let j = 0; j < cells.length; j++) {
      const align = j >= 2 ? 'right' : 'left';
      const tx = align === 'right' ? cx + colMes[j] - cellPad : cx + cellPad;
      doc.text(cells[j], tx, y + 5.5, { align });
      cx += colMes[j];
    }
    y += rowH;
  }

  // Total row for mes table
  if (y + rowH > usableBottom) {
    doc.addPage();
    y = margin;
  }
  doc.setFillColor(...TOTAL_ROW_BG);
  doc.rect(margin, y, contentWidth, rowH, 'F');
  doc.setFontSize(8);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(...DARK);
  const totalLabel = isEs ? 'Total' : 'Total';
  doc.text(totalLabel, margin + cellPad, y + 5.5);
  const totalMesCells = ['', '', String(totalOcupMes), String(totalDispMes), formatPct(data.tasa_ocupacion_global)];
  let cxT = margin;
  for (let j = 0; j < totalMesCells.length; j++) {
    if (totalMesCells[j]) {
      const align = j >= 2 ? 'right' : 'left';
      const tx = align === 'right' ? cxT + colMes[j] - cellPad : cxT + cellPad;
      doc.text(totalMesCells[j], tx, y + 5.5, { align });
    }
    cxT += colMes[j];
  }
  y += rowH + 10;

  // ── Table 2: por habitación ───────────────────────────────────────────────
  if (y + 20 > usableBottom) {
    doc.addPage();
    y = margin;
  }

  doc.setFontSize(11);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(...DARK);
  doc.text(isEs ? 'Ocupación por Habitación' : 'Occupation by Room', margin, y);
  y += 6;

  const colHab: [number, number, number, number, number] = [22, 22, 35, 35, 0];
  colHab[4] = contentWidth - colHab[0] - colHab[1] - colHab[2] - colHab[3];
  const headersHab = isEs
    ? ['Número', 'Cap.', 'Noches Ocup.', 'Noches Disp.', '% Ocup.']
    : ['Number', 'Cap.', 'Occupied N.', 'Avail. N.', '% Occup.'];

  const drawHabHeader = (): void => {
    doc.setFillColor(...TABLE_HEADER_BG);
    doc.rect(margin, y, contentWidth, rowH, 'F');
    doc.setFontSize(8);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(255, 255, 255);
    let cx = margin;
    for (let i = 0; i < headersHab.length; i++) {
      const align = i >= 2 ? 'right' : 'left';
      const tx = align === 'right' ? cx + colHab[i] - cellPad : cx + cellPad;
      doc.text(headersHab[i], tx, y + 5.5, { align });
      cx += colHab[i];
    }
    y += rowH;
  };

  drawHabHeader();

  for (let i = 0; i < data.ocupacion_por_habitacion.length; i++) {
    if (y + rowH > usableBottom) {
      doc.addPage();
      y = margin;
      drawHabHeader();
    }
    const row = data.ocupacion_por_habitacion[i];
    if (i % 2 === 1) {
      doc.setFillColor(...ROW_ALT_BG);
      doc.rect(margin, y, contentWidth, rowH, 'F');
    }
    doc.setFontSize(8);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...DARK);

    const cells = [
      row.numero,
      String(row.capacidad),
      String(row.noches_ocupadas),
      String(row.noches_disponibles),
      formatPct(row.tasa_ocupacion),
    ];
    let cx = margin;
    for (let j = 0; j < cells.length; j++) {
      const align = j >= 2 ? 'right' : 'left';
      const tx = align === 'right' ? cx + colHab[j] - cellPad : cx + cellPad;
      doc.text(cells[j], tx, y + 5.5, { align });
      cx += colHab[j];
    }
    y += rowH;
  }

  // ── Footers ───────────────────────────────────────────────────────────────
  const totalPagesRef = doc.internal.pages.length - 1;
  for (let p = 1; p <= totalPagesRef; p++) {
    doc.setPage(p);
    drawFooter(p, totalPagesRef);
  }

  doc.save(isEs ? 'reporte-ocupacion.pdf' : 'occupation-report.pdf');
}
