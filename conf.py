import os
import ast
from dotenv import load_dotenv

# 加载环境文件中的环境变量
load_dotenv('.env')

# 使用os模块访问环境变量
# 学生id
STUDENTID = ast.literal_eval(os.environ.get('USTCCC_STUDENTID'))
# 学期id
TURNID = ast.literal_eval(os.environ.get('USTCCC_TURNID'))
# cookie
COOKIE = os.environ.get('USTCCC_COOKIE')
# 要选的课
COURSE_TO_CHOOSE = ast.literal_eval(os.environ.get('USTCCC_COURSE_TO_CHOOSE'))
# 开始选课时间戳(2025/01/08 15:00:00)
START_TIME = ast.literal_eval(os.environ.get('USTCCC_START_TIME'))