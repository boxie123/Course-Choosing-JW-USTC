# 导入配置信息
from conf import *
from choosing import *

if __name__ == '__main__':
	stu = Student(STUDENTID, TURNID, COOKIE, START_TIME, CONTINUOUSLY)
	stu.chooseCourseMultiThread(COURSE_TO_CHOOSE)