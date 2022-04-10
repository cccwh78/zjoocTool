import requests
import ddddocr
import re
import html
# from rich import print
'''
脱机实现 zjooc 秒过章节内容和作业、测验、考试等。
'''

Headers = {
     'Accept':'application/json, text/javascript, */*; q=0.01',
     'SignCheck':'311b2837001279449a9ac84d026e11c5',
     'TimeDate':'1646754554000',
     # 这里的TimeDate 和 SignCheck 是时间戳和加密后的token
     'User-Agent':'Mozilla/5.0(WindowsNT10.0;Win64;x64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/99.0.4844.51Safari/537.36',
    }
couseLst=[]
videoMsgLst=[]
unvideoMsgLst=[]
examMsgLst=[]
quizeMsgLst=[]
userInfoLst=[]
batchDict={}

def getCaptchaCode() -> dict :# 获取验证码信息
    headers = {
    'User-Agent':'Mozilla/5.0(WindowsNT10.0;Win64;x64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/98.0.4758.102Safari/537.36',
    }
    captchaurl = 'https://centro.zjlll.net/ajax?&service=/centro/api/authcode/create&params='
    res = requests.get(captchaurl,headers=headers).json()['data']
    #    img_bytes = base64.b64decode(b64_img)
    #   with open("test.jpg", 'wb') as f:
    #         f.write(img_bytes)
    return res

# 这里进行账号登陆
def login(username='', password=''):
    captchaCodedata = getCaptchaCode()
    captchaId = captchaCodedata['id']# 验证码ID
    ocr = ddddocr.DdddOcr()
    captchaCode = ocr.classification(img_base64=captchaCodedata['image'])# 验证码内容
    print(captchaId)
    logindata = {
        'login_name':username,
        'password':password,
        'captchaCode':captchaCode,
        'captchaId':captchaId,
        'redirect_url':'https://www.zjooc.cn',
        'app_key':'0f4cbab4-84ee-48c3-ba4c-874578754b29',
        'utoLoginTime':'7'
    }
    # 这里并没有做异常处理 一般情况下你账号密码正确 没有什么问题 可能验证码错误重试即可。
    res = requests.post('https://centro.zjlll.net/login/doLogin', data = logindata).json()
    param = {
        #'time': 'm6kxkKnDKxj7kP6yziFQiB8JcAXrsBC41646796129000',
        # time 可以不传 是一个时间戳加密后的数据
        'auth_code': res['authorization_code'],
        'autoLoginTime': '7'
    }
    res = requests.get('https://www.zjooc.cn/autoLogin',params=param)
    
    global cookie 
    cookie = requests.utils.dict_from_cookiejar(res.cookies)

def getUserInfo() -> list :
    userInfoData = requests.get('https://www.zjooc.cn/ajax?service=/centro/api/user/getProfile&params[withDetail]=true',headers=Headers,cookies=cookie).json()['data']
    global cuserInfoDLst
    # userInfoLst=[]
    print(userInfoData)
    
    couseMsg={
        'name':userInfoData['name'],
        'corpName':userInfoData['corpName'],
        'studentNo':userInfoData['studentNo'],
        'loginName':userInfoData['loginName'],
        'roleType':userInfoData['roleType'],
        }
    userInfoLst.append(couseMsg)
    print(userInfoLst)
    return userInfoLst
def getCourseMsg() -> list:
    courseMsgData = requests.get('https://www.zjooc.cn/ajax?service=/jxxt/api/course/courseStudent/student/course&params[pageNo]=1&params[pageSize]=5&params[coursePublished]=&params[courseName]=&params[publishStatus]=&params[batchKey]=',headers=Headers,cookies=cookie).json()['data']
    global couseLst
    global batchDict
    # couseLst=[]
    # batchDict={}
    for i in range(len(courseMsgData)):
        couseMsg={
            'id':i,
            'courseId':courseMsgData[i]['id'],
            'courseName':courseMsgData[i]['name'],
            'courseBatchId':courseMsgData[i]['batchId'],
            'courseProcessStatus':courseMsgData[i]['processStatus'],
        }
        couseLst.append(couseMsg)
        batchDict.update({
            courseMsgData[i]['id']:courseMsgData[i]['batchId']
        })
    print(couseLst)
    return couseLst

