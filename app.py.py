import json
import os
import re
import time
import streamlit as st

st.set_page_config(page_title="내 취향 영화 추천", page_icon="🎬", layout="centered")
st.markdown("""
<style>
.stApp {background:#101116;color:#ececf0}.block-container{max-width:900px;padding-top:2rem}
.hero{padding:1.5rem;border:1px solid #343642;border-radius:18px;background:linear-gradient(135deg,#20171b,#151720);text-align:center;margin-bottom:1.5rem}
.hero h1{color:#ff5262}.movie-card{padding:1rem 1.2rem;margin:.7rem 0;border:1px solid #343642;border-radius:14px;background:#191a21}
.muted{color:#aaa}
</style>
""", unsafe_allow_html=True)

# Curated catalogue: recommendations are selected only from this list.
MOVIES = [
 {"title":"기생충","year":2019,"country":"한국","genres":["드라마","스릴러·미스터리","범죄·느와르"],"mood":["어둡고 진중한","긴장되고 불안한"],"pace":"균형 잡힌 전개","ending":"씁쓸하지만 현실적인 결말","characters":["복잡하고 모순적인 인물","선악을 판단하기 어려운 인물"],"reality":"현실적인 이야기와 생활감","qualities":["탄탄하고 흥미로운 이야기","현실을 바라보게 하는 주제","예상하기 어려운 전개와 반전"],"intensity":3,"language":"한국 영화","runtime":"보통 길이","tags":["계급","가족","풍자","반전"]},
 {"title":"헤어질 결심","year":2022,"country":"한국","genres":["드라마","로맨스","스릴러·미스터리"],"mood":["감성적이고 서정적인","기묘하고 몽환적인"],"pace":"천천히 인물과 관계를 쌓는 전개","ending":"해석을 관객에게 맡기는 열린 결말","characters":["복잡하고 모순적인 인물"],"reality":"현실에 약간의 환상이나 비현실성이 섞인 이야기","qualities":["입체적인 인물과 인물 간 관계","영상미와 색감","감정적인 여운과 공감"],"intensity":2,"language":"한국 영화","runtime":"보통 길이","tags":["사랑","수사","여운","영상미"]},
 {"title":"살인의 추억","year":2003,"country":"한국","genres":["드라마","스릴러·미스터리","범죄·느와르"],"mood":["어둡고 진중한","긴장되고 불안한"],"pace":"단서가 쌓이며 마지막에 풀리는 전개","ending":"씁쓸하지만 현실적인 결말","characters":["평범하고 현실적인 인물","복잡하고 모순적인 인물"],"reality":"실제 사건이나 사회 문제를 다룬 이야기","qualities":["탄탄하고 흥미로운 이야기","현실을 바라보게 하는 주제","긴장감과 속도감"],"intensity":3,"language":"한국 영화","runtime":"보통 길이","tags":["수사","실화","사회","미스터리"]},
 {"title":"올드보이","year":2003,"country":"한국","genres":["스릴러·미스터리","액션·모험","드라마"],"mood":["어둡고 진중한","긴장되고 불안한"],"pace":"예상 밖의 사건이 계속되는 전개","ending":"강한 반전이 있는 결말","characters":["복잡하고 모순적인 인물","상처를 딛고 나아가는 인물"],"reality":"현실에 약간의 환상이나 비현실성이 섞인 이야기","qualities":["예상하기 어려운 전개와 반전","감정적인 여운과 공감","영상미와 색감"],"intensity":3,"language":"한국 영화","runtime":"보통 길이","tags":["복수","반전","미스터리","강렬함"]},
 {"title":"버닝","year":2018,"country":"한국","genres":["드라마","스릴러·미스터리"],"mood":["어둡고 진중한","기묘하고 몽환적인"],"pace":"큰 사건보다 분위기와 감정을 따라가는 전개","ending":"해석을 관객에게 맡기는 열린 결말","characters":["복잡하고 모순적인 인물","선악을 판단하기 어려운 인물"],"reality":"현실적인 이야기와 생활감","qualities":["현실을 바라보게 하는 주제","독창적인 세계관과 상상력","영상미와 색감"],"intensity":2,"language":"한국 영화","runtime":"느린 영화도 분위기가 좋으면 선호함","tags":["계급","모호함","청춘","여운"]},
 {"title":"리틀 포레스트","year":2018,"country":"한국","genres":["드라마","로맨스"],"mood":["따뜻하고 편안한","감성적이고 서정적인"],"pace":"큰 사건보다 분위기와 감정을 따라가는 전개","ending":"희망과 위로가 남는 결말","characters":["평범하고 현실적인 인물","성장하고 변화하는 인물"],"reality":"현실적인 이야기와 생활감","qualities":["감정적인 여운과 공감","영상미와 색감","음악과 사운드"],"intensity":1,"language":"한국 영화","runtime":"보통 길이","tags":["힐링","음식","성장","자연"]},
 {"title":"극한직업","year":2019,"country":"한국","genres":["코미디","액션·모험"],"mood":["밝고 경쾌한"],"pace":"시작부터 빠르게 몰입되는 전개","ending":"갈등이 명확히 해결되는 결말","characters":["유쾌하고 매력적인 인물"],"reality":"현실과 환상이 섞인 이야기","qualities":["유머와 오락성","긴장감과 속도감"],"intensity":1,"language":"한국 영화","runtime":"짧고 속도감 있는 영화","tags":["팀워크","코미디","액션"]},
 {"title":"택시운전사","year":2017,"country":"한국","genres":["드라마","액션·모험"],"mood":["감정적이고 서정적인","웅장하고 스펙터클한"],"pace":"빠른 장면과 느린 장면이 적절히 섞인 전개","ending":"희망과 위로가 남는 결말","characters":["성장하고 변화하는 인물","평범하고 현실적인 인물"],"reality":"실제 사건이나 사회 문제를 다룬 이야기","qualities":["감정적인 여운과 공감","현실을 바라보게 하는 주제"],"intensity":2,"language":"한국 영화","runtime":"보통 길이","tags":["역사","실화","연대","사회"]},
 {"title":"완벽한 타인","year":2018,"country":"한국","genres":["드라마","코미디"],"mood":["밝고 경쾌한","긴장되고 불안한"],"pace":"단서가 쌓이며 마지막에 풀리는 전개","ending":"작품에 따라 다름","characters":["복잡하고 모순적인 인물","인물보다 사건과 세계관이 중요함"],"reality":"현실적인 이야기와 생활감","qualities":["입체적인 인물과 인물 간 관계","예상하기 어려운 전개와 반전","유머와 오락성"],"intensity":2,"language":"한국 영화","runtime":"보통 길이","tags":["우정","비밀","관계","대화"]},
 {"title":"남산의 부장들","year":2020,"country":"한국","genres":["드라마","범죄·느와르","스릴러·미스터리"],"mood":["어둡고 진중한","긴장되고 불안한"],"pace":"천천히 인물과 관계를 쌓는 전개","ending":"씁쓸하지만 현실적인 결말","characters":["유능하고 주도적인 인물","복잡하고 모순적인 인물"],"reality":"실제 사건이나 사회 문제를 다룬 이야기","qualities":["현실을 바라보게 하는 주제","입체적인 인물과 인물 간 관계"],"intensity":2,"language":"한국 영화","runtime":"보통 길이","tags":["정치","역사","권력","실화"]},
 {"title":"인터스텔라","year":2014,"country":"영어권 영화","genres":["SF·판타지","드라마","액션·모험"],"mood":["웅장하고 스펙터클한","감성적이고 서정적인"],"pace":"빠른 장면과 느린 장면이 적절히 섞인 전개","ending":"희망과 위로가 남는 결말","characters":["상처를 딛고 나아가는 인물"],"reality":"독창적인 세계관과 설정이 중심인 이야기","qualities":["독창적인 세계관과 상상력","감정적인 여운과 공감","음악과 사운드"],"intensity":2,"language":"영어권 영화","runtime":"길어도 몰입감 있으면 괜찮음","tags":["우주","가족","시간","과학"]},
 {"title":"인셉션","year":2010,"country":"영어권 영화","genres":["SF·판타지","액션·모험","스릴러·미스터리"],"mood":["긴장되고 불안한","웅장하고 스펙터클한"],"pace":"예상 밖의 사건이 계속되는 전개","ending":"해석을 관객에게 맡기는 열린 결말","characters":["유능하고 주도적인 인물"],"reality":"독창적인 세계관과 설정이 중심인 이야기","qualities":["독창적인 세계관과 상상력","예상하기 어려운 전개와 반전","음악과 사운드"],"intensity":2,"language":"영어권 영화","runtime":"길어도 몰입감 있으면 괜찮음","tags":["꿈","두뇌게임","반전","액션"]},
 {"title":"쇼생크 탈출","year":1994,"country":"영어권 영화","genres":["드라마","범죄·느와르"],"mood":["따뜻하고 편안한","감정적이고 서정적인"],"pace":"천천히 인물과 관계를 쌓는 전개","ending":"희망과 위로가 남는 결말","characters":["상처를 딛고 나아가는 인물","성장하고 변화하는 인물"],"reality":"현실적인 이야기와 생활감","qualities":["탄탄하고 흥미로운 이야기","감정적인 여운과 공감"],"intensity":2,"language":"영어권 영화","runtime":"길어도 몰입감 있으면 괜찮음","tags":["우정","희망","자유","성장"]},
 {"title":"굿 윌 헌팅","year":1997,"country":"영어권 영화","genres":["드라마","로맨스"],"mood":["따뜻하고 편안한","감정적이고 서정적인"],"pace":"천천히 인물과 관계를 쌓는 전개","ending":"희망과 위로가 남는 결말","characters":["성장하고 변화하는 인물","상처를 딛고 나아가는 인물"],"reality":"현실적인 이야기와 생활감","qualities":["입체적인 인물과 인물 간 관계","감정적인 여운과 공감"],"intensity":1,"language":"영어권 영화","runtime":"보통 길이","tags":["우정","성장","상처","대화"]},
 {"title":"이터널 선샤인","year":2004,"country":"영어권 영화","genres":["로맨스","SF·판타지","드라마"],"mood":["감성적이고 서정적인","기묘하고 몽환적인"],"pace":"큰 사건보다 분위기와 감정을 따라가는 전개","ending":"해석을 관객에게 맡기는 열린 결말","characters":["복잡하고 모순적인 인물"],"reality":"현실에 약간의 환상이나 비현실성이 섞인 이야기","qualities":["입체적인 인물과 인물 간 관계","독창적인 세계관과 상상력","감정적인 여운과 공감"],"intensity":2,"language":"영어권 영화","runtime":"보통 길이","tags":["기억","사랑","이별","상상력"]},
 {"title":"라라랜드","year":2016,"country":"영어권 영화","genres":["로맨스","드라마","코미디"],"mood":["감성적이고 서정적인","밝고 경쾌한"],"pace":"빠른 장면과 느린 장면이 적절히 섞인 전개","ending":"씁쓸하지만 현실적인 결말","characters":["성장하고 변화하는 인물"],"reality":"현실에 약간의 환상이나 비현실성이 섞인 이야기","qualities":["음악과 사운드","영상미와 색감","감정적인 여운과 공감"],"intensity":1,"language":"영어권 영화","runtime":"보통 길이","tags":["꿈","음악","사랑","예술"]},
 {"title":"대부","year":1972,"country":"영어권 영화","genres":["범죄·느와르","드라마"],"mood":["어둡고 진중한"],"pace":"천천히 인물과 관계를 쌓는 전개","ending":"씁쓸하지만 현실적인 결말","characters":["복잡하고 모순적인 인물","유능하고 주도적인 인물"],"reality":"현실적인 이야기와 생활감","qualities":["입체적인 인물과 인물 간 관계","탄탄하고 흥미로운 이야기"],"intensity":2,"language":"영어권 영화","runtime":"길어도 몰입감 있으면 괜찮음","tags":["가족","권력","범죄","고전"]},
 {"title":"다크 나이트","year":2008,"country":"영어권 영화","genres":["액션·모험","범죄·느와르","드라마"],"mood":["어둡고 진중한","긴장되고 불안한"],"pace":"빠른 장면과 느린 장면이 적절히 섞인 전개","ending":"씁쓸하지만 현실적인 결말","characters":["선악을 판단하기 어려운 인물","유능하고 주도적인 인물"],"reality":"현실과 환상이 섞인 이야기","qualities":["현실을 바라보게 하는 주제","긴장감과 속도감","입체적인 인물과 인물 간 관계"],"intensity":3,"language":"영어권 영화","runtime":"길어도 몰입감 있으면 괜찮음","tags":["영웅","정의","도덕","범죄"]},
 {"title":"포레스트 검프","year":1994,"country":"영어권 영화","genres":["드라마","로맨스","코미디"],"mood":["따뜻하고 편안한","감정적이고 서정적인"],"pace":"빠른 장면과 느린 장면이 적절히 섞인 전개","ending":"희망과 위로가 남는 결말","characters":["평범하고 현실적인 인물","성장하고 변화하는 인물"],"reality":"실제 사건이나 사회 문제를 다룬 이야기","qualities":["감정적인 여운과 공감","탄탄하고 흥미로운 이야기"],"intensity":1,"language":"영어권 영화","runtime":"길어도 몰입감 있으면 괜찮음","tags":["인생","역사","사랑","여정"]},
 {"title":"겟 아웃","year":2017,"country":"영어권 영화","genres":["공포","스릴러·미스터리"],"mood":["긴장되고 불안한","어둡고 진중한"],"pace":"단서가 쌓이며 마지막에 풀리는 전개","ending":"강한 반전이 있는 결말","characters":["선악을 판단하기 어려운 인물"],"reality":"현실을 상징이나 비유로 표현하는 작품","qualities":["예상하기 어려운 전개와 반전","현실을 바라보게 하는 주제","긴장감과 속도감"],"intensity":3,"language":"영어권 영화","runtime":"짧고 속도감 있는 영화","tags":["사회","풍자","공포","미스터리"]},
 {"title":"위플래쉬","year":2014,"country":"영어권 영화","genres":["드라마","음악"],"mood":["긴장되고 불안한","어둡고 진중한"],"pace":"시작부터 빠르게 몰입되는 전개","ending":"비극적이어도 주제가 분명한 결말","characters":["유능하고 주도적인 인물","복잡하고 모순적인 인물"],"reality":"현실적인 이야기와 생활감","qualities":["긴장감과 속도감","음악과 사운드","입체적인 인물과 인물 간 관계"],"intensity":3,"language":"영어권 영화","runtime":"짧고 속도감 있는 영화","tags":["음악","집념","경쟁","성취"]},
 {"title":"트루먼 쇼","year":1998,"country":"영어권 영화","genres":["드라마","코미디","SF·판타지"],"mood":["밝고 경쾌한","감성적이고 서정적인"],"pace":"빠른 장면과 느린 장면이 적절히 섞인 전개","ending":"희망과 위로가 남는 결말","characters":["성장하고 변화하는 인물"],"reality":"현실을 상징이나 비유로 표현하는 작품","qualities":["현실을 바라보게 하는 주제","독창적인 세계관과 상상력","유머와 오락성"],"intensity":1,"language":"영어권 영화","runtime":"보통 길이","tags":["자유","미디어","정체성","풍자"]},
 {"title":"매드맥스: 분노의 도로","year":2015,"country":"영어권 영화","genres":["액션·모험","SF·판타지"],"mood":["웅장하고 스펙터클한","긴장되고 불안한"],"pace":"시작부터 빠르게 몰입되는 전개","ending":"갈등이 명확히 해결되는 결말","characters":["유능하고 주도적인 인물","상처를 딛고 나아가는 인물"],"reality":"독창적인 세계관과 설정이 중심인 이야기","qualities":["긴장감과 속도감","영상미와 색감","독창적인 세계관과 상상력"],"intensity":3,"language":"영어권 영화","runtime":"보통 길이","tags":["추격","생존","액션","여성 주인공"]},
 {"title":"컨택트","year":2016,"country":"영어권 영화","genres":["SF·판타지","드라마","미스터리"],"mood":["감성적이고 서정적인","긴장되고 불안한"],"pace":"천천히 인물과 관계를 쌓는 전개","ending":"해석을 관객에게 맡기는 열린 결말","characters":["유능하고 주도적인 인물"],"reality":"독창적인 세계관과 설정이 중심인 이야기","qualities":["독창적인 세계관과 상상력","감정적인 여운과 공감","음악과 사운드"],"intensity":2,"language":"영어권 영화","runtime":"보통 길이","tags":["외계인","언어","시간","가족"]},
 {"title":"그랜드 부다페스트 호텔","year":2014,"country":"영어권 영화","genres":["코미디","드라마","모험"],"mood":["밝고 경쾌한","기묘하고 몽환적인"],"pace":"빠른 장면과 느린 장면이 적절히 섞인 전개","ending":"씁쓸하지만 현실적인 결말","characters":["유쾌하고 매력적인 인물"],"reality":"현실과 환상이 섞인 이야기","qualities":["영상미와 색감","유머와 오락성","독창적인 세계관과 상상력"],"intensity":1,"language":"영어권 영화","runtime":"보통 길이","tags":["우정","모험","미장센","유머"]},
 {"title":"문라이트","year":2016,"country":"영어권 영화","genres":["드라마","로맨스"],"mood":["감성적이고 서정적인","어둡고 진중한"],"pace":"큰 사건보다 분위기와 감정을 따라가는 전개","ending":"해석을 관객에게 맡기는 열린 결말","characters":["성장하고 변화하는 인물","상처를 딛고 나아가는 인물"],"reality":"현실적인 이야기와 생활감","qualities":["입체적인 인물과 인물 간 관계","영상미와 색감","감정적인 여운과 공감"],"intensity":2,"language":"영어권 영화","runtime":"짧고 속도감 있는 영화","tags":["정체성","성장","관계","영상미"]},
 {"title":"프란시스 하","year":2012,"country":"영어권 영화","genres":["코미디","드라마"],"mood":["밝고 경쾌한","감성적이고 서정적인"],"pace":"큰 사건보다 분위기와 감정을 따라가는 전개","ending":"희망과 위로가 남는 결말","characters":["평범하고 현실적인 인물","성장하고 변화하는 인물"],"reality":"현실적인 이야기와 생활감","qualities":["입체적인 인물과 인물 간 관계","유머와 오락성","음악과 사운드"],"intensity":1,"language":"영어권 영화","runtime":"짧고 속도감 있는 영화","tags":["우정","청춘","성장","도시"]},
 {"title":"타이타닉","year":1997,"country":"영어권 영화","genres":["로맨스","드라마","액션·모험"],"mood":["감성적이고 서정적인","웅장하고 스펙터클한"],"pace":"빠른 장면과 느린 장면이 적절히 섞인 전개","ending":"비극적이어도 주제가 분명한 결말","characters":["성장하고 변화하는 인물","상처를 딛고 나아가는 인물"],"reality":"실제 사건이나 사회 문제를 다룬 이야기","qualities":["감정적인 여운과 공감","음악과 사운드","탄탄하고 흥미로운 이야기"],"intensity":2,"language":"영어권 영화","runtime":"길어도 몰입감 있으면 괜찮음","tags":["사랑","재난","계급","역사"]},
 {"title":"스파이더맨: 뉴 유니버스","year":2018,"country":"영어권 영화","genres":["애니메이션","액션·모험","SF·판타지"],"mood":["밝고 경쾌한","웅장하고 스펙터클한"],"pace":"시작부터 빠르게 몰입되는 전개","ending":"희망과 위로가 남는 결말","characters":["성장하고 변화하는 인물","유쾌하고 매력적인 인물"],"reality":"독창적인 세계관과 설정이 중심인 이야기","qualities":["영상미와 색감","독창적인 세계관과 상상력","긴장감과 속도감"],"intensity":1,"language":"영어권 영화","runtime":"짧고 속도감 있는 영화","tags":["성장","히어로","가족","스타일"]},
 {"title":"센과 치히로의 행방불명","year":2001,"country":"일본 영화","genres":["애니메이션","SF·판타지","모험"],"mood":["기묘하고 몽환적인","따뜻하고 편안한"],"pace":"빠른 장면과 느린 장면이 적절히 섞인 전개","ending":"희망과 위로가 남는 결말","characters":["성장하고 변화하는 인물","유쾌하고 매력적인 인물"],"reality":"독창적인 세계관과 설정이 중심인 이야기","qualities":["독창적인 세계관과 상상력","영상미와 색감","감정적인 여운과 공감"],"intensity":1,"language":"일본 영화","runtime":"보통 길이","tags":["성장","모험","정령","상상력"]},
 {"title":"이웃집 토토로","year":1988,"country":"일본 영화","genres":["애니메이션","SF·판타지"],"mood":["따뜻하고 편안한","기묘하고 몽환적인"],"pace":"큰 사건보다 분위기와 감정을 따라가는 전개","ending":"희망과 위로가 남는 결말","characters":["평범하고 현실적인 인물"],"reality":"현실과 환상이 섞인 이야기","qualities":["영상미와 색감","감정적인 여운과 공감"],"intensity":1,"language":"일본 영화","runtime":"짧고 속도감 있는 영화","tags":["가족","자연","어린이","힐링"]},
 {"title":"너의 이름은.","year":2016,"country":"일본 영화","genres":["애니메이션","로맨스","SF·판타지"],"mood":["감성적이고 서정적인","웅장하고 스펙터클한"],"pace":"빠른 장면과 느린 장면이 적절히 섞인 전개","ending":"희망과 위로가 남는 결말","characters":["성장하고 변화하는 인물"],"reality":"현실에 약간의 환상이나 비현실성이 섞인 이야기","qualities":["영상미와 색감","음악과 사운드","감정적인 여운과 공감"],"intensity":1,"language":"일본 영화","runtime":"보통 길이","tags":["운명","사랑","시간","재난"]},
 {"title":"바람이 분다","year":2013,"country":"일본 영화","genres":["애니메이션","드라마","로맨스"],"mood":["감성적이고 서정적인","어둡고 진중한"],"pace":"천천히 인물과 관계를 쌓는 전개","ending":"씁쓸하지만 현실적인 결말","characters":["성장하고 변화하는 인물"],"reality":"실제 사건이나 사회 문제를 다룬 이야기","qualities":["영상미와 색감","감정적인 여운과 공감","현실을 바라보게 하는 주제"],"intensity":2,"language":"일본 영화","runtime":"길어도 몰입감 있으면 괜찮음","tags":["꿈","역사","사랑","선택"]},
 {"title":"하나와 앨리스","year":2004,"country":"일본 영화","genres":["드라마","코미디","로맨스"],"mood":["밝고 경쾌한","감성적이고 서정적인"],"pace":"큰 사건보다 분위기와 감정을 따라가는 전개","ending":"작품에 따라 다름","characters":["평범하고 현실적인 인물","유쾌하고 매력적인 인물"],"reality":"현실적인 이야기와 생활감","qualities":["입체적인 인물과 인물 간 관계","영상미와 색감","유머와 오락성"],"intensity":1,"language":"일본 영화","runtime":"보통 길이","tags":["우정","청춘","첫사랑","일상"]},
 {"title":"화양연화","year":2000,"country":"아시아권 영화","genres":["로맨스","드라마"],"mood":["감성적이고 서정적인","어둡고 진중한"],"pace":"큰 사건보다 분위기와 감정을 따라가는 전개","ending":"해석을 관객에게 맡기는 열린 결말","characters":["복잡하고 모순적인 인물"],"reality":"현실적인 이야기와 생활감","qualities":["영상미와 색감","음악과 사운드","입체적인 인물과 인물 간 관계"],"intensity":1,"language":"아시아권 영화 전반","runtime":"짧고 속도감 있는 영화","tags":["사랑","그리움","미장센","여운"]},
 {"title":"중경삼림","year":1994,"country":"아시아권 영화","genres":["로맨스","코미디","드라마"],"mood":["밝고 경쾌한","감성적이고 서정적인"],"pace":"큰 사건보다 분위기와 감정을 따라가는 전개","ending":"작품에 따라 다름","characters":["평범하고 현실적인 인물","유쾌하고 매력적인 인물"],"reality":"현실적인 이야기와 생활감","qualities":["영상미와 색감","음악과 사운드","입체적인 인물과 인물 간 관계"],"intensity":1,"language":"아시아권 영화 전반","runtime":"짧고 속도감 있는 영화","tags":["도시","사랑","외로움","감각"]},
 {"title":"무간도","year":2002,"country":"아시아권 영화","genres":["범죄·느와르","스릴러·미스터리","드라마"],"mood":["어둡고 진중한","긴장되고 불안한"],"pace":"단서가 쌓이며 마지막에 풀리는 전개","ending":"씁쓸하지만 현실적인 결말","characters":["복잡하고 모순적인 인물","유능하고 주도적인 인물"],"reality":"현실적인 이야기와 생활감","qualities":["예상하기 어려운 전개와 반전","입체적인 인물과 인물 간 관계","긴장감과 속도감"],"intensity":2,"language":"아시아권 영화 전반","runtime":"보통 길이","tags":["경찰","범죄","정체성","잠입"]},
 {"title":"중경삼림","year":1994,"country":"아시아권 영화","genres":["로맨스","코미디","드라마"],"mood":["밝고 경쾌한","감성적이고 서정적인"],"pace":"큰 사건보다 분위기와 감정을 따라가는 전개","ending":"작품에 따라 다름","characters":["평범하고 현실적인 인물","유쾌하고 매력적인 인물"],"reality":"현실적인 이야기와 생활감","qualities":["영상미와 색감","음악과 사운드","입체적인 인물과 인물 간 관계"],"intensity":1,"language":"아시아권 영화 전반","runtime":"짧고 속도감 있는 영화","tags":["도시","사랑","외로움","감각"]},
 {"title":"시네마 천국","year":1988,"country":"유럽 영화","genres":["드라마","로맨스"],"mood":["따뜻하고 편안한","감성적이고 서정적인"],"pace":"천천히 인물과 관계를 쌓는 전개","ending":"감정적인 여운이 남는 결말","characters":["성장하고 변화하는 인물","평범하고 현실적인 인물"],"reality":"현실적인 이야기와 생활감","qualities":["감정적인 여운과 공감","음악과 사운드","탄탄하고 흥미로운 이야기"],"intensity":1,"language":"유럽 영화","runtime":"길어도 몰입감 있으면 괜찮음","tags":["영화","성장","추억","고전"]},
 {"title":"아멜리에","year":2001,"country":"유럽 영화","genres":["로맨스","코미디","드라마"],"mood":["밝고 경쾌한","기묘하고 몽환적인"],"pace":"큰 사건보다 분위기와 감정을 따라가는 전개","ending":"희망과 위로가 남는 결말","characters":["유쾌하고 매력적인 인물","평범하고 현실적인 인물"],"reality":"현실에 약간의 환상이나 비현실성이 섞인 이야기","qualities":["영상미와 색감","유머와 오락성","감정적인 여운과 공감"],"intensity":1,"language":"유럽 영화","runtime":"보통 길이","tags":["파리","사랑","일상","상상력"]},
 {"title":"인생은 아름다워","year":1997,"country":"유럽 영화","genres":["드라마","코미디","로맨스"],"mood":["따뜻하고 편안한","감정적이고 서정적인"],"pace":"빠른 장면과 느린 장면이 적절히 섞인 전개","ending":"비극적이어도 주제가 분명한 결말","characters":["성장하고 변화하는 인물","유쾌하고 매력적인 인물"],"reality":"실제 사건이나 사회 문제를 다룬 이야기","qualities":["감정적인 여운과 공감","유머와 오락성","입체적인 인물과 인물 간 관계"],"intensity":2,"language":"유럽 영화","runtime":"보통 길이","tags":["가족","전쟁","사랑","희망"]},
 {"title":"그을린 사랑","year":2010,"country":"유럽 영화","genres":["드라마","미스터리"],"mood":["어둡고 진중한","긴장되고 불안한"],"pace":"단서가 쌓이며 마지막에 풀리는 전개","ending":"강한 반전이 있는 결말","characters":["복잡하고 모순적인 인물","상처를 딛고 나아가는 인물"],"reality":"실제 사건이나 사회 문제를 다룬 이야기","qualities":["탄탄하고 흥미로운 이야기","현실을 바라보게 하는 주제","예상하기 어려운 전개와 반전"],"intensity":3,"language":"유럽 영화","runtime":"길어도 몰입감 있으면 괜찮음","tags":["가족","전쟁","진실","반전"]},
 {"title":"더 헌트","year":2012,"country":"유럽 영화","genres":["드라마","스릴러·미스터리"],"mood":["어둡고 진중한","긴장되고 불안한"],"pace":"천천히 인물과 관계를 쌓는 전개","ending":"씁쓸하지만 현실적인 결말","characters":["평범하고 현실적인 인물","선악을 판단하기 어려운 인물"],"reality":"현실적인 이야기와 생활감","qualities":["현실을 바라보게 하는 주제","입체적인 인물과 인물 간 관계"],"intensity":3,"language":"유럽 영화","runtime":"보통 길이","tags":["사회","편견","도덕","관계"]},
 {"title":"타인의 삶","year":2006,"country":"유럽 영화","genres":["드라마","스릴러·미스터리"],"mood":["어둡고 진중한","감성적이고 서정적인"],"pace":"천천히 인물과 관계를 쌓는 전개","ending":"희망과 위로가 남는 결말","characters":["성장하고 변화하는 인물","복잡하고 모순적인 인물"],"reality":"실제 사건이나 사회 문제를 다룬 이야기","qualities":["입체적인 인물과 인물 간 관계","현실을 바라보게 하는 주제","감정적인 여운과 공감"],"intensity":2,"language":"유럽 영화","runtime":"길어도 몰입감 있으면 괜찮음","tags":["감시","예술","양심","변화"]},
 {"title":"퍼펙트 블루","year":1997,"country":"일본 영화","genres":["애니메이션","스릴러·미스터리","공포"],"mood":["어둡고 진중한","기묘하고 몽환적인","긴장되고 불안한"],"pace":"예상 밖의 사건이 계속되는 전개","ending":"해석을 관객에게 맡기는 열린 결말","characters":["복잡하고 모순적인 인물"],"reality":"현실에 약간의 환상이나 비현실성이 섞인 이야기","qualities":["예상하기 어려운 전개와 반전","현실을 바라보게 하는 주제","영상미와 색감"],"intensity":3,"language":"일본 영화","runtime":"짧고 속도감 있는 영화","tags":["정체성","심리","미디어","불안"]},
 {"title":"코코","year":2017,"country":"영어권 영화","genres":["애니메이션","모험","드라마"],"mood":["따뜻하고 편안한","감성적이고 서정적인"],"pace":"빠른 장면과 느린 장면이 적절히 섞인 전개","ending":"희망과 위로가 남는 결말","characters":["성장하고 변화하는 인물","유쾌하고 매력적인 인물"],"reality":"현실과 환상이 섞인 이야기","qualities":["음악과 사운드","감정적인 여운과 공감","독창적인 세계관과 상상력"],"intensity":1,"language":"영어권 영화","runtime":"보통 길이","tags":["가족","기억","음악","모험"]},
 {"title":"월-E","year":2008,"country":"영어권 영화","genres":["애니메이션","SF·판타지","로맨스"],"mood":["따뜻하고 편안한","웅장하고 스펙터클한"],"pace":"큰 사건보다 분위기와 감정을 따라가는 전개","ending":"희망과 위로가 남는 결말","characters":["평범하고 현실적인 인물","상처를 딛고 나아가는 인물"],"reality":"현실을 상징이나 비유로 표현하는 작품","qualities":["독창적인 세계관과 상상력","영상미와 색감","현실을 바라보게 하는 주제"],"intensity":1,"language":"영어권 영화","runtime":"짧고 속도감 있는 영화","tags":["환경","사랑","로봇","미래"]},
 {"title":"소셜 네트워크","year":2010,"country":"영어권 영화","genres":["드라마","범죄·느와르"],"mood":["어둡고 진중한","긴장되고 불안한"],"pace":"시작부터 빠르게 몰입되는 전개","ending":"씁쓸하지만 현실적인 결말","characters":["유능하고 주도적인 인물","복잡하고 모순적인 인물"],"reality":"실제 사건이나 사회 문제를 다룬 이야기","qualities":["탄탄하고 흥미로운 이야기","입체적인 인물과 인물 간 관계","음악과 사운드"],"intensity":1,"language":"영어권 영화","runtime":"보통 길이","tags":["기술","성공","우정","야망"]},
 {"title":"나이브스 아웃","year":2019,"country":"영어권 영화","genres":["스릴러·미스터리","코미디","범죄·느와르"],"mood":["밝고 경쾌한","긴장되고 불안한"],"pace":"단서가 쌓이며 마지막에 풀리는 전개","ending":"강한 반전이 있는 결말","characters":["유쾌하고 매력적인 인물","선악을 판단하기 어려운 인물"],"reality":"현실적인 이야기와 생활감","qualities":["예상하기 어려운 전개와 반전","유머와 오락성","탄탄하고 흥미로운 이야기"],"intensity":1,"language":"영어권 영화","runtime":"보통 길이","tags":["추리","가족","살인","유머"]},
 {"title":"프레스티지","year":2006,"country":"영어권 영화","genres":["드라마","스릴러·미스터리","SF·판타지"],"mood":["어둡고 진중한","긴장되고 불안한"],"pace":"단서가 쌓이며 마지막에 풀리는 전개","ending":"강한 반전이 있는 결말","characters":["유능하고 주도적인 인물","복잡하고 모순적인 인물"],"reality":"현실에 약간의 환상이나 비현실성이 섞인 이야기","qualities":["예상하기 어려운 전개와 반전","탄탄하고 흥미로운 이야기"],"intensity":2,"language":"영어권 영화","runtime":"보통 길이","tags":["마술","경쟁","집착","미스터리"]},
 {"title":"조조 래빗","year":2019,"country":"영어권 영화","genres":["코미디","드라마","전쟁"],"mood":["밝고 경쾌한","감성적이고 서정적인"],"pace":"빠른 장면과 느린 장면이 적절히 섞인 전개","ending":"희망과 위로가 남는 결말","characters":["성장하고 변화하는 인물","유쾌하고 매력적인 인물"],"reality":"실제 사건이나 사회 문제를 다룬 이야기","qualities":["유머와 오락성","현실을 바라보게 하는 주제","감정적인 여운과 공감"],"intensity":2,"language":"영어권 영화","runtime":"보통 길이","tags":["전쟁","성장","풍자","우정"]},
 {"title":"미드소마","year":2019,"country":"영어권 영화","genres":["공포","드라마","미스터리"],"mood":["기묘하고 몽환적인","어둡고 진중한"],"pace":"천천히 인물과 관계를 쌓는 전개","ending":"해석을 관객에게 맡기는 열린 결말","characters":["복잡하고 모순적인 인물","상처를 딛고 나아가는 인물"],"reality":"현실에 약간의 환상이나 비현실성이 섞인 이야기","qualities":["영상미와 색감","독창적인 세계관과 상상력","감정적인 여운과 공감"],"intensity":3,"language":"영어권 영화","runtime":"느린 영화도 분위기가 좋으면 선호함","tags":["공동체","상실","의식","불안"]},
 {"title":"조커","year":2019,"country":"영어권 영화","genres":["드라마","범죄·느와르","스릴러·미스터리"],"mood":["어둡고 진중한","긴장되고 불안한"],"pace":"천천히 인물과 관계를 쌓는 전개","ending":"씁쓸하지만 현실적인 결말","characters":["상처를 딛고 나아가는 인물","선악을 판단하기 어려운 인물"],"reality":"현실을 상징이나 비유로 표현하는 작품","qualities":["입체적인 인물과 인물 간 관계","현실을 바라보게 하는 주제","감정적인 여운과 공감"],"intensity":3,"language":"영어권 영화","runtime":"보통 길이","tags":["사회","소외","정체성","심리"]},
 {"title":"에브리씽 에브리웨어 올 앳 원스","year":2022,"country":"영어권 영화","genres":["SF·판타지","액션·모험","코미디","드라마"],"mood":["밝고 경쾌한","웅장하고 스펙터클한","감성적이고 서정적인"],"pace":"예상 밖의 사건이 계속되는 전개","ending":"희망과 위로가 남는 결말","characters":["성장하고 변화하는 인물","복잡하고 모순적인 인물"],"reality":"독창적인 세계관과 설정이 중심인 이야기","qualities":["독창적인 세계관과 상상력","감정적인 여운과 공감","유머와 오락성"],"intensity":2,"language":"영어권 영화","runtime":"보통 길이","tags":["가족","다중우주","정체성","액션"]},
 {"title":"블레이드 러너 2049","year":2017,"country":"영어권 영화","genres":["SF·판타지","드라마","스릴러·미스터리"],"mood":["어둡고 진중한","기묘하고 몽환적인"],"pace":"큰 사건보다 분위기와 감정을 따라가는 전개","ending":"해석을 관객에게 맡기는 열린 결말","characters":["복잡하고 모순적인 인물","상처를 딛고 나아가는 인물"],"reality":"독창적인 세계관과 설정이 중심인 이야기","qualities":["영상미와 색감","음악과 사운드","독창적인 세계관과 상상력"],"intensity":2,"language":"영어권 영화","runtime":"길어도 몰입감 있으면 괜찮음","tags":["인공지능","정체성","미래","존재"]},
 {"title":"미나리","year":2020,"country":"영어권 영화","genres":["드라마"],"mood":["따뜻하고 편안한","감성적이고 서정적인"],"pace":"큰 사건보다 분위기와 감정을 따라가는 전개","ending":"희망과 위로가 남는 결말","characters":["평범하고 현실적인 인물","성장하고 변화하는 인물"],"reality":"현실적인 이야기와 생활감","qualities":["입체적인 인물과 인물 간 관계","감정적인 여운과 공감","현실을 바라보게 하는 주제"],"intensity":1,"language":"영어권 영화","runtime":"보통 길이","tags":["가족","이민","일상","성장"]},
 {"title":"룸","year":2015,"country":"영어권 영화","genres":["드라마","스릴러·미스터리"],"mood":["어둡고 진중한","감정적이고 서정적인"],"pace":"천천히 인물과 관계를 쌓는 전개","ending":"희망과 위로가 남는 결말","characters":["상처를 딛고 나아가는 인물","성장하고 변화하는 인물"],"reality":"현실적인 이야기와 생활감","qualities":["입체적인 인물과 인물 간 관계","감정적인 여운과 공감"],"intensity":3,"language":"영어권 영화","runtime":"보통 길이","tags":["가족","생존","회복","모성"]},
 {"title":"더 랍스터","year":2015,"country":"유럽 영화","genres":["코미디","SF·판타지","로맨스"],"mood":["기묘하고 몽환적인","어둡고 진중한"],"pace":"큰 사건보다 분위기와 감정을 따라가는 전개","ending":"해석을 관객에게 맡기는 열린 결말","characters":["선악을 판단하기 어려운 인물","복잡하고 모순적인 인물"],"reality":"현실을 상징이나 비유로 표현하는 작품","qualities":["독창적인 세계관과 상상력","현실을 바라보게 하는 주제","유머와 오락성"],"intensity":2,"language":"유럽 영화","runtime":"보통 길이","tags":["사랑","사회풍자","부조리","관계"]},
 {"title":"패터슨","year":2016,"country":"영어권 영화","genres":["드라마","로맨스"],"mood":["따뜻하고 편안한","감성적이고 서정적인"],"pace":"큰 사건보다 분위기와 감정을 따라가는 전개","ending":"희망과 위로가 남는 결말","characters":["평범하고 현실적인 인물"],"reality":"현실적인 이야기와 생활감","qualities":["영상미와 색감","감정적인 여운과 공감","음악과 사운드"],"intensity":1,"language":"영어권 영화","runtime":"느린 영화도 분위기가 좋으면 선호함","tags":["시","일상","예술","소소함"]},
]

