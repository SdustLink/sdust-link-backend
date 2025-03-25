import datetime
import json
import string
import traceback
from random import choices, random

from django.contrib.sites import requests
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
import requests as requests

from django.conf import settings
from django.contrib.auth import authenticate
from django.core.cache import cache
from hashlib import md5
import jwt
from ConQZ.models import User,DepartmentClass,Share,LikesInfo,Course,CourseTime,CourseSchedule,FoodLocation,Food,Static
from requests import RequestException
import logging

# Create a logger for this file
logger = logging.getLogger(__name__)

global HEADERS,url

from django.shortcuts import render

# Create your views here.
HEADERS = {
   "User-Agent": "Mozilla/5.0 (Linux; U; Mobile; Android 6.0.1;C107-9 Build/FRF91 )",
   "Referer": "http://www.baidu.com",
   "Accept-encoding": "gzip, deflate, br",
   "Accept-language": "zh-CN,zh-TW;q=0.8,zh;q=0.6,en;q=0.4,ja;q=0.2",
   "Cache-control": "max-age=0"
}
url = "http://jwgl.sdust.edu.cn/app.do"

# 配置日志





def auth_by_snumber(snumber, encrypted_snumber):
    """如果encrypted_snumber等于固定值就会返回true"""
    if not encrypted_snumber:
        return False
    if encrypted_snumber == 'wxdb4a3a20947d7c4a':
        return True
    return False


#加密/解密邀请码
ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
mappings = {c: i for i, c in enumerate(ALPHABET)}
# 事先约定的密钥
key = [1, 2, 3, 4, 5, 6]

# 随机生成函数
characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789&#@'

def generate_code(id):
    base_code = ''
    for i in range(8):
        index = ((id * 23 + i * 17) % len(characters))
        base_code += characters[index]
    code = base_code

    # 检测invitecode是否唯一,如果不唯一则进行处理
    while DepartmentClass.objects.filter(invitecode=code).exists():
        code = base_code + str(id)
        id += 1

    return code

#登录
def Logininfo(request):
    """
    鉴权登录并创建用户表，返回用户对话token
    :return: 用户对话token
    """
    log_data = {
        'view': 'Logininfo',
        'method': request.method,
        'path': request.path,
    }

    
    if request.method == 'POST':
        try:
            json_param = json.loads(request.body.decode())
        except json.JSONDecodeError as e:
            log_data['error'] = str(e)
            logger.error("JSON parsing error", extra=log_data)
            return JsonResponse({'status': 'error', 'message': 'JSON解析错误: {}'.format(str(e))})

        try:
            account = int(json_param.get('snumber'))
            name = json_param.get('name')
            classname = json_param.get('classname')
            majorname = json_param.get('majorname')
            collegename = json_param.get('collegename')
            enteryear = int(json_param.get('enteryear'))
            gradenumber = int(json_param.get('gradenumber'))
            code = json_param.get('code')
        except (TypeError, ValueError) as e:
            log_data['error'] = str(e)
            logger.error("Parameter error", extra=log_data)
            return JsonResponse({'status': 'error', 'message': '参数错误: {}'.format(str(e))})

        if not code:
            log_data['error'] = 'Missing code parameter'
            logger.warning("Missing code parameter", extra=log_data)
            return JsonResponse({'status': 'error', 'message': '缺少 code 参数'})

        try:
            if not auth_by_snumber(account, code):
                return JsonResponse({'code': 4000, 'message': 'TOKEN Error'})
        except Exception as e:
            log_data['error'] = str(e)
            logger.error("Authentication error", extra=log_data)
            return JsonResponse({'status': 'error', 'message': '鉴权错误: {}'.format(str(e))})

        try:
            user_obj, created = User.objects.get_or_create(
                Snumber=account,
                defaults={
                    'Name': name,
                    'Classname': classname,
                    'Majorname': majorname,
                    'Collegename': collegename,
                    'Enteryear': enteryear,
                    'Gradenumber': gradenumber,
                    'Openid': code
                }
            )
            if not created:
                user_obj.Name = name
                user_obj.Classname = classname
                user_obj.Majorname = majorname
                user_obj.Collegename = collegename
                user_obj.Enteryear = enteryear
                user_obj.Gradenumber = gradenumber
                user_obj.Openid = code
                user_obj.save()
            share_obj, created = Share.objects.get_or_create(Usernumber_id=account)

            return JsonResponse({'status': 'success', 'token': code})
        except Exception as e:
            log_data['error'] = str(e)
            logger.error("Database operation error", extra=log_data)
            return JsonResponse({'status': 'error', 'message': '数据库操作错误: {}'.format(str(e))})

    else:
        log_data['error'] = 'Invalid HTTP method'
        logger.warning("Received non-POST request for login", extra=log_data)
        return JsonResponse({'status': 'error', 'message': '仅支持 POST 请求'})
# 提交课程记录

#共享课表路由

def PostClassInfo(request):
    log_data = {
        'view': 'PostClassInfo',
        'method': request.method,
        'path': request.path,
    }

    # 获取请求体中的参数
    try:
        json_param = json.loads(request.body.decode())
        table_ord = json_param.get('table_ord', [])
        week = json_param.get('week')
        token = json_param.get("token")
        snumber = json_param.get("snumber")
    except Exception as e:
        log_data['error'] = str(e)
        logger.error("Invalid Parameters", extra=log_data)
        return JsonResponse({"code": 4000, "message": "Invalid Parameters"})

    if not auth_by_snumber(snumber, token):
        log_data['error'] = "Authentication failed"
        logger.warning("TOKEN Error", extra=log_data)
        return JsonResponse({"code": 4000, "message": "TOKEN Error"})

    created_courses = {}
    tablesame = [[-1 for j in range(2)] for k in range(35)]
    tablecolor = ["#ebb5cc", "#b2c196", "#edd492", "#fee5a3", "#e9daa3", "#ea7375", "#a286ea", "#776fdf", "#7bc6e6", "#efb293"]
    table = [[[[] for j in range(5)] for i in range(5)] for k in range(7)]
    flag_i_color = 0

    for newtable in table_ord:
        if newtable is None or not all(key in newtable for key in ['kcmc', 'jsmc', 'jsxm', 'kkzc', 'kcsj']):
            continue

        try:
            get_kcmc = newtable.get("kcmc")
            get_jsmc = newtable.get("jsmc")
            get_jsxm = newtable.get("jsxm")
            get_kkzc = newtable.get("kkzc")
            get_kcsj = newtable.get("kcsj")

            course_key = (get_kcmc, get_jsxm)
            kcsj_day = int(get_kcsj[0]) - 1
            cout = int(int(get_kcsj[3] + get_kcsj[4]) / 2) - 1

            table[kcsj_day][cout] = [get_kcmc, get_jsmc, get_jsxm]

            if course_key not in created_courses:
                Course_result, created = Course.objects.get_or_create(CourseName=get_kcmc, CourseTeacher=get_jsxm)
                created_courses[course_key] = Course_result
            else:
                Course_result = created_courses[course_key]

            CourseTime.objects.get_or_create(
                CourseId=Course_result,
                CourseTime=get_kcsj,
                CourseWeek=get_kkzc,
                CoursePlace=get_jsmc
            )

            for tablesame_i in tablesame:
                if tablesame_i[0] == get_kcmc:
                    table[kcsj_day][cout].append(tablesame_i[1])
                    break
                if tablesame_i[0] == -1:
                    tablesame_i[0] = get_kcmc
                    tablesame_i[1] = tablecolor[flag_i_color % 7]
                    flag_i_color += 1
                    table[kcsj_day][cout].append(tablesame_i[1])
                    break

        except Exception as e:
            log_data['error'] = str(e)
            logger.warning(f"Error processing course: {get_kcmc}", extra=log_data)
            continue

    try:
        str_json = json.dumps(table, ensure_ascii=False, indent=2)
    except Exception as e:
        log_data['error'] = str(e)
        logger.error("JSON encoding error", extra=log_data)
        return HttpResponse(content=f"An error occurred: {e}", status=500)

    try:
        user = User.objects.get(Snumber=snumber)
    except User.DoesNotExist:
        log_data['error'] = "User not found"
        logger.error("No User", extra=log_data)
        return JsonResponse({"code": 4000, "message": "No User"})

    try:
        schedule, created = CourseSchedule.objects.update_or_create(
            user=user, week_number=week,
            defaults={'schedule': str_json}
        )
    except Exception as e:
        log_data['error'] = str(e)
        logger.error("Error saving course schedule", extra=log_data)
        return JsonResponse({'status': 'error', 'message': '保存课程表时出错'})

    return JsonResponse({'status': 'success'})

