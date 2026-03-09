"""
PDF æŠ¥å‘Šå¯¼å‡ºæ¨¡å— - æ¨¡å¼ 2 å’Œæ¨¡å¼ 3
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import io
import os

def register_chinese_font():
    """æ³¨å†Œä¸­æ–‡å­—ä½“"""
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

def export_mode2_pdf(data: dict, input_params: dict) -> bytes:
    """å¯¼å‡ºæ¨¡å¼ 2 PDF æŠ¥å‘Šï¼ˆå…ˆè†¨èƒ€åå›çƒ­ï¼‰"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    
    font_name = register_chinese_font()
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#00D4FF'),
        alignment=TA_CENTER,
        fontName=font_name,
        spaceAfter=20
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#00D4FF'),
        fontName=font_name,
        spaceAfter=12,
        spaceBefore=12
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        fontName=font_name,
    )
    
    elements = []
    
    # æ ‡é¢˜
    title = Paragraph("PDS CALC - è®¡ç®—æŠ¥å‘Š", title_style)
    elements.append(title)
    
    subtitle = Paragraph("æ¨¡å¼ 2: å…ˆè†¨èƒ€åå›çƒ­", ParagraphStyle('Subtitle', parent=normal_style, alignment=TA_CENTER, fontSize=12))
    elements.append(subtitle)
    elements.append(Spacer(1, 0.3*cm))
    
    # æ—¶é—´
    time_text = f"è®¡ç®—æ—¶é—´ï¼š{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    elements.append(Paragraph(time_text, ParagraphStyle('Time', parent=normal_style, alignment=TA_CENTER, textColor=colors.gray)))
    elements.append(Spacer(1, 0.5*cm))
    
    # è¾“å…¥å‚æ•°
    elements.append(Paragraph("è¾“å…¥å‚æ•°", heading_style))
    
    turbine_in = input_params.get('turbine_in', {})
    turbine_params = input_params.get('turbine_params', {})
    hx_cold_out = input_params.get('hx_cold_out', {})
    hx_hot = input_params.get('hx_hot', {})
    
    input_data = [
        ['å‚æ•°', 'æ¶¡è½®å…¥å£', 'æ¶¡è½®å‚æ•°', 'æ¢çƒ­å™¨å†·è¾¹å‡ºå£', 'æ¢çƒ­å™¨çƒ­è¾¹'],
        ['ä»‹è´¨', turbine_in.get('medium', '-'), '-', '-', hx_hot.get('medium', '-')],
        ['æµé‡', f"{turbine_in.get('flow_rate', 0)} {turbine_in.get('flow_unit', '')}", '-', '-', f"{hx_hot.get('flow_rate', 0)} {hx_hot.get('flow_unit', '')}"],
        ['å…¥å£å‹åŠ› (MPa.G)', str(turbine_in.get('p_in', '-')), '-', str(hx_cold_out.get('p_out', '-')), str(hx_hot.get('p_in', '-'))],
        ['å‡ºå£å‹åŠ› (MPa.G)', str(turbine_params.get('p_out', '-')), '-', str(hx_cold_out.get('p_out', '-')), str(hx_hot.get('p_out', '-'))],
        ['å…¥å£æ¸©åº¦ (Â°C)', str(turbine_in.get('t_in', '-')), '-', '-', str(hx_hot.get('t_in', '-'))],
        ['å‡ºå£æ¸©åº¦ (Â°C)', '-', '-', str(hx_cold_out.get('t_out', '-')), '-'],
        ['ç»çƒ­æ•ˆç‡ (%)', '-', str(turbine_params.get('adiabatic_efficiency', '-')), '-', '-'],
    ]
    
    input_table = Table(input_data, colWidths=[2.5*cm, 3.5*cm, 3*cm, 3.5*cm, 3.5*cm])
    input_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), font_name),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), font_name),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    elements.append(input_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # è®¡ç®—ç»“æœ
    elements.append(Paragraph("è®¡ç®—ç»“æœ", heading_style))
    
    result_data = [
        ['é¡¹ç›®', 'æ•°å€¼', 'å•ä½'],
        ['æ¶¡è½®è½´åŠŸç‡', f"{data.get('turbine', {}).get('power_shaft', 0):.2f}", 'kW'],
        ['å‘ç”µåŠŸç‡', f"{data.get('turbine', {}).get('power_electric', 0):.2f}", 'kW'],
        ['æ¶¡è½®å‡ºå£æ¸©åº¦', f"{data.get('turbine', {}).get('t_out', 0):.1f}", 'Â°C'],
        ['æ¢çƒ­åŠŸç‡', f"{data.get('heat_exchanger', {}).get('q_power', 0):.2f}", 'kW'],
        ['çƒ­è¾¹å‡ºå£æ¸©åº¦', f"{data.get('heat_exchanger', {}).get('t_hot_out', 0):.1f}", 'Â°C'],
        ['ç”µæœºé€‰å‹', f"{data.get('selection', {}).get('motor', 0)}", 'kW'],
        ['è¿›å£ç®¡é“', f"DN{data.get('selection', {}).get('pipe_inlet', {}).get('recommended_dn', 0)}", '-'],
        ['å‡ºå£ç®¡é“', f"DN{data.get('selection', {}).get('pipe_outlet', {}).get('recommended_dn', 0)}", '-'],
        ['é˜€é—¨', f"DN{data.get('selection', {}).get('valve', {}).get('valve_dn', 0)}", '-'],
    ]
    
    result_table = Table(result_data, colWidths=[5*cm, 4*cm, 2*cm])
    result_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), font_name),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), font_name),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    elements.append(result_table)
    
    # é¡µè„š
    elements.append(Spacer(1, 1*cm))
    footer = Paragraph(
        "<para alignment='center'><font color='gray' size='8'>PDS CALC V1.0 | ç”Ÿæˆæ—¶é—´ï¼š{}</font></para>".format(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ),
        normal_style
    )
    elements.append(footer)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.read()