# Remove duplicate titles while keeping the first metadata entry.
MOVIES = list({m["title"]: m for m in reversed(MOVIES)}.values())
BY_TITLE = {m["title"]: m for m in MOVIES}

def normalize_title(value):
    return re.sub(r"[^0-9a-z가-힣]", "", value.casefold())

TITLE_ALIASES = {
    "parasite":"기생충", "oldboy":"올드보이", "memories of murder":"살인의 추억", "burning":"버닝", "little forest":"리틀 포레스트", "a taxi driver":"택시운전사",
    "interstellar":"인터스텔라", "inception":"인셉션", "the shawshank redemption":"쇼생크 탈출", "good will hunting":"굿 윌 헌팅", "eternal sunshine of the spotless mind":"이터널 선샤인", "la la land":"라라랜드", "the godfather":"대부", "the dark knight":"다크 나이트", "forrest gump":"포레스트 검프", "get out":"겟 아웃", "whiplash":"위플래쉬", "the truman show":"트루먼 쇼", "mad max fury road":"매드맥스: 분노의 도로", "arrival":"컨택트", "the grand budapest hotel":"그랜드 부다페스트 호텔", "moonlight":"문라이트", "titanic":"타이타닉", "spirited away":"센과 치히로의 행방불명", "my neighbor totoro":"이웃집 토토로", "your name":"너의 이름은.", "in the mood for love":"화양연화", "chungking express":"중경삼림", "cinema paradiso":"시네마 천국", "amelie":"아멜리에", "life is beautiful":"인생은 아름다워", "incendies":"그을린 사랑", "the hunt":"더 헌트", "the lives of others":"타인의 삶", "perfect blue":"퍼펙트 블루", "coco":"코코", "wall-e":"월-E", "knives out":"나이브스 아웃", "the prestige":"프레스티지", "joker":"조커", "everything everywhere all at once":"에브리씽 에브리웨어 올 앳 원스", "blade runner 2049":"블레이드 러너 2049", "minari":"미나리", "room":"룸", "the lobster":"더 랍스터", "paterson":"패터슨"
}
NORMALIZED_ALIASES = {normalize_title(alias): title for alias, title in TITLE_ALIASES.items()}

