import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException

# --- 설정 ---
LOTTO_URL = 'https://www.dhlottery.co.kr/login'
USER_ID = 'ddma13'       # ← 실제 아이디 입력
USER_PW = 'gurwoek13!' # ← 실제 비밀번호 입력

driver = webdriver.Chrome()
driver.maximize_window() # 창을 최대화해야 요소가 잘 클릭됩니다.
wait = WebDriverWait(driver, 15)

try:
    # 1. 로그인 프로세스
    driver.get(LOTTO_URL)
    wait.until(EC.presence_of_element_located((By.ID, 'inpUserId'))).send_keys(USER_ID)
    wait.until(EC.presence_of_element_located((By.ID, 'inpUserPswdEncn'))).send_keys(USER_PW)
    wait.until(EC.element_to_be_clickable((By.ID, 'btnLogin'))).click()

    # 로그인 성공 확인 (로그아웃 버튼 등장 대기)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'btn-logIn')))
    print("✅ 로그인 성공")

    # 2. 구매 페이지 이동 및 프레임 진입
    driver.get('https://ol.dhlottery.co.kr/olotto/game/game645.do')
    
    # 페이지 안정화를 위한 대기
    time.sleep(3) 
    
    # [중요] iframe 내부로 진입해야 모든 버튼 조작이 가능합니다.
    # wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'ifrm_tab')))
    print("✅ iframe(구매창) 진입 성공")

    # 3. 자동번호 2개 선택
    # '자동번호발급' 라디오 버튼 클릭
    auto_radio = wait.until(EC.element_to_be_clickable((By.ID, "num2")))
    driver.execute_script("arguments[0].click();", auto_radio)
    
    # 수량 선택 (2개)
    amt_select = Select(wait.until(EC.presence_of_element_located((By.ID, "amoundApply"))))
    amt_select.select_by_value('2')
    
    # '확인' 버튼 클릭 (선택 목록에 추가)
    driver.find_element(By.ID, "btnSelectNum").click()
    print("✅ 자동 2개 선택 완료")

    # 4. 수동(나의 번호) 3개 선택
    # '나의 번호' 탭 클릭
    wait.until(EC.element_to_be_clickable((By.ID, "num4"))).click()
    
    # 번호 리스트 로드 대기 후 1~3번째 번호 체크
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="myList"]/li[1]/input')))
    for i in range(1, 4):
        checkbox = driver.find_element(By.XPATH, f'//*[@id="myList"]/li[{i}]/input')
        driver.execute_script("arguments[0].click();", checkbox)
    
    # '확인' 버튼 클릭 (선택 목록에 추가)
    driver.find_element(By.NAME, "btnMyNumber").click()
    print("✅ 나의 번호 3개 적용 완료")

    # 5. 최종 구매하기 버튼 클릭
    buy_btn = wait.until(EC.element_to_be_clickable((By.ID, "btnBuy")))
    buy_btn.click()
    print("🚀 구매 버튼 클릭! 최종 팝업 처리 중...")

    # 6. "구매하시겠습니까?" 레이어 팝업 처리
    # 팝업이 나타날 때까지 대기
    wait.until(EC.visibility_of_element_located((By.ID, "popupLayerConfirm")))
    
    # 팝업 내 '확인' 버튼을 특정하여 클릭 (JavaScript 방식이 가장 확실)
    # XPath: ID가 popupLayerConfirm인 div 내부의 '확인' 버튼
    confirm_xpath = "//div[@id='popupLayerConfirm']//input[@value='확인']"
    confirm_btn = wait.until(EC.element_to_be_clickable((By.XPATH, confirm_xpath)))
    
    # 방법 A: 일반 클릭
    # 방법 B: JavaScript 강제 클릭 (추천)
    driver.execute_script("arguments[0].click();", confirm_btn)
    
    # 방법 C: 직접 함수 호출 (최후의 수단)
    # driver.execute_script("closepopupLayerConfirm(true);")

    now = datetime.datetime.now()
    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] 🎉 로또 구매 완료!")

except Exception as e:
    print(f"❌ 오류 발생: {e}")
    driver.save_screenshot(f"error_{int(time.time())}.png")
    print("📸 에러 스크린샷이 저장되었습니다.")

finally:
    # 잠시 결과 확인 후 브라우저 종료 (원치 않으면 주석 처리)
    time.sleep(3)
    driver.save_screenshot(f"success_{int(time.time())}.png")
    print("📸 로또 스크린샷이 저장되었습니다.")
    time.sleep(3)
    # driver.quit()