def ReplyShareState(request):
    log_data = {
        'view': 'ReplyShareState',
        'method': request.method,
        'path': request.path,
    }

    # 解析请求体
    try:
        json_param = json.loads(request.body.decode())
        _account = json_param.get('account')
        token = json_param.get("token")
        _reply = json_param.get('reply')
        _postnum = json_param.get('postnum')
        _cont = json_param.get("cont")  # ABCDE
        log_data.update({'account': _account, 'reply': _reply, 'postnum': _postnum, 'cont': _cont})
    except json.JSONDecodeError as e:
        logger.error("Invalid request body", extra=log_data)
        return JsonResponse({"code": 4004, "message": "Invalid Request"}, status=400)

    # 验证token
    if not auth_by_snumber(_account, token):
        logger.warning("Token authentication failed", extra=log_data)
        return JsonResponse({"code": 4000, "message": "TOKEN Error"}, status=400)

    # 查找用户是否存在
    try:
        Userresult = User.objects.filter(Snumber=_account)
        if not Userresult.exists():
            logger.warning("User not found", extra=log_data)
            return JsonResponse({"code": 4001, "message": "Not User"}, status=400)
    except Exception as e:
        logger.error(f"Database error when checking user: {str(e)}", extra=log_data)
        return JsonResponse({"code": 4004, "message": f"DB Error: {str(e)}"}, status=400)

    # 查找共享表是否存在
    try:
        Shareresult = Share.objects.filter(Usernumber_id=_account)
        if not Shareresult.exists():
            Share.objects.create(Usernumber_id=_account)
            logger.warning("Created new share entry for user", extra=log_data)
    except Exception as e:
        logger.error(f"Database error when checking/creating share: {str(e)}", extra=log_data)
        return JsonResponse({"code": 4004, "message": "DB Error"}, status=400)

    # 获取状态字段和编号字段
    try:
        share_bind_dict = {
            'A': ('CBindAState', 'CBindANumber'),
            'B': ('CBindBState', 'CBindBNumber'),
            'C': ('CBindCState', 'CBindCNumber'),
            'D': ('CBindDState', 'CBindDNumber'),
            'E': ('CBindEState', 'CBindENumber')
        }
        state_field, number_field = share_bind_dict[_cont]
    except KeyError:
        logger.error("Invalid course id", extra=log_data)
        return JsonResponse({"code": 4006, "message": "Invalid course id"}, status=400)

    # 处理回复
    try:
        if _reply:
            # 检查接受人状态
            sharebind = Share.objects.filter(Usernumber_id=_account).values(state_field)[0][state_field]
            if sharebind != 2:
                logger.warning("Invalid receiver state", extra=log_data)
                return JsonResponse({"code": 4005, "message": "relation error"}, status=400)

            # 检查发送人状态
            sharebind = Share.objects.filter(Usernumber_id=_postnum).values(state_field)[0][state_field]
            if sharebind != 1:
                logger.warning("Invalid sender state", extra=log_data)
                return JsonResponse({"code": 4005, "message": "relation error"}, status=400)

            # 更新状态
            Share.objects.filter(Usernumber_id=_account).update(**{state_field: 3, number_field: _postnum})
            Share.objects.filter(Usernumber_id=_postnum).update(**{state_field: 3, number_field: _account})
        else:
            # 拒绝请求，重置状态
            Share.objects.filter(Usernumber_id=_account).update(**{state_field: 0, number_field: -1})
            Share.objects.filter(Usernumber_id=_postnum).update(**{state_field: 0, number_field: -1})

    except Exception as e:
        logger.error(f"Database error when updating share state: {str(e)}", extra=log_data)
        return JsonResponse({"code": 4004, "message": "DB Error"}, status=400)

    return JsonResponse({"code": 2000, "message": "Perfect"}, status=200)