def resolve_known_favorites(titles):
    resolved=[]
    for entry in titles:
        normalized=normalize_title(entry)
        found = NORMALIZED_ALIASES.get(normalized)
        if not found:
            for title in BY_TITLE:
                if normalized == normalize_title(title):
                    found=title
                    break
        if not found:
            for alias, title in NORMALIZED_ALIASES.items():
                if len(alias) >= 6 and alias in normalized:
                    found=title
                    break
        if found and found not in resolved: resolved.append(found)
    return resolved

def parse_movie_titles(raw):
    parts = re.split(r"[,;\n，；、]+", raw)
    result=[]
    for part in parts:
        title=re.sub(r"^\s*(?:[-•*]|\d+[.)、])\s*", "", part).strip().strip("\"'“”‘’")
        if title and title not in result: result.append(title)
    return result

GENRES = ["드라마","스릴러·미스터리","범죄·느와르","SF·판타지","로맨스","코미디","액션·모험","공포","애니메이션","다큐멘터리","장르를 가리지 않음"]
QUALITIES = ["탄탄하고 흥미로운 이야기","입체적인 인물과 인물 간 관계","예상하기 어려운 전개와 반전","감정적인 여운과 공감","독창적인 세계관과 상상력","현실을 바라보게 하는 주제","영상미와 색감","음악과 사운드","긴장감과 속도감","유머와 오락성"]
MOODS = ["밝고 경쾌한","따뜻하고 편안한","감성적이고 서정적인","어둡고 진중한","긴장되고 불안한","기묘하고 몽환적인","웅장하고 스펙터클한","작품에 따라 다름"]
PACES = ["시작부터 빠르게 몰입되는 전개","단서가 쌓이며 마지막에 풀리는 전개","인물과 관계를 천천히 쌓는 전개","예상 밖의 사건이 계속되는 전개","큰 사건보다 분위기와 감정을 따라가는 전개","속도보다 완성도가 중요함"]
ENDINGS = ["갈등이 명확히 해결되는 결말","희망과 위로가 남는 결말","씁쓸하지만 현실적인 결말","해석을 관객에게 맡기는 열린 결말","강한 반전이 있는 결말","비극적이어도 오래 여운이 남는 결말","작품에 따라 다름"]
CHARACTERS = ["성장하고 변화하는 인물","복잡하고 모순적인 인물","유능하고 주도적인 인물","상처를 딛고 나아가는 인물","평범하고 현실적인 인물","유쾌하고 매력적인 인물","선악을 판단하기 어려운 인물","인물보다 사건과 세계관이 중요함"]
REALITIES = ["현실적인 이야기와 생활감","실제 사건이나 사회 문제를 다룬 이야기","현실을 상징이나 비유로 표현하는 작품","현실과 환상이 섞인 이야기","독창적인 세계관과 설정이 중심인 이야기","둘 다 좋아함"]
INTENSITY_CHOICES = ["편안하고 부담 없는 영화","적당한 긴장과 감정 변화가 있는 영화","강렬한 감정과 충격적인 장면이 있는 영화","어둡고 불편해도 의미가 있으면 괜찮음","폭력·공포·잔혹한 장면은 피하고 싶음"]
LANGUAGES = ["한국 영화","영어권 영화","일본 영화","유럽 영화","아시아권 영화 전반","애니메이션","언어권을 가리지 않음"]
RUNTIMES = ["짧고 속도감 있는 영화","보통 길이로 균형 잡힌 영화","길어도 몰입감 있으면 괜찮음","느린 영화도 분위기가 좋으면 선호함","러닝타임보다 이야기의 밀도가 중요함"]
AVOID = ["잔인한 폭력","공포·점프 스케어","우울하거나 절망적인 분위기","억지스러운 로맨스","과도한 신파","복잡하고 불친절한 전개","긴 러닝타임"]

