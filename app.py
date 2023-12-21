# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import jieba
import seaborn as sns
from streamlit_echarts import st_echarts
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)


def run():
    st.title("获取页面内容并显示")
    url = st.text_input("请输入网址")
    if st.button("获取内容"):
        if url:
            try:
                response = requests.get(url)  
                soup = BeautifulSoup(response.content, 'html.parser')  
                content = soup.get_text() 
                words = jieba.lcut(content) 
                counts = {} 
                for word in words:
                    if len(word) == 1:
                        continue  
                    else:
                        counts[word] = counts.get(word, 0) + 1 
                items = list(counts.items())  
                items.sort(key=lambda x: x[1], reverse=True)  
                # dir = {}
                for i in range(min(20, len(items))):
                    word, count = items[i]
                    # st.write("{0:<5}{1:>5}".format(word, count))
                    # dir[word]=count    
                top_words = [items[i][0] for i in range(min(20, len(items)))]
                top_counts = [items[i][1] for i in range(min(20, len(items)))]
                sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
                top_20_counts = dict(sorted_counts[:20])
                options = {
                    "xAxis": {
                        "type": "category",
                        "data": top_words,
                        "axisLabel": {
                            "rotate": 45
                        }

                    },
                    "yAxis": {"type": "value"},
                    "series": [{"data": top_counts, "type": "bar"}],
                }
                st_echarts(options=options, height="500px")
                data = [
                    {"name": word, "value": count}
                    for word, count in top_20_counts.items()
                ]
                wordcloud_option = {"series": [{"type": "wordCloud", "data": data}]}
                st_echarts(wordcloud_option)     
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

                st.markdown("饼状图")
                events = {
                    "legendselectchanged": "function(params) { return params.selected }",
                }

                s = st_echarts(options=options, events=events, height="600px", key="render_pie_events")

                if s is not None:
                    st.write(s)                   
            except Exception as e:
                st.write(f"发生错误：{e}") 




if __name__ == "__main__":
    run()
