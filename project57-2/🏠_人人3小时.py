import random
import base64
import time
import uuid
import json
import re
import os

import streamlit as st
import requests

from components.CookieManager import CookieManager, JSCookieManager
from components.Webdav import JianGuoYunClient
from utils.refreshPage import refreshPage


headers = {
    "Host": "3hours.taobao.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    "csr-account-v2": "true",
    "csr-front-v": "1.1.0",
    "charset": "utf-8",
    "content-type": "application/json;charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (Linux; Android 7.1.2; PCRT00 Build/N2G48H; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/68.0.3440.70 Mobile Safari/537.36 MMWEBID/4072 MicroMessenger/8.0.2.1860(0x28000234) Process/appbrand0 WeChat/arm32 Weixin NetType/WIFI Language/zh_CN ABI/arm32 MiniProgramEnv/android",
    "Referer": "https://servicewechat.com/wxf51565575243eee6/46/page-frame.html"
}


# 装饰器: 错误捕获
def ErrorCatcher(func):
    def wrapper(*args, **kwargs):
        try:
            if kwargs:
                response = func(*args, **kwargs)
            elif args:
                response = func(*args)
            else:
                response = func()
            return response
        except Exception as error:
            return {"code": -100, "error": str(error)}

    return wrapper


@ErrorCatcher
def getCsrf():
    """获取 p_csrf 参数

    :return:
    """
    url = "https://3hours.taobao.com/login"
    params = {
        "type": "login",
        "autoCheckSession": "false",
        "redirectHome": "true"
    }
    html = requests.get(url=url, params=params).text
    csrf = re.compile(r'<script>window.th_csrf="(.*?)"</script>').findall(html)[0]
    return {"code": 200, "p_csrf": csrf}


@ErrorCatcher
def sendCaptcha():
    """发送验证码

    :return:
    """
    url = "https://3hours.taobao.com/user/v2/login/sendCaptcha"
    params = {
        "p_csrf": p_csrf,
        "threehours-from-channel": ""
    }
    data = {
        "phoneNumber": phoneNumber,
        "scenes": "ACCOUNT_LOGIN"
    }
    response = requests.post(url=url, params=params, json=data, headers=headers).json()
    return response


@ErrorCatcher
def login():
    """通过手机号登录

    :return:
    """
    url = "https://3hours.taobao.com/user/v2/login/phoneNumber"
    params = {
        "p_csrf": p_csrf,
        "threehours-from-channel": ""
    }
    data = {
        "phoneNumber": phoneNumber,
        "captcha": captcha,
        "isAuthorized": "true"
    }
    response = requests.post(url=url, params=params, json=data, headers=headers)
    return {"code": 200, "login_response": response}


@ErrorCatcher
def getVoteList():
    """获取投票列表

    :return:
    """
    url = "https://m.3hours.taobao.com/content/vote/list"
    params = {
        "sceneCode": "TEAM_TOGETHER_GUARD_PROJECT_82",
        "pageIndex": "1",
        "pageSize": "10",
        "isIncludeToDay": "true"
    }
    response = requests.get(url=url, params=params).json()
    return response


@ErrorCatcher
def vote(voteId, userOption=1):
    """投票

    :param userOption: 用户投票选项, 默认为第 1 项
    :param voteId: 投票 id
    :return:
    """
    url = "https://m.3hours.taobao.com/content/vote/create"
    params = {
        "p_csrf": p_csrf,
        "threehours-from-channel": ""
    }
    data = {
        "voteId": voteId,
        "userOption": userOption
    }
    jar_cookies = requests.utils.cookiejar_from_dict(cookie)
    response = requests.post(url=url, params=params, json=data, headers=headers, cookies=jar_cookies).json()
    return response


@ErrorCatcher
def getQuestion(topicId=239, activityId=115):
    """获取问题列表

    :param topicId: 主题 id
    :param activityId: 活动 id
    :return:
    """
    url = "https://ef.3hours.taobao.com/eknow/activity/getQuestionPage"
    params = {
        "topicId": topicId,
        "activityId": activityId
    }
    jar_cookies = requests.utils.cookiejar_from_dict(cookie)
    response = requests.get(url=url, params=params, headers=headers, cookies=jar_cookies).json()
    return response