def intensity_level(answer):
    if answer == INTENSITY_CHOICES[0]: return 1
    if answer == INTENSITY_CHOICES[1]: return 2
    if answer == INTENSITY_CHOICES[2]: return 3
    if answer == INTENSITY_CHOICES[3]: return 4
    return 0

def score_movie(m, answers, favorites):
    score = 0.0
    score += 3.0 * len(set(answers["genres"]) & set(m["genres"]))
    if "장르를 가리지 않음" in answers["genres"]: score += 1
    score += 2.0 * len(set(answers["qualities"]) & set(m["qualities"]))
    if answers["mood"] in m["mood"]: score += 2.3
    if answers["pace"] in (m["pace"], "작품에 따라 다름"): score += 1.8
    if answers["ending"] in (m["ending"], "작품에 따라 다름"): score += 1.8
    score += 1.3 * len(set(answers["characters"]) & set(m["characters"]))
    if answers["reality"] in (m["reality"], "둘 다 좋아함"): score += 1.5
    if answers["runtime"] in (m["runtime"], "러닝타임보다 이야기의 밀도가 중요함"): score += 1.1
    chosen_languages = answers["language"]
    if "언어권을 가리지 않음" in chosen_languages or m["language"] in chosen_languages or ("아시아권 영화 전반" in chosen_languages and m["country"] == "아시아권 영화") or ("애니메이션" in chosen_languages and "애니메이션" in m["genres"]): score += 1.2
    level = intensity_level(answers["intensity"])
    if level:
        if level == 4: score += 1.0 if m["intensity"] >= 2 else 0.3
        else: score += max(0, 1.8 - abs(level - m["intensity"]) * .65)
    if answers["intensity"] == INTENSITY_CHOICES[4] and m["intensity"] >= 3: score -= 5
    # Similarity to the selected favorites gives the chosen films a strong voice.
    known_favorites = resolve_known_favorites(favorites)
    if known_favorites:
        sim = []
        for fav in known_favorites:
            f = BY_TITLE[fav]
            overlap = len(set(m["genres"]) & set(f["genres"])) * 1.2 + len(set(m["tags"]) & set(f["tags"])) * .55 + len(set(m["qualities"]) & set(f["qualities"])) * .45
            sim.append(overlap)
        score += min(4.0, max(sim, default=0) * .25)
    avoid = set(answers["avoid"])
    if "잔인한 폭력" in avoid and m["intensity"] >= 3: score -= 8
    if "공포·점프 스케어" in avoid and "공포" in m["genres"]: score -= 10
    if "우울하거나 절망적인 분위기" in avoid and "어둡고 진중한" in m["mood"]: score -= 5
    if "복잡하고 불친절한 전개" in avoid and m["ending"] == "해석을 관객에게 맡기는 열린 결말": score -= 5
    if "긴 러닝타임" in avoid and m["runtime"] == "길어도 몰입감 있으면 괜찮음": score -= 4
    return score