def PostShareState(request):
    log_data = {
        'view': 'PostShareState',
        'method': request.method,
        'path': request.path,
    }

    try:
        json_param = json.loads(request.body.decode())
        _cancel = json_param.get("cancel")
        _account = json_param.get('account')
        _postnum = json_param.get('postnum')
        _cont = json_param.get("cont")
        token = json_param.get("token")
        log_data.update({'account': _account, 'postnum': _postnum, 'cont': _cont, 'cancel': _cancel})
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in request body", extra=log_data)
        return JsonResponse({"code": 4004, "message": "Invalid Request"}, status=400)

    try:
        if not auth_by_snumber(_account, token):
            logger.warning("Token authentication failed", extra=log_data)
            return JsonResponse({"code": 4000, "message": "TOKEN Error"}, status=400)
    except Exception as e:
        logger.error(f"Token authentication error: {str(e)}", extra=log_data)
        return JsonResponse({"code": 4004, "message": f"TOKEN Error: {str(e)}"}, status=400)

    try:
        if not User.objects.filter(Snumber=_account).exists():
            logger.warning("User not found", extra=log_data)
            return JsonResponse({"code": 4001, "message": "Not User"}, status=400)

        Share.objects.get_or_create(Usernumber_id=_account)

        if not User.objects.filter(Snumber=_postnum).exists():
            logger.warning("Other user not found", extra=log_data)
            return JsonResponse({"code": 4002, "message": "Not User Other"}, status=400)

        share_bind_dict = {
            'A': ('CBindAState', 'CBindANumber'),
            'B': ('CBindBState', 'CBindBNumber'),
            'C': ('CBindCState', 'CBindCNumber'),
            'D': ('CBindDState', 'CBindDNumber'),
            'E': ('CBindEState', 'CBindENumber')
        }
        state_field, number_field = share_bind_dict.get(_cont, (None, None))
        if not state_field:
            logger.error("Invalid content type", extra=log_data)
            return JsonResponse({"code": 4001, "message": "CONT ERROR"}, status=400)

        if not _cancel:
            sender_share = Share.objects.get(Usernumber_id=_account)
            receiver_share = Share.objects.get(Usernumber_id=_postnum)

            if getattr(sender_share, state_field) != 0 or getattr(receiver_share, state_field) != 0:
                logger.warning("Invalid share state", extra=log_data)
                return JsonResponse({"code": 4005, "message": "relation error"}, status=400)

            setattr(sender_share, state_field, 1)
            setattr(sender_share, number_field, _postnum)
            setattr(receiver_share, state_field, 2)
            setattr(receiver_share, number_field, _account)
            sender_share.save()
            receiver_share.save()
        else:
            sender_share = Share.objects.get(Usernumber_id=_account)
            receiver_share = Share.objects.get(Usernumber_id=_postnum)

            setattr(sender_share, state_field, 0)
            setattr(sender_share, number_field, -1)
            setattr(receiver_share, state_field, 0)
            setattr(receiver_share, number_field, -1)
            sender_share.save()
            receiver_share.save()

    except Exception as e:
        logger.error(f"Database operation error: {str(e)}", extra=log_data)
        return JsonResponse({"code": 4004, "message": "DB Error"}, status=400)

    return JsonResponse({"code": 2000, "message": "Perfect"}, status=200)



def GetShareState(request):
    log_data = {
        'view': 'GetShareState',
        'method': request.method,
        'path': request.path,
    }

    try:
        json_param = json.loads(request.body.decode())
        _account = json_param.get('account')
        token = json_param.get("token")
        log_data['account'] = _account
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body", extra=log_data)
        return JsonResponse({"code": 4004, "message": "Invalid Request"}, status=400)
    except KeyError:
        logger.error("Missing required parameters", extra=log_data)
        return JsonResponse({"code": 4004, "message": "Invalid Parameters"}, status=400)

    try:
        if not auth_by_snumber(_account, token):
            logger.warning("Token authentication failed", extra=log_data)
            return JsonResponse({"code": 4000, "message": "TOKEN Error"}, status=400)
    except Exception as e:
        logger.error(f"Token authentication error: {str(e)}", extra=log_data)
        return JsonResponse({"code": 4004, "message": f"TOKEN Error: {str(e)}"}, status=400)

    try:
        user = User.objects.get(Snumber=_account)
    except User.DoesNotExist:
        logger.warning("User not found", extra=log_data)
        return JsonResponse({"code": 4001, "message": "Not User"}, status=400)
    except Exception as e:
        logger.error(f"Database error when fetching user: {str(e)}", extra=log_data)
        return JsonResponse({"code": 4004, "message": f"DB Error: {str(e)}"}, status=400)

    try:
        share_obj, created = Share.objects.get_or_create(Usernumber_id=_account)
        if created:
            logger.warning("Created new share entry for user", extra=log_data)
    except Exception as e:
        logger.error(f"Database error when fetching/creating share: {str(e)}", extra=log_data)
        return JsonResponse({"code": 4004, "message": "DB Error"}, status=400)

    try:
        data = serializers.serialize("json", [share_obj])
        data_json = json.loads(data)[0].get('fields')

        for dep in ['A', 'B', 'C', 'D']:
            dep_id = data_json.get(f'BindDepart{dep}')
            if dep_id and dep_id != 'None':
                try:
                    dep_name = DepartmentClass.objects.get(invitecode=dep_id).departName
                    data_json[f'DepartName{dep}'] = dep_name
                except ObjectDoesNotExist:
                    logger.warning(f"Department not found for BindDepart{dep}", extra=log_data)
                    data_json[f'DepartName{dep}'] = None
                except Exception as e:
                    logger.error(f"Error fetching department name: {str(e)}", extra=log_data)
                    data_json[f'DepartName{dep}'] = None

    except Exception as e:
        logger.error(f"Error serializing or processing share data: {str(e)}", extra=log_data)
        return JsonResponse({"code": 4004, "message": f"DB Error: {str(e)}"}, status=400)

    return HttpResponse(content=json.dumps(data_json), content_type='application/json')


def GetShareInfo(request):
    log_data = {
        'view': 'GetShareInfo',
        'method': request.method,
        'path': request.path,
    }

    try:
        json_param = json.loads(request.body.decode())
        account = json_param['account']
        token = json_param['token']
        cont = json_param['cont']
        week_number = json_param['week_number']
        postnum = json_param['postnum']
        log_data.update({'account': account, 'cont': cont, 'week_number': week_number, 'postnum': postnum})
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body", extra=log_data)
        return JsonResponse({"code": 4004, "message": "Invalid Request"}, status=400)
    except KeyError as e:
        logger.error(f"Missing required parameter: {str(e)}", extra=log_data)
        return JsonResponse({"code": 4004, "message": "Invalid Parameters"}, status=400)

    try:
        if not auth_by_snumber(account, token):
            logger.warning("Token authentication failed", extra=log_data)
            return JsonResponse({"code": 4000, "message": "TOKEN Error"}, status=400)
    except Exception as e:
        logger.error(f"Token authentication error: {str(e)}", extra=log_data)
        return JsonResponse({"code": 4004, "message": f"TOKEN Error: {str(e)}"}, status=400)

    try:
        if not User.objects.filter(Snumber=account).exists():
            logger.warning("User not found", extra=log_data)
            return JsonResponse({"code": 4001, "message": "Not User"}, status=400)

        if not Share.objects.filter(Usernumber_id=account).exists():
            logger.warning("Share not found for user", extra=log_data)
            return JsonResponse({"code": 4004, "message": "DB Error"}, status=400)

        if not User.objects.filter(Snumber=postnum).exists():
            logger.warning("Other user not found", extra=log_data)
            return JsonResponse({"code": 4002, "message": "Not User Other"}, status=400)

        share_bind_dict = {
            'A': ('CBindAState', 'CBindANumber'),
            'B': ('CBindBState', 'CBindBNumber'),
            'C': ('CBindCState', 'CBindCNumber'),
            'D': ('CBindDState', 'CBindDNumber'),
            'E': ('CBindEState', 'CBindENumber')
        }
        
        try:
            state_field, number_field = share_bind_dict[cont]
        except KeyError:
            logger.error("Invalid content type", extra=log_data)
            return JsonResponse({"code": 4001, "message": "CONT ERROR"}, status=400)

        user_share = Share.objects.get(Usernumber_id=account)
        other_share = Share.objects.get(Usernumber_id=postnum)

        if getattr(user_share, state_field) != 3 or getattr(other_share, state_field) != 3:
            logger.warning("Invalid share state", extra=log_data)
            return JsonResponse({"code": 4005, "message": "relation error"}, status=400)

        schedule = CourseSchedule.objects.filter(user=postnum, week_number=week_number).values('schedule')
        
        if not schedule.exists():
            logger.warning("Schedule not found for other user", extra=log_data)
            return JsonResponse({"code": 4006, "message": "对方课表未同步"}, status=400)

        schedule_data = json.loads(schedule[0]['schedule'])
        return JsonResponse(schedule_data, safe=False, status=200)

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", extra=log_data)
        return JsonResponse({"code": 4004, "message": f"DB Error: {str(e)}"}, status=400)

