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
        
        # 1. 计算基础频率和相关性分数
        scores = []
        for answer in answers:
            score = {
                'text': answer,
                'freq': knowledge.count(answer),  # 完整匹配频率
                'char_freq': sum(knowledge.count(char) for char in answer),  # 字符匹配频率
                'context_score': 0  # 上下文相关性分数
            }
            
            # 2. 分析上下文相关性
            answer_pos = knowledge.find(answer)
            if answer_pos != -1:
                context = knowledge[max(0, answer_pos-50):min(len(knowledge), answer_pos+50)]
                # 检查上下文中是否包含一些关键词标识
                context_keywords = ['是', '对', '正确', '表示', '意味着', '说明']
                score['context_score'] += sum(1 for keyword in context_keywords if keyword in context)
                
                # 检查否定词
                negative_keywords = ['不是', '错误', '并非', '相反']
                score['context_score'] -= sum(2 for keyword in negative_keywords if keyword in context)
            
            # 3. 计算最终得分
            final_score = (
                score['freq'] * 3 +  # 完整匹配权重最高
                score['char_freq'] * 1 +  # 字符匹配作为补充
                score['context_score'] * 2  # 上下文相关性
            )
            scores.append((final_score, answer))
        
        # 4. 选择得分最高的答案
        scores.sort(reverse=True)
        right_answer = scores[0][1]
        
        # 5. 生成置信度
        total_score = sum(score[0] for score in scores) or 1
        confidence = [score[0]/total_score for score, _ in scores]
        
        # 6. 生成提示信息
        answer_pos = knowledge.find(right_answer)
        if answer_pos != -1:
            context_start = max(0, answer_pos-30)
            context_end = min(len(knowledge), answer_pos+50)
            hint = f"...{knowledge[context_start:context_end]}..."
        else:
            hint = "未找到直接相关上下文"

        return confidence, right_answer, hint


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