def export_mode3_pdf(data: dict, input_params: dict) -> bytes:
    """å¯¼å‡ºæ¨¡å¼ 3 PDF æŠ¥å‘Šï¼ˆç›´æ¥è†¨èƒ€ï¼‰"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    
    font_name = register_chinese_font()
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#00D4FF'),
        alignment=TA_CENTER,
        fontName=font_name,
        spaceAfter=20
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#00D4FF'),
        fontName=font_name,
        spaceAfter=12,
        spaceBefore=12
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        fontName=font_name,
    )
    
    elements = []
    
    # æ ‡é¢˜
    title = Paragraph("PDS CALC - è®¡ç®—æŠ¥å‘Š", title_style)
    elements.append(title)
    
    subtitle = Paragraph("æ¨¡å¼ 3: ç›´æ¥è†¨èƒ€", ParagraphStyle('Subtitle', parent=normal_style, alignment=TA_CENTER, fontSize=12))
    elements.append(subtitle)
    elements.append(Spacer(1, 0.3*cm))
    
    # æ—¶é—´
    time_text = f"è®¡ç®—æ—¶é—´ï¼š{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    elements.append(Paragraph(time_text, ParagraphStyle('Time', parent=normal_style, alignment=TA_CENTER, textColor=colors.gray)))
    elements.append(Spacer(1, 0.5*cm))
    
    # è¾“å…¥å‚æ•°
    elements.append(Paragraph("è¾“å…¥å‚æ•°", heading_style))
    
    turbine_in = input_params.get('turbine_in', {})
    turbine_params = input_params.get('turbine_params', {})
    
    input_data = [
        ['å‚æ•°', 'æ•°å€¼'],
        ['ä»‹è´¨', turbine_in.get('medium', '-')],
        ['æµé‡', f"{turbine_in.get('flow_rate', 0)} {turbine_in.get('flow_unit', '')}"],
        ['å…¥å£å‹åŠ› (MPa.G)', str(turbine_in.get('p_in', '-'))],
        ['å…¥å£æ¸©åº¦ (Â°C)', str(turbine_in.get('t_in', '-'))],
        ['å‡ºå£å‹åŠ› (MPa.G)', str(turbine_params.get('p_out', '-'))],
        ['ç»çƒ­æ•ˆç‡ (%)', str(turbine_params.get('adiabatic_efficiency', '-'))],
    ]
    
    input_table = Table(input_data, colWidths=[6*cm, 6*cm])
    input_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), font_name),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), font_name),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    elements.append(input_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # è®¡ç®—ç»“æœ
    elements.append(Paragraph("è®¡ç®—ç»“æœ", heading_style))
    
    result_data = [
        ['é¡¹ç›®', 'æ•°å€¼', 'å•ä½'],
        ['æ¶¡è½®è½´åŠŸç‡', f"{data.get('turbine', {}).get('power_shaft', 0):.2f}", 'kW'],
        ['å‘ç”µåŠŸç‡', f"{data.get('turbine', {}).get('power_electric', 0):.2f}", 'kW'],
        ['æ¶¡è½®å‡ºå£æ¸©åº¦', f"{data.get('turbine', {}).get('t_out', 0):.1f}", 'Â°C'],
        ['ç”µæœºé€‰å‹', f"{data.get('selection', {}).get('motor', 0)}", 'kW'],
        ['è¿›å£ç®¡é“', f"DN{data.get('selection', {}).get('pipe_inlet', {}).get('recommended_dn', 0)}", '-'],
        ['å‡ºå£ç®¡é“', f"DN{data.get('selection', {}).get('pipe_outlet', {}).get('recommended_dn', 0)}", '-'],
        ['é˜€é—¨', f"DN{data.get('selection', {}).get('valve', {}).get('valve_dn', 0)}", '-'],
    ]
    
    result_table = Table(result_data, colWidths=[5*cm, 4*cm, 2*cm])
    result_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), font_name),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), font_name),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    elements.append(result_table)
    
    # é¡µè„š
    elements.append(Spacer(1, 1*cm))
    footer = Paragraph(
        "<para alignment='center'><font color='gray' size='8'>PDS CALC V1.0 | ç”Ÿæˆæ—¶é—´ï¼š{}</font></para>".format(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ),
        normal_style
    )
    elements.append(footer)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.read()

# ============ V2.0 ĞÂÔöµ¼³ö ============

def export_mode4_pdf(data: dict, input_params: dict) -> bytes:
    """µ¼³öÄ£Ê½ 4 PDF ±¨¸æ£¨·ÖÀëÆ÷Éè¼Æ£©"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    font_name = register_chinese_font()
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#00D4FF'), alignment=TA_CENTER, fontName=font_name, spaceAfter=20)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#00D4FF'), fontName=font_name, spaceAfter=12, spaceBefore=12)
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#333333'), fontName=font_name)
    elements = []
    elements.append(Paragraph("PDS CALC V2.0 - ·ÖÀëÆ÷Éè¼Æ±¨¸æ", title_style))
    elements.append(Paragraph("Ä£Ê½ 4: Á÷³Ì½Úµã·ÖÀëÆ÷", ParagraphStyle('Subtitle', parent=normal_style, alignment=TA_CENTER, fontSize=12)))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(Paragraph(f"¼ÆËãÊ±¼ä£º{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ParagraphStyle('Time', parent=normal_style, alignment=TA_CENTER, textColor=colors.gray)))
    elements.append(Spacer(1, 0.5*cm))
    node_params = input_params.get('node_params', {})
    input_data = [['²ÎÊı', 'ÊıÖµ'], ['Ìí¼ÓÎ»ÖÃ', input_params.get('node_id', '-')], ['Ñ¹Á¦ (MPa.G)', str(node_params.get('p', '-'))], ['ÎÂ¶È (¡ãC)', str(node_params.get('t', '-'))], ['Á÷Á¿', f"{node_params.get('flow_rate', 0)} {node_params.get('flow_unit', '')}"], ['ÆøÌåÃÜ¶È (kg/m3)', str(node_params.get('rho', '-'))]]
    input_table = Table(input_data, colWidths=[6*cm, 6*cm])
    input_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')), ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('FONTNAME', (0, 0), (-1, 0), font_name), ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    elements.append(input_table)
    elements.append(Spacer(1, 0.5*cm))
    vle_result = data.get('vle', {})
    if vle_result and not vle_result.get('skip', False):
        elements.append(Paragraph("ÆøÒºÆ½ºâ¼ÆËã", heading_style))
        vle_data = [['²ÎÊı', 'ÊıÖµ'], ['ÆøÏà·ÖÂÊ', f"{vle_result.get('vapor_frac', 0) * 100:.1f} %"], ['ÒºÏà·ÖÂÊ', f"{vle_result.get('liquid_frac', 0) * 100:.1f} %"], ['ÀäÄıÒºÁ÷Á¿ (T/h)', f"{vle_result.get('liquid_flow', 0):.2f}"]]
        vle_table = Table(vle_data, colWidths=[6*cm, 6*cm])
        vle_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')), ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
        elements.append(vle_table)
        elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph("·ÖÀëÆ÷³ß´ç", heading_style))
    result_data = [['²ÎÊı', 'ÊıÖµ'], ['·ÖÀëÆ÷Ö±¾¶ (mm)', str(data.get('diameter', 0))], ['·ÖÀëÆ÷¸ß¶È/³¤¶È (mm)', str(data.get('length', 0))], ['ÒºÌåÍ£ÁôÊ±¼ä (s)', f"{data.get('residence_time', 0):.1f}"], ['Ğ£ºË½á¹û', 'OK' if data.get('check_passed') else 'WARN']]
    result_table = Table(result_data, colWidths=[6*cm, 6*cm])
    result_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00D4FF')), ('TEXTCOLOR', (0, 0), (-1, 0), colors.white), ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    elements.append(result_table)
    elements.append(Spacer(1, 1*cm))
    footer = Paragraph("<para alignment='center'><font color='gray' size='8'>PDS CALC V2.0 | {}</font></para>".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), normal_style)
    elements.append(footer)
    doc.build(elements)
    buffer.seek(0)
    return buffer.read()


