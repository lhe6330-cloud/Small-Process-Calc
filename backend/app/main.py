"""
PDS Calc Backend - FastAPI 主应用
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Dict, Optional, List
from datetime import datetime
import traceback
import io

# 导入计算模块
try:
    from app.core.thermodynamics import get_fluid_property, gauge_to_absolute
    from app.core.turbine import calculate_turbine
    from app.core.heat_exchanger import calculate_heat_exchanger
    from app.core.selection import select_motor, select_pipe_diameter, select_valve, calculate_pipe_flow
    from app.core.calculator import calculate_mode2, calculate_mode3
    # V2.0 新增模块
    from app.core.vle import vle_calc
    from app.core.separator import separator_design
    from app.core.turbine_1d import turbine_1d_design
    print("[OK] All modules imported successfully")
except Exception as e:
    print(f"[ERROR] Import failed: {e}")
    traceback.print_exc()
    raise

app = FastAPI(title="PDS Calc API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ 数据模型 ============

class FluidParams(BaseModel):
    medium_type: str
    medium: Optional[str] = None
    mix_composition: Optional[Dict[str, float]] = None
    composition_type: str = 'mole'
    flow_rate: float
    flow_unit: str
    p_in: float
    p_out: float
    t_in: float
    t_out: Optional[float] = None

class TurbineParams(BaseModel):
    p_out: float
    adiabatic_efficiency: float

class Mode1Request(BaseModel):
    cold_side: FluidParams
    hot_side: FluidParams
    turbine: TurbineParams

class Mode2Request(BaseModel):
    turbine_in: FluidParams
    turbine_params: TurbineParams
    hx_cold_out: Dict = {'p_out': 0.1, 't_out': 100}
    hx_hot: FluidParams

class Mode3Request(BaseModel):
    turbine_in: FluidParams
    turbine_params: TurbineParams

# ============ API 接口 ============

@app.get("/api/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.post("/api/calculate/mode1")
def calculate_mode1(req: Mode1Request):
    try:
        cold_params = req.cold_side.model_dump()
        hot_params = req.hot_side.model_dump()
        
        hx_result = calculate_heat_exchanger(cold_params, hot_params)
        
        turbine_result = calculate_turbine(
            p_in_gauge=req.cold_side.p_out,
            t_in=req.cold_side.t_out,
            p_out_gauge=req.turbine.p_out,
            flow_rate=req.cold_side.flow_rate,
            flow_unit=req.cold_side.flow_unit,
            adiabatic_efficiency=req.turbine.adiabatic_efficiency,
            medium_type=req.cold_side.medium_type,
            medium=req.cold_side.medium,
            mix_composition=req.cold_side.mix_composition,
            composition_type=req.cold_side.composition_type,
        )

        # 检查涡轮计算是否失败（如入口温度过低）
        if not turbine_result.get('success', True):
            return turbine_result

        motor = select_motor(turbine_result['power_shaft'])
        
        vol_in = calculate_pipe_flow(
            req.cold_side.flow_rate, req.cold_side.flow_unit,
            req.cold_side.p_in, req.cold_side.t_in,
            req.cold_side.medium_type, req.cold_side.medium,
            req.cold_side.mix_composition, req.cold_side.composition_type,
        )
        is_steam = req.cold_side.medium == 'H2O' and req.cold_side.t_in > 100
        pipe_in = select_pipe_diameter(vol_in, req.cold_side.medium, is_steam)
        
        vol_out = calculate_pipe_flow(
            req.cold_side.flow_rate, req.cold_side.flow_unit,
            req.turbine.p_out, turbine_result['t_out'],
            req.cold_side.medium_type, req.cold_side.medium,
            req.cold_side.mix_composition, req.cold_side.composition_type,
        )
        is_steam_out = req.cold_side.medium == 'H2O' and turbine_result['t_out'] > 100
        pipe_out = select_pipe_diameter(vol_out, req.cold_side.medium, is_steam_out)
        
        state_in = get_fluid_property(
            req.cold_side.p_in, req.cold_side.t_in,
            req.cold_side.medium_type, req.cold_side.medium,
            req.cold_side.mix_composition, req.cold_side.composition_type,
        )
        valve = select_valve(
            req.cold_side.flow_rate, req.cold_side.flow_unit,
            state_in['rho'], pipe_in['recommended_dn'],
            req.cold_side.medium_type, req.cold_side.medium,
        )
        
        return {
            "success": True,
            "heat_exchanger": {
                "q_power": hx_result['q_power'],
                "t_hot_out": hx_result['t_hot_out'],
            },
            "turbine": {
                "p_in": req.cold_side.p_out,  # 涡轮进口压力 = 冷边出口压力
                "t_in": req.cold_side.t_out,  # 涡轮进口温度 = 冷边出口温度
                "p_out": req.turbine.p_out,
                "t_out": turbine_result['t_out'],
                "x_out": turbine_result['x_out'],
                "liquid_percent": turbine_result.get('liquid_percent'),
                "liquid_warning": turbine_result.get('liquid_warning'),
                "power_shaft": turbine_result['power_shaft'],
                "power_electric": turbine_result['power_electric'],
                "rho_in": turbine_result['rho_in'],
                "rho_out": turbine_result.get('rho_out', 1.2),
                "mass_flow": turbine_result['mass_flow'],
                "medium_type": req.cold_side.medium_type,
                "medium": req.cold_side.medium,
                "mix_composition": req.cold_side.mix_composition,  # 混合介质组分
                "flow_rate": req.cold_side.flow_rate,
                "flow_unit": req.cold_side.flow_unit,
            },
            "selection": {
                "motor": motor,
                "pipe_inlet": pipe_in,
                "pipe_outlet": pipe_out,
                "valve": valve,
            }
        }
        
    except Exception as e:
        print(f"[ERROR] calculate_mode1 failed: {e}")
        traceback.print_exc()
        # 返回友好的错误信息
        return {
            "success": False,
            "error": True,
            "error_message": f"计算失败：{str(e)[:200]}。请检查输入参数是否合理，或尝试调整参数范围。"
        }

@app.get("/api/standards/motors")
def get_motors():
    from app.core.selection import MOTORS
    return {"motors": MOTORS}

@app.get("/api/standards/pipes")
def get_pipes():
    from app.core.selection import PIPES
    return {"pipes": PIPES}

@app.get("/api/thermo/water/saturation")
def get_water_saturation_temp(p: float):
    """获取水的饱和温度 (MPa.A → °C)"""
    from app.core.thermodynamics import WaterProperty
    t_sat = WaterProperty.get_saturation_temp(p)
    return {"saturation_temp": t_sat}

@app.post("/api/calculate/mode2")
def calculate_mode2_api(req: Mode2Request):
    """模式 2: 先膨胀后回热"""
    try:
        turbine_in = req.turbine_in.model_dump()
        hx_cold = {'p_out': req.hx_cold_out['p_out'], 't_out': req.hx_cold_out['t_out'],
            'flow_rate': req.turbine_in.flow_rate, 'flow_unit': req.turbine_in.flow_unit,
            'medium_type': req.turbine_in.medium_type, 'medium': req.turbine_in.medium,
            'mix_composition': req.turbine_in.mix_composition, 'composition_type': req.turbine_in.composition_type}
        hx_hot = req.hx_hot.model_dump()
        result = calculate_mode2(turbine_in, req.turbine_params.model_dump(), hx_cold, hx_hot)
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/calculate/mode3")
def calculate_mode3_api(req: Mode3Request):
    """模式 3: 直接膨胀"""
    try:
        turbine_in = req.turbine_in.model_dump()
        result = calculate_mode3(turbine_in, req.turbine_params.model_dump())
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export/excel/mode1")
def export_excel_mode1(req: Mode1Request):
    """导出模式 1 Excel 报告"""
    try:
        from app.reports.excel_export import export_mode1_report
        from fastapi.responses import StreamingResponse
        import io
        
        # 先计算
        cold_params = req.cold_side.model_dump()
        hot_params = req.hot_side.model_dump()
        hx_result = calculate_heat_exchanger(cold_params, hot_params)
        turbine_result = calculate_turbine(
            p_in_gauge=req.cold_side.p_out, t_in=req.cold_side.t_out,
            p_out_gauge=req.turbine.p_out, flow_rate=req.cold_side.flow_rate,
            flow_unit=req.cold_side.flow_unit, adiabatic_efficiency=req.turbine.adiabatic_efficiency,
            medium_type=req.cold_side.medium_type, medium=req.cold_side.medium
        )
        vol_in = calculate_pipe_flow(req.cold_side.flow_rate, req.cold_side.flow_unit,
            req.cold_side.p_in, req.cold_side.t_in, req.cold_side.medium_type, req.cold_side.medium)
        is_steam = req.cold_side.medium == 'H2O' and req.cold_side.t_in > 100
        pipe_in = select_pipe_diameter(vol_in, req.cold_side.medium, is_steam)
        
        vol_out = calculate_pipe_flow(req.cold_side.flow_rate, req.cold_side.flow_unit,
            req.turbine.p_out, turbine_result['t_out'], req.cold_side.medium_type, req.cold_side.medium)
        is_steam_out = req.cold_side.medium == 'H2O' and turbine_result['t_out'] > 100
        pipe_out = select_pipe_diameter(vol_out, req.cold_side.medium, is_steam_out)
        
        state_in = get_fluid_property(req.cold_side.p_in, req.cold_side.t_in,
            req.cold_side.medium_type, req.cold_side.medium)
        valve = select_valve(req.cold_side.flow_rate, req.cold_side.flow_unit,
            state_in['rho'], pipe_in['recommended_dn'], req.cold_side.medium_type, req.cold_side.medium)
        
        motor = select_motor(turbine_result['power_shaft'])
        
        data = {
            "heat_exchanger": {"q_power": hx_result['q_power'], "t_hot_out": hx_result['t_hot_out']},
            "turbine": {"power_shaft": turbine_result['power_shaft'], "power_electric": turbine_result['power_electric'],
                       "t_out": turbine_result['t_out'], "x_out": turbine_result['x_out']},
            "selection": {"motor": motor, "pipe_inlet": pipe_in, "pipe_outlet": pipe_out, "valve": valve}
        }
        
        excel_bytes = export_mode1_report(data, req.model_dump())
        return StreamingResponse(io.BytesIO(excel_bytes), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       headers={"Content-Disposition": f"attachment; filename=report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"})
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export/pdf/mode1")
def export_pdf_mode1(req: Mode1Request):
    """导出模式 1 PDF 报告"""
    try:
        from app.reports.pdf_export import export_mode1_pdf
        from fastapi.responses import StreamingResponse
        import io
        
        # 先计算
        cold_params = req.cold_side.model_dump()
        hot_params = req.hot_side.model_dump()
        hx_result = calculate_heat_exchanger(cold_params, hot_params)
        turbine_result = calculate_turbine(
            p_in_gauge=req.cold_side.p_out, t_in=req.cold_side.t_out,
            p_out_gauge=req.turbine.p_out, flow_rate=req.cold_side.flow_rate,
            flow_unit=req.cold_side.flow_unit, adiabatic_efficiency=req.turbine.adiabatic_efficiency,
            medium_type=req.cold_side.medium_type, medium=req.cold_side.medium
        )
        vol_in = calculate_pipe_flow(req.cold_side.flow_rate, req.cold_side.flow_unit,
            req.cold_side.p_in, req.cold_side.t_in, req.cold_side.medium_type, req.cold_side.medium)
        is_steam = req.cold_side.medium == 'H2O' and req.cold_side.t_in > 100
        pipe_in = select_pipe_diameter(vol_in, req.cold_side.medium, is_steam)
        
        vol_out = calculate_pipe_flow(req.cold_side.flow_rate, req.cold_side.flow_unit,
            req.turbine.p_out, turbine_result['t_out'], req.cold_side.medium_type, req.cold_side.medium)
        is_steam_out = req.cold_side.medium == 'H2O' and turbine_result['t_out'] > 100
        pipe_out = select_pipe_diameter(vol_out, req.cold_side.medium, is_steam_out)
        
        state_in = get_fluid_property(req.cold_side.p_in, req.cold_side.t_in,
            req.cold_side.medium_type, req.cold_side.medium)
        valve = select_valve(req.cold_side.flow_rate, req.cold_side.flow_unit,
            state_in['rho'], pipe_in['recommended_dn'], req.cold_side.medium_type, req.cold_side.medium)
        
        motor = select_motor(turbine_result['power_shaft'])
        
        data = {
            "heat_exchanger": {"q_power": hx_result['q_power'], "t_hot_out": hx_result['t_hot_out']},
            "turbine": {"power_shaft": turbine_result['power_shaft'], "power_electric": turbine_result['power_electric'],
                       "t_out": turbine_result['t_out'], "x_out": turbine_result['x_out']},
            "selection": {"motor": motor, "pipe_inlet": pipe_in, "pipe_outlet": pipe_out, "valve": valve}
        }
        
        pdf_bytes = export_mode1_pdf(data, req.model_dump())
        return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf",
                       headers={"Content-Disposition": f"attachment; filename=report_mode1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"})
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export/pdf/mode2")
def export_pdf_mode2(req: Mode2Request):
    """导出模式 2 PDF 报告"""
    try:
        from app.reports.pdf_export_modes import export_mode2_pdf
        from fastapi.responses import StreamingResponse
        import io
        
        turbine_in = req.turbine_in.model_dump()
        hx_cold = {'p_out': req.hx_cold_out['p_out'], 't_out': req.hx_cold_out['t_out'],
            'flow_rate': req.turbine_in.flow_rate, 'flow_unit': req.turbine_in.flow_unit,
            'medium_type': req.turbine_in.medium_type, 'medium': req.turbine_in.medium}
        hx_hot = req.hx_hot.model_dump()
        result = calculate_mode2(turbine_in, req.turbine_params.model_dump(), hx_cold, hx_hot)
        
        pdf_bytes = export_mode2_pdf(result, req.model_dump())
        return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf",
                       headers={"Content-Disposition": f"attachment; filename=report_mode2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"})
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export/pdf/mode3")
def export_pdf_mode3(req: Mode3Request):
    """导出模式 3 PDF 报告"""
    try:
        from app.reports.pdf_export_modes import export_mode3_pdf
        from fastapi.responses import StreamingResponse
        import io
        
        turbine_in = req.turbine_in.model_dump()
        result = calculate_mode3(turbine_in, req.turbine_params.model_dump())
        
        pdf_bytes = export_mode3_pdf(result, req.model_dump())
        return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf",
                       headers={"Content-Disposition": f"attachment; filename=report_mode3_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"})
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export/excel/mode2")
def export_excel_mode2(req: Mode2Request):
    """导出模式 2 Excel 报告"""
    try:
        from app.reports.excel_export import export_mode2_report
        from fastapi.responses import StreamingResponse
        import io
        
        turbine_in = req.turbine_in.model_dump()
        hx_cold = {'p_out': req.hx_cold_out['p_out'], 't_out': req.hx_cold_out['t_out'],
            'flow_rate': req.turbine_in.flow_rate, 'flow_unit': req.turbine_in.flow_unit,
            'medium_type': req.turbine_in.medium_type, 'medium': req.turbine_in.medium}
        hx_hot = req.hx_hot.model_dump()
        result = calculate_mode2(turbine_in, req.turbine_params.model_dump(), hx_cold, hx_hot)
        
        excel_bytes = export_mode2_report(result, req.model_dump())
        return StreamingResponse(io.BytesIO(excel_bytes), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       headers={"Content-Disposition": f"attachment; filename=report_mode2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"})
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export/excel/mode3")
def export_excel_mode3(req: Mode3Request):
    """导出模式 3 Excel 报告"""
    try:
        from app.reports.excel_export import export_mode3_report
        from fastapi.responses import StreamingResponse
        import io
        
        turbine_in = req.turbine_in.model_dump()
        result = calculate_mode3(turbine_in, req.turbine_params.model_dump())
        
        excel_bytes = export_mode3_report(result, req.model_dump())
        return StreamingResponse(io.BytesIO(excel_bytes), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       headers={"Content-Disposition": f"attachment; filename=report_mode3_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"})
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ============ V2.0 新增 API ============

# 流程节点定义
FLOW_NODES = {
    'mode1': [
        {'id': 'cold_inlet', 'name': '冷边入口', 'position': 'start'},
        {'id': 'hx_in', 'name': '换热器入口', 'position': 'before_hx'},
        {'id': 'hx_out', 'name': '换热器出口', 'position': 'after_hx'},
        {'id': 'turbine_in', 'name': '涡轮入口', 'position': 'before_turbine'},
        {'id': 'turbine_out', 'name': '涡轮出口', 'position': 'after_turbine'},
        {'id': 'outlet', 'name': '总出口', 'position': 'end'},
    ],
    'mode2': [
        {'id': 'cold_inlet', 'name': '冷边入口', 'position': 'start'},
        {'id': 'turbine_in', 'name': '涡轮入口', 'position': 'before_turbine'},
        {'id': 'turbine_out', 'name': '涡轮出口', 'position': 'after_turbine'},
        {'id': 'hx_in', 'name': '换热器入口', 'position': 'before_hx'},
        {'id': 'hx_out', 'name': '换热器出口', 'position': 'after_hx'},
        {'id': 'outlet', 'name': '总出口', 'position': 'end'},
    ],
    'mode3': [
        {'id': 'cold_inlet', 'name': '冷边入口', 'position': 'start'},
        {'id': 'turbine_in', 'name': '涡轮入口', 'position': 'before_turbine'},
        {'id': 'turbine_out', 'name': '涡轮出口', 'position': 'after_turbine'},
        {'id': 'outlet', 'name': '总出口', 'position': 'end'},
    ],
}


class VleRequest(BaseModel):
    """气液平衡计算请求"""
    p: float = Field(description="压力 (MPa.G)")
    t: float = Field(description="温度 (°C)")
    composition: Dict[str, float] = Field(description="介质组成")
    total_flow: float = Field(description="总流量")
    flow_unit: str = Field(default='T/h', description="流量单位")


class SeparatorRequest(BaseModel):
    """分离器计算请求"""
    source_mode: str = Field(description="来源模式 (mode1/mode2/mode3)")
    node_id: str = Field(description="添加位置节点 ID")
    node_params: Dict = Field(description="节点工况参数")
    vle_result: Optional[Dict] = Field(default=None, description="气液平衡结果")
    droplet_size: float = Field(default=100, description="设计液滴粒径 (μm)")
    length_ratio: float = Field(default=3.0, description="长径比 L/D")
    separator_type: str = Field(default='vertical', description="分离器类型 (vertical/horizontal)")
    residence_time_req: float = Field(default=180, description="要求停留时间 (s)")


class Turbine1DRequest(BaseModel):
    """涡轮一维设计请求"""
    source_mode: str = Field(description="来源模式")
    flow_rate: float = Field(description="流量")
    flow_unit: str = Field(description="流量单位")
    p_in: float = Field(description="进口压力 (MPa.G)")
    p_out: float = Field(description="出口压力 (MPa.G)")
    t_in: float = Field(description="进口温度 (°C)")
    t_out: float = Field(description="出口温度 (°C)")
    rho_in: float = Field(description="进口密度 (kg/m³)")
    rho_out: float = Field(description="出口密度 (kg/m³)")
    power_shaft: float = Field(description="轴功率 (kW)")
    speed_rpm: float = Field(default=3000, description="转速 (rpm)")
    blade_count: int = Field(default=13, description="叶片数")
    speed_ratio: float = Field(default=0.65, description="速比 (u/C₀)")
    reaction: float = Field(default=50, description="反动度 (%)")


@app.get("/api/flow/{mode}/nodes")
def get_flow_nodes(mode: str):
    """获取流程节点列表"""
    nodes = FLOW_NODES.get(mode, [])
    return {"success": True, "nodes": nodes}


@app.post("/api/vle/calc")
def calculate_vle(req: VleRequest):
    """气液平衡计算 (PT 闪蒸)"""
    try:
        result = vle_calc(
            p=req.p,
            t=req.t,
            composition=req.composition,
            total_flow=req.total_flow,
            flow_unit=req.flow_unit,
            p_unit='MPa.G'
        )
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/calculate/separator")
def calculate_separator(req: SeparatorRequest):
    """分离器设计计算"""
    try:
        # 从节点参数中提取工况
        node_params = req.node_params
        
        # 获取气体参数
        rho_gas = node_params.get('rho_gas', node_params.get('rho', 1.25))
        mu_gas = node_params.get('mu_gas', 1.8e-5)
        gas_flow = node_params.get('flow_rate', 1000)
        flow_unit = node_params.get('flow_unit', 'Nm3/h')
        
        # 从 VLE 结果获取液体参数
        if req.vle_result and not req.vle_result.get('skip', False):
            liquid_flow = req.vle_result.get('liquid_flow', 0)
            rho_liquid = req.vle_result.get('rho_liquid', 958)
        else:
            # 无 VLE 计算时，用户输入或默认值
            liquid_flow = node_params.get('liquid_flow', 0)
            rho_liquid = node_params.get('rho_liquid', 958)
        
        result = separator_design(
            gas_flow=gas_flow,
            rho_gas=rho_gas,
            mu_gas=mu_gas,
            liquid_flow=liquid_flow,
            rho_liquid=rho_liquid,
            droplet_size=req.droplet_size,
            length_ratio=req.length_ratio,
            separator_type=req.separator_type,
            residence_time_req=req.residence_time_req,
            flow_unit=flow_unit,
            liquid_flow_unit='T/h',
        )
        
        # 添加 VLE 结果
        if req.vle_result:
            result['vle'] = req.vle_result
        
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/calculate/mode5")
def calculate_mode5(req: Turbine1DRequest):
    """模式 5：涡轮一维通流设计"""
    try:
        result = turbine_1d_design(
            flow_rate=req.flow_rate,
            flow_unit=req.flow_unit,
            p_in=req.p_in,
            p_out=req.p_out,
            t_in=req.t_in,
            t_out=req.t_out,
            rho_in=req.rho_in,
            rho_out=req.rho_out,
            power_shaft=req.power_shaft,
            speed_rpm=req.speed_rpm,
            blade_count=req.blade_count,
            speed_ratio=req.speed_ratio,
            reaction=req.reaction,
        )
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/export/pdf/mode4")
def export_pdf_mode4(req: SeparatorRequest):
    """Export Mode 4 PDF Report (Separator)"""
    try:
        from app.reports.pdf_export_v2 import export_mode4_pdf
        from fastapi.responses import StreamingResponse
        
        # 先计算
        node_params = req.node_params
        vle_result = req.vle_result
        
        result = separator_design(
            gas_flow=node_params.get('flow_rate', 1000),
            rho_gas=node_params.get('rho', 1.25),
            mu_gas=node_params.get('mu', 1.8e-5),
            liquid_flow=vle_result.get('liquid_flow', 0) if vle_result and not vle_result.get('skip') else 0,
            rho_liquid=vle_result.get('rho_liquid', 958) if vle_result and not vle_result.get('skip') else 958,
            droplet_size=req.droplet_size,
            length_ratio=req.length_ratio,
            separator_type=req.separator_type,
            residence_time_req=req.residence_time_req,
        )
        
        input_params = {
            'node_id': req.node_id,
            'node_params': node_params,
            'designParams': {
                'dropletSize': req.droplet_size,
                'lengthRatio': req.length_ratio,
                'separatorType': req.separator_type,
                'residenceTimeReq': req.residence_time_req,
            }
        }
        
        pdf_bytes = export_mode4_pdf(result, input_params)
        return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf",
                       headers={"Content-Disposition": f"attachment; filename=separator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"})
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/export/pdf/mode5")
def export_pdf_mode5(req: Turbine1DRequest):
    """Export Mode 5 PDF Report (Turbine)"""
    try:
        from app.reports.pdf_export_v2 import export_mode5_pdf
        from fastapi.responses import StreamingResponse
        
        result = turbine_1d_design(
            flow_rate=req.flow_rate,
            flow_unit=req.flow_unit,
            p_in=req.p_in,
            p_out=req.p_out,
            t_in=req.t_in,
            t_out=req.t_out,
            rho_in=req.rho_in,
            rho_out=req.rho_out,
            power_shaft=req.power_shaft,
            speed_rpm=req.speed_rpm,
            blade_count=req.blade_count,
            speed_ratio=req.speed_ratio,
            reaction=req.reaction,
        )
        
        input_params = {
            'speed_rpm': req.speed_rpm,
            'speed_ratio': req.speed_ratio,
            'reaction': req.reaction,
        }
        
        pdf_bytes = export_mode5_pdf(result, input_params)
        return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf",
                       headers={"Content-Disposition": f"attachment; filename=turbine_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"})
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/export/excel/mode4")
def export_excel_mode4(req: SeparatorRequest):
    """Export Mode 4 Excel Report (Separator)"""
    try:
        from app.reports.excel_export_v2 import export_mode4_excel
        from fastapi.responses import StreamingResponse
        
        node_params = req.node_params
        vle_result = req.vle_result
        
        result = separator_design(
            gas_flow=node_params.get('flow_rate', 1000),
            rho_gas=node_params.get('rho', 1.25),
            mu_gas=node_params.get('mu', 1.8e-5),
            liquid_flow=vle_result.get('liquid_flow', 0) if vle_result and not vle_result.get('skip') else 0,
            rho_liquid=vle_result.get('rho_liquid', 958) if vle_result and not vle_result.get('skip') else 958,
            droplet_size=req.droplet_size,
            length_ratio=req.length_ratio,
            separator_type=req.separator_type,
            residence_time_req=req.residence_time_req,
        )
        
        input_params = {
            'node_id': req.node_id,
            'node_params': node_params,
            'designParams': {
                'dropletSize': req.droplet_size,
                'lengthRatio': req.length_ratio,
                'separatorType': req.separator_type,
                'residenceTimeReq': req.residence_time_req,
            }
        }
        
        excel_bytes = export_mode4_excel(result, input_params)
        return StreamingResponse(io.BytesIO(excel_bytes), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       headers={"Content-Disposition": f"attachment; filename=separator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"})
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/export/excel/mode5")
def export_excel_mode5(req: Turbine1DRequest):
    """Export Mode 5 Excel Report (Turbine)"""
    try:
        from app.reports.excel_export_v2 import export_mode5_excel
        from fastapi.responses import StreamingResponse
        
        result = turbine_1d_design(
            flow_rate=req.flow_rate,
            flow_unit=req.flow_unit,
            p_in=req.p_in,
            p_out=req.p_out,
            t_in=req.t_in,
            t_out=req.t_out,
            rho_in=req.rho_in,
            rho_out=req.rho_out,
            power_shaft=req.power_shaft,
            speed_rpm=req.speed_rpm,
            blade_count=req.blade_count,
            speed_ratio=req.speed_ratio,
            reaction=req.reaction,
        )
        
        input_params = {
            'speed_rpm': req.speed_rpm,
            'speed_ratio': req.speed_ratio,
            'reaction': req.reaction,
        }
        
        excel_bytes = export_mode5_excel(result, input_params)
        return StreamingResponse(io.BytesIO(excel_bytes), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       headers={"Content-Disposition": f"attachment; filename=turbine_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"})
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    print("Starting PDS Calc API server...")
    print("URL: http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
