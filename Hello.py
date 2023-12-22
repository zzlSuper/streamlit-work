import jieba
import seaborn as sns
from streamlit_echarts import st_echarts
from streamlit.logger import get_logger
import urllib.request
from urllib.parse import urlparse
from typing import Dict, List, Tuple
import streamlit as st
import requests
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import re

LOGGER = get_logger(__name__)

def get_web_content(url: str) -> Tuple[Dict[str, int], List[str], List[int]]:
    """
    进行分词及词频统计
    """
    response = requests.get(url)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.content, 'html.parser')
    content = soup.get_text()
    pattern = re.compile(r'[^a-zA-Z0-9\u4e00-\u9fa5]')
    new_content = re.sub(pattern, '', content)
    words = jieba.lcut(new_content)
    counts = {}
    for word in words:
        if len(word) == 1:
            continue
        else:
            counts[word] = counts.get(word, 0) + 1
    items = list(counts.items())
    items.sort(key=lambda x: x[1], reverse=True)
    top_words = [items[i][0] for i in range(min(20, len(items)))]
    top_counts = [items[i][1] for i in range(min(20, len(items)))]
    return counts, top_words, top_counts


def get_top_counts(counts: Dict[str, int], num: int = 20) -> Dict[str, int]:
    """
    获取单词数在指定范围的
    """
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    top_counts = dict(sorted_counts[:num])
    return top_counts


def display_bar_chart(words: List[str], counts: List[int]) -> None:
    """
    显示柱状图，显示单词和数量。
    """
    options = {
    "xAxis": {
        "type": "category",
        "data": words,
        "axisLabel": {
            "rotate": 45
               }
            },
    "yAxis": {"type": "value"},
    "series": [{"data": counts, "type": "bar"}],
            }
    s =st_echarts(options=options, height="500px")
    if s is not None:
        st.write(s)


def display_word_cloud(top_counts: Dict[str, int]) -> None:
    """
    显示词云。
    """
    data = [{"name": word, "value": count} for word, count in top_counts.items()]
    wordcloud_option = {"series": [{"type": "wordCloud", "data": data}]}
    st_echarts(wordcloud_option)

def display_area_chart(words: List[str], counts: List[int]) ->None:
    """
    基本面积图
    """
    options = {
    "xAxis": {
        "type": "category",
        "boundaryGap": False,
        "axisLabel": {
            "rotate": 45
               },
        "data": words,
    },
    "yAxis": {"type": "value"},
    "series": [
        {
            "data": counts,
            "type": "line",
            "areaStyle": {},
        }
    ],
}
    st_echarts(options=options)

def display_pie_chart(top_counts: Dict[str, int]) -> None:
    """
    显示饼图。
    """
    data = [{"name": word, "value": count} for word, count in top_counts.items()]
    options = {
        "title": {"text": "", "subtext": "", "left": "center"},
        "tooltip": {"trigger": "item"},
        "legend": {
            "orient": "vertical",
            "left": "left",
        },
        "series": [
            {

                "name": "访问来源",
                "type": "pie",
                 "radius": "50%",
                 "data": data,
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowOffsetX": 0,
                        "shadowColor": "rgba(0, 0, 0, 0.5)",
                    }
                },
            }
        ],
    }
    events = {
            "legendselectchanged": "function(params) { return params.selected }",
        }
    st_echarts(options=options, events=events, height="600px", key="render_pie_events")




def display_images(soup: BeautifulSoup) -> None:
    """
    显示页面中的所有图片。
    """
    images = soup.find_all('img')
    if images:
        for img in images:
            img_url = img['src']
            try:
                image = requests.get(img_url).content
                st.image(image, caption=img_url, use_column_width=True)
            except Exception as e:
                st.warning(f"无法下载或显示图片: {img_url}, 错误信息：{e}")
    else:
        st.write("页面中没有图片。")

        
def display_web_content(url: str) -> None:
    """
    获取网页中的内容，进行分词并统计词频，并显示一些图片。
    """
    try:
        counts, top_words, top_counts = get_web_content(url)
        top_20_counts = get_top_counts(counts, num=20)
        soup = BeautifulSoup(requests.get(url).content, 'html.parser')
        display_images(soup)
    except Exception as e:
        st.write(f"发生错误：{e}")


def display_line_chart(words: List[str], counts: List[int]) -> None:
    """
    显示折线图。
    """
    option = {
        "xAxis": {
            "type": "category",
            "data": words,
            "axisLabel": {
                "rotate": 45
            }
        },
        "yAxis": {"type": "value"},
        "series": [{"data": counts, "type": "line"}],
    }
    st_echarts(
        options=option, height="400px",
    )

def display_scatter_chart(top_counts: Dict[str, int],words: List[str], counts: List[int]) -> None:
    """
    显示散点图。
    """
    data = []
    for word, count in top_counts.items():
        data.append({"name": word, "value": count})
    options = {
        "xAxis": {
            "type": "category",
            "data": words,
            "axisLabel": {
                "rotate": 45
            }
        },
        "yAxis": {"type": "value"},
        "series": [
            {
                "symbolSize": 20,
                "data": data,
                "type": "scatter",
            }
        ],
    }
    st_echarts(options=options, height="500px")

def display_customized_chart(top_counts: Dict[str, int], words: List[str], counts: List[int]) -> None:
    """
    显示漏斗图
    """
    total_count = sum(counts)
    data = [{"name": word, "value": round(count / total_count * 100, 2)} for word, count in top_counts.items()]
    option = {
        "title": {"text": "", "subtext": ""},
        "tooltip": {"trigger": "item", "formatter": "{a} <br/>{b} : {c}%"},
        "series": [
            {
                "name": "词语比例",
                "type": "funnel",
                "left": "10%",
                "width": "80%",
                "data": data,
                "label": {"formatter": "{b}"},
                "labelLine": {"show": False},
                "itemStyle": {"opacity": 0.7},
                "emphasis": {
                "label": {"position": "inside", "formatter": "{b} : {c}%"}
                },
            }
        ],
        "toolbox": {
            "feature": {
                
            }
        },
        "legend": {"data": words},
    }
    st_echarts(option, height="500px")

def display_sidebar_options():
    option = st.sidebar.selectbox("请选择功能", ["柱状图", "词云" ,"折线图","散点图", "图片","漏斗图","饼图","基本面积图"])
    return option

def run() -> None:
    st.title("获取页面内容并显示")
    url = st.text_input("请输入网址")

    # 添加侧边栏
    option = display_sidebar_options()

    if st.button("获取内容"):
        if url:
            counts, top_words, top_counts = get_web_content(url)
            top_20_counts = get_top_counts(counts, num=20)
            if option:
                if option == "柱状图":
                    display_bar_chart(top_words, top_counts)
                if option == "基本面积图":
                    display_area_chart(top_words, top_counts)
                elif option == "散点图":
                    display_scatter_chart(top_20_counts,top_words, top_counts)
                elif option == "词云":
                    display_word_cloud(top_20_counts)
                elif option == "折线图":
                    display_line_chart(top_words, top_counts)
                elif option == "饼图":
                    display_pie_chart(top_20_counts)
                elif option == "漏斗图":
                    display_customized_chart(top_20_counts,top_words, top_counts)                    
                elif option == "图片":
                        soup = BeautifulSoup(requests.get(url).content, 'html.parser')
                        display_images(soup)
            else:
                st.write("请选择一个功能")



if __name__ == "__main__":
    run()

