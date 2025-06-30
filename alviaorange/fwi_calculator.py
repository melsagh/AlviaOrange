"""
Canadian Forest Fire Weather Index (FWI) System Calculator.

This module implements the core equations of the Canadian FWI System,
a widely used method for rating fire danger. The calculations are based on
consecutive daily observations of temperature, relative humidity, wind speed,
and 24-hour precipitation.

References:
- Van Wagner, C.E. (1987). Development and structure of the Canadian Forest
  Fire Weather Index System. Canadian Forestry Service, Forestry Technical
  Report 35, Ottawa, ON.
- Wang, Y., Anderson, K. R., & Suddaby, R. M. (2015). Updated source code
  for calculating fire danger indices in the Canadian Forest Fire
  Danger Rating System. Natural Resources Canada, Canadian Forest Service,
  Northern Forestry Centre, Edmonton, Alberta. Information Report NOR-X-424.
"""

from __future__ import annotations
import math
from typing import Dict, Any
from datetime import datetime

from .config import fwi_config

# ============================================================================
# MAIN CALCULATION FUNCTION
# ============================================================================

def calculate_fwi(
    temp: float,
    rh: float,
    wind: float,
    precip: float,
    ffmc_prev: float,
    dmc_prev: float,
    dc_prev: float
) -> Dict[str, Any]:
    """
    Calculate all components of the Canadian FWI System.

    Args:
        temp: Temperature (Celsius)
        rh: Relative humidity (%)
        wind: Wind speed (km/h)
        precip: 24-hour precipitation (mm)
        ffmc_prev: Previous day's Fine Fuel Moisture Code
        dmc_prev: Previous day's Duff Moisture Code
        dc_prev: Previous day's Drought Code

    Returns:
        A dictionary containing all FWI components.
    """
    # 1. Fine Fuel Moisture Code (FFMC)
    ffmc = _calculate_ffmc(temp, rh, wind, precip, ffmc_prev)
    
    # 2. Duff Moisture Code (DMC)
    dmc = _calculate_dmc(temp, rh, precip, dmc_prev)
    
    # 3. Drought Code (DC)
    dc = _calculate_dc(temp, precip, dc_prev)
    
    # 4. Initial Spread Index (ISI)
    isi = _calculate_isi(wind, ffmc)
    
    # 5. Buildup Index (BUI)
    bui = _calculate_bui(dmc, dc)
    
    # 6. Fire Weather Index (FWI)
    fwi = _calculate_fwi_final(isi, bui)

    # Determine danger class
    danger_class = fwi_config.get_danger_class(fwi)
    
    return {
        "ffmc": round(ffmc, 1),
        "dmc": round(dmc, 1),
        "dc": round(dc, 1),
        "isi": round(isi, 1),
        "bui": round(bui, 1),
        "fwi": round(fwi, 1),
        "danger_class": danger_class,
        "risk_level": _map_danger_to_risk(danger_class) # As per user requirement
    }

# ============================================================================
# FWI COMPONENT CALCULATIONS
# ============================================================================

def _calculate_ffmc(temp: float, rh: float, wind: float, precip: float, ffmc_prev: float) -> float:
    """Calculate the Fine Fuel Moisture Code (FFMC)."""
    # Effect of moisture on fine fuel
    m_o = (147.2 * (101.0 - ffmc_prev)) / (59.5 + ffmc_prev)
    
    if precip > 0.5:
        # Rainfall effect
        rf = precip - 0.5
        if m_o > 150.0:
            m_o += 0.0015 * (m_o - 150.0)**2 + rf
        else:
            m_o += rf
        if m_o > 250.0:
            m_o = 250.0
    
    # Equilibrium moisture content
    e_d = (0.942 * rh**0.679 + 11.0 * math.exp((rh - 100.0) / 10.0) +
           0.18 * (21.1 - temp) * (1.0 - 1.0 / math.exp(rh * 0.115)))
    e_w = (0.618 * rh**0.753 + 10.0 * math.exp((rh - 100.0) / 10.0) +
           0.18 * (21.1 - temp) * (1.0 - 1.0 / math.exp(rh * 0.115)))

    if m_o > e_d:
        # Drying phase
        k_a = (0.424 * (1.0 - ((100.0 - rh) / 100.0)**1.7) +
               0.0694 * wind**0.5 * (1.0 - ((100.0 - rh) / 100.0)**8))
        k_d = k_a * 0.581 * math.exp(0.0365 * temp)
        m = e_d + (m_o - e_d) * 10**(-k_d)
    elif m_o < e_w:
        # Wetting phase
        k_b = (0.424 * (1.0 - (rh / 100.0)**1.7) +
               0.0694 * wind**0.5 * (1.0 - (rh / 100.0)**8))
        k_w = k_b * 0.581 * math.exp(0.0365 * temp)
        m = e_w - (e_w - m_o) * 10**(-k_w)
    else:
        m = m_o

    ffmc = (59.5 * (250.0 - m)) / (147.2 + m)
    return max(0.0, min(ffmc, 101.0))

