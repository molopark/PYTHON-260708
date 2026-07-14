import sqlite3
import os
import sys
from datetime import datetime

DB_FILE = "members.db"

def init_db():
    """데이터베이스 파일 및 테이블 초기화"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # members 테이블 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def get_db_connection():
    """데이터베이스 연결 생성"""
    return sqlite3.connect(DB_FILE)

def register_member():
    """회원 등록 프롬프트"""
    print("\n" + "="*30)
    print("        [ 회원 등록 ]")
    print("="*30)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. 회원 ID 입력 및 중복 체크
    while True:
        username = input("회원 ID (ID/영어/숫자): ").strip()
        if not username:
            print("❌ 회원 ID는 필수 입력값입니다.")
            continue
        
        # 중복 체크
        cursor.execute("SELECT id FROM members WHERE username = ?", (username,))
        if cursor.fetchone():
            print(f"❌ '{username}'은(는) 이미 존재하는 ID입니다. 다른 ID를 입력해주세요.")
            continue
        break
    
    # 2. 이름 입력
    while True:
        name = input("이름: ").strip()
        if not name:
            print("❌ 이름은 필수 입력값입니다.")
            continue
        break
        
    # 3. 이메일 입력 (옵션)
    email = input("이메일 (엔터 시 건너뜀): ").strip()
    if not email:
        email = None
        
    # 4. 전화번호 입력 (옵션)
    phone = input("전화번호 (엔터 시 건너뜀): ").strip()
    if not phone:
        phone = None
        
    # 데이터베이스 삽입
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        cursor.execute("""
            INSERT INTO members (username, name, email, phone, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (username, name, email, phone, created_at))
        conn.commit()
        print("\n🎉 회원 등록이 성공적으로 완료되었습니다!")
    except sqlite3.Error as e:
        print(f"❌ 오류가 발생했습니다: {e}")
    finally:
        conn.close()

def list_members():
    """회원 목록 전체 조회"""
    print("\n" + "="*80)
    print("                              [ 전체 회원 목록 ]")
    print("="*80)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, name, email, phone, created_at FROM members ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("등록된 회원이 없습니다.")
        print("="*80)
        return
        
    # 포맷 맞춰 출력
    print(f"{'No.':<5} | {'ID':<15} | {'이름':<12} | {'이메일':<25} | {'전화번호':<15} | {'가입일시':<19}")
    print("-" * 110)
    for row in rows:
        email = row[3] if row[3] else "-"
        phone = row[4] if row[4] else "-"
        print(f"{row[0]:<5} | {row[1]:<15} | {row[2]:<12} | {email:<25} | {phone:<15} | {row[5]}")
    print("="*80)

def search_member():
    """회원 검색"""
    print("\n" + "="*30)
    print("        [ 회원 검색 ]")
    print("="*30)
    
    keyword = input("검색할 ID 또는 이름을 입력하세요: ").strip()
    if not keyword:
        print("❌ 검색어를 입력해야 합니다.")
        return
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # ID 또는 이름 패턴 매칭 검색
    cursor.execute("""
        SELECT id, username, name, email, phone, created_at 
        FROM members 
        WHERE username LIKE ? OR name LIKE ?
        ORDER BY id DESC
    """, (f"%{keyword}%", f"%{keyword}%"))
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print(f"🔍 '{keyword}' 검색 결과가 존재하지 않습니다.")
        return
        
    print(f"\n🔍 '{keyword}' 검색 결과 ({len(rows)}건):")
    print("-" * 110)
    print(f"{'No.':<5} | {'ID':<15} | {'이름':<12} | {'이메일':<25} | {'전화번호':<15} | {'가입일시':<19}")
    print("-" * 110)
    for row in rows:
        email = row[3] if row[3] else "-"
        phone = row[4] if row[4] else "-"
        print(f"{row[0]:<5} | {row[1]:<15} | {row[2]:<12} | {email:<25} | {phone:<15} | {row[5]}")
    print("="*110)

def delete_member():
    """회원 삭제"""
    print("\n" + "="*30)
    print("        [ 회원 삭제 ]")
    print("="*30)
    
    username = input("삭제할 회원의 ID를 정확히 입력하세요: ").strip()
    if not username:
        print("❌ ID를 입력해야 합니다.")
        return
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 해당 회원 존재 여부 확인
    cursor.execute("SELECT name FROM members WHERE username = ?", (username,))
    row = cursor.fetchone()
    
    if not row:
        print(f"❌ ID가 '{username}'인 회원을 찾을 수 없습니다.")
        conn.close()
        return
        
    name = row[0]
    confirm = input(f"⚠️ 정말로 {name}(ID: {username}) 회원을 삭제하시겠습니까? (y/n): ").strip().lower()
    
    if confirm == 'y':
        try:
            cursor.execute("DELETE FROM members WHERE username = ?", (username,))
            conn.commit()
            print(f"🗑️ {name} 회원의 정보가 정상적으로 삭제되었습니다.")
        except sqlite3.Error as e:
            print(f"❌ 삭제 중 오류가 발생했습니다: {e}")
    else:
        print("❌ 삭제 작업이 취소되었습니다.")
        
    conn.close()

def main_menu():
    """메인 컨트롤 루프"""
    init_db()
    
    while True:
        print("\n" + "★"*20 + " [ SQLite 회원 관리 프로그램 ] " + "★"*20)
        print(" 1. 회원 등록")
        print(" 2. 전체 회원 목록 조회")
        print(" 3. 회원 검색 (ID 또는 이름)")
        print(" 4. 회원 정보 삭제")
        print(" 5. 프로그램 종료")
        print("★"*62)
        
        choice = input("원하시는 메뉴 번호를 입력하세요: ").strip()
        
        if choice == '1':
            register_member()
        elif choice == '2':
            list_members()
        elif choice == '3':
            search_member()
        elif choice == '4':
            delete_member()
        elif choice == '5':
            print("\n👋 프로그램을 종료합니다. 이용해 주셔서 감사합니다!")
            break
        else:
            print("❌ 올바른 메뉴 번호(1~5)를 입력해 주세요.")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 인터럽트 감지. 프로그램을 안전하게 종료합니다.")
        sys.exit(0)
