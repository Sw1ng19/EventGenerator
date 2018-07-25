# -*- coding: utf-8 -*-
# Author: Shiyun Li
# Mail: lishiyun@163.com
# Created Time: Tue Dec 19 18:20:55 2017

import random
import time

class LogEventGen(object):
    def __init__(self):
        self.user_agent_dist = {0.0 : "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0",
                                0.1 : "Mozilla/4.0 (compatible; MSIE6.0; Windows NT 5.0; .NET CLR 1.1.4322)",
                                0.2 : "Mozilla/5.0 (iPhone; CPU iPhone OS 7_0_3 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11B511 Safari/9537.53",
                                0.3 : "Mozilla/5.0 (Linux; Android 4.2.1; Galaxy Nexus Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19",
                                0.4 : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36"}
        self.ip_slice_list = [10,29,30,46,55,63,72,87,98,132,156,124,167,143,187,168,190,201,202,214]
        self.url_path_list = ["login.php","view.php","list.php","upload.php","admin.php","edit.php","index.html"]
        self.http_refer_list = ["http://www.baidu.com/s?wd={query}",
                            "http://www.google.cn/search?q={query}",
                            "http://www.sogou.com/web?query={query}",
                            "http://one.cn.yahoo.com/s?p={query}",
                            "http://cn.bing.com/search?q={query}"]
        self.search_keyword = ["spark","hadoop","hive","spark mlib","spark sql"]                                                      

    def event_ip(self):
        ip_slice = random.sample(self.ip_slice_list, 4)
        # str.join(seq) 将序列中元素以指定的字符连接生成新字符串
        return  ".".join([str(ip) for ip in ip_slice])

    def event_path(self):
        # random.sample(seq, k) 从序列中选取k个随机且独立的数组成新的序列
        return random.sample(self.url_path_list, 1)[0]

    def event_user_agent(self):
        # random.uniform(a, b) 返回 a,b 之间的浮点数
        dist_uppon = random.uniform(0, 0.4)
        return self.user_agent_dist[float('%0.1f' % dist_uppon)]

    def event_refer(self):
        if random.uniform(0, 1) > 0.2:
            return "-"

        refer_str = random.sample(self.http_refer_list, 1)[0]
        query_str = random.sample(self.search_keyword, 1)[0]

        # str.format() 字符串格式化函数
        # print "{}|{}|{}".format(a,b,c)
        # print "{}, {}".format("lishiyun", 29)
        # print "{name}, {age}".format(name="lishiyun", age=29)
        return refer_str.format(query=query_str)

    def web_log(self, count = 3):
        local_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        while count > 1:
            query_log = "{ip} - - [{local_time}] \"GET /{path} HTTP/1.1\" 200 \ {refer} \"{user_agent}\"".format(ip=self.event_ip(),local_time=local_time,path=self.event_path(),refer=self.event_refer(),user_agent=self.event_user_agent())
            print query_log
            count = count - 1

if __name__ == "__main__":
    log = LogEventGen()
    log.web_log(random.uniform(10, 100))