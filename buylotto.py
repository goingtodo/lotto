import datetime
import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
#DRIVER_PATH = ''
#driver = webdriver.Chrome(executable_path=DRIVER_PATH)

#동행 복권 로그인 창 접속
driver = webdriver.Chrome('/Users/dongminlee/python/chromedriver')

LOTTO_URL = 'https://dhlottery.co.kr/user.do?method=login&returnUrl='
driver.get(LOTTO_URL)

elem_login = driver.find_element_by_id('userId')
elem_login.send_keys('')

elem_pw = driver.find_element_by_name('password')
elem_pw.send_keys('')

LOGIN_PATH = '//*[@id="article"]/div[2]/div/form/div/div[1]/fieldset/div[1]/a'
driver.find_element_by_xpath(LOGIN_PATH).click()

#번호
driver.get('https://el.dhlottery.co.kr/game/TotalGame.jsp?LottoId=LO40')
driver.switch_to.frame('ifrm_tab')

#자동2개
driver.find_element_by_xpath('//*[@id="num2"]').click()
select = Select(driver.find_element_by_xpath('//*[@id="amoundApply"]'))
select.select_by_value('2')
driver.find_element_by_xpath('//*[@id="btnSelectNum"]').click()

driver.find_element_by_xpath('//*[@id="num4"]').click()

#페이지 로딩되는 시간
time.sleep(2)
#수동 3개
driver.find_element_by_xpath('//*[@id="myList"]/li[1]/input').click()
driver.find_element_by_xpath('//*[@id="myList"]/li[2]/input').click() 
driver.find_element_by_xpath('//*[@id="myList"]/li[3]/input').click() 
driver.find_element_by_xpath('//*[@name="btnMyNumber"]').click()


driver.find_element_by_xpath('//*[@id="btnBuy"]').click()

alert = driver.switch_to.alert
now = datetime.datetime.now()
print( now.strftime('%Y-%m-%d %H:%M:%S') + "  "+ alert.text)
alert.accept()
#driver.close()
driver.quit()