def reason_for(m, answers):
    matches = []
    shared_genres = [g for g in answers["genres"] if g in m["genres"] and g != "장르를 가리지 않음"]
    shared_qualities = [q for q in answers["qualities"] if q in m["qualities"]]
    if shared_genres: matches.append("선호 장르인 " + ", ".join(shared_genres))
    if answers["mood"] in m["mood"]: matches.append(answers["mood"] + " 분위기")
    if answers["ending"] == m["ending"]: matches.append(answers["ending"])
    if shared_qualities: matches.append(shared_qualities[0])
    if not matches: matches.append("선택한 영화들과 이야기 요소가 가까운 작품")
    return "와 잘 맞아요. 특히 " + ", ".join(matches[:3]) + "을 좋아한다면 즐길 가능성이 높습니다."

def build_profile(a):
    parts=[]
    if a["genres"] and "장르를 가리지 않음" not in a["genres"]: parts.append("선호 장르는 " + ", ".join(a["genres"][:3]) + "입니다")
    if a["qualities"]: parts.append("영화에서 " + ", ".join(a["qualities"][:2]) + "을 중요하게 봅니다")
    parts.append(a["mood"] + " 분위기와 " + a["pace"] + "을 선호합니다")
    parts.append(a["ending"] + "을 선택했습니다")
    return ". ".join(parts) + "."