@ErrorCatcher
def saveAnswer(pageId, questionId, activityId=115, topicId=239, optionId=1):
    """保存用户答案

    :param optionId: 用户选项 id
    :param pageId: 页码
    :param questionId: 问题 id
    :param activityId: 活动 id
    :param topicId: 主题 id
    :return:
    """
    url = "https://ef.3hours.taobao.com/eknow/user/saveUserAnswer"
    params = {
        "p_csrf": p_csrf,
        "threehours-from-channel": ""
    }
    data = {
        "activityId": activityId,
        "topicId": topicId,
        "pageId": pageId,
        "questionId": questionId,
        "optionId": optionId,
        "showParse": "true"
    }
    jar_cookies = requests.utils.cookiejar_from_dict(cookie)
    response = requests.post(url=url, params=params, json=data, headers=headers, cookies=jar_cookies).json()
    return response


@ErrorCatcher
def processAnswer(pageId, activityId=115, topicId=239):
    """处理用户答案

    :param pageId: 页码
    :param activityId: 活动 id
    :param topicId: 主题 id
    :return:
    """
    url = "https://ef.3hours.taobao.com/eknow/user/processUserAnswer"
    params = {
        "p_csrf": p_csrf,
        "threehours-from-channel": ""
    }
    data = {
        "activityId": activityId,
        "topicId": topicId,
        "pageId": pageId
    }
    jar_cookies = requests.utils.cookiejar_from_dict(cookie)
    response = requests.post(url=url, params=params, json=data, headers=headers, cookies=jar_cookies).json()
    return response


@ErrorCatcher
def donateSteps(superTeamId=4590, dsSteps=5000):
    """捐步

    :param superTeamId: 队伍 id
    :param dsSteps: 步数
    :return:
    """
    url = "https://cwp.alibabafoundation.com/superTeam/donateStep"
    params = {
        "p_csrf": p_csrf
    }
    data = {
        "superTeamId": superTeamId,
        "dsSteps": dsSteps
    }
    jar_cookies = requests.utils.cookiejar_from_dict(cookie)
    response = requests.post(url=url, params=params, json=data, headers=headers, cookies=jar_cookies).json()
    return response


@ErrorCatcher
def getUser():
    url = "https://m.3hours.taobao.com/user/userIndex"
    get_user_headers = {
        "Host": "m.3hours.taobao.com",
        "csr-token": csr_token,
        "csr-uuid": csr_uuid,
        "csr-account-v2": "true",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
        "Content-Type": "application/json;charset=UTF-8",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "csr-front-v": "1.1.0",
        "Origin": "https://3hours.taobao.com",
        "Referer": "https://3hours.taobao.com/"
    }
    jar_cookies = requests.utils.cookiejar_from_dict(cookie)
    response = requests.get(url=url, headers=get_user_headers, cookies=jar_cookies).json()
    return response


# 页面基本配置
st.set_page_config(page_title="人人3小时", page_icon="🏠")
st.markdown("### 🏠 人人3小时一键执行")

# 获取 cookie 管理器
cm = CookieManager()
# 获取用户配置
user_config_res = cm.get("user_config")

# 初始化一些变量
csr_uuid = None
user_config = {}
user_effective = False
user_config_success = False

