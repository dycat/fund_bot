import json

import tushare as ts


def main():
    fund_name = read_json('fund_name.json')
    fund_code = [k for k,v in fund_name.items()]
    fund_data = get_fund_data(fund_code)
    fund_cleaned = comput_fund_to_info(fund_data,fund_name)
    buying_point = ma_rule(fund_cleaned)
    if buying_point != None:
        print(make_messege(buying_point))
    else:
        print("无买入点")


class Fund:
    def __init__(self,code):
        self.name:str = ''
        self.code:str = code
        self.current_price:float = 0.0
        self.ma_365:float  = 0.0
        self.ma_180:float = 0.0
        self.ma_60:float = 0.0
        self.price_to_ma365:float = 0.0
        self.price_to_ma180:float = 0.0
        self.price_to_ma60:float = 0.0

    def __str__(self):
        if self.name != None:
            return self.name + ' ' + self.code
        else:
            return self.code

def read_json(file_path):
	with open(file_path,'r',encoding='utf-8') as f:
		dic = json.load(f)
		return dic

def calculate_ma(fund_dataframe,days):
    fund_df_new = fund_dataframe.sort_index()
    return fund_df_new['close'].rolling(days).mean()[-1]


def compare_to_ma(current_price,ma):
    return current_price / ma - 1

def get_fund_data(fund_code_list):
    return {code:ts.get_hist_data(code) for code in fund_code_list}

def comput_fund_to_info(fund_data,fund_name):
    fund_dict = {}
    for fund in fund_data:
        fund_class = Fund(fund)
        fund_class.name = fund_name.get(fund)
        fund_class.current_price = fund_data[fund]['close'][0]
        fund_class.ma_365 = calculate_ma(fund_data[fund],365)
        fund_class.ma_180 = calculate_ma(fund_data[fund], 180)
        fund_class.ma_60 = calculate_ma(fund_data[fund], 60)
        fund_class.price_to_ma365 =  compare_to_ma(fund_class.current_price,fund_class.ma_365)
        fund_class.price_to_ma180 =  compare_to_ma(fund_class.current_price,fund_class.ma_180)
        fund_class.price_to_ma60  =  compare_to_ma(fund_class.current_price,fund_class.ma_60)
        fund_dict[fund] = fund_class
    return  fund_dict


def ma_rule(fund_cleaned):
    to_be_info = {}
    for k,v in fund_cleaned.items():
        if v.price_to_ma365 < -0.03 or v.price_to_ma180 < -0.05 or v.price_to_ma60 < -0.08:
            to_be_info[k] = v
    if to_be_info != {}:
        return to_be_info
    else:
        return None

def make_messege(buying_point):
    text = ''
    num = 1
    for key,fund in buying_point.items():
        text += f"{str(num)}. {fund.code} {fund.name},相比365日均线： {fund.price_to_ma365:.4f}，相比180日均线： {fund.price_to_ma180:.4f}，相比60日均线 {fund.price_to_ma60:.4f}。\n"
        num += 1
    return text


main()