def call_ai_ranker(provider, key, answers, favorites, count=5):
    prompt = f"""당신은 영화 추천 큐레이터입니다. 다음 취향에 맞는 실제 개봉 영화를 정확히 {count}편 추천하세요. 영화 목록에 한정하지 말고, 유명한 작품부터 숨은 작품까지 폭넓게 고려하세요. 이미 본 영화와 같은 작품은 원제나 번역 제목이 다르더라도 제외하세요. 영화의 존재나 줄거리가 불확실한 작품은 추천하지 마세요. 각 추천 이유는 사용자가 고른 취향과 구체적으로 연결해 한국어로 설명하세요. 성격 진단은 하지 마세요. 사용자가 고른 추천 방향과 새로움 선호도 반영하세요. 반드시 순수 JSON 배열만 출력하고 각 항목은 title, reason 키를 가지세요.\n사용자 취향: {json.dumps(answers,ensure_ascii=False)}\n이미 봤거나 이번 결과에서 제외할 영화: {json.dumps(favorites,ensure_ascii=False)}\n형식: [{{\"title\":\"영화 제목\",\"reason\":\"취향과 맞는 추천 이유\"}}]"""
    if provider == "Gemini":
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=key)
        raw = ""
        last_error = None
        model_fallbacks = [
            ("gemini-3.8-flash", 2),
            ("gemini-3.7-flash", 1),
            ("gemini-3.6-flash", 1),
            ("gemini-3.5-flash-lite", 1),
        ]
        for model_name, attempts in model_fallbacks:
            for attempt in range(attempts):
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            thinking_config=types.ThinkingConfig(thinking_level="low"),
                        ),
                    )
                    raw = response.text or ""
                    if raw.strip():
                        break
                    raise RuntimeError(f"{model_name}에서 빈 응답을 받았습니다.")
                except Exception as exc:
                    last_error = exc
                    error_text = str(exc).lower()
                    is_temporary_capacity_error = "503" in error_text or "unavailable" in error_text or "high demand" in error_text
                    can_try_another_model = is_temporary_capacity_error or any(code in error_text for code in ("404", "not_found", "429", "quota", "resource_exhausted"))
                    if not can_try_another_model:
                        raise
                    if attempt < attempts - 1:
                        time.sleep(1)
            if raw.strip():
                break
        if not raw.strip():
            raise last_error or RuntimeError("Gemini 모델에서 응답을 받지 못했습니다.")
    else:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        response = client.responses.create(model="gpt-4.1-mini", input=prompt)
        raw = response.output_text or ""
    raw = re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", raw.strip())
    parsed = json.loads(raw)
    known_favorites = set(resolve_known_favorites(favorites))
    favorite_normalized = [normalize_title(x) for x in favorites]
    recommendations=[]
    seen=set()
    for item in parsed:
        if not isinstance(item,dict) or not isinstance(item.get("title"),str): continue
        title=item["title"].strip()
        normalized=normalize_title(title)
        if not title or title in known_favorites or normalized in seen: continue
        if any(normalized == x or (len(x) >= 6 and (normalized in x or x in normalized)) for x in favorite_normalized): continue
        known=resolve_known_favorites([title])
        if known and any(x in known_favorites for x in known): continue
        recommendations.append({"title":title,"reason":str(item.get("reason", "선택한 취향과 잘 맞을 수 있는 작품입니다."))})
        seen.add(normalized)
        if len(recommendations)==count: break
    return recommendations