def _calculate_dmc(temp: float, rh: float, precip: float, dmc_prev: float) -> float:
    """Calculate the Duff Moisture Code (DMC)."""
    if precip > 1.5:
        re = 0.92 * precip - 1.27
        m_o = 20.0 + math.exp(5.6348 - dmc_prev / 43.43)
        if dmc_prev <= 33.0:
            b = 100.0 / (0.5 + 0.3 * dmc_prev)
        elif dmc_prev <= 65.0:
            b = 14.0 - 1.3 * math.log(dmc_prev)
        else:
            b = 6.2 * math.log(dmc_prev) - 17.2
        m = m_o + 1000.0 * re / (48.77 + b * re)
        dmc = 43.43 * (5.6348 - math.log(m - 20.0))
    else:
        dmc = dmc_prev

    dmc = max(0.0, dmc)
    
    # Drying process
    if temp > -1.1:
        # Effective day length
        l_e_map = [6.5, 7.5, 9.0, 12.8, 13.9, 13.9, 12.4, 10.9, 9.4, 8.0, 7.0, 6.0]
        l_e = l_e_map[datetime.now().month - 1]
        
        k = 1.894 * (temp + 1.1) * (100.0 - rh) * l_e * 1e-6
        dmc += k
    
    return max(0.0, dmc)

def _calculate_dc(temp: float, precip: float, dc_prev: float) -> float:
    """Calculate the Drought Code (DC)."""
    if precip > 2.8:
        rd = 0.83 * precip - 1.27
        q_o = 800.0 * math.exp(-dc_prev / 400.0)
        qr = q_o + 3.937 * rd
        dc = 400.0 * math.log(800.0 / qr)
    else:
        dc = dc_prev
        
    dc = max(0.0, dc)

    if temp > -2.8:
        # Potential evapotranspiration
        pe = (0.36 * (temp + 2.8) + (-0.15 * temp + 0.15 * -2.8)) / 2
        dc += pe
    
    return max(0.0, dc)

def _calculate_isi(wind: float, ffmc: float) -> float:
    """Calculate the Initial Spread Index (ISI)."""
    m = (147.2 * (101.0 - ffmc)) / (59.5 + ffmc)
    f_f = 91.9 * math.exp(-0.1386 * m) * (1.0 + m**5.31 / 4.93e7)
    f_w = math.exp(0.05039 * wind)
    isi = 0.208 * f_w * f_f
    return isi

def _calculate_bui(dmc: float, dc: float) -> float:
    """Calculate the Buildup Index (BUI)."""
    if dmc <= 0.4 * dc:
        bui = (0.8 * dc * dmc) / (dmc + 0.4 * dc)
    else:
        bui = dmc - (1.0 - 0.8 * dc / (dmc + 0.4 * dc)) * (0.92 + (0.0114 * dmc)**1.7)
    return max(0.0, bui)

def _calculate_fwi_final(isi: float, bui: float) -> float:
    """Calculate the final Fire Weather Index (FWI)."""
    if bui > 80.0:
        f_d = 0.6 * math.log(bui) - 1.0
    else:
        f_d = (1000.0 * bui) / (40.0 * bui + 340.0)
        
    b = 0.1 * isi * f_d
    
    if b > 1.0:
        fwi = math.exp(2.72 * (0.434 * math.log(b))**0.647)
    else:
        fwi = b
    return fwi

def _map_danger_to_risk(danger_class: str) -> str:
    """Map FWI danger class to the risk level required by user."""
    mapping = {
        "Very Low": "Low",
        "Low": "Low",
        "Moderate": "Medium",
        "High": "High",
        "Very High": "High",
        "Extreme": "Extreme"
    }
    return mapping.get(danger_class, "Unknown") 