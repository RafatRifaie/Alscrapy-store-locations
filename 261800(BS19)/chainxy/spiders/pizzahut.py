from __future__ import unicode_literals
import scrapy
import json
import os
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from chainxy.items import ChainItem
from lxml import etree
from selenium import webdriver
from lxml import html
import usaddress
import pdb

class pizzahut(scrapy.Spider):
	name = 'pizzahut'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.pizzahut.com/api.php/site/api_ajax/search/carryout'
		payload = {"customer_postal_code":"90001","limit":"9"}
		header = {
			":authority":"www.pizzahut.com",
			":method":"POST",
			":path":"/api.php/site/api_ajax/search/carryout",
			":scheme":"https",
			"accept":"application/json, text/plain, */*",
			"accept-encoding":"gzip, deflate, br",
			"content-type":"application/json;charset=UTF-8",
		}
		# yield scrapy.Request(url=init_url, headers=header, body=json.dumps(payload), method='post', callback=self.body) 
		yield scrapy.Request(url='https://www.pizzahut.com/api.php/site/api_ajax/stores/getCustomDimensions', callback=self.body)

	def body(self, response):
		print("=========  Checking.......", response.body)
		with open('response.html', 'wb') as f:
			f.write(response.body)

		# store_list = json.loads(response.body)
		# for store in store_list:
		# 	try:
		# 		item = ChainItem()
		# 		detail = self.eliminate_space(store.xpath())
		# 		item['store_name'] = self.validate(store['name'])
		# 		item['store_number'] = self.validate(store['store_number'])
		# 		item['address'] = self.validate(store['address'])
		# 		item['address2'] = self.validate(store['address2'])
				
		# 		address = ''
		# 		item['address'] = ''
		# 		item['city'] = ''
		# 		addr = usaddress.parse(address)
		# 		for temp in addr:
		# 			if temp[1] == 'PlaceName':
		# 				item['city'] += temp[0].replace(',','')	+ ' '
		# 			elif temp[1] == 'StateName':
		# 				item['state'] = temp[0].replace(',','')
		# 			elif temp[1] == 'ZipCode':
		# 				item['zip_code'] = temp[0].replace(',','')
		# 			else:
		# 				item['address'] += temp[0].replace(',', '') + ' '

		# 		address = ''
		# 		addr = address.split(',')
		# 		item['city'] = self.validate(addr[0].strip())
		# 		item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
		# 		item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())

		# 		item['city'] = self.validate(store['city'])
		# 		item['state'] = self.validate(store['state'])
		# 		item['zip_code'] = self.validate(store['zip'])
		# 		item['country'] = self.validate(store['country'])
		# 		item['phone_number'] = self.validate(store['phone'])
		# 		item['latitude'] = self.validate(store['latitude'])
		# 		item['longitude'] = self.validate(store['longitude'])

		# 		h_temp = ''
		# 		hour_list = self.eliminate_space(response.xpath('//text()').extract())
		# 		cnt = 1
		# 		for hour in hour_list:
		# 			h_temp += hour
		# 			if cnt % 2 == 0:
		# 				h_temp += ', '
		# 			else:
		# 				h_temp += ' '
		# 			cnt += 1
		# 		item['store_hours'] = h_temp[:-2]

		# 		item['store_hours'] = self.validate(store['hours'])
		# 		item['store_type'] = ''
		# 		item['other_fields'] = ''
		# 		item['coming_soon'] = ''
		# 		if item['address']+item['phone_number'] not in self.history:
		# 			self.history.append(item['address']+item['phone_number'])
		# 			yield item	
		# 	except:
		# 		pdb.set_trace()		

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp

	def str_concat(self, items, unit):
		tmp = ''
		for item in items[:-1]:
			if self.validate(item) != '':
				tmp += self.validate(item) + unit
		tmp += self.validate(items[-1])
		return tmp

	def check_country(self, item):
		for state in self.US_CA_States_list:
			if item.lower() in state['abbreviation'].lower():
				return state['country']
		return ''

	def get_state(self, item):
		for state in self.US_States_list:
			if item.lower() in state['name'].lower():
				return state['abbreviation']
		return ''

	def format(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''

	def fixLazyJson (self, in_text):
		tokengen = tokenize.generate_tokens(StringIO(in_text).readline)
		result = []
		for tokid, tokval, _, _, _ in tokengen:
			if (tokid == token.NAME):
				if tokval not in ['true', 'false', 'null', '-Infinity', 'Infinity', 'NaN']:
					tokid = token.STRING
					tokval = u'"%s"' % tokval
			elif (tokid == token.STRING):
				if tokval.startswith ("'"):
					tokval = u'"%s"' % tokval[1:-1].replace ('"', '\\"')
			elif (tokid == token.OP) and ((tokval == '}') or (tokval == ']')):
				if (len(result) > 0) and (result[-1][1] == ','):
					result.pop()			
			elif (tokid == token.STRING):
				if tokval.startswith ("'"):
					tokval = u'"%s"' % tokval[1:-1].replace ('"', '\\"')
			result.append((tokid, tokval))

		return tokenize.untokenize(result)
