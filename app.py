from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
import threading
from follow_authors import BilibiliFollower
import time
import os
import random

app = Flask(__name__)
CORS(app)

# 存储任务状态
task_status = {
    'is_running': False,
    'total_users': 0,
    'current_count': 0,
    'success_count': 0,
    'fail_count': 0,
    'current_user': '',
    'waiting_time': 0,
    'log_messages': []
}

def add_log_message(message):
    task_status['log_messages'].append(message)
    if len(task_status['log_messages']) > 100:  # 保持最新的100条日志
        task_status['log_messages'].pop(0)

def follow_task(cookie_str):
    global task_status
    task_status['is_running'] = True
    task_status['log_messages'] = []
    
    try:
        follower = BilibiliFollower()
        if not follower.login_with_cookies(cookie_str):
            add_log_message("登录失败，请检查Cookie是否正确")
            task_status['is_running'] = False
            return

        # 获取所有merged_unique开头的txt文件
        txt_files = [f for f in os.listdir('.') if f.startswith('merged_unique') and f.endswith('.txt')]
        if not txt_files:
            add_log_message("未找到任何merged_unique*.txt文件")
            task_status['is_running'] = False
            return

        total_users = 0
        for txt_file in txt_files:
            with open(txt_file, 'r', encoding='utf-8') as f:
                total_users += len([line for line in f if line.strip()])
        
        task_status['total_users'] = total_users
        task_status['current_count'] = 0
        task_status['success_count'] = 0
        task_status['fail_count'] = 0

        for txt_file in txt_files:
            add_log_message(f"开始处理文件: {txt_file}")
            with open(txt_file, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]

            for url in urls:
                if not task_status['is_running']:  # 检查是否应该停止
                    add_log_message("任务已手动停止")
                    return

                task_status['current_user'] = url
                task_status['current_count'] += 1
                add_log_message(f"正在处理: {url}")

                try:
                    success, result_msg = follower.follow_user(url)
                    if success:
                        task_status['success_count'] += 1
                        add_log_message(f"✅ 成功关注: {url}")
                    else:
                        task_status['fail_count'] += 1
                        # 检查是否是-352错误
                        if "错误码: -352" in result_msg:
                            add_log_message(f"❌ 请求频繁，需要等待")
                        else:
                            add_log_message(f"❌ {result_msg}")
                except Exception as e:
                    task_status['fail_count'] += 1
                    add_log_message(f"❌ 处理出错: {str(e)}")

                # 随机延迟(8-20秒)
                delay = random.uniform(8, 20)
                task_status['waiting_time'] = round(delay, 1)
                add_log_message(f"等待 {delay:.1f} 秒...")
                
                # 模拟倒计时的开始时间
                start_time = time.time()
                
                # 使用分段睡眠，以便能够响应停止请求
                while time.time() - start_time < delay:
                    if not task_status['is_running']:  # 如果任务被停止了，提前退出
                        break
                    # 更新剩余等待时间
                    remaining = delay - (time.time() - start_time)
                    if remaining > 0:
                        task_status['waiting_time'] = round(remaining, 1)
                    time.sleep(0.1)  # 小段睡眠，允许快速响应停止请求
                
                # 重置等待时间
                task_status['waiting_time'] = 0
                
                # 每关注10个用户后休息一段较长时间，避免风控
                if task_status['current_count'] % 10 == 0 and task_status['current_count'] < task_status['total_users']:
                    long_delay = random.uniform(60, 120)
                    task_status['waiting_time'] = round(long_delay, 1)
                    add_log_message(f"已关注10个用户，休息 {long_delay:.1f} 秒避免风控...")
                    
                    # 模拟倒计时的开始时间
                    start_time = time.time()
                    
                    # 使用分段睡眠，以便能够响应停止请求
                    while time.time() - start_time < long_delay:
                        if not task_status['is_running']:  # 如果任务被停止了，提前退出
                            break
                        # 更新剩余等待时间
                        remaining = long_delay - (time.time() - start_time)
                        if remaining > 0:
                            task_status['waiting_time'] = round(remaining, 1)
                        time.sleep(0.1)  # 小段睡眠，允许快速响应停止请求
                    
                    # 重置等待时间
                    task_status['waiting_time'] = 0

    except Exception as e:
        add_log_message(f"任务执行出错: {str(e)}")
    finally:
        task_status['is_running'] = False
        add_log_message("任务完成")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_follow', methods=['POST'])
def start_follow():
    if task_status['is_running']:
        return jsonify({'status': 'error', 'message': '任务已在运行中'})
    
    cookie = request.form.get('cookie', '').strip()
    if not cookie:
        return jsonify({'status': 'error', 'message': '请输入Cookie'})
    
    # 在新线程中启动关注任务
    thread = threading.Thread(target=follow_task, args=(cookie,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'status': 'success', 'message': '任务已启动'})

@app.route('/stop_follow', methods=['POST'])
def stop_follow():
    task_status['is_running'] = False
    return jsonify({'status': 'success', 'message': '正在停止任务'})

@app.route('/status')
def get_status():
    return jsonify(task_status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 