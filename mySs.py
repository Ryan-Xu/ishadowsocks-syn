#-*- coding: utf-8 -*-
#!/usr/bin/env python
import urllib2
import re
import json
import zlib
import subprocess
import time
#import msvcrt
#import socks
#import socket



class GatherConfig:
	def __init__(self, baseurl, headers):
		self.baseurl = baseurl
		self.headers = headers

	def gatherJson(self):
		try:
			#socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 6999)
			#socket.socket = socks.socksocket

			req = urllib2.Request(self.baseurl, headers = self.headers)
			res = urllib2.urlopen(req)
			pagedata = res.read()
			if res.info().get("Content-Encoding") == "gzip":
				pagedata = zlib.decompress(pagedata, 16 + zlib.MAX_WBITS)

		except urllib2.URLError, e:
			if hasattr(e, "code"):
				print e.code
			if hasattr(e, "reason"):
				print e.reason

		pattern = r'''<div class="col-lg-4 text-center">
                    .*?<h4>.*?服务器地址:([.\w]+)</h4>
                    .*?<h4>端口:(\d+)</h4>
.*?<h4>.*?密码:(\d+)</h4>
                    .*?<h4>加密方式:(.+)</h4>
                    .*?<h4>状态:<font color="green">(.+)</font></h4>
                    .*?<h4><font color="red">注意：每6小时更换一次密码</font></h4>
                </div>'''
		items = re.findall(pattern, pagedata)
		if not items:
			print '获取配置信息错误！'
			return None
		else:
			subconfig = []
			for item in items:
				config =   {
					"server" : unicode(item[0]),
					"server_port" : unicode(item[1]),
					"password" : unicode(item[2]),
					"method" : unicode(item[3]),
					"remarks" : unicode(item[0])}
				subconfig.append(config)


			global_configs = {
				"configs" : subconfig,
				"index" : 1,
				"global" : False,
				"enabled" : True,
				"shareOverLan" : False,
				"isDefault" : False,
				"localPort" : 1080,
				"pacUrl" : None,
				"useOnlinePac" : False}

		return global_configs


# 更新本地配置文件
class FlushConfig:
	def __init__(self, cfgfile):
		self.cfgfile = cfgfile

	def flushConfig(self, cfginfo):
		with open(self.cfgfile, 'w') as f:
			json.dump(cfginfo, f, sort_keys=True,
                    indent=4, separators=(',', ':'))


# 启动shadowsocks客户端
class StartShadowsocksClient:
	def __init__(self, procname):
		self.proc = procname

	def start(self):
		start = time.time()
		subprocess.Popen(self.proc)
		print 'Shadowsocks running time:%s' % (time.time() - start)
		#msvcrt.getch()


if __name__ == '__main__':
	# 从http://www.ishadowsocks.com/获取配置信息
	ishadowsocks_url = 'http://www.ishadowsocks.com/'
	headers = {
	'Host':'www.ishadowsocks.com', 'Connection':'keep-alive',
	'Cache-Control':'max-age=0', 'Accept': 'text/html, */*; q=0.01',
	'X-Requested-With': 'XMLHttpRequest',
	'User-Agent': 'Mozilla/5.0 (X11;Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36',
	'DNT':'1', 'Referer':
	'http://www.ishadowsocks.com', 'Accept-Encoding': 'gzip, deflate,sdch', 'Accept-Language': 'zh-CN,zh;q=0.8,ja;q=0.6'
	}

	gc = GatherConfig(ishadowsocks_url, headers)
	sjson = gc.gatherJson()

	fc = FlushConfig("gui-config.json")
	fc.flushConfig(sjson)

	ssc = StartShadowsocksClient("Shadowsocks.exe");
	ssc.start()


