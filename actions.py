
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from rasa_sdk import Action
from rasa_sdk.events import SlotSet
from rasa_sdk.events import UserUtteranceReverted
from rasa_sdk.events import AllSlotsReset
from rasa_sdk.events import Restarted

import requests
import json
import feedparser
import urllib.request
from bs4 import BeautifulSoup
from pyvi import ViTokenizer, ViPosTagger
import numpy as np

def name_cap(text):
    tarr = text.split()
    for idx in range(len(tarr)):
        tarr[idx] = tarr[idx].capitalize()
    return ' '.join(tarr)

class action_save_cust_info(Action):
    def name(self):
        return 'action_save_cust_info'

    def run(self, dispatcher, tracker, domain):
        user_id = (tracker.current_state())["sender_id"]
        print(user_id)
        cust_name = next(tracker.get_latest_entity_values("cust_name"), None)
        cust_sex = next(tracker.get_latest_entity_values("cust_sex"), None)
        bot_position = "SHB"

        if (cust_sex is  None):
            cust_sex = "Quý khách"

        if (cust_sex == "anh") | (cust_sex == "chị"):
           bot_position = "em"
        elif (cust_sex == "cô") | (cust_sex == "chú"):
            bot_position = "cháu"
        else:
            cust_sex = "Quý khách"
            bot_position = "SHB"

        if not cust_name:
            #dispatcher.utter_template("utter_greet_name",tracker)
            return []

        print (name_cap(cust_name))
        return [SlotSet('cust_name', " "+name_cap(cust_name)),SlotSet('cust_sex', name_cap(cust_sex)),SlotSet('bot_position', name_cap(bot_position))]

class action_save_mobile_no(Action):
    def name(self):
        return 'action_save_mobile_no'

    def run(self, dispatcher, tracker, domain):
        user_id = (tracker.current_state())["sender_id"]
        print(user_id)
        mobile_no = next(tracker.get_latest_entity_values("inp_number"), None)

        if not mobile_no:
            return  [UserUtteranceReverted()]

        mobile_no = mobile_no.replace(" ","")
        #print (cust_name)
        return [SlotSet('mobile_no', mobile_no)]



class action_reset_slot(Action):

    def name(self):
        return "action_reset_slot"

    def run(self, dispatcher, tracker, domain):
        return [SlotSet("transfer_nick", None),SlotSet("transfer_amount", None),SlotSet("transfer_amount_unit", None)]
def lay_tt(s):
    dulieu = json.loads(s)
    ten = 'Tên cơ quan: '+ dulieu['tccn_ten']  
    diachi= 'Địa chỉ: '+ dulieu['tccn_diachi'] 
    email= 'Email: '+ dulieu['tccn_email']  
    so_cmnd = 'Số CMND: ' + dulieu['ttcn_socmnd_or_dkkd'] 
    ngay_tn = 'Ngày tiếp nhận: ' + dulieu['ngaytiepnhan'] 
    trang_thai ='Tình trạng xử lý hồ sơ: ' + dulieu['message']
    ngay_tkq= 'Ngày trả kết quả: ' + dulieu['ngaytraketqua']
    ngay_xlx='Ngày xử lý xong: ' + dulieu['ngayxulyxong']
    sdt='Số điện thoại: ' + dulieu['tccn_phone']
    kq = ten + '\n' + diachi +'\n' + email
    if so_cmnd !='0000000000':
        kq = kq + '\n' + so_cmnd
    kq = kq + '\n' +ngay_tn +'\n'+trang_thai+'\n'+ngay_tkq+'\n'+ sdt
    return kq
class action_tra_cuu_hs(Action):
    def name(self):
        # Doan nay khai bao giong het ten ham ben tren la okie
            return 'action_tra_cuu_hs'
    
    def run(self, dispatcher, tracker, domain):
        # Khai bao dia chi luu tru ket qua so xo. O day lam vi du nen minh lay ket qua SX Mien Bac
        ma_hs = next(tracker.get_latest_entity_values("ma_hs"), None)
        ma_hs = ma_hs.replace(" ","")
        print(ma_hs)
        url = 'http://dichvucong.soctrang.gov.vn/api/hoso/tracuuhoso?tukhoa='+ma_hs
        # Tien hanh lay thong tin tu URL
        page = urllib.request.urlopen(url)
        soup = BeautifulSoup(page, 'html.parser')
        s = str(np.copy(str(soup)))
        return_msg = lay_tt(s)
        print(lay_tt(s))
        dispatcher.utter_message(return_msg)
        return []

donvi_cb=''
class action_thong_ke(Action):
    def name(self):
        # Doan nay khai bao giong het ten ham ben tren la okie
        return 'action_thong_ke'
    
    def run(self, dispatcher, tracker, domain):
        global donvi_cb
        donvi_cb =''
        donvi_cb = next(tracker.get_latest_entity_values("don_vi"),None)
        donvi_cb = donvi_cb.lower()
        print(donvi_cb)
        return []
def xuly1(s,s1,s2):
            vt1 = s.find(s1)+len(s1)+2
            vt2 = s.find(s2)-2
            return s[vt1:vt2]