def friendly_ai_errors(errors):
    messages = []
    for error in errors:
        provider, _, detail = error.partition(":")
        lowered = detail.lower()
        if "503" in lowered or "unavailable" in lowered or "high demand" in lowered:
            messages.append(f"{provider} 서버가 일시적으로 혼잡해 기본 추천을 표시합니다. 잠시 후 다시 시도해 주세요.")
        elif "429" in lowered or "quota" in lowered or "resource_exhausted" in lowered:
            messages.append(f"{provider} 사용 한도에 도달해 기본 추천을 표시합니다. 잠시 후 사용량을 확인해 주세요.")
        else:
            messages.append(f"{provider} 분석에 실패해 기본 추천을 표시합니다.")
    return " ".join(messages)

def read_server_secret(name):
    try:
        value = st.secrets.get(name, "")
    except Exception:
        value = ""
    return str(value or os.getenv(name, "")).strip()

st.markdown("<div class='hero'><h1>🎬 내 취향 영화 추천</h1><p>좋아하는 영화와 감상 취향을 바탕으로 다음에 볼 영화를 찾아드려요.</p></div>", unsafe_allow_html=True)
st.caption("선택형 설문으로 영화 취향을 정리하고, 이미 본 작품을 제외해 추천합니다.")

st.sidebar.header("선택형 AI 보강")
server_gemini_key = read_server_secret("GEMINI_API_KEY")
server_openai_key = read_server_secret("OPENAI_API_KEY")
if server_gemini_key:
    gemini_key = server_gemini_key
    st.sidebar.success("Gemini 서버 키 연결됨")
else:
    gemini_key = st.sidebar.text_input("Gemini API 키 (선택)", value="", type="password", key="gemini_key")
if server_openai_key:
    openai_key = server_openai_key
    st.sidebar.success("OpenAI 서버 키 연결됨")
else:
    openai_key = st.sidebar.text_input("OpenAI API 키 (선택)", value="", type="password", key="openai_key")
use_ai = st.sidebar.checkbox("AI로 추천 목록과 이유 만들기", value=bool(gemini_key or openai_key), key="use_ai")
st.sidebar.caption("서버 비밀 설정 또는 개인 API 키로 AI 추천을 이용합니다. API 사용료는 각 서비스 계정에서 발생합니다.")