def getQuizeMsg() -> list :  
    params = {
        'service':'/tkksxt/api/admin/paper/student/page',
        'params[pageNo]':'1',
        'params[pageSize]':'20',
        'params[paperType]':'1',
        'params[courseId]':'',
        'params[processStatus]':'',
        'params[batchKey]':''
    }
    quizeMsgData = requests.get('https://www.zjooc.cn/ajax', params=params,cookies=cookie,headers=Headers).json()['data']

    global quizeMsgLst
    # quizeMsgLst=[]
    for i in range(len(quizeMsgData)):
        quizeMsg={
            'id':i,
            'courseName':quizeMsgData[i]['courseName'],
            'paperName':quizeMsgData[i]['paperName'],
            'classId':quizeMsgData[i]['classId'],
            'courseId':quizeMsgData[i]['courseId'],
            'paperId':quizeMsgData[i]['paperId'],
            'scorePropor':quizeMsgData[i]['scorePropor']
        }
        quizeMsgLst.append(quizeMsg)
    print(quizeMsgLst)
    return quizeMsgLst

def getExamMsg() -> list :  
    params = {
    'service':'/tkksxt/api/admin/paper/student/page',
    'params[pageNo]':'1',
    'params[pageSize]':'20',
    'params[paperType]':'0',
    'params[courseId]':'',
    'params[processStatus]':'',
    'params[batchKey]':''
    }
    exameMsgData = requests.get('https://www.zjooc.cn/ajax', params=params, cookies=cookie, headers=Headers).json()['data']
    global examMsgLst
    # examMsgLst=[]
    for i in range(len(exameMsgData)):
        examMsg={
            'id':i,
            'courseName':exameMsgData[i]['courseName'],
            'paperName':exameMsgData[i]['paperName'],
            'classId':exameMsgData[i]['classId'],
            'courseId':exameMsgData[i]['courseId'],
            'paperId':exameMsgData[i]['paperId'],
            'scorePropor':exameMsgData[i]['scorePropor']
        }
        examMsgLst.append(examMsg)
    print(examMsgLst)
    return examMsgLst

def getWorkMsg() -> list :
    ...# 作业还未涉及到先画个大饼。

def getAnswers(paperId,courseId) -> dict :
    answesdata = {
    'service':'/tkksxt/api/student/score/scoreDetail',
    'body':'true',
    'params[batchKey]':batchDict[courseId],
    'params[paperId]':paperId,
    'params[courseId]':courseId
    }
    answerMsgData = requests.post('https://www.zjooc.cn/ajax',data=answesdata,headers=Headers,cookies=cookie).json()['data']['paperSubjectList']
    print({html.unescape(re.sub(r'<[^>]*?>','',andata['subjectName'])).replace('\n',''):andata['rightAnswer'] for andata in answerMsgData})
    # 返回题目ID及其对应的答案,后面直接上传
    return {andata['id']:andata['rightAnswer'] for andata in answerMsgData}
    
def getVideoMsg(courseId) -> list:  
    videoMsgData = requests.get('https://www.zjooc.cn/ajax?service=/jxxt/api/course/courseStudent/getStudentCourseChapters&params[pageNo]=1&params[courseId]='+courseId+'&params[urlNeed]=0',headers=Headers).json()['data']
    global videoMsgLst
    global unvideoMsgLst
    # videoMsgLst=[]
    # unvideoMsgLst=[]
    x = 0
    for videodata in range(len(videoMsgData)):
        className = videodata['name']
        videoMsgData1 = videodata['children']
        for videodata1 in videoMsgData1:
            className1 = videodata1['name']
            videoMsgData2 = videodata1['children']
            for videodata2 in videoMsgData2:
                # resourceType -> 1和2是视频或者字幕
                # learnStatus  -> 0:表示尚未学习 2:表示已学习 1:可能处于学与未学的薛定谔状态
               if (videodata2['resourceType']==1 or videodata2['resourceType']==2) and  videodata2['learnStatus']==0:
                    videoMsg = {
                        'id':x,
                        'Name':className+'-'+className1+'-'+videodata2['name'],
                        'courseId':courseId,
                        'chapterId':videodata2['id'],
                        'time':videodata2['vedioTimeLength'],
                      # 'learnStatus':videoMsgData2[n]['learnStatus']
                    }
                    videoMsgLst.append(videoMsg)
               elif videodata2['learnStatus']==0 :
                    videoMsg = {
                        'id':x,
                        'Name':className+'-'+className1+'-'+videodata2['name'],
                        'courseId':courseId,
                        'chapterId':videodata2['id'],
                        #'learnStatus':videoMsgData2[n]['learnStatus']
                    }
                    unvideoMsgLst.append(videoMsg)
            x+=1
    print(videoMsgLst)