def lay_tttk(s):
    dulieu = json.loads(s)
    tl_thang = round(float(xuly1(s,'tile_daxuly_thang','hs_xldunghan_nam'))*100,2)
    tl_nam =  round(float(xuly1(s,'tile_daxuly_nam' , 'hs_tronghan_thang'))*100,2)
    dunghan_thang = 'Hồ sơ xử lý đúng hạn theo tháng: '+ xuly1(s,'hs_xldunghan_thang','tile_daxuly_thang')
    tile_thang= 'Tỉ lệ đúng hạn theo tháng: '+ str(tl_thang)+'%'
    dunghan_nam= 'Hồ sơ xử lý đúng hạn theo năm: '+ xuly1(s,'hs_xldunghan_nam','hs_tronghan_nam')
    tronghan_nam = 'Hồ sơ xử lý trong hạn theo năm: ' + xuly1(s,'hs_tronghan_nam','hs_xl_trehan_thang')
    trehan_thang = 'Hồ sơ xử lý trễ hạn theo tháng: ' + xuly1(s,'hs_xl_trehan_thang','tile_daxuly_nam')
    tile_nam = 'Tỉ lệ đúng hạn theo năm: ' + str(tl_nam)+'%'
    tronghan_thang ='Hồ sơ xử lý trong hạn theo tháng: ' + xuly1(s,'hs_tronghan_thang', 'hs_moitiepnhan_thang')
    moi_thang ='Hồ sơ mới tiếp nhận theo tháng: ' + xuly1(s,'hs_moitiepnhan_thang', 'hs_moitiepnhan_nam')
    moi_nam ='Hồ sơ mới tiếp nhận theo năm: ' + xuly1(s,'hs_moitiepnhan_nam', 'hs_xl_trehan_nam')
    trehan_nam='Hồ sơ xử lý trễ hạn năm: ' + s[s.rfind(':')+1:len(s)-1]
    kq_thang = moi_thang + '\n' + dunghan_thang + '\n' + tronghan_thang + '\n' + trehan_thang + '\n'+ tile_thang
    kq_nam = moi_nam + '\n' + dunghan_nam + '\n' + tronghan_nam + '\n' + trehan_nam + '\n'+ tile_nam
    kq = kq_thang + '\n' + kq_nam
    return kq
            
class action_thong_ke_thangnam(Action):
    def name(self):
        # Doan nay khai bao giong het ten ham ben tren la okie
            return 'action_thong_ke_thangnam'
    
    def run(self, dispatcher, tracker, domain):
        # Khai bao dia chi luu tru ket qua so xo. O day lam vi du nen minh lay ket qua SX Mien Bac
        thang = next(tracker.get_latest_entity_values("thang_tk"), None)
        thang = thang.replace(" ","")
        nam = next(tracker.get_latest_entity_values("nam_tk"), None)
        nam = nam.replace(" ","")
        print(donvi_cb,' ',thang,' ',nam)
        with open('donvi.json') as file_write:
            d = json.load(file_write)
        domain = d[donvi_cb]
        print(domain,' ',thang,' ',nam)
        url = 'http://dichvucong.soctrang.gov.vn/api/hoso/tkttxlhs?domain='+domain+'&thang='+thang+'&nam='+nam
        # Tien hanh lay thong tin tu URL
        page = urllib.request.urlopen(url)
        soup = BeautifulSoup(page, 'html.parser')
        s = str(np.copy(str(soup)))
        return_msg = lay_tttk(s)
        print(return_msg)
        dispatcher.utter_message(return_msg)
        return []

class action_thong_ke_full(Action):
    def name(self):
        # Doan nay khai bao giong het ten ham ben tren la okie
            return 'action_thong_ke_full'
    
    def run(self, dispatcher, tracker, domain):
        # Khai bao dia chi luu tru ket qua so xo. O day lam vi du nen minh lay ket qua SX Mien Bac
        thang = next(tracker.get_latest_entity_values("thang_tk"), None)
        thang = thang.replace(" ","")
        nam = next(tracker.get_latest_entity_values("nam_tk"), None)
        nam = nam.replace(" ","")
        donvi_cb = next(tracker.get_latest_entity_values("don_vi"),None)
        donvi_cb = donvi_cb.lower()
        with open('donvi.json') as file_write:
            d = json.load(file_write)
        domain = d[donvi_cb]
        print(domain,' ',thang,' ',nam)
        url = 'http://dichvucong.soctrang.gov.vn/api/hoso/tkttxlhs?domain='+domain+'&thang='+thang+'&nam='+nam
        # Tien hanh lay thong tin tu URL
        page = urllib.request.urlopen(url)
        soup = BeautifulSoup(page, 'html.parser')
        s = str(np.copy(str(soup)))
        return_msg = lay_tttk(s)
        print(return_msg)
        dispatcher.utter_message(return_msg)
        return []

class action_tra_cuu_diachi(Action):
    def name(self):
        # Doan nay khai bao giong het ten ham ben tren la okie
            return 'action_tra_cuu_diachi'
    
    def run(self, dispatcher, tracker, domain):
        # Khai bao dia chi luu tru ket qua so xo. O day lam vi du nen minh lay ket qua SX Mien Bac
        donvi_cb = next(tracker.get_latest_entity_values("don_vi"),None)
        donvi_cb = donvi_cb.lower()
        with open('diachi.json') as file_write:
            d = json.load(file_write)
        diachi = d[donvi_cb]
        print(diachi)
        dispatcher.utter_message(diachi)
        return []