# 部门课表
def CreateDept(request):
    log_data = {
        'view': 'CreateDept',
        'method': request.method,
        'path': request.path,
    }

    # 获取请求体
    try:
        json_param = json.loads(request.body.decode())
        cont = json_param.get("cont")
        account = json_param.get('account')
        token = json_param.get("token")
        name = json_param.get("name")
        log_data.update({'cont': cont, 'account': account, 'name': name})
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body", extra=log_data)
        return JsonResponse({"code": 4004, "message": "Invalid Request"}, status=400)
    except KeyError as e:
        logger.error(f"Missing required parameter: {str(e)}", extra=log_data)
        return JsonResponse({"code": 4004, "message": "Invalid Parameters"}, status=400)

    # 验证token
    try:
        if not auth_by_snumber(account, token):
            logger.warning("Token authentication failed", extra=log_data)
            return JsonResponse({"code": 4000, "message": "TOKEN Error"}, status=400)
    except Exception as e:
        logger.error(f"Token authentication error: {str(e)}", extra=log_data)
        return JsonResponse({"code": 4004, "message": f"TOKEN Error: {str(e)}"}, status=400)

    # 查询用户绑定信息
    try:
        share = Share.objects.get(Usernumber=account)
    except Share.DoesNotExist:
        logger.error("Share not found for user", extra=log_data)
        return JsonResponse({"code": 4004, "message": "DB Error"}, status=400)
    except Exception as e:
        logger.error(f"Database error: {str(e)}", extra=log_data)
        return JsonResponse({"code": 4004, "message": "DB Error"}, status=400)

    # 查询用户的部门槽是否创建了部门
    bind_field = f'BindDepart{cont}'
    if getattr(share, bind_field) is not None:
        logger.warning(f"Department slot {cont} is already occupied", extra=log_data)
        return JsonResponse({"code": 4004, "message": f"部门槽{cont}已被占用"}, status=400)

    # 查找用户已创建的部门数
    try:
        dept_count = DepartmentClass.objects.filter(creatornum=account).count()
    except Exception as e:
        logger.error(f"Error counting user departments: {str(e)}", extra=log_data)
        return JsonResponse({"code": 4004, "message": f"DB Error: {str(e)}"}, status=400)

    # 如果部门数小于4,可以创建新部门
    if dept_count < 4:
        try:
            dept = DepartmentClass.objects.create(creatornum_id=account)
            dept_id_encrypt = generate_code(int(dept.id))
            dept.invitecode = dept_id_encrypt
            dept.departName = name
            dept.save()

            setattr(share, bind_field, dept_id_encrypt)
            share.save()

            logger.info(f"Department created successfully: {dept_id_encrypt}", extra=log_data)
            return JsonResponse({'dept': dept_id_encrypt})
        except Exception as e:
            logger.error(f"Error creating department: {str(e)}", extra=log_data)
            return JsonResponse({"code": 4004, "message": f"DB Error: {str(e)}"}, status=400)
    else:
        logger.warning("User has reached maximum department limit", extra=log_data)
        return JsonResponse({'error': 'Over'})
def JoinDept(request):
    log_data = {
        'view': 'JoinDept',
        'method': request.method,
        'path': request.path,
    }

    # 获取请求体
    try:
        json_param = json.loads(request.body.decode())
        code = json_param.get('code')
        cont = json_param.get("cont")
        account = json_param.get('account')
        token = json_param.get("token")
        log_data.update({'code': code, 'cont': cont, 'account': account})
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body", extra=log_data)
        return JsonResponse({"code": 4004, "message": "Invalid Request"}, status=400)
    except KeyError as e:
        logger.error(f"Missing required parameter: {str(e)}", extra=log_data)
        return JsonResponse({"code": 4004, "message": "Invalid Parameters"}, status=400)

    # 验证token
    try:
        if not auth_by_snumber(account, token):
            logger.warning("Token authentication failed", extra=log_data)
            return JsonResponse({"code": 4000, "message": "TOKEN Error"}, status=400)
    except Exception as e:
        logger.error(f"Token authentication error: {str(e)}", extra=log_data)
        return JsonResponse({"code": 4004, "message": f"TOKEN Error: {str(e)}"}, status=400)

    # 根据邀请码获取部门id
    try:
        dept = DepartmentClass.objects.get(invitecode=code)
    except DepartmentClass.DoesNotExist:
        logger.warning("Invalid invitation code", extra=log_data)
        return JsonResponse({"code": 4001, "message": "邀请码不存在"}, status=400)
    except Exception as e:
        logger.error(f"Database error when fetching department: {str(e)}", extra=log_data)
        return JsonResponse({"code": 4004, "message": f"DB Error: {str(e)}"}, status=400)

    # 查询用户绑定信息
    try:
        share = Share.objects.get(Usernumber=account)
    except Share.DoesNotExist:
        logger.error("Share not found for user", extra=log_data)
        return JsonResponse({"code": 4004, "message": "DB Error: Share not found"}, status=400)
    except Exception as e:
        logger.error(f"Database error when fetching share: {str(e)}", extra=log_data)
        return JsonResponse({"code": 4004, "message": f"DB Error: {str(e)}"}, status=400)

    # 进行绑定操作
    try:
        bind_field = f'BindDepart{cont}'
        if hasattr(share, bind_field):
            setattr(share, bind_field, code)
            share.save()
            logger.info(f"User {account} joined department {code}", extra=log_data)
        else:
            logger.warning(f"Invalid cont value: {cont}", extra=log_data)
            return JsonResponse({"code": 4004, "message": "Invalid cont value"}, status=400)
    except Exception as e:
        logger.error(f"Error during department binding: {str(e)}", extra=log_data)
        return JsonResponse({"code": 4004, "message": f"DB Error: {str(e)}"}, status=400)

    return JsonResponse({'success': True})
