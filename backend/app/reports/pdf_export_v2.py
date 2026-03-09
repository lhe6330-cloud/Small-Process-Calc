"""
PDF 报告导出模块 - V2.0 新增（模式 4 和模式 5）
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import io
import os


def register_chinese_font():
    """注册中文字体"""
    font_paths = [
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\simsun.ttc",
        r"C:\Windows\Fonts\simhei.ttf",
    ]
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('Chinese', font_path))
                return 'Chinese'
            except:
                continue
    return 'Helvetica'


def export_mode4_pdf(data: dict, input_params: dict) -> bytes:
    """Export Mode 4 PDF Report (Separator Design)"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    
    font_name = register_chinese_font()
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18,
        textColor=colors.HexColor('#00D4FF'), alignment=TA_CENTER, fontName=font_name, spaceAfter=20)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14,
        textColor=colors.HexColor('#00D4FF'), fontName=font_name, spaceAfter=12, spaceBefore=12)
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'], fontSize=10,
        textColor=colors.HexColor('#333333'), fontName=font_name)
    
    elements = []
    
    # Title
    elements.append(Paragraph("PDS CALC V2.0 - Separator Design Report", title_style))
    elements.append(Paragraph("Mode 4: Process Node Separator", ParagraphStyle('Subtitle', parent=normal_style, 
        alignment=TA_CENTER, fontSize=12)))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
        ParagraphStyle('Time', parent=normal_style, alignment=TA_CENTER, textColor=colors.gray)))
    elements.append(Spacer(1, 0.5*cm))
    
    # Node Parameters
    elements.append(Paragraph("Node Parameters", heading_style))
    node_params = input_params.get('node_params', {})
    input_data = [
        ['Parameter', 'Value'],
        ['Position', input_params.get('node_id', '-')],
        ['Pressure (MPa.G)', str(node_params.get('p', '-'))],
        ['Temperature (C)', str(node_params.get('t', '-'))],
        ['Flow Rate', f"{node_params.get('flow_rate', 0)} {node_params.get('flow_unit', '')}"],
        ['Gas Density (kg/m3)', str(node_params.get('rho', '-'))],
    ]
    input_table = Table(input_data, colWidths=[6*cm, 6*cm])
    input_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), font_name),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(input_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # VLE Result
    vle_result = data.get('vle', {})
    if vle_result and not vle_result.get('skip', False):
        elements.append(Paragraph("Vapor-Liquid Equilibrium", heading_style))
        vle_data = [
            ['Parameter', 'Value'],
            ['Vapor Fraction', f"{vle_result.get('vapor_frac', 0) * 100:.1f} %"],
            ['Liquid Fraction', f"{vle_result.get('liquid_frac', 0) * 100:.1f} %"],
            ['Liquid Flow (T/h)', f"{vle_result.get('liquid_flow', 0):.2f}"],
        ]
        vle_table = Table(vle_data, colWidths=[6*cm, 6*cm])
        vle_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(vle_table)
        elements.append(Spacer(1, 0.5*cm))
    
    # Separator Dimensions
    elements.append(Paragraph("Separator Dimensions", heading_style))
    result_data = [
        ['Parameter', 'Value'],
        ['Diameter (mm)', str(data.get('diameter', 0))],
        ['Length (mm)', str(data.get('length', 0))],
        ['Residence Time (s)', f"{data.get('residence_time', 0):.1f}"],
        ['Check', 'OK' if data.get('check_passed') else 'WARN'],
    ]
    result_table = Table(result_data, colWidths=[6*cm, 6*cm])
    result_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00D4FF')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(result_table)
    
    # Footer
    elements.append(Spacer(1, 1*cm))
    footer = Paragraph("<para alignment='center'><font color='gray' size='8'>PDS CALC V2.0 | {}</font></para>".format(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')), normal_style)
    elements.append(footer)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.read()


def export_mode5_pdf(data: dict, input_params: dict) -> bytes:
    """Export Mode 5 PDF Report (Turbine 1D Design)"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    
    font_name = register_chinese_font()
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18,
        textColor=colors.HexColor('#00D4FF'), alignment=TA_CENTER, fontName=font_name, spaceAfter=20)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14,
        textColor=colors.HexColor('#00D4FF'), fontName=font_name, spaceAfter=12, spaceBefore=12)
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'], fontSize=10,
        textColor=colors.HexColor('#333333'), fontName=font_name)
    
    elements = []
    
    # Title
    elements.append(Paragraph("PDS CALC V2.0 - Turbine 1D Design Report", title_style))
    elements.append(Paragraph("Mode 5: Radial Turbine Throughflow Design", ParagraphStyle('Subtitle', parent=normal_style, 
        alignment=TA_CENTER, fontSize=12)))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
        ParagraphStyle('Time', parent=normal_style, alignment=TA_CENTER, textColor=colors.gray)))
    elements.append(Spacer(1, 0.5*cm))
    
    # Design Parameters
    elements.append(Paragraph("Design Parameters", heading_style))
    design_data = [
        ['Parameter', 'Value'],
        ['Speed (rpm)', str(input_params.get('speed_rpm', 3000))],
        ['Speed Ratio (u/C0)', str(input_params.get('speed_ratio', 0.65))],
        ['Reaction (%)', str(input_params.get('reaction', 50))],
    ]
    design_table = Table(design_data, colWidths=[6*cm, 6*cm])
    design_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(design_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # Dimensions
    elements.append(Paragraph("Dimensions", heading_style))
    dims = data.get('dimensions', {})
    dim_data = [
        ['Parameter', 'Symbol', 'Value (mm)'],
        ['Impeller Outer Diameter', 'D1', str(dims.get('D1', 0))],
        ['Impeller Inner Diameter', 'D2', str(dims.get('D2', 0))],
        ['Inlet Blade Height', 'b1', str(dims.get('b1', 0))],
        ['Outlet Blade Height', 'b2', str(dims.get('b2', 0))],
    ]
    dim_table = Table(dim_data, colWidths=[4*cm, 2*cm, 4*cm])
    dim_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00D4FF')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(dim_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # Velocity Triangle - Inlet
    elements.append(Paragraph("Velocity Triangle - Inlet", heading_style))
    vel_in = data.get('velocity_triangle_in', {})
    vel_in_data = [
        ['Parameter', 'Value'],
        ['Absolute Velocity C1', f"{vel_in.get('C1', 0)} m/s"],
        ['Relative Velocity W1', f"{vel_in.get('W1', 0)} m/s"],
        ['Tangential Velocity U1', f"{vel_in.get('U1', 0)} m/s"],
        ['Absolute Flow Angle alpha1', f"{vel_in.get('alpha1', 0)} deg"],
        ['Relative Flow Angle beta1', f"{vel_in.get('beta1', 0)} deg"],
    ]
    vel_in_table = Table(vel_in_data, colWidths=[6*cm, 6*cm])
    vel_in_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(vel_in_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # Velocity Triangle - Outlet
    elements.append(Paragraph("Velocity Triangle - Outlet", heading_style))
    vel_out = data.get('velocity_triangle_out', {})
    vel_out_data = [
        ['Parameter', 'Value'],
        ['Absolute Velocity C2', f"{vel_out.get('C2', 0)} m/s"],
        ['Relative Velocity W2', f"{vel_out.get('W2', 0)} m/s"],
        ['Tangential Velocity U2', f"{vel_out.get('U2', 0)} m/s"],
        ['Absolute Flow Angle alpha2', f"{vel_out.get('alpha2', 0)} deg"],
        ['Relative Flow Angle beta2', f"{vel_out.get('beta2', 0)} deg"],
    ]
    vel_out_table = Table(vel_out_data, colWidths=[6*cm, 6*cm])
    vel_out_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(vel_out_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # Performance
    elements.append(Paragraph("Performance", heading_style))
    perf = data.get('performance', {})
    perf_data = [
        ['Parameter', 'Value'],
        ['Stage Efficiency', f"{data.get('thermo_params', {}).get('eta', 0)} %"],
        ['Calculated Power', f"{perf.get('P_calc', 0)} kW"],
        ['Input Power', f"{perf.get('P_input', 0)} kW"],
        ['Match', 'OK' if perf.get('match') else 'WARN'],
    ]
    perf_table = Table(perf_data, colWidths=[6*cm, 6*cm])
    perf_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00D4FF')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(perf_table)
    
    # Footer
    elements.append(Spacer(1, 1*cm))
    footer = Paragraph("<para alignment='center'><font color='gray' size='8'>PDS CALC V2.0 | {}</font></para>".format(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')), normal_style)
    elements.append(footer)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.read()
