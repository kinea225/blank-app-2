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
import numpy as np


st.set_page_config(page_title="프로젝트 작성", layout="centered")
#배경 설정

st.markdown(f"""

<style>
.stApp,.stAppHeader{{
        background-image: url("https://cdn.pixabay.com/photo/2024/05/30/19/37/girl-8799169_1280.jpg");
            background-attachment: fixed;
            background-size: cover;
            isolation: isolate;}}
.stApp::after,.stAppHeader:after {{
    content: '';
    position: absolute;
    background: white;
    z-index: -1;
    inset: 0;
    opacity: 0.5;
}}
</style>
""", unsafe_allow_html=True)
# 사이드 바
st.markdown("""
<style>
/* 노멀라이즈 시작 */
body, ul, li {
  margin: 0;
  padding: 0;
  list-style: none;   	    /* 해당 태그의 list-style을 none으로 하는 것으로 ●을 제거한다 */
}

a {
  color: inherit;   	    /* 부모 엘리먼트의 값을 물려받는다 */
  text-decoration: none !important;    /* 해당 태그의 text-decoration 속성을 none 값으로 하는 것으로 밑줄을 제거한다 */
}
/* 노멀라이즈 끝 */
/* 2차 이상의 메뉴를 숨기기 */
.side-bar > ul ul {
  display: none;
}

/* 사이드바의 너비와 높이를 변수를 통해 통제 */
:root {
  --side-bar-width: 850px;
  //--side-bar-height: 90vh;
}
aside ul {
    margin-top: 20%;}
.side-bar {
  position: fixed;    /* 스크롤을 따라오도록 지정 */
  background-image: url("https://cdn.pixabay.com/photo/2021/12/01/21/32/mountains-6839168_1280.jpg");
  background-size: cover;
  background-position: right center;    /* 배경 이미지의 위치를 오른쪽 중앙으로 지정 */
  width: 270px;
  min-height: 80%;   /* 사이드바의 높이를 전체 화면 높이의 90%로 지정 */
  //margin-top: calc((100vh - var(--side-bar-height)) / 2);    /* 사이드바 위와 아래의 마진을 동일하게 지정 */
}

/* 모든 메뉴의 a에 속성값 부여 */
.side-bar ul > li > a {
  display: block;
  color: white;
  font-size: 1.4rem;
  font-weight: bold;
  padding-top: 20px;
  padding-bottom: 20px;
  padding-left: 50px;
}
/* 자식의 position이 absolute일 때 자식을 영역 안에 가두어 준다 */
.side-bar > ul > li {
  margin: 0;
  padding: 0;
  position: relative;
}

/* 모든 메뉴가 마우스 인식 시 반응 */
.side-bar ul > li:hover > a {
  backdrop-filter:blur(10px);    /* 배경 흐림 효과 */;
  border: 0.2px solid gray;
}

/* 사이드바 너비의 80%만큼 왼쪽으로 이동 */
.side-bar {
  box-shadow: 0px 0px 30px black;
  border-radius: 20px;
  transform: translate(calc(var(--side-bar-width)*-1), 0);  /* X축 이동, Y축 고정 */
  transition: .5s;
}

/* 마우스 인식 시 원래의 위치로 이동 */
.side-bar:hover {
  transform: translate(-600px, 0);   /* 둥근 모서리의 너비만큼 X축 이동, Y축 고정 */
}
.side-bar_footer {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  padding: 20px;
  background-color: rgba(0, 0, 0, 0.2); /* 반투명 배경 */
  color: white;
  text-align: left;
}
.side-bar_footer >.information {
    text-align: center;
    margin-top: 20px;
    font-size: 0.8rem;
    color: lightgray;
}
</style>
<aside class="side-bar">
  <section class="side-bar__icon-box">
    <section class="side-bar__icon-1">
      <div></div>
      <div></div>
      <div></div>
    </section>
  </section>
  <ul>
    <li>
      <a href="https://bobtong-sub-one.streamlit.app/" target="_self">비교 자료보기</a>
    </li>
    <li>
      <a href="#" target="_self">발생위치 보기</a>
    </li>
    <li>
      <a href="#" target="_self">지역별 건수 보기</a>
    </li>
    <li>
      <a href="#" target="_self">연도별 건수 보기</a>
    </li>
    <li>
      <a href="https://bobtong-main.streamlit.app/~/+/" target="_self">홈으로</a>
    </li>
  </ul>
  <div class="side-bar_footer">
    <p>팀명 : 밥통</p>
    <p>팀원 : 남경태, 김태홍, 이도영</p>
    <p>주제 : 산불 발생 현황</p>         
    <p class="information">© 22~23년 산불 발생 현황</p>
  </div>
</aside>

""",
    unsafe_allow_html=True
)
month = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
ty1 = [0, 50, 100, 150, 200, 250, 300]
ty2 = [0, 5, 10, 15, 20, 25]
# 데이터 불러오기
file = pd.read_csv("fire.csv", encoding='cp949')
forestFires = pd.DataFrame(file)
koreanCoordinate = pd.DataFrame(pd.read_csv("korea.csv",encoding='cp949'))