def export_mode5_pdf(data: dict, input_params: dict) -> bytes:
    """µ¼³öÄ£Ê½ 5 PDF ±¨¸æ£¨ÎĞÂÖÒ»Î¬Éè¼Æ£©"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    font_name = register_chinese_font()
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#00D4FF'), alignment=TA_CENTER, fontName=font_name, spaceAfter=20)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#00D4FF'), fontName=font_name, spaceAfter=12, spaceBefore=12)
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#333333'), fontName=font_name)
    elements = []
    elements.append(Paragraph("PDS CALC V2.0 - ÎĞÂÖÒ»Î¬Éè¼Æ±¨¸æ", title_style))
    elements.append(Paragraph("Ä£Ê½ 5: ¾¶Á÷Ê½ÎĞÂÖÍ¨Á÷Éè¼Æ", ParagraphStyle('Subtitle', parent=normal_style, alignment=TA_CENTER, fontSize=12)))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(Paragraph(f"¼ÆËãÊ±¼ä£º{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ParagraphStyle('Time', parent=normal_style, alignment=TA_CENTER, textColor=colors.gray)))
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph("Éè¼Æ²ÎÊı", heading_style))
    design_data = [['²ÎÊı', 'ÊıÖµ'], ['×ªËÙ n (rpm)', str(input_params.get('speed_rpm', 3000))], ['ËÙ±È u/C?', str(input_params.get('speed_ratio', 0.65))], ['·´¶¯¶È ¦¸ (%)', str(input_params.get('reaction', 50))]]
    design_table = Table(design_data, colWidths=[6*cm, 6*cm])
    design_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')), ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    elements.append(design_table)
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph("»ù±¾³ß´ç", heading_style))
    dims = data.get('dimensions', {})
    dim_data = [['²ÎÊı', '·ûºÅ', 'ÊıÖµ (mm)'], ['Ò¶ÂÖÍâ¾¶', 'D?', str(dims.get('D1', 0))], ['Ò¶ÂÖÄÚ¾¶', 'D?', str(dims.get('D2', 0))], ['½ø¿ÚÒ¶Æ¬¸ß¶È', 'b?', str(dims.get('b1', 0))], ['³ö¿ÚÒ¶Æ¬¸ß¶È', 'b?', str(dims.get('b2', 0))]]
    dim_table = Table(dim_data, colWidths=[4*cm, 2*cm, 4*cm])
    dim_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00D4FF')), ('TEXTCOLOR', (0, 0), (-1, 0), colors.white), ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    elements.append(dim_table)
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph("ËÙ¶ÈÈı½ÇĞÎ - ½ø¿Ú", heading_style))
    vel_in = data.get('velocity_triangle_in', {})
    vel_in_data = [['²ÎÊı', 'ÊıÖµ'], ['¾ø¶ÔËÙ¶È C?', f"{vel_in.get('C1', 0)} m/s"], ['Ïà¶ÔËÙ¶È W?', f"{vel_in.get('W1', 0)} m/s"], ['Ô²ÖÜËÙ¶È U?', f"{vel_in.get('U1', 0)} m/s"], ['¾ø¶ÔÆøÁ÷½Ç ¦Á?', f"{vel_in.get('alpha1', 0)} ¡ã"], ['Ïà¶ÔÆøÁ÷½Ç ¦Â?', f"{vel_in.get('beta1', 0)} ¡ã"]]
    vel_in_table = Table(vel_in_data, colWidths=[6*cm, 6*cm])
    vel_in_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')), ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    elements.append(vel_in_table)
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph("ËÙ¶ÈÈı½ÇĞÎ - ³ö¿Ú", heading_style))
    vel_out = data.get('velocity_triangle_out', {})
    vel_out_data = [['²ÎÊı', 'ÊıÖµ'], ['¾ø¶ÔËÙ¶È C?', f"{vel_out.get('C2', 0)} m/s"], ['Ïà¶ÔËÙ¶È W?', f"{vel_out.get('W2', 0)} m/s"], ['Ô²ÖÜËÙ¶È U?', f"{vel_out.get('U2', 0)} m/s"], ['¾ø¶ÔÆøÁ÷½Ç ¦Á?', f"{vel_out.get('alpha2', 0)} ¡ã"], ['Ïà¶ÔÆøÁ÷½Ç ¦Â?', f"{vel_out.get('beta2', 0)} ¡ã"]]
    vel_out_table = Table(vel_out_data, colWidths=[6*cm, 6*cm])
    vel_out_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')), ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    elements.append(vel_out_table)
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph("ĞÔÄÜÑéÖ¤", heading_style))
    perf = data.get('performance', {})
    perf_data = [['²ÎÊı', 'ÊıÖµ'], ['¼¶Ğ§ÂÊ ¦Ç', f"{data.get('thermo_params', {}).get('eta', 0)} %"], ['¼ÆËã¹¦ÂÊ', f"{perf.get('P_calc', 0)} kW"], ['ÊäÈë¹¦ÂÊ', f"{perf.get('P_input', 0)} kW"], ['¹¦ÂÊÑéÖ¤', 'OK' if perf.get('match') else 'WARN']]
    perf_table = Table(perf_data, colWidths=[6*cm, 6*cm])
    perf_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00D4FF')), ('TEXTCOLOR', (0, 0), (-1, 0), colors.white), ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    elements.append(perf_table)
    elements.append(Spacer(1, 1*cm))
    footer = Paragraph("<para alignment='center'><font color='gray' size='8'>PDS CALC V2.0 | {}</font></para>".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), normal_style)
    elements.append(footer)
    doc.build(elements)
    buffer.seek(0)
    return buffer.read()

