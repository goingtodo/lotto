import time
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException

# --- [1. 이메일 설정 정보] ---
# Gmail 사용 시 '앱 비밀번호' 생성이 필수입니다.
SENDER_EMAIL = ""    # 보내는 구글 메일
SENDER_PASSWORD = "" # 구글 앱 비밀번호 16자리
RECEIVER_EMAIL = ""     # 알림 받을 메일 주소

# --- [2. 로또 설정 정보] ---
LOTTO_URL = 'https://www.dhlottery.co.kr/login'
USER_ID = ''               # ← 실제 아이디
USER_PW = '!'              # ← 실제 비밀번호

# --- [이메일 전송 함수 정의] ---
def send_email_notification(subject, body, attachment_path=None):
    try:
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        msg.attach(MIMEText(body, 'plain'))

        if attachment_path:
            with open(attachment_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={attachment_path}')
                msg.attach(part)

        # SMTP 서버 연결 (Gmail)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"📧 이메일 알림 전송 완료 ({subject})")
    except Exception as e:
        print(f"❌ 이메일 전송 중 에러 발생: {e}")

# --- [메인 실행 로직] ---
options = webdriver.ChromeOptions()
options.add_argument('--headless')          # 눈에 보이지 않게 실행
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080') # 가상 창 크기 고정 (매우 중요)

driver = webdriver.Chrome(options=options)
driver.maximize_window()
wait = WebDriverWait(driver, 15)

try:
    # 1. 로그인 프로세스
    driver.get(LOTTO_URL)
    wait.until(EC.presence_of_element_located((By.ID, 'inpUserId'))).send_keys(USER_ID)
    wait.until(EC.presence_of_element_located((By.ID, 'inpUserPswdEncn'))).send_keys(USER_PW)
    wait.until(EC.element_to_be_clickable((By.ID, 'btnLogin'))).click()

    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'btn-logIn')))
    print("✅ 로그인 성공")

    # 2. 구매 페이지 이동 및 프레임 진입
    driver.get('https://ol.dhlottery.co.kr/olotto/game/game645.do')
    time.sleep(3) 
    
    # iframe 진입 (주석 해제)
    # wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'ifrm_tab')))
    print("✅ iframe(구매창) 진입 성공")

    # 3. 자동번호 2개 선택
    auto_radio = wait.until(EC.element_to_be_clickable((By.ID, "num2")))
    driver.execute_script("arguments[0].click();", auto_radio)
    
    amt_select = Select(wait.until(EC.presence_of_element_located((By.ID, "amoundApply"))))
    amt_select.select_by_value('2')
    driver.find_element(By.ID, "btnSelectNum").click()
    print("✅ 자동 2개 선택 완료")

    # 4. 수동(나의 번호) 3개 선택
    wait.until(EC.element_to_be_clickable((By.ID, "num4"))).click()
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="myList"]/li[1]/input')))
    
    for i in range(1, 4):
        checkbox = driver.find_element(By.XPATH, f'//*[@id="myList"]/li[{i}]/input')
        driver.execute_script("arguments[0].click();", checkbox)
    
    driver.find_element(By.NAME, "btnMyNumber").click()
    print("✅ 나의 번호 3개 적용 완료")

    # 5. 최종 구매하기 버튼 클릭
    buy_btn = wait.until(EC.element_to_be_clickable((By.ID, "btnBuy")))
    buy_btn.click()
    print("🚀 구매 버튼 클릭! 최종 팝업 처리 중...")

    # 6. 최종 확인 팝업 처리
    wait.until(EC.visibility_of_element_located((By.ID, "popupLayerConfirm")))
    
    # 팝업 내 확인 버튼 타겟팅 및 JS 클릭
    confirm_xpath = "//div[@id='popupLayerConfirm']//input[@value='확인']"
    confirm_btn = wait.until(EC.element_to_be_clickable((By.XPATH, confirm_xpath)))
    driver.execute_script("arguments[0].click();", confirm_btn)

    # 성공 결과 기록
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{now_str}] 🎉 로또 구매 명령 완료!")
    
    # 스크린샷 저장 및 메일 발송
    time.sleep(2)
    success_file = f"success_{int(time.time())}.png"
    driver.save_screenshot(success_file)
    send_email_notification(
        subject="🎉 [로또 자동구매] 구매 성공 알림",
        body=f"구매가 성공적으로 완료되었습니다.\n일시: {now_str}",
        attachment_path=success_file
    )

except Exception as e:
    err_msg = f"❌ 오류 발생: {e}"
    print(err_msg)
    
    # 에러 스크린샷 저장 및 메일 발송
    error_file = f"error_{int(time.time())}.png"
    driver.save_screenshot(error_file)
    send_email_notification(
        subject="⚠️ [로또 자동구매] 에러 발생 알림",
        body=f"구매 진행 중 오류가 발생했습니다.\n\n에러 내용:\n{err_msg}",
        attachment_path=error_file
    )

finally:
    time.sleep(3)
    driver.quit()