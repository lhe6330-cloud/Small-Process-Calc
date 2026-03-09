"""
PDS Calc Backend - FastAPI 主应用
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Optional, List
from datetime import datetime
import traceback

# 导入计算模块
try:
    from app.core.thermodynamics import get_fluid_property, gauge_to_absolute
    from app.core.turbine import calculate_turbine
    from app.core.heat_exchanger import calculate_heat_exchanger
    from app.core.selection import select_motor, select_pipe_diameter, select_valve, calculate_pipe_flow
    from app.core.calculator import calculate_mode2, calculate_mode3
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
                "power_shaft": turbine_result['power_shaft'],
                "power_electric": turbine_result['power_electric'],
                "t_out": turbine_result['t_out'],
                "x_out": turbine_result['x_out'],
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
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/standards/motors")
def get_motors():
    from app.core.selection import MOTORS
    return {"motors": MOTORS}

@app.get("/api/standards/pipes")
def get_pipes():
    from app.core.selection import PIPES
    return {"pipes": PIPES}

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

if __name__ == "__main__":
    import uvicorn
    print("Starting PDS Calc API server...")
    print("URL: http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
