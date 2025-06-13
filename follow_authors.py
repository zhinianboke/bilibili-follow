import os
import glob
import requests
import time
import random
import re
from datetime import datetime

class BilibiliFollower:
    def __init__(self):
        self.session = requests.Session()
        self.follow_api = "https://api.bilibili.com/x/relation/modify"
        # 设置基础请求头
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://space.bilibili.com",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
        }
        
    def login_with_cookies(self, cookie_str):
        """使用Cookie字符串登录"""
        if not cookie_str:
            raise ValueError("Cookie不能为空")
            
        # 设置Cookie
        self.headers["Cookie"] = cookie_str
        
        # 从Cookie中提取CSRF令牌
        csrf_match = re.search(r'bili_jct=([^;]+)', cookie_str)
        if not csrf_match:
            raise ValueError("Cookie中未找到bili_jct (CSRF令牌)")
        self.csrf = csrf_match.group(1)
        
        # 验证登录状态
        try:
            response = self.session.get(
                "https://api.bilibili.com/x/web-interface/nav",
                headers=self.headers
            )
            data = response.json()
            if data["code"] == 0:
                print(f"登录成功！用户名: {data['data']['uname']}")
                return True
            else:
                print(f"登录失败: {data['message']}")
                return False
        except Exception as e:
            print(f"验证登录状态时出错: {str(e)}")
            return False

    def follow_user(self, url):
        """关注指定用户"""
        try:
            # 从URL中提取用户ID
            uid_match = re.search(r'space\.bilibili\.com/(\d+)', url)
            if not uid_match:
                return False, f"无法从URL中提取用户ID: {url}"
            
            uid = uid_match.group(1)
            
            data = {
                "fid": uid,
                "act": 1,  # 1: 关注, 2: 取消关注
                "re_src": 11,  # 关注来源
                "csrf": self.csrf
            }
            
            response = self.session.post(
                self.follow_api,
                data=data,
                headers=self.headers
            )
            
            result = response.json()
            if result["code"] == 0:
                return True, "关注成功"
            else:
                error_messages = {
                    -101: "账号未登录",
                    -102: "账号被封停",
                    -111: "csrf校验失败",
                    -352: "请求频繁",
                    -400: "请求错误",
                    -403: "访问权限不足",
                    22001: "不能关注自己",
                    22003: "用户不存在",
                    22005: "已经关注过该用户",
                    22006: "关注已达上限"
                }
                error_msg = error_messages.get(result["code"], result.get("message", "未知错误"))
                return False, f"关注失败 (错误码: {result['code']}): {error_msg}"
                
        except Exception as e:
            return False, f"关注出错: {str(e)}"

    def process_url_files(self):
        """处理所有merged_unique开头的txt文件"""
        # 获取所有文件
        txt_files = glob.glob('merged_unique*.txt')
        if not txt_files:
            print("未找到任何merged_unique*.txt文件")
            return
        
        # 记录成功和失败的数量
        success_count = 0
        fail_count = 0
        
        # 记录日志
        log_file = f"follow_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        for txt_file in txt_files:
            print(f"\n处理文件: {txt_file}")
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    urls = [line.strip() for line in f if line.strip()]
                
                total_urls = len(urls)
                print(f"找到 {total_urls} 个URL")
                
                for index, url in enumerate(urls, 1):
                    print(f"\n处理第 {index}/{total_urls} 个URL: {url}")
                    
                    # 添加随机延迟（8-20秒）
                    delay = random.uniform(20, 50)
                    print(f"等待 {delay:.1f} 秒...")
                    time.sleep(delay)
                    
                    # 尝试关注用户
                    success, result_msg = self.follow_user(url)
                    if success:
                        success_count += 1
                        # 记录成功的关注
                        with open(log_file, 'a', encoding='utf-8') as log:
                            log.write(f"成功关注: {url}\n")
                    else:
                        fail_count += 1
                        # 记录失败的关注
                        with open(log_file, 'a', encoding='utf-8') as log:
                            log.write(f"关注失败: {url} - {result_msg}\n")
                            
                    # 每关注10个用户后休息一段较长时间，避免风控
                    if index % 10 == 0 and index < total_urls:
                        long_delay = random.uniform(60, 120)
                        print(f"已关注10个用户，休息 {long_delay:.1f} 秒避免风控...")
                        time.sleep(long_delay)
                    
            except Exception as e:
                print(f"处理文件 {txt_file} 时出错: {str(e)}")
                continue
        
        print(f"\n处理完成:")
        print(f"成功关注: {success_count} 个用户")
        print(f"失败: {fail_count} 个用户")
        print(f"详细日志已保存到: {log_file}")

def main():
    follower = BilibiliFollower()
    
    # 请在这里填入你的B站Cookie
    cookie_str = input("请输入你的B站Cookie: ").strip()
    
    if not follower.login_with_cookies(cookie_str):
        print("登录失败，请检查Cookie是否正确")
        return
    
    try:
        follower.process_url_files()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序发生错误: {str(e)}")

if __name__ == "__main__":
    main() 