def DismissDept(request):
    # 获取请求体
    try:
        postbody = request.body
        json_param = json.loads(postbody.decode())
    except:
        error = {
            "code": 4004,
            "message": "Invalid Request"
        }
        return JsonResponse(error, status=400)

    # 获取请求参数
    try:
        code = json_param.get('code')
        account = json_param.get('account')
        token = json_param.get("token")
    except:
        error = {
            "code": 4004,
            "message": "Invalid Parameters"
        }
        return JsonResponse(error, status=400)

    # 验证token
    try:
        if not auth_by_snumber(account, token):
            error = {"code": 4000, "message": "TOKEN Error"}
            return JsonResponse(error, status=400)
    except Exception as e:
        error = {
            "code": 4004,
            "message": f"TOKEN Error: {str(e)}"
        }
        return JsonResponse(error, status=400)

    # 邀请码解密获取部门id
    try:
        dept = DepartmentClass.objects.get(invitecode=code)
    except DepartmentClass.DoesNotExist:
        error = {"code": 4001, "message": "邀请码不存在"}
        return JsonResponse(error, status=400)
    except Exception as e:
        error = {
            "code": 4004,
            "message": f"DB Error: {str(e)}"
        }
        return JsonResponse(error, status=400)

    # 检验部门创建者是否为当前用户
    try:
        if dept.creatornum_id != int(account):
            error = {'error': '无权限解散该部门!'}
            return JsonResponse(error, status=400)
    except Exception as e:
        error = {
            "code": 4004,
            "message": f"DB Error: {str(e)}"
        }
        return JsonResponse(error, status=400)

    # 删除部门记录
    try:
        dept.delete()
    except Exception as e:
        error = {
            "code": 4004,
            "message": f"DB Error: {str(e)}"
        }
        return JsonResponse(error, status=400)

    # 查询用户绑定信息
    try:
        shares = Share.objects.filter()
    except Exception as e:
        error = {
            "code": 4004,
            "message": f"DB Error: {str(e)}"
        }
        return JsonResponse(error, status=400)

    # 将所有绑定当前部门id的记录设置为-1
    try:
        shares.filter(BindDepartA=code).update(BindDepartA=None)
        shares.filter(BindDepartB=code).update(BindDepartB=None)
        shares.filter(BindDepartC=code).update(BindDepartC=None)
        shares.filter(BindDepartD=code).update(BindDepartD=None)
    except Exception as e:
        error = {
            "code": 4004,
            "message": f"DB Error: {str(e)}"
        }
        return JsonResponse(error, status=400)
    return JsonResponse({'success': True})

def QuitDept(request):
    # 获取请求体
    try:
        postbody = request.body
        json_param = json.loads(postbody.decode())
    except:
        error = {
            "code": 4004,
            "message": "Invalid Request"
        }
        return JsonResponse(error, status=400)

    # 获取请求参数
    try:
        cont = json_param.get("cont")
        account = json_param.get('account')
        token = json_param.get("token")
    except:
        error = {
            "code": 4004,
            "message": "Invalid Parameters"
        }
        return JsonResponse(error, status=400)

    # 验证token
    try:
        if not auth_by_snumber(account, token):
            error = {"code": 4000, "message": "TOKEN Error"}
            return JsonResponse(error, status=400)
    except Exception as e:
        error = {
            "code": 4004,
            "message": f"TOKEN Error: {str(e)}"
        }
        return JsonResponse(error, status=400)

    # 查询用户绑定信息
    try:
        share = Share.objects.get(Usernumber=account)
    except Exception as e:
        error = {
            "code": 4004,
            "message": f"DB Error: {str(e)}"
        }
        return JsonResponse(error, status=400)

    # 进行解绑操作
    try:
        if cont == 'A':
            share.BindDepartA = None
        elif cont == 'B':
            share.BindDepartB = None
        elif cont == 'C':
            share.BindDepartC = None
        elif cont == 'D':
            share.BindDepartD = None
        share.save()
    except Exception as e:
        error = {
            "code": 4004,
            "message": f"DB Error: {str(e)}"
        }
        return JsonResponse(error, status=400)

    return JsonResponse({'success': True})

def KickDept(request):
    # 获取请求体
    try:
        postbody = request.body
        json_param = json.loads(postbody.decode())
    except:
        error = {
            "code": 4004,
            "message": "Invalid Request"
        }
        return JsonResponse(error, status=400)

    # 获取请求参数
    try:
        cont = json_param.get("cont") # 被踢出的用户学号
        code = json_param.get('code')
        account = json_param.get('account')
        token = json_param.get("token")
    except:
        error = {
            "code": 4004,
            "message": "Invalid Parameters"
        }
        return JsonResponse(error, status=400)

    # 验证token
    try:
        if not auth_by_snumber(account, token):
            error = {"code": 4000, "message": "TOKEN Error"}
            return JsonResponse(error, status=400)
    except Exception as e:
        error = {
            "code": 4004,
            "message": f"TOKEN Error: {str(e)}"
        }
        return JsonResponse(error, status=400)

    # 邀请码解密获取部门id

    try:
        dept = DepartmentClass.objects.get(invitecode=code)
    except DepartmentClass.DoesNotExist:
        error = {"code": 4001, "message": "邀请码不存在"}
        return JsonResponse(error, status=400)
    except Exception as e:
        error = {
            "code": 4004,
            "message": f"DB Error: {str(e)}"
        }
        return JsonResponse(error, status=400)
    # 检验部门创建者是否为当前用户
    try:
        if dept.creatornum_id != int(account):
            error = {'error': '无权限解散该部门!'}
            return JsonResponse(error, status=400)
    except Exception as e:
        error = {
            "code": 4004,
            "message": f"DB Error: {str(e)}"
        }
        return JsonResponse(error, status=400)

    try:
        share = Share.objects.get(Usernumber=cont)
        if share.BindDepartA == code:
            share.BindDepartA = None
        elif share.BindDepartB == code:
            share.BindDepartB = None
        elif share.BindDepartC == code:
            share.BindDepartC = None
        elif share.BindDepartD == code:
            share.BindDepartD = None
        share.save()

    except Exception as e:
        error = {
            "code": 4004,
            "message": f"DB Error: {str(e)}"
        }
        return JsonResponse(error, status=400)
    return JsonResponse({'success': True})



