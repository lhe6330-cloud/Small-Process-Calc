"""
PDF 报告导出模块 - 模式 2 和模式 3
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

def export_mode2_pdf(data: dict, input_params: dict) -> bytes:
    """导出模式 2 PDF 报告（先膨胀后回热）"""
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
    
    # 标题
    title = Paragraph("PDS CALC - 计算报告", title_style)
    elements.append(title)
    
    subtitle = Paragraph("模式 2: 先膨胀后回热", ParagraphStyle('Subtitle', parent=normal_style, alignment=TA_CENTER, fontSize=12))
    elements.append(subtitle)
    elements.append(Spacer(1, 0.3*cm))
    
    # 时间
    time_text = f"计算时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    elements.append(Paragraph(time_text, ParagraphStyle('Time', parent=normal_style, alignment=TA_CENTER, textColor=colors.gray)))
    elements.append(Spacer(1, 0.5*cm))
    
    # 输入参数
    elements.append(Paragraph("输入参数", heading_style))
    
    turbine_in = input_params.get('turbine_in', {})
    turbine_params = input_params.get('turbine_params', {})
    hx_cold_out = input_params.get('hx_cold_out', {})
    hx_hot = input_params.get('hx_hot', {})
    
    input_data = [
        ['参数', '涡轮入口', '涡轮参数', '换热器冷边出口', '换热器热边'],
        ['介质', turbine_in.get('medium', '-'), '-', '-', hx_hot.get('medium', '-')],
        ['流量', f"{turbine_in.get('flow_rate', 0)} {turbine_in.get('flow_unit', '')}", '-', '-', f"{hx_hot.get('flow_rate', 0)} {hx_hot.get('flow_unit', '')}"],
        ['入口压力 (MPa.G)', str(turbine_in.get('p_in', '-')), '-', str(hx_cold_out.get('p_out', '-')), str(hx_hot.get('p_in', '-'))],
        ['出口压力 (MPa.G)', str(turbine_params.get('p_out', '-')), '-', str(hx_cold_out.get('p_out', '-')), str(hx_hot.get('p_out', '-'))],
        ['入口温度 (°C)', str(turbine_in.get('t_in', '-')), '-', '-', str(hx_hot.get('t_in', '-'))],
        ['出口温度 (°C)', '-', '-', str(hx_cold_out.get('t_out', '-')), '-'],
        ['绝热效率 (%)', '-', str(turbine_params.get('adiabatic_efficiency', '-')), '-', '-'],
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
    
    # 计算结果
    elements.append(Paragraph("计算结果", heading_style))
    
    result_data = [
        ['项目', '数值', '单位'],
        ['涡轮轴功率', f"{data.get('turbine', {}).get('power_shaft', 0):.2f}", 'kW'],
        ['发电功率', f"{data.get('turbine', {}).get('power_electric', 0):.2f}", 'kW'],
        ['涡轮出口温度', f"{data.get('turbine', {}).get('t_out', 0):.1f}", '°C'],
        ['换热功率', f"{data.get('heat_exchanger', {}).get('q_power', 0):.2f}", 'kW'],
        ['热边出口温度', f"{data.get('heat_exchanger', {}).get('t_hot_out', 0):.1f}", '°C'],
        ['电机选型', f"{data.get('selection', {}).get('motor', 0)}", 'kW'],
        ['进口管道', f"DN{data.get('selection', {}).get('pipe_inlet', {}).get('recommended_dn', 0)}", '-'],
        ['出口管道', f"DN{data.get('selection', {}).get('pipe_outlet', {}).get('recommended_dn', 0)}", '-'],
        ['阀门', f"DN{data.get('selection', {}).get('valve', {}).get('valve_dn', 0)}", '-'],
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
    
    # 页脚
    elements.append(Spacer(1, 1*cm))
    footer = Paragraph(
        "<para alignment='center'><font color='gray' size='8'>PDS CALC V1.0 | 生成时间：{}</font></para>".format(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ),
        normal_style
    )
    elements.append(footer)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.read()

def export_mode3_pdf(data: dict, input_params: dict) -> bytes:
    """导出模式 3 PDF 报告（直接膨胀）"""
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
    
    # 标题
    title = Paragraph("PDS CALC - 计算报告", title_style)
    elements.append(title)
    
    subtitle = Paragraph("模式 3: 直接膨胀", ParagraphStyle('Subtitle', parent=normal_style, alignment=TA_CENTER, fontSize=12))
    elements.append(subtitle)
    elements.append(Spacer(1, 0.3*cm))
    
    # 时间
    time_text = f"计算时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    elements.append(Paragraph(time_text, ParagraphStyle('Time', parent=normal_style, alignment=TA_CENTER, textColor=colors.gray)))
    elements.append(Spacer(1, 0.5*cm))
    
    # 输入参数
    elements.append(Paragraph("输入参数", heading_style))
    
    turbine_in = input_params.get('turbine_in', {})
    turbine_params = input_params.get('turbine_params', {})
    
    input_data = [
        ['参数', '数值'],
        ['介质', turbine_in.get('medium', '-')],
        ['流量', f"{turbine_in.get('flow_rate', 0)} {turbine_in.get('flow_unit', '')}"],
        ['入口压力 (MPa.G)', str(turbine_in.get('p_in', '-'))],
        ['入口温度 (°C)', str(turbine_in.get('t_in', '-'))],
        ['出口压力 (MPa.G)', str(turbine_params.get('p_out', '-'))],
        ['绝热效率 (%)', str(turbine_params.get('adiabatic_efficiency', '-'))],
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
    
    # 计算结果
    elements.append(Paragraph("计算结果", heading_style))
    
    result_data = [
        ['项目', '数值', '单位'],
        ['涡轮轴功率', f"{data.get('turbine', {}).get('power_shaft', 0):.2f}", 'kW'],
        ['发电功率', f"{data.get('turbine', {}).get('power_electric', 0):.2f}", 'kW'],
        ['涡轮出口温度', f"{data.get('turbine', {}).get('t_out', 0):.1f}", '°C'],
        ['电机选型', f"{data.get('selection', {}).get('motor', 0)}", 'kW'],
        ['进口管道', f"DN{data.get('selection', {}).get('pipe_inlet', {}).get('recommended_dn', 0)}", '-'],
        ['出口管道', f"DN{data.get('selection', {}).get('pipe_outlet', {}).get('recommended_dn', 0)}", '-'],
        ['阀门', f"DN{data.get('selection', {}).get('valve', {}).get('valve_dn', 0)}", '-'],
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
    
    # 页脚
    elements.append(Spacer(1, 1*cm))
    footer = Paragraph(
        "<para alignment='center'><font color='gray' size='8'>PDS CALC V1.0 | 生成时间：{}</font></para>".format(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ),
        normal_style
    )
    elements.append(footer)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.read()