def doAnswer(paperId, courseId,classId) -> int :
    '''
    做答案
    '''
    # 获取题目答案
    qaData = getAnswers(paperId,courseId)
    # 申请答题
    answesparams = {
    'service':'/tkksxt/api/admin/paper/getPaperInfo',
    'params[paperId]':paperId,
    'params[courseId]':courseId,
    'params[classId]':classId,    
    'params[batchKey]':batchDict[courseId],
    }
    MsgData = requests.get('https://www.zjooc.cn/ajax',params=answesparams,cookies=cookie,headers=Headers).json()['data']
    # 提交答案
    #batchKey
    id = MsgData['id']
    stuId = MsgData['stuId']
    #clazzId=calssid
    scoreId=MsgData['scoreId']
    MsgData1 = MsgData['paperSubjectList']
    sendAnswerData = {       
    'service':'/tkksxt/api/student/score/sendSubmitAnswer',
    'body':'true',
    'params[batchKey]':batchDict[courseId],
    'params[id]':id,
    'params[stuId]':stuId,
    'params[clazzId]':classId,
    'params[scoreId]':scoreId,
    }

    for i in range(len(MsgData1)):
        qadic = {
            f'params[paperSubjectList][{i}][id]':MsgData1[i]['id'],
            f'params[paperSubjectList][{i}][subjectType]':MsgData1[i]['subjectType'],
            f'params[paperSubjectList][{i}][answer]':qaData[MsgData1[i]['id']]
        }
        sendAnswerData.update(qadic)
    print(sendAnswerData)
    res = requests.post('https://www.zjooc.cn/ajax',data=sendAnswerData,cookies=cookie,headers=Headers).content.decode('utf-8')
    print(res)

def doVideo() -> int :
    '''
    秒过章节内容。
    '''
    for i in videoMsgLst:
        videoparams = {
        'service':'/learningmonitor/api/learning/monitor/videoPlaying',
        'params[chapterId]':i['chapterId'],
        'params[courseId]':i['courseId'],
        '&params[playTime]':i['time'],    
        'params[percent]':'100'
        }
        params = 'service=/learningmonitor/api/learning/monitor/videoPlaying&params[chapterId]='+i['chapterId']+'&params[courseId]='+i['courseId']+'&params[playTime]='+str(i['time'])+'&params[percent]=100'
        res = requests.get('https://www.zjooc.cn/ajax?'+params,headers=Headers).json()
        print(res)
    for n in unvideoMsgLst:
        params = 'service=/learningmonitor/api/learning/monitor/finishTextChapter&params[courseId]='+n['courseId']+'&params[chapterId]='+n['chapterId']
        res = requests.get('https://www.zjooc.cn/ajax?'+params,headers=Headers).json()
        print(res)


def doan():
    '''
    秒过测验、考试  作业还没搞
    '''
    for exammsg in examMsgLst:
        if exammsg['scorePropor'] != '100/100.0':
            doAnswer(paperId=exammsg['paperId'], courseId=exammsg['courseId'],classId=exammsg['classId'])

    for quizemsg in examMsgLst:
        if quizemsg['scorePropor'] != '100/100.0':
            doAnswer(paperId=quizemsg['paperId'], courseId=quizemsg['courseId'],classId=quizemsg['classId'])


def getans():
    '''
    秒过测验、考试  作业还没搞
    '''
    for exammsg in examMsgLst:
        if exammsg['scorePropor'] != '100/100.0':
            getAnswers(paperId=exammsg['paperId'],courseId=exammsg['courseId'])


    for quizemsg in examMsgLst:
        if quizemsg['scorePropor'] != '100/100.0':
            getAnswers(paperId=quizemsg['paperId'],courseId=quizemsg['courseId'])


if __name__=="__main__":
    ##########初始化##########
    login()
    getCourseMsg()
    #########################
    # getUserInfo()
    # getQuizeMsg()
    getExamMsg()
    # doVideo()
    getans()
    doan()