def GetDeptInfo(request):
    log_data = {
        'view': 'GetDeptInfo',
        'method': request.method,
        'path': request.path,
    }

    try:
        json_param = json.loads(request.body.decode())
        account = json_param['account']
        token = json_param['token']
        cont = json_param['cont']
        week_number = json_param['week_number']
        log_data.update({'account': account, 'cont': cont, 'week_number': week_number})
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body", extra=log_data)
        return JsonResponse({"code": 4004, "message": "Invalid Request"}, status=400)
    except KeyError as e:
        logger.error(f"Missing required parameter: {str(e)}", extra=log_data)
        return JsonResponse({"code": 4004, "message": "Invalid Parameters"}, status=400)

    try:
        if not auth_by_snumber(account, token):
            logger.warning("Token authentication failed", extra=log_data)
            return JsonResponse({"code": 4000, "message": "TOKEN Error"}, status=400)
    except Exception as e:
        logger.error(f"Token authentication error: {str(e)}", extra=log_data)
        return JsonResponse({"code": 4004, "message": f"TOKEN Error: {str(e)}"}, status=400)

    try:
        if not User.objects.filter(Snumber=account).exists():
            logger.warning("User not found", extra=log_data)
            return JsonResponse({"code": 4001, "message": "Not User"}, status=400)

        if not Share.objects.filter(Usernumber_id=account).exists():
            logger.warning("Share not found for user", extra=log_data)
            return JsonResponse({"code": 4004, "message": "DB Error"}, status=400)

        share_bind_dict = {
            'A': 'BindDepartA',
            'B': 'BindDepartB',
            'C': 'BindDepartC',
            'D': 'BindDepartD'
        }
        
        try:
            state_field = share_bind_dict[cont]
        except KeyError:
            logger.error("Invalid content type", extra=log_data)
            return JsonResponse({"code": 4001, "message": "CONT ERROR"}, status=400)

        depbind = Share.objects.filter(Usernumber_id=account).values(state_field).first()
        if not depbind or depbind[state_field] is None:
            logger.warning("Department not bound", extra=log_data)
            return JsonResponse({"code": 4005, "message": "bind error"}, status=400)

        invitecode = depbind[state_field]
        userlist = Share.objects.filter(
            Q(BindDepartA=invitecode) | Q(BindDepartB=invitecode) | 
            Q(BindDepartC=invitecode) | Q(BindDepartD=invitecode)
        ).values_list('Usernumber', flat=True)

        userlist = list(User.objects.filter(Snumber__in=userlist).values('Snumber', 'Name'))
        logger.info(f"Found {len(userlist)} users in department", extra=log_data)

        scheduletable = [[[[[],[]] for _ in range(len(userlist)+1)] for _ in range(5)] for _ in range(7)]

        for i, user in enumerate(userlist):
            try:
                schedule = CourseSchedule.objects.get(user=user['Snumber'], week_number=week_number).schedule
                schedule = json.loads(schedule)
            except CourseSchedule.DoesNotExist:
                logger.warning(f"Schedule not found for user {user['Name']}", extra=log_data)
                return JsonResponse({
                    "code": 4100,
                    "message": f"{user['Name']}尚未存入本周课表，请他完成课表上传功能."
                }, status=400)
            
            for j in range(7):
                for k in range(5):
                    if schedule[j][k][0]:
                        scheduletable[j][k][i][0] = user['Name']
                        scheduletable[j][k][i][1] = user['Snumber']

        logger.info("Successfully generated schedule table", extra=log_data)
        return JsonResponse(scheduletable, safe=False, status=200)

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", extra=log_data)
        return JsonResponse({"code": 4004, "message": f"DB Error: {str(e)}"}, status=400)

def GetWeekPostState(request):
    # 获取请求体
    try:
        postbody = request.body
        json_param = json.loads(postbody.decode())
    except:
        error = {
            "code": 4004,
            "message": "Invalid Request"
        }
        return JsonResponse(error, status=400)

    # 获取请求参数
    try:
        account = json_param.get('account')
        token = json_param.get("token")
    except:
        error = {
            "code": 4004,
            "message": "Invalid Parameters"
        }
        return JsonResponse(error, status=400)

    # 验证token
    try:
        if not auth_by_snumber(account, token):
            error = {"code": 4000, "message": "TOKEN Error"}
            return JsonResponse(error, status=400)
    except Exception as e:
        error = {
            "code": 4004,
            "message": f"TOKEN Error: {str(e)}"
        }
        return JsonResponse(error, status=400)

    # 获取用户信息
    try:
        user = User.objects.get(Snumber=account)
    except Exception as e:
        error = {
            "code": 4004,
            "message": f"DB Error: {str(e)}"
        }
        return JsonResponse(error, status=400)

    # 获取CourseSchedule表中该用户的所有记录
    try:
        schedule_list = CourseSchedule.objects.filter(user=user)
    except Exception as e:
        error = {
            "code": 4004,
            "message": f"DB Error: {str(e)}"
        }
        return JsonResponse(error, status=400)

    # 存储所有星期信息的列表
    week_list = []

    # 遍历该用户的所有课表记录
    for schedule in schedule_list:
        # 获取该条记录的星期信息
        try:
            week_number = schedule.week_number
        except:
            error = {
                "code": 4004,
                "message": "DB Error"
            }
            return JsonResponse(error, status=400)

            # 添加到星期列表中
        week_list.append(week_number)

    # 获取所有可能的星期(这里定义为1-20周)
    all_weeks = [i for i in range(1, 21)]

    # 获取还未有课表的星期
    weeks_not_exist = list(set(all_weeks).difference(set(week_list)))

    # 将数据返回给前端
    data = {"weeks_not_exist": weeks_not_exist}
    return JsonResponse(data)

def GetDepartmentMemberInfo(request):
    log_data = {
        'view': 'GetDepartmentMemberInfo',
        'method': request.method,
        'path': request.path,
    }

    # 获取请求体
    try:
        json_param = json.loads(request.body.decode())
        account = json_param.get('account')
        token = json_param.get("token")
        cont = json_param.get("cont")
        log_data.update({'account': account, 'cont': cont})
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body", extra=log_data)
        return JsonResponse({"code": 4004, "message": "Invalid Request"}, status=400)
    except KeyError as e:
        logger.error(f"Missing required parameter: {str(e)}", extra=log_data)
        return JsonResponse({"code": 4004, "message": "Invalid Parameters"}, status=400)

    # 验证token
    try:
        if not auth_by_snumber(account, token):
            logger.warning("Token authentication failed", extra=log_data)
            return JsonResponse({"code": 4000, "message": "TOKEN Error"}, status=400)
    except Exception as e:
        logger.error(f"Token authentication error: {str(e)}", extra=log_data)
        return JsonResponse({"code": 4004, "message": f"TOKEN Error: {str(e)}"}, status=400)

    # 查找用户是否存在
    try:
        Userresult = User.objects.filter(Snumber=account)
        if not Userresult.exists():
            logger.warning("User not found", extra=log_data)
            return JsonResponse({"code": 4001, "message": "Not User"}, status=400)
    except Exception as e:
        logger.error(f"Database error when checking user: {str(e)}", extra=log_data)
        return JsonResponse({"code": 4004, "message": f"DB Error: {str(e)}"}, status=400)

    # 查找共享表是否存在
    try:
        Shareresult = Share.objects.filter(Usernumber_id=account)
        if not Shareresult.exists():
            logger.warning("Share not found for user", extra=log_data)
            return JsonResponse({"code": 4004, "message": "DB Error"}, status=400)
    except Exception as e:
        logger.error(f"Database error when checking share: {str(e)}", extra=log_data)
        return JsonResponse({"code": 4004, "message": "DB Error"}, status=400)

    share_bind_dict = {
        'A': 'BindDepartA',
        'B': 'BindDepartB',
        'C': 'BindDepartC',
        'D': 'BindDepartD'
    }

    # 定位部门记号
    try:
        state_field = share_bind_dict[cont]
    except KeyError:
        logger.error(f"Invalid cont value: {cont}", extra=log_data)
        return JsonResponse({"code": 4001, "message": "CONT ERROR"}, status=400)

    # 查询共享表字段是否已经绑定部门
    try:
        depbind = Share.objects.filter(Usernumber_id=account).values(state_field).first()
        if not depbind or depbind[state_field] is None:
            logger.warning("Department not bound for user", extra=log_data)
            return JsonResponse({"code": 4005, "message": "bind error"}, status=400)
        invitecode = depbind[state_field]
    except Exception as e:
        logger.error(f"Error checking department binding: {str(e)}", extra=log_data)
        return JsonResponse({"code": 4004, "message": "Share State Error"}, status=400)

    try:
        userlist = Share.objects.filter(
            Q(BindDepartA=invitecode) | Q(BindDepartB=invitecode) | 
            Q(BindDepartC=invitecode) | Q(BindDepartD=invitecode)
        ).values_list('Usernumber', flat=True)

        userlist = list(User.objects.filter(Snumber__in=userlist).values('Snumber', 'Name'))
        logger.info(f"Retrieved {len(userlist)} users for department", extra=log_data)
        return JsonResponse(userlist, safe=False)
    except Exception as e:
        logger.error(f"Error retrieving department members: {str(e)}", extra=log_data)
        return JsonResponse({"code": 4004, "message": "DB Error"}, status=400)