if user_config_res:
    # 存在本地配置
    if user_config_res.get("code") == 200:
        user_config = json.loads(base64.b64decode(user_config_res.get("value")).decode())
        p_csrf = user_config["p_csrf"]
        csr_uuid = user_config["csr_uuid"]
        phoneNumber = user_config["phoneNumber"]
        timestamp = user_config["timestamp"]
        status = user_config["status"]
        if (status == 0) and (time.time() - timestamp < 180):
            headers["csr_uuid"] = csr_uuid
            user_config_success = True
        if status == 200:
            csr_token = user_config["csr_token"]
            csr_csrf = user_config["csr_csrf"]
            cookie = user_config["cookie"]
            headers["csr-token"] = csr_token
            headers["csr-csrf"] = csr_csrf
            with st.spinner("正在检查登录状态"):
                getUser_res = getUser()
                if getUser_res["code"] != 200:
                    st.warning("用户身份失效，需要重新登录！")
                    JSCookieManager(key="user_config", delete=True)
                    jgy = None
                    with st.spinner("尝试连接云端以删除无效数据..."):
                        new_jgy = JianGuoYunClient()
                        jgy_login_res = new_jgy.login()
                        if jgy_login_res["code"] == 200:
                            jgy = new_jgy
                            st.success("云端连接成功！")
                        else:
                            st.warning("云端连接失败！")
                            st.write(jgy_login_res)
                    if jgy is not None:
                        with st.spinner("尝试删除云端无效数据..."):
                            delete_user_config_res = jgy.delete(str(phoneNumber))
                            if delete_user_config_res and delete_user_config_res.get("code") == 200:
                                st.success("删除云端无效数据成功！")
                            else:
                                st.warning("删除云端无效数据失败！")
                                st.write(delete_user_config_res)
                else:
                    st.success("用户身份验证成功！")
                    user_config_success = True
                    user_effective = True
            if not user_effective:
                refreshPage()

    # 本地配置不存在或者失效
    if not user_config_success:
        csr_uuid = str(uuid.uuid4())
        headers["csr_uuid"] = csr_uuid
        with st.form(key="phoneNumber_form"):
            phoneNumber = st.text_input(label="请输入手机号码：", key="phoneNumber_input")
            if st.form_submit_button("确定"):
                data_from_cloud = False
                jgy = None
                with st.spinner("尝试连接云端以获取数据..."):
                    new_jgy = JianGuoYunClient()
                    jgy_login_res = new_jgy.login()
                    if jgy_login_res["code"] == 200:
                        jgy = new_jgy
                        st.success("云端连接成功！")
                    else:
                        st.warning("云端连接失败！")
                        st.write(jgy_login_res)
                if jgy is not None:
                    with st.spinner("尝试从云端获取数据..."):
                        cloud_user_config_res = jgy.get(str(phoneNumber))
                        if cloud_user_config_res and cloud_user_config_res.get("code") == 200:
                            user_config = json.loads(base64.b64decode(cloud_user_config_res["value"]).decode())
                            JSCookieManager(key="user_config", value=json.dumps(user_config))
                            st.success("云端数据获取成功！")
                            data_from_cloud = True
                if data_from_cloud:
                    refreshPage()
                else:
                    getCsrf_success = False
                    with st.spinner("正在获取 CSRF 参数..."):
                        getCsrf_res = getCsrf()
                        if getCsrf_res["code"] == 200:
                            p_csrf = getCsrf_res["p_csrf"]
                            getCsrf_success = True
                            st.success("获取 CSRF 参数成功！")
                        else:
                            st.warning("获取 CSRF 参数失败！")
                            st.write(getCsrf_success)
                    if getCsrf_success:
                        getCaptcha_success = False
                        with st.spinner("正在获取验证码..."):
                            sendCaptcha_res = sendCaptcha()
                            if sendCaptcha_res["code"] != 200:
                                st.warning("获取验证码失败！")
                                st.write(sendCaptcha_res)
                            else:
                                getCaptcha_success = True
                                st.success("获取验证码成功！")
                                user_config = {
                                    "csr_uuid": csr_uuid,
                                    "p_csrf": p_csrf,
                                    "phoneNumber": phoneNumber,
                                    "timestamp": time.time(),
                                    "status": 0
                                }
                                JSCookieManager(key="user_config", value=json.dumps(user_config))
                        if getCaptcha_success:
                            refreshPage()

    # 本地配置存在但未登录成功
    if user_config_success and not user_effective:
        with st.form(key="captcha_form"):
            show_phoneNumber = st.text_input(label="手机号码：", key="show_phoneNumber", disabled=True, value=phoneNumber)
            captcha = st.text_input(label="请输入验证码：", key="captcha_input")
            captcha_submit = st.form_submit_button("确定")
            change = st.form_submit_button("更改手机号码")
            if captcha_submit:
                login_success = False
                with st.spinner("正在登录..."):
                    login_res = login()
                    if login_res["code"] != 200:
                        st.warning("登录失败！")
                        st.write(login_res)
                    else:
                        login_res = login_res["login_response"]
                        login_json = login_res.json()
                        if login_json["code"] != 200:
                            st.warning("登录失败！")
                            st.write(login_json)
                        else:
                            login_success = True
                if login_success:
                    csr_token = login_json["data"]["sid"]
                    csr_csrf = login_json["data"]["token"]
                    cookie = login_res.cookies.get_dict()
                    user_config["csr_token"] = csr_token
                    user_config["csr_csrf"] = csr_csrf
                    user_config["cookie"] = cookie
                    user_config["status"] = 200
                    JSCookieManager(key="user_config", value=json.dumps(user_config))
                    st.success("登录成功！")
                    refreshPage()
            if change:
                JSCookieManager(key="user_config", delete=True)
                refreshPage()

    # 登录成功
    if user_effective:
        st.info("可以选择将数据上传云端，每天 06:00 自动执行！")
        with st.form("execute_form"):
            show_phoneNumber = st.text_input(label="手机号码：", key="show_phoneNumber", disabled=True, value=phoneNumber)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                execute_submit = st.form_submit_button("一键执行")
            with col2:
                change = st.form_submit_button("更换账号")
            with col3:
                upload_submit = st.form_submit_button("上传至云端")
            with col4:
                delete_from_cloud = st.form_submit_button("从云端删除")

            if upload_submit:
                jgy = None
                with st.spinner("尝试连接云端..."):
                    new_jgy = JianGuoYunClient()
                    jgy_login_res = new_jgy.login()
                    if jgy_login_res["code"] == 200:
                        jgy = new_jgy
                        st.success("云端连接成功！")
                    else:
                        st.warning("云端连接失败！")
                        st.write(jgy_login_res)
                if jgy is not None:
                    with st.spinner("正在上传数据..."):
                        upload_res = jgy.set(param=str(phoneNumber), value=json.dumps(user_config))
                        if upload_res["code"] == 200:
                            st.success("数据上传成功！")
                        else:
                            st.warning("数据上传失败！")
                            st.write(upload_res)

            if delete_from_cloud:
                jgy = None
                with st.spinner("尝试连接云端..."):
                    new_jgy = JianGuoYunClient()
                    jgy_login_res = new_jgy.login()
                    if jgy_login_res["code"] == 200:
                        jgy = new_jgy
                        st.success("云端连接成功！")
                    else:
                        st.warning("云端连接失败！")
                        st.write(jgy_login_res)
                if jgy is not None:
                    with st.spinner("正在删除云端数据..."):
                        delete_user_config_res = jgy.delete(str(phoneNumber))
                        if delete_user_config_res and delete_user_config_res.get("code") == 200:
                            JSCookieManager(key="user_config", delete=True)
                            st.success("删除云端数据成功！")
                            refreshPage()
                        else:
                            st.warning("删除云端数据失败！")
                            st.write(delete_user_config_res)

            if change:
                JSCookieManager(key="user_config", delete=True)
                refreshPage()

            if execute_submit:
                # ***** 投票 ***** #
                getVoteList_success = False
                with st.spinner("正在获取投票列表..."):
                    voteList_res = getVoteList()
                    if voteList_res["code"] != 200:
                        st.warning("获取投票列表失败！")
                        st.write(voteList_res)
                    else:
                        getVoteList_success = True
                if getVoteList_success:
                    headers["Host"] = "m.3hours.taobao.com"
                    vote_failed = 0
                    vote_success = 0
                    with st.spinner("正在执行投票..."):
                        vote_list = [i for i in voteList_res["data"]["list"] if i["userOption"] is None][:1]
                        if len(vote_list) < 1:
                            vote_list = [i for i in voteList_res["data"]["list"] if i["userOption"]][:1]
                        for vote_dict in vote_list:
                            vote_id = vote_dict["voteId"]
                            vote_res = vote(voteId=vote_id)
                            if vote_res["code"] != 200:
                                vote_failed += 1
                                st.warning(f"投票失败 {vote_failed} 次！")
                                st.write(vote_res)
                            else:
                                vote_success += 1
                                st.info(f"投票成功 {vote_success} 次！")
                    if vote_success == 1:
                        st.success("投票任务已完成！")
                # ***** 益起猜 ***** #
                headers["Host"] = "ef.3hours.taobao.com"
                getQuestion_success = False
                with st.spinner("正在获取益起猜题目..."):
                    getQuestion_res = getQuestion()
                    if getQuestion_res["code"] != 200:
                        st.warning("获取益起猜题目失败！")
                        st.write(getQuestion_res)
                    else:
                        getQuestion_success = True
                if getVoteList_success:
                    question_id = getQuestion_res["data"]["questionList"][0]["questionId"]
                    page_id = getQuestion_res["data"]["pageId"]
                    saveAnswer_success = False
                    with st.spinner("正在保存益起猜答案..."):
                        saveAnswer_res = saveAnswer(pageId=page_id, questionId=question_id)
                        if saveAnswer_res["code"] != 200:
                            st.warning("获取益起猜豆子失败！")
                            st.write(saveAnswer_res)
                        else:
                            saveAnswer_success = True
                    if saveAnswer_success:
                        with st.spinner("正在获取益起猜豆子..."):
                            processAnswer_res = processAnswer(pageId=page_id)
                            if processAnswer_res["code"] != 200:
                                st.warning("获取益起猜豆子失败！")
                                st.write(processAnswer_res)
                            else:
                                st.success("益起猜任务已完成！")
                # ***** 捐步 ***** #
                with st.spinner("正在执行益起动捐步..."):
                    headers["Host"] = "cwp.alibabafoundation.com"
                    headers["Origin"] = "https://cwp.alibabafoundation.com"
                    del headers["Referer"]
                    donateSteps_res = donateSteps()
                    if donateSteps_res["code"] != 200:
                        st.warning("益起动捐步任务失败！")
                        st.write(donateSteps_res)
                    else:
                        st.success("益起动捐步任务已完成！")







