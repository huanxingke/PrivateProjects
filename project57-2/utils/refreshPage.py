import time

import streamlit as st


def refreshPage():
    code = """
    <head>
        <script src="https://cdn.staticfile.org/jquery/3.4.0/jquery.min.js"></script>
    </head>
    <body>
        <script>
            //隐藏本组件
            var parent = $(window.frameElement).parent();
            parent.css("display", "none");
            //刷新整个页面
            window.top.location.reload()
        </script>
    </body>"""
    with st.spinner("即将刷新页面..."):
        waits = 0
        for i in range(2):
            time.sleep(1)
            waits += 1
        if waits >= 2:
            st.components.v1.html(html=code, height=0)