#Project 小科通讯录
#Task 同好群查询
def GetLikesInfo(request):
    log_data = {
        'view': 'GetLikesInfo',
        'method': request.method,
        'path': request.path,
    }

    try:
        json_param = json.loads(request.body.decode())
        logger.info("Successfully parsed request body", extra=log_data)
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body", extra=log_data)
        error = {
            "code": 4004,
            "message": "Invalid Request"
        }
        return JsonResponse(error, status=400)

    logger.debug(f"All LikesInfo objects: {serializers.serialize('json', LikesInfo.objects.all())}", extra=log_data)

    page = json_param.get("page")
    like_name = json_param.get('likename')
    log_data.update({'page': page, 'like_name': like_name})

    if like_name is None or page is None:
        logger.warning("Missing required parameters", extra=log_data)
        error = {
            "code": 4009,
            "message": "Begin Data Error"
        }
        return HttpResponse(content=json.dumps(error), content_type='application/json', status=400)

    course_lib = LikesInfo.objects.filter(Groupname__icontains=like_name)
    logger.info(f"Found {course_lib.count()} matching LikesInfo objects", extra=log_data)

    course_lib_json = serializers.serialize('json', course_lib)
    course_lib_list = json.loads(course_lib_json)

    start_index = (page - 1) * 5
    end_index = min(page * 5, len(course_lib_list))

    course_lib_top_5 = []
    for index in range(start_index, end_index):
        current_item = course_lib_list[index]['fields']
        current_item['id'] = course_lib_list[index]['pk']
        course_lib_top_5.append(current_item)

    logger.info(f"Returning {len(course_lib_top_5)} items for page {page}", extra=log_data)
    course_lib_top_5_json = json.dumps(course_lib_top_5)
    return HttpResponse(content=course_lib_top_5_json, content_type='application/json')

def GetSciencesInfo(request):
    log_data = {
        'view': 'GetSciencesInfo',
        'method': request.method,
        'path': request.path,
    }

    try:
        json_param = json.loads(request.body.decode())
        page = json_param.get("page")
        like_name = json_param.get('likename')
        log_data.update({'page': page, 'like_name': like_name})
        logger.info("Received request parameters", extra=log_data)

        if like_name is None or page is None:
            logger.warning("Missing required parameters", extra=log_data)
            error = {
                "code": 4009,
                "message": "Begin Data Error"
            }
            return HttpResponse(content=json.dumps(error), content_type='application/json', status=400)

        course_lib = LikesInfo.objects.filter(Groupname__icontains=like_name)
        logger.info(f"Found {course_lib.count()} matching LikesInfo objects", extra=log_data)

        course_lib_json = serializers.serialize('json', course_lib)
        course_lib_list = json.loads(course_lib_json)

        start_index = (page - 1) * 5
        end_index = min(page * 5, len(course_lib_list))
        
        course_lib_top_5 = []
        for index in range(start_index, end_index):
            current_item = course_lib_list[index]['fields']
            current_item['id'] = course_lib_list[index]['pk']
            course_lib_top_5.append(current_item)

        logger.info(f"Returning {len(course_lib_top_5)} items for page {page}", extra=log_data)
        course_lib_top_5_json = json.dumps(course_lib_top_5)
        return HttpResponse(content=course_lib_top_5_json, content_type='application/json')

    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body", extra=log_data)
        error = {
            "code": 4004,
            "message": "Invalid Request"
        }
        return HttpResponse(content=json.dumps(error), content_type='application/json', status=400)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", extra=log_data)
        error = {
            "code": 5000,
            "message": "Internal Server Error"
        }
        return HttpResponse(content=json.dumps(error), content_type='application/json', status=500)
#Project 教室课表
def GetCRoomlib(request):
    log_data = {
        'view': 'GetCRoomlib',
        'method': request.method,
        'path': request.path,
    }

    try:
        json_param = json.loads(request.body.decode())
        _cont = json_param.get("cont")
        _page = json_param.get("page")
        log_data.update({'cont': _cont, 'page': _page})
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body", extra=log_data)
        return JsonResponse({"code": 4004, "message": "Invalid Request"}, status=400)
    except KeyError as e:
        logger.error(f"Missing required parameter: {str(e)}", extra=log_data)
        return JsonResponse({"code": 4004, "message": "Invalid Parameters"}, status=400)

    try:
        # 返回所有的教室
        Class_ord = CourseTime.objects.all().distinct().values_list("CoursePlace")
        logger.info(f"Retrieved {len(Class_ord)} distinct course places", extra=log_data)

        Class_list = [Class_ord[index][0] for index in range(len(Class_ord))]
        
        Course_lib_json = json.dumps(Class_list)
        logger.info("Successfully created JSON response", extra=log_data)
        
        return HttpResponse(content=Course_lib_json, content_type='application/json')
    except Exception as e:
        logger.error(f"Error processing classroom data: {str(e)}", extra=log_data)
        return JsonResponse({"code": 4004, "message": f"DB Error: {str(e)}"}, status=400)

#小科课程库
def GetCourselib(request):
    log_data = {
        'view': 'GetCourselib',
        'method': request.method,
        'path': request.path,
    }

    # 检查请求类型
    if request.method != 'POST':
        logger.warning("Invalid request method", extra=log_data)
        return JsonResponse({"code": 400, "message": "无效的请求方式"}, status=400)

    # 解析 JSON 参数
    try:
        json_param = json.loads(request.body.decode())
        page = json_param.get("page")
        coursename = json_param.get('coursename')
        teachername = json_param.get('teachername')
        log_data.update({'page': page, 'coursename': coursename, 'teachername': teachername})
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body", extra=log_data)
        return JsonResponse({"code": 4009, "message": "无效的JSON数据"}, status=400)

    # 校验必要的参数
    if page is None or coursename is None or teachername is None:
        logger.warning("Missing required parameters", extra=log_data)
        return JsonResponse({"code": 400, "message": "'cont=0'请求中缺少参数"}, status=400)

    try:
        # 查询课程并生成结果
        courses = Course.objects.filter(CourseName__icontains=coursename, CourseTeacher__icontains=teachername)
        course_list = [{
            "id": course.id,
            "CourseName": course.CourseName,
            "CourseTeacher": course.CourseTeacher,
        } for course in courses[(page - 1) * 10: page * 10]]

        logger.info(f"Retrieved {len(course_list)} courses for page {page}", extra=log_data)
        return JsonResponse({"code": 200, "data": course_list}, status=200)
    except Exception as e:
        logger.error(f"Error retrieving course data: {str(e)}", extra=log_data)
        return JsonResponse({"code": 5000, "message": f"服务器错误: {str(e)}"}, status=500)

