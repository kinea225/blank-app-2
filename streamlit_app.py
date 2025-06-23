import streamlit as st
from streamlit_folium import folium_static
import folium
from folium.plugins import MarkerCluster
import pandas as pd
import time 
import matplotlib.pyplot as plt
import koreanize_matplotlib
import geopandas as gpd
import geodatasets
from folium.features import GeoJsonTooltip

name_map = {
    "서울": "서울특별시",
    "부산": "부산광역시",
    "대구": "대구광역시",
    "인천": "인천광역시",
    "광주": "광주광역시",
    "대전": "대전광역시",
    "울산": "울산광역시",
    "세종": "세종특별자치시",
    "경기": "경기도",
    "강원도": "강원특별자치도",  # 또는 "강원도"
    "충북": "충청북도",
    "전북": "전라북도",
    "전남": "전라남도",
    "경북": "경상북도",
    "경남": "경상남도",
    "제주": "제주특별자치도"
}

@st.cache_data
def load_fire_data(csv_path):
    df = pd.read_csv(csv_path, encoding="cp949")
    # 열 이름 재설정: 발생장소_시도 -> 시군구
    df = df.rename(columns={'발생장소_시도': '시도'})
    # 각 시군구별로 "발생건수", "평균피해면적", "피해면적합계"를 계산합니다.
    fire_counts = df.groupby('시도').agg(
        발생건수=('피해면적_합계', 'count'),
        평균피해면적=('피해면적_합계', 'mean'),
        피해면적합계=('피해면적_합계', 'sum')
    ).reset_index()
    #st.dataframe(fire_counts)
    return fire_counts
    
# Shapefile (또는 GeoJSON) 로딩 및 지오메트리 단순화를 캐싱합니다.
@st.cache_resource
def load_shapefile(shp_path, tolerance=0.01):
    gdf = gpd.read_file(shp_path, encoding='euc-kr')
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:5179")
    # 폴리곤의 복잡도를 줄여서 렌더링 속도를 개선 (tolerance 값은 조정 필요)
    gdf['geometry'] = gdf['geometry'].simplify(tolerance=tolerance)
    return gdf
# 함수 밖에 정의
def style_function(x):
    return {'fillColor': 'transparent', 'color': 'black', 'weight': 0.5}

def highlight_function(x):
    return {'weight': 3, 'fillColor': 'yellow', 'fillOpacity': 0.5}

def find_full_name(short_name, gdf_names):
    # 완전 일치 우선, 없으면 부분 일치
    for full_name in gdf_names:
        if short_name == full_name:
            return full_name
    for full_name in gdf_names:
        if short_name in full_name or full_name in short_name:
            return full_name
    return None
def create_map():
    fire_counts = load_fire_data("fire.csv")
    gdf = load_shapefile('./ctprvn/ctprvn.shp', tolerance=0.05)
    fire_counts.replace("강원도",'강원',inplace=True)

    gdf_names = list(gdf['CTP_KOR_NM'])
    fire_counts['시도_정규화'] = fire_counts['시도'].apply(lambda x: find_full_name(x, gdf_names))
    #st.dataframe(fire_counts)
    merged = gdf.merge(fire_counts, left_on="CTP_KOR_NM", right_on="시도_정규화", how="left")
    merged["발생건수"] = merged["발생건수"].fillna(0)
    
    m = folium.Map(location=[36.5, 127.5], zoom_start=6, control_scale=True)
    
    # 로딩이 너무 오래 걸림
    folium.Choropleth(
        geo_data=merged,
        data=merged,
        columns=["CTP_KOR_NM", "발생건수"],
        key_on="feature.properties.CTP_KOR_NM",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="화재 발생 건수"
    ).add_to(m)
    
    tooltip = GeoJsonTooltip(
        fields=["CTP_KOR_NM", "발생건수", "피해면적합계"],
        aliases=["시도:", "화재 건수:", "피해 면적 합계:"],
        localize=True
    )
    folium.GeoJson(
        merged,
        tooltip=tooltip,
        style_function=style_function,
        highlight_function=highlight_function
    ).add_to(m)

    return m