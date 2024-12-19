# -*- coding: utf-8 -*-
import time
import random
from urllib import request, parse
from functools import reduce
from bs4 import BeautifulSoup
import json
import logging

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Query:

    def _getKnowledge(self, question):
        url = 'https://cn.bing.com/search?q={}'.format(parse.quote(question))
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.74',
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'host': 'cn.bing.com'
        }
        req = request.Request(url, headers=headers)
        response = request.urlopen(req)
        content = response.read().decode('utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        knowledge = soup.get_text()
        if('网络不给力，请稍后重试' in knowledge):
            time.sleep(0.5)
            print('怕不是被封了…')
            return None
        return knowledge

    def _preprocessKnowledge(self, knowledge):
        # 去除 HTML 标签和特殊字符
        knowledge = BeautifulSoup(knowledge, 'html.parser').get_text()
        knowledge = ''.join(e for e in knowledge if e.isalnum() or e.isspace())
        return knowledge

    def _query(self, knowledge, answers):
        knowledge = self._preprocessKnowledge(knowledge)

        freq = [knowledge.count(item) + 1 for item in answers]
        rightAnswer = None
        hint = None

        if freq.count(1) == len(answers):
            freqDict = {}
            for item in answers:
                for char in item:
                    if char not in freqDict:
                        freqDict[char] = knowledge.count(char)
            for index in range(len(answers)):
                for char in answers[index]:
                    freq[index] += freqDict[char]
            rightAnswer = answers[freq.index(max(freq))]

            threshold = 50  # 前后 50 字符
            hint = ''.join(knowledge[:threshold].split())
        else:
            rightAnswer = answers[freq.index(max(freq))]
            threshold = 80  # 前后 50 字符
            hintIndex = max(knowledge.find(rightAnswer), threshold)
            hint = ''.join(knowledge[hintIndex - 20:hintIndex + threshold].split())

        total_freq = reduce(lambda a, b: a + b, freq)


        return [f / total_freq for f in freq], rightAnswer, hint


    def run(self, question, answers):
        if not answers:
            return [], None, None
        knowledge = None
        while knowledge is None:
            knowledge = self._getKnowledge(question)
        try:
            freq, rightAnswer, hint = self._query(knowledge, answers)
        except Exception as e:
            logging.error(f'出现异常: {e}')
            freq, rightAnswer, hint = [], None, None
        return freq, rightAnswer, hint


if __name__ == "__main__":
    query = Query()
    question = "Python 是什么"
    answers = ["编程语言", "操作系统", "数据库"]
    freq, rightAnswer, hint = query.run(question, answers)
    print(f'频率分布: {freq}')
    print(f'正确答案: {rightAnswer}')
    print(f'提示: {hint}')