#24년도 데이터 제거
forestFires=forestFires[forestFires['발생일시_년']!=2024]
# 각 달 별로 산불 발생 건수 계산
forestFires= forestFires.groupby(['발생일시_월']).size().reset_index(name='발생건수')
# 각 달 별로 산불 발생 건수의 비율 계산
forestFires['발생비율'] = (forestFires['발생건수'] / forestFires['발생건수'].sum() * 100).round(2)
# 차트 그리기
x = month
y1 = forestFires['발생건수']
y2 = forestFires['발생비율']
fig, ax1 = plt.subplots(figsize=(40, 35))

bars = ax1.bar(x, y1, color=['#FF6347', '#FF8C00',  '#1E90FF', '#9400D3'], label='발생건수')
ax1.set_xlabel('산불이 발생한 달 (월 단위)', fontsize=90,labelpad=20, fontweight='bold', color='black')
ax1.set_xticks(month)
ax1.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x)}월'))  # x축 월 포맷
ax1.tick_params(axis='x', labelcolor='black', labelsize=50)
                      
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x)}건'))  # y축 건수 포맷
ax1.set_yticks(ty1)
ax1.set_ylabel('건수',color='black',fontweight='bold',fontsize=80,labelpad=50,rotation=0)
ax1.tick_params(axis='y', labelcolor='black',labelsize=50)

# 막대 위에 발생 건수 표시
for bar, count in zip(bars, y1):
    ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height()/2, str(count), 
             ha='center', va='bottom', fontsize=30, color='black', fontweight='bold')

ax2 = ax1.twinx()
ax2.plot(x, y2, color='green', marker='o', label='발생비율')

ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x)}%'))  # y축 비율 포맷
ax2.set_ylabel('비율', color='black',fontweight='bold',fontsize=80,labelpad=50,rotation=0)
ax2.set_yticks(ty2)
ax2.tick_params(axis='y', labelcolor='black',labelsize=50)
ax1.set_title('2022~2023년도 산불 발생 현황', fontsize=100, fontweight='bold', color='black', pad=100)

# 선 위에 발생 비율 표시
for i, txt in enumerate(y2):
    ax2.text(x[i], y2[i] + 0.5, f'{txt}%', ha='center', va='bottom', fontsize=30, color='black', fontweight='bold')

# 범례 추가
ax1.legend(loc='upper left',fontsize=60)
ax2.legend(loc='upper right',fontsize=60)

# 그래프 레이아웃 조정
fig.tight_layout()

                    

# Streamlit에 표시

st.markdown(
    "<h1 style = 'text-align : center; font-size:50px;'>22~23년도 산불 발생 현황</h1>",
    unsafe_allow_html=True)
st.pyplot(fig)



# 데이터 보기기
#st.dataframe(koreanCoordinate)
#st.dataframe(forestFires)



# 아직 사용안하고 있는 데이터
# 연도 및 한국 좌표 배열열
# korea = [36.3, 127]
# option = [2023,2022]
# 지역 배열
# option2 = ["경기도", "서울", "부산", "인천", "경상남도", "경상북도", "대구",
#     "충청남도", "전라남도", "전라북도", "충청북도", "강원도", "대전", "광주",
#     "울산", "세종"]
# 지도 위치 표시에 사용되는 데이터 
# dataCity = gpd.read_file('./ctprvn/ctprvn.shp',encoding='euc-kr')
# dataNeighborhood = gpd.read_file('./sig/sig.shp',encoding='euc-kr')
