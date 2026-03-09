"""
PDF 报告导出模块
使用 reportlab 生成中文 PDF 报告
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import io
import os

# 注册中文字体
def register_chinese_font():
    """注册中文字体"""
    # 尝试常见中文字体路径
    font_paths = [
        r"C:\Windows\Fonts\msyh.ttc",      # 微软雅黑
        r"C:\Windows\Fonts\simsun.ttc",    # 宋体
        r"C:\Windows\Fonts\simhei.ttf",    # 黑体
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('Chinese', font_path))
                return 'Chinese'
            except:
                continue
    
    # 如果都没有，使用默认字体（可能不支持中文）
    return 'Helvetica'

def export_mode1_pdf(data: dict, input_params: dict) -> bytes:
    """导出模式 1 PDF 报告"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    
    # 注册字体
    font_name = register_chinese_font()
    
    # 样式
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
    
    # 构建内容
    elements = []
    
    # 标题
    title = Paragraph("PDS CALC - 计算报告", title_style)
    elements.append(title)
    
    subtitle = Paragraph("模式 1: 先加热再膨胀", ParagraphStyle('Subtitle', parent=normal_style, alignment=TA_CENTER, fontSize=12))
    elements.append(subtitle)
    elements.append(Spacer(1, 0.3*cm))
    
    # 时间
    time_text = f"计算时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    elements.append(Paragraph(time_text, ParagraphStyle('Time', parent=normal_style, alignment=TA_CENTER, textColor=colors.gray)))
    elements.append(Spacer(1, 0.5*cm))
    
    # 输入参数
    elements.append(Paragraph("输入参数", heading_style))
    
    input_data = [
        ['参数', '冷边', '热边', '涡轮'],
        ['介质', 
         input_params['cold_side']['medium'], 
         input_params['hot_side']['medium'], 
         '-'],
        ['流量', 
         f"{input_params['cold_side']['flow_rate']} {input_params['cold_side']['flow_unit']}", 
         f"{input_params['hot_side']['flow_rate']} {input_params['hot_side']['flow_unit']}", 
         '-'],
        ['入口压力 (MPa.G)', 
         str(input_params['cold_side']['p_in']), 
         str(input_params['hot_side']['p_in']), 
         '-'],
        ['出口压力 (MPa.G)', 
         str(input_params['cold_side']['p_out']), 
         str(input_params['hot_side']['p_out']), 
         str(input_params['turbine']['p_out'])],
        ['入口温度 (°C)', 
         str(input_params['cold_side']['t_in']), 
         str(input_params['hot_side']['t_in']), 
         str(input_params['cold_side']['t_out'])],
        ['出口温度 (°C)', 
         str(input_params['cold_side']['t_out']), 
         '-', 
         '-'],
        ['绝热效率 (%)', 
         '-', 
         '-', 
         str(input_params['turbine']['adiabatic_efficiency'])],
    ]
    
    input_table = Table(input_data, colWidths=[3*cm, 4*cm, 4*cm, 3*cm])
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
        ['换热功率', f"{data['heat_exchanger']['q_power']:.2f}", 'kW'],
        ['热边出口温度', f"{data['heat_exchanger']['t_hot_out']:.1f}", '°C'],
        ['涡轮轴功率', f"{data['turbine']['power_shaft']:.2f}", 'kW'],
        ['发电功率', f"{data['turbine']['power_electric']:.2f}", 'kW'],
        ['涡轮出口温度', f"{data['turbine']['t_out']:.1f}", '°C'],
        ['电机选型', f"{data['selection']['motor']}", 'kW'],
        ['进口管道', f"DN{data['selection']['pipe_inlet']['recommended_dn']}", '-'],
        ['出口管道', f"DN{data['selection']['pipe_outlet']['recommended_dn']}", '-'],
        ['阀门', f"DN{data['selection']['valve']['valve_dn']}", '-'],
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
    elements.append(Spacer(1, 0.5*cm))
    
    # 设备选型详情
    elements.append(Paragraph("设备选型详情", heading_style))
    
    selection_data = [
        ['类型', '规格', '参数'],
        ['电机', f"{data['selection']['motor']} kW", '标准系列'],
        ['进口管道', f"DN{data['selection']['pipe_inlet']['recommended_dn']}", 
         f"流速 {data['selection']['pipe_inlet']['velocity']:.1f} m/s"],
        ['出口管道', f"DN{data['selection']['pipe_outlet']['recommended_dn']}", 
         f"流速 {data['selection']['pipe_outlet']['velocity']:.1f} m/s"],
        ['阀门', f"DN{data['selection']['valve']['valve_dn']}", 
         f"Kv={data['selection']['valve']['kv_rated']}"],
    ]
    
    selection_table = Table(selection_data, colWidths=[3*cm, 4*cm, 5*cm])
    selection_table.setStyle(TableStyle([
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
    elements.append(selection_table)
    
    # 页脚
    elements.append(Spacer(1, 1*cm))
    footer = Paragraph(
        "<para alignment='center'><font color='gray' size='8'>PDS CALC V1.0 | 生成时间：{}</font></para>".format(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ),
        normal_style
    )
    elements.append(footer)
    
    # 构建 PDF
    doc.build(elements)
    
    buffer.seek(0)
    return buffer.read()
