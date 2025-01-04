# course-choosing-jw-ustc

ustc自动选课

适用于在网站`https://jw.ustc.edu.cn/for-std/course-select/{student_id}/turn/{turn_id}/select`选课的同学

这是作者写来自用的库，部分代码参考了[Course-Choosing-SSE-USTC](https://github.com/jianhu-chen/Course-Choosing-SSE-USTC)，如果你发现了本仓库，可以使用，但请勿传播，否则所造成一切后果作者概不负责。

## 使用方法
使用前需先安装`python`，版本 >= 3.8

1. `clone`本仓库
   ```batch
   git clone https://github.com/boxie123/Course-Choosing-JW-USTC.git
   ```
2. 填写环境变量
   - 在`main.py`同级文件夹中新建环境变量文件`.env`，用文本编辑器打开，按照下方示例填写
   ```env
   # 学生id，网址中{student_id}处的数字
   USTCCC_STUDENTID=000000
   # 学期id，网址中{turn_id}处的数字
   USTCCC_TURNID=1042
   # 你的cookie（从选课页面任意网络请求中复制字符串）
   USTCCC_COOKIE=""
   # 要选的课的代码（下方填写的代码仅示例，使用前请更改为你想选的课）
   USTCCC_COURSE_TO_CHOOSE=["MARX6103U.01","MARX6102U.01"]
   # 开始选课时间戳(示例为2025/01/08 15:00:00)
   USTCCC_START_TIME=1736319600
   ```
3. 配置python运行环境并运行
   - 如果已安装[`rye`](https://github.com/astral-sh/rye)：
   ```batch
   rye sync
   rye run python ./main.py
   ```
   - 如果未安装：
   ```batch
   python -m venv .venv
   .venv\Scripts\activate
   pip install httpx jmespath python-dotenv
   python ./main.py
   ```

## 声明
> [!CAUTION]
> 请勿滥用，本项目仅用于学习和测试！请勿滥用，本项目仅用于学习和测试！请勿滥用，本项目仅用于学习和测试！
>
> 本项目遵守 CC-BY-NC 4.0 协议，禁止一切商业使用，造成的一切不良后果与本人无关！ 