def GetLibdetail(request):
    log_data = {
        'view': 'GetLibdetail',
        'method': request.method,
        'path': request.path,
    }

    # 检查请求类型
    if request.method != 'POST':
        logger.warning("Invalid request method", extra=log_data)
        return JsonResponse({"code": 400, "message": "无效的请求方式"}, status=400)

    # 解析 JSON 参数
    try:
        json_param = json.loads(request.body.decode())
        toweek = json_param.get('toweek')
        course_id = json_param.get("id")
        log_data.update({'toweek': toweek, 'course_id': course_id})
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body", extra=log_data)
        return JsonResponse({"code": 4009, "message": "无效的JSON数据"}, status=400)

    # 校验必要的参数
    if not toweek or not course_id or not isinstance(toweek, int):
        logger.warning("Missing or invalid required parameters", extra=log_data)
        return JsonResponse({"code": 400, "message": "Bad Request: Missing required parameters."}, status=400)

    try:
        course = Course.objects.get(id=course_id)
        course_detail = course.coursetime_set.all().values_list('CourseWeek', 'CourseTime', 'CoursePlace')
        log_data['course_name'] = course.CourseName
    except Course.DoesNotExist:
        logger.error("Course not found", extra=log_data)
        return JsonResponse({"code": 4009, "message": "Begin Data Error"}, status=400)

    timetable = [[[[] for j in range(5)] for i in range(5)] for k in range(7)]  # 课程

    for detail in course_detail:
        week_nums = detail[0].split(',')
        time_range = detail[1]
        place = detail[2]

        time_slot = int(time_range[3] + time_range[4])
        time_slot = int(time_slot / 2) - 1  # 节数

        for week_num in week_nums:
            if '-' in week_num:
                start_week, end_week = map(int, week_num.split('-'))
                if start_week <= toweek <= end_week:
                    day = int(time_range[0]) - 1
                    timetable[day][time_slot] = [course.CourseName, place, course.CourseTeacher, detail[0]]
            else:
                if int(week_num) == toweek:
                    day = int(time_range[0]) - 1
                    timetable[day][time_slot] = [course.CourseName, place, course.CourseTeacher, detail[0]]

    logger.info(f"Timetable generated for course {course.CourseName}", extra=log_data)
    return HttpResponse(content=json.dumps(timetable, ensure_ascii=False, indent=2),
                        content_type='application/json')
#Project 小科食物库

import json
import logging
from django.http import JsonResponse
from django.core.cache import cache
from .models import Food
from django.db.models import Max
import gzip

logger = logging.getLogger(__name__)

def GetFoodKind(request):
    log_data = {
        'view': 'GetFoodKind',
        'method': request.method,
        'path': request.path,
    }

    try:
        json_param = json.loads(request.body.decode())
        account = json_param['account']
        token = json_param['token']
        log_data['account'] = account
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Invalid request: {str(e)}", extra=log_data)
        return JsonResponse({"code": 4004, "message": "Invalid Request"}, status=400)

    try:
        if not auth_by_snumber(account, token):
            logger.warning("Token authentication failed", extra=log_data)
            return JsonResponse({"code": 4000, "message": "TOKEN Error"}, status=400)
    except Exception as e:
        logger.error(f"Token authentication error: {str(e)}", extra=log_data)
        return JsonResponse({"code": 4004, "message": f"TOKEN Error: {str(e)}"}, status=400)

    cache_key = 'food_list_data'
    cache_version_key = 'food_list_version'

    try:
        # Check if we need to update the cache
        db_version = Food.objects.aggregate(Max('updated'))['updated__max']
        cached_version = cache.get(cache_version_key)

        if cached_version is None or db_version > cached_version:
            # Data has changed, update cache
            foods = Food.objects.all().values('name', 'kind', 'phone', 'address', 'location__name')
            food_list = [
                {
                    "name": food['name'],
                    "kind": food['kind'],
                    "phone": food['phone'],
                    "address": food['address'],
                    "location": food['location__name']
                }
                for food in foods
            ]
            response = {"foodList": food_list}
            
            # Compress data before caching
            compressed_data = gzip.compress(json.dumps(response).encode('utf-8'))
            
            # Cache the compressed data and update the version
            cache.set(cache_key, compressed_data, None)  # Cache indefinitely
            cache.set(cache_version_key, db_version, None)
            
            logger.info("Food data cache updated", extra=log_data)
        else:
            # Use cached data
            compressed_data = cache.get(cache_key)
            if compressed_data is None:
                raise Exception("Cache miss after version check")
            
            response = json.loads(gzip.decompress(compressed_data).decode('utf-8'))
            logger.info("Served food data from cache", extra=log_data)

        return JsonResponse(response)

    except Exception as e:
        logger.error(f"Error processing food data: {str(e)}", extra=log_data)
        return JsonResponse({"code": 5000, "message": f"Server Error: {str(e)}"}, status=500)
# 静态资源管理
def GetStaticResource(request):
    # 检查请求类型
    if request.method != 'POST':
        return JsonResponse({"code": 400, "message": "无效的请求方式"}, status=400)

    # 解析 JSON 参数
    try:
        json_param = json.loads(request.body.decode())
    except ValueError:
        return JsonResponse({"code": 4009, "message": "无效的JSON数据"}, status=400)

    # 获取并校验必要的参数
    kind = json_param.get('kind')
    if kind is None:
        return JsonResponse({"code": 400, "message": "'kind'请求中缺少参数"}, status=400)
    # 从数据库中找出kind等于输入kind的值并返回其查询所有内容数组
    try:
        static_resource = Static.objects.filter(kind=kind).values()
    except Static.DoesNotExist:
        error = {
            "code": 4009,
            "message": "Begin Data Error"
        }
        return HttpResponse(content=json.dumps(error), content_type='application/json')
    try:
        # 尝试将查询到的数组转换成列表
        static_resource_list = list(static_resource)
    except TypeError:
        error = {
            "code": 4009,
            "message": "查询到的数组转换成列表失败"
        }
        return HttpResponse(content=json.dumps(error), content_type='application/json')

    try:
        # 尝试将列表转换成json格式
        static_resource_json = json.dumps(static_resource_list)
    except json.JSONDecodeError:
        error = {
            "code": 4009,
            "message": "列表转换成json格式"
        }
        return HttpResponse(content=json.dumps(error), content_type='application/json')    # 返回json格式数据
    return HttpResponse(content=static_resource_json, content_type='application/json')















