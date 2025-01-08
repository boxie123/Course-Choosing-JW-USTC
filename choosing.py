import os
import json
import httpx
import time
import random
import threading # 多线程
from urllib import parse

import jmespath


class Student:
	def __init__(self, studentID, turnID, cookie, start_time, continuously):
		'''
			作用：初始化用户信息
		'''
		self.studentID = studentID
		self.turnID = turnID
		self.cookie = cookie
		self.start_time = start_time
		self.count = 0
		self.continuously = bool(continuously)
		self.filename = f"AddableCourse_{studentID}.json"
        # 构建一个Session对象，可以保存页面Cookie
		self.sess = httpx.Client(headers={
			'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
			"Cookie": cookie,
			"Content-Type":"application/x-www-form-urlencoded",
        })


	def getStuChoosedHtml(self):
		'''
			作用：获取已选课程
			返回：已选课程
		'''
		self.writeLogs('正在查询您的已选课程，请稍候...')
		# 用已有登录状态的Cookie发送请求，获取目标页面源码
		params = {
			"studentId": self.studentID,
            "turnId": self.turnID,
        }
		stuChoosedUrl = 'https://jw.ustc.edu.cn/ws/for-std/course-select/selected-lessons'
		response = self.sess.post(stuChoosedUrl, data=parse.urlencode(params))
		try:
			stuChoosedJSON = response.json()
		except json.decoder.JSONDecodeError:
			self.writeLogs("获取列表失败，请检查Cookie是否过期")
			raise
		return stuChoosedJSON

	def getAddableCourseList(self):
		'''
			获取可选列表
		'''
		# 发送请求
		stuChooseListUrl = 'https://jw.ustc.edu.cn/ws/for-std/course-select/addable-lessons'
		params = {
			"studentId": self.studentID,
            "turnId": self.turnID,
        }
		response = self.sess.post(stuChooseListUrl, data=parse.urlencode(params))
		response.encoding = "UTF-8"
		stuChooseListJSON = response.json()
		
		with open(self.filename, 'w', encoding="utf-8") as f:
			json.dump(stuChooseListJSON, f, ensure_ascii=False, indent=2)
		return stuChooseListJSON

	def getCourseStatusJSON(self):
		'''
			作用：从文件读取【可选列表】
		'''
		# 如果已有，不再重复爬取
		if os.path.exists(self.filename):
			with open(self.filename, 'r', encoding="utf-8") as f:
				data = json.load(f)
			return data
		else:
			self.writeLogs("文件不存在")
			raise
	
	def getCourseID(self, courseCode):
		'''
			作用：打印某门课的状态
			courseCode ：课程Code
			返回：课程id
		'''
		self.writeLogs('正在查询课程【{}】状态...'.format(courseCode))
		courseStatusJSON = self.getCourseStatusJSON()
		coursejson = jmespath.search(f'[?code==`{courseCode}`]', courseStatusJSON)
		if len(coursejson) == 1:
			self.writeLogs(f'课程名称为：{coursejson[0]["course"]["nameZh"]}')
			return coursejson[0]["id"]
		else:
			self.writeLogs("错误，未找到此可选课程")
			raise

	def chooseCourse(self, index, courseCode):
		'''
			作用：抢某门课
		'''
		courseID = self.getCourseID(courseCode)
		chooseCouserUrl = 'https://jw.ustc.edu.cn/ws/for-std/course-select/add-request'
		dropRespUrl = "https://jw.ustc.edu.cn/ws/for-std/course-select/add-drop-response"
		params = {
			"studentAssoc": self.studentID,
            "courseSelectTurnAssoc": self.turnID,
			"lessonAssoc": courseID,
			"scheduleGroupAssoc": "",
			"virtualCost": 0,
        }

		# 线程抢课
		while True:
			self.count += 1
			# 发送抢课需要的POST数据，获取登录后的Cookie(保存在sess里)
			response = self.sess.post(chooseCouserUrl, data=parse.urlencode(params))
			try:
				req_id = response.text
				# 一个元祖，里面包含该课程的 已选人数/最大人数
				self.writeLogs(f"获取到请求id：{req_id}")
			except:
				self.writeLogs('线程{}：正在抢课【{}】\t结果：未搜索到课程【{}】，请检查：课程名是否正确/或该课程已在您的选课列表中...'.format(index, courseID, courseID), error=True)					
				self.writeLogs('线程{}：关闭...'.format(index))
				break
			else:
				params2 = {
                    "studentId": self.studentID,
                    "requestId": req_id,
                }
				resp2 = self.sess.post(dropRespUrl, data=parse.urlencode(params2))
				try:
					result = resp2.json()
					self.writeLogs('线程{}：正在抢课【{}】'.format(index, courseCode))
					is_succ = result["success"]
				except:
					self.writeLogs('线程{}：抢课【{}】时发生错误...错误信息：{}，请检查cookie是否过期'.format(index, courseCode, result))
					continue
				# 选课成功，关闭线程
				if is_succ:
					self.writeLogs('线程{}：选课成功...'.format(index))
					self.writeLogs('线程{}：关闭...'.format(index))
					break# 关闭该线程
				# 满了，继续抢
				elif self.count >= 100 and (not self.continuously):
					self.writeLogs('线程{}：已达最大尝试次数，关闭'.format(index))
					break
				else:
					self.writeLogs('线程{}：抢课【{}】时发生错误...错误信息：{}'.format(index, courseCode, result))
					self.writeLogs('线程{}：重试中'.format(index))
					threadSleepTime = random.uniform(0.1, 0.3)
					self.writeLogs('线程{}：防止被发现，休息{:.2f}秒...'.format(index, threadSleepTime))
					time.sleep(threadSleepTime) # 休息一会儿

	def chooseCourseMultiThread(self, wantedCourseList):
		'''多线程抢课'''
		courseNum = len(wantedCourseList)
		self.writeLogs('共检测到{}个任务，正在分配线程处理...'.format(courseNum))
		if courseNum < 1:
			raise
		self.getAddableCourseList()
		self.wait_local_timer()
		for i, courseCode in enumerate(wantedCourseList):
			thread = threading.Thread(target=self.chooseCourse, args=(i, courseCode))
			thread.daemon = False # 这个线程是重要的，在进程退出的时候，等待这个线程退出
			thread.start()

	def wait_local_timer(self):
		start_time = self.start_time
		local_time = time.time()
		timeArray = time.localtime(start_time)
		FormatLocalTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
		self.writeLogs(f'预计开始选课时间为：{FormatLocalTime}')

		while start_time > local_time:
			print('\r当前本地时间: %f' % local_time, end="")
			time.sleep(0.1)  # pause for 100 milliseconds
			local_time = time.time()

	def writeLogs(self, log, isPrint=True, info=True, error=False):
		if error:
			log = '[ERROR] ' + log
		elif info:
			log = '[INFO] ' + log
		else: 
			pass
		if isPrint:
			print(log)
		with open('runtime.logs', 'a') as f:
			f.write('['+time.ctime()+']\n'+log+'\n\n')