with st.form("taste_form"):
    st.subheader("1. 감명 깊게 본 영화")
    favorite_text = st.text_area("감명 깊게 본 영화를 3편 이상 적어주세요", placeholder="예: 12명의 성난 사람들, 액트 오브 킬링, 하라키리", help="쉼표나 줄바꿈으로 영화를 구분해 주세요. 입력한 영화는 추천에서 제외합니다.")
    st.subheader("2. 선호하는 장르와 감상 요소")
    genres = st.multiselect("특히 좋아하는 장르 (복수 선택)", GENRES, default=[])
    qualities = st.multiselect("영화에서 중요하게 생각하는 요소 (최대 3개)", QUALITIES, max_selections=3)
    mood = st.radio("선호하는 분위기", MOODS, horizontal=False)
    pace = st.radio("잘 맞는 전개 방식", PACES)
    ending = st.radio("선호하는 결말", ENDINGS)
    characters = st.multiselect("끌리는 인물 유형 (복수 선택)", CHARACTERS, max_selections=4)
    st.subheader("3. 소재와 관람 강도")
    reality = st.radio("현실과 상상력 중 선호", REALITIES)
    intensity = st.radio("선호하는 자극의 정도", INTENSITY_CHOICES)
    runtime = st.radio("영화 길이와 호흡", RUNTIMES)
    language = st.multiselect("선호하는 언어권 또는 형식", LANGUAGES, default=["언어권을 가리지 않음"])
    avoid = st.multiselect("피하고 싶은 요소 (선택 사항)", AVOID)
    st.subheader("4. 추천 방향")
    novelty = st.radio("얼마나 새로운 영화를 추천받고 싶나요?", ["좋아하는 스타일과 매우 비슷한 영화","익숙한 취향에 새로운 요소가 조금 있는 영화","평소 취향에서 벗어나도 흥미로울 영화","익숙한 영화와 새로운 영화를 섞은 추천"])
    reco_style = st.radio("추천 결과의 방향", ["취향에 가장 잘 맞는 영화만","취향에 맞는 영화와 새로운 도전작을 함께","가볍게 볼 영화 위주","깊이 생각할 거리가 있는 영화 위주","여러 장르를 골고루"])
    submitted = st.form_submit_button("내 취향 분석하고 영화 추천받기", use_container_width=True)

if "recommendation_bundle" not in st.session_state:
    st.session_state["recommendation_bundle"] = None

if submitted:
    favorite_titles = parse_movie_titles(favorite_text)
    if len(favorite_titles) < 3:
        st.error("감명 깊게 본 영화를 최소 3편 입력해주세요. 쉼표나 줄바꿈으로 구분하면 됩니다.")
    else:
        answers = {"genres": genres, "qualities": qualities, "mood": mood, "pace": pace, "ending": ending, "characters": characters, "reality": reality, "intensity": intensity, "runtime": runtime, "language": language or ["언어권을 가리지 않음"], "avoid": avoid, "novelty": novelty, "style": reco_style}
        known_favorites = resolve_known_favorites(favorite_titles)
        candidates = [m for m in MOVIES if m["title"] not in known_favorites]
        scored = sorted(((score_movie(m, answers, favorite_titles), m) for m in candidates), key=lambda x: x[0], reverse=True)
        ranked = [{"title": m["title"], "reason": reason_for(m, answers)} for _, m in scored[:15]]
        used_ai = False
        ai_errors = []
        if use_ai and (gemini_key or openai_key):
            with st.spinner("영화 취향을 살펴보고 추천을 고르는 중이에요. 잠시만 기다려 주세요…"):
                ai_items = []
                providers = []
                for provider, key in [("Gemini", gemini_key), ("OpenAI", openai_key)]:
                    if not key:
                        continue
                    try:
                        ai_items.extend(call_ai_ranker(provider, key, answers, favorite_titles))
                        providers.append(provider)
                    except Exception as exc:
                        ai_errors.append(f"{provider}: {exc}")
                deduped = []
                seen_titles = set()
                for item in ai_items:
                    normalized = normalize_title(item["title"])
                    if normalized not in seen_titles:
                        deduped.append(item)
                        seen_titles.add(normalized)
                if deduped:
                    ranked = deduped[:5]
                    used_ai = True
                    for item in [{"title": m["title"], "reason": reason_for(m, answers)} for _, m in scored]:
                        if len(ranked) >= 5:
                            break
                        if normalize_title(item["title"]) not in seen_titles:
                            ranked.append(item)
                            seen_titles.add(normalize_title(item["title"]))
        elif use_ai:
            st.info("사이드바에 Gemini 또는 OpenAI API 키를 입력하고 AI 추천을 켜면 취향 기반 추천을 받을 수 있습니다.")

        if not used_ai:
            if answers["style"] == "가볍게 볼 영화 위주":
                ranked.sort(key=lambda x: BY_TITLE[x["title"]]["intensity"])
            elif answers["style"] == "깊이 생각할 거리가 있는 영화 위주":
                ranked.sort(key=lambda x: "현실을 바라보게 하는 주제" not in BY_TITLE[x["title"]]["qualities"])
            if answers["novelty"] == "평소 취향에서 벗어나도 흥미로울 영화":
                ranked.sort(key=lambda x: score_movie(BY_TITLE[x["title"]], answers, favorite_titles))
            elif answers["novelty"] == "익숙한 영화와 새로운 영화를 섞은 추천" and len(ranked) > 3:
                ranked = ranked[:3] + ranked[5:7]

        st.session_state["recommendation_bundle"] = {
            "ranked": ranked[:5],
            "answers": answers,
            "favorites": favorite_titles,
            "excluded": favorite_titles.copy(),
            "used_ai": used_ai,
            "ai_errors": ai_errors,
        }

bundle = st.session_state.get("recommendation_bundle")
if bundle:
    st.markdown("---")
    st.header("나의 영화 취향")
    st.write(build_profile(bundle["answers"]))
    st.caption("감명 깊게 본 영화: " + " · ".join(bundle["favorites"]))
    st.header("이런 영화는 어떠세요?")
    st.caption("이미 본 작품은 ‘이미 봤어요’를 눌러 교체하세요. 클릭한 작품은 이 세션의 다음 추천에서도 제외됩니다.")
    if bundle["ai_errors"]:
        st.warning(friendly_ai_errors(bundle["ai_errors"]))
    for i, item in enumerate(bundle["ranked"]):
        movie = BY_TITLE.get(item["title"])
        reason = item.get("reason") or (reason_for(movie, bundle["answers"]) if movie else "선택한 취향과 가까운 작품으로 추천되었습니다.")
        with st.container(border=True):
            st.subheader(f"{i + 1}. {item['title']}" + (f" ({movie['year']})" if movie else ""))
            st.write(reason)
            if movie:
                st.caption(" · ".join(movie["genres"]) + " | " + movie["country"])
            if st.button("이미 봤어요 · 다른 영화로 교체", key=f"replace_seen_{i}_{normalize_title(item['title'])}"):
                bundle["excluded"] = list(dict.fromkeys(bundle.get("excluded", bundle["favorites"]) + [item["title"]]))
                excluded = list(dict.fromkeys(bundle["excluded"] + [x["title"] for x in bundle["ranked"]]))
                st.session_state["recommendation_bundle"] = bundle
                replacement = []
                replacement_errors = []
                if use_ai and (gemini_key or openai_key):
                    with st.spinner("이미 본 영화를 제외하고 다른 작품을 찾고 있어요…"):
                        for provider, key in [("Gemini", gemini_key), ("OpenAI", openai_key)]:
                            if not key:
                                continue
                            try:
                                replacement = call_ai_ranker(provider, key, bundle["answers"], excluded, count=1)
                                if replacement:
                                    break
                            except Exception as exc:
                                replacement_errors.append(f"{provider}: {exc}")
                if not replacement:
                    excluded_titles = set(resolve_known_favorites(excluded))
                    candidates = [m for m in MOVIES if m["title"] not in excluded_titles and normalize_title(m["title"]) not in {normalize_title(x) for x in excluded}]
                    candidates.sort(key=lambda m: score_movie(m, bundle["answers"], bundle["favorites"]), reverse=True)
                    if candidates:
                        replacement = [{"title": candidates[0]["title"], "reason": reason_for(candidates[0], bundle["answers"])}]
                if replacement:
                    bundle["ranked"][i] = replacement[0]
                    bundle["ai_errors"] = replacement_errors
                    st.session_state["recommendation_bundle"] = bundle
                    st.rerun()
                else:
                    st.warning("겹치지 않는 대체 영화를 찾지 못했어요. 잠시 후 다시 눌러주세요.")
    st.caption("AI 추천은 입력한 취향과 영화 제목을 바탕으로 생성됩니다. API를 사용할 수 없을 때는 앱 내장 영화 목록에서 추천합니다.")
