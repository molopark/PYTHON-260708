import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
from member_manager import init_db, get_db_connection

app = Flask(__name__)
app.secret_key = "member_manager_secret_key_flask"

# DB 초기화 실행 (프로그램 구동 시 테이블 자동 생성)
init_db()

@app.route('/')
def index():
    """메인 화면: 전체 회원 목록 조회 및 검색 기능 통합"""
    search_keyword = request.args.get('q', '').strip()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if search_keyword:
        # ID 또는 이름 패턴 매칭 검색
        cursor.execute("""
            SELECT id, username, name, email, phone, created_at 
            FROM members 
            WHERE username LIKE ? OR name LIKE ?
            ORDER BY id DESC
        """, (f"%{search_keyword}%", f"%{search_keyword}%"))
    else:
        # 전체 회원 목록 조회
        cursor.execute("""
            SELECT id, username, name, email, phone, created_at 
            FROM members 
            ORDER BY id DESC
        """)
        
    rows = cursor.fetchall()
    conn.close()
    
    # 튜플 형태에서 딕셔너리 리스트로 변환하여 템플릿에 전달하기 쉽게 처리
    members = []
    for row in rows:
        members.append({
            'id': row[0],
            'username': row[1],
            'name': row[2],
            'email': row[3] if row[3] else '-',
            'phone': row[4] if row[4] else '-',
            'created_at': row[5]
        })
        
    return render_template('index.html', members=members, search_keyword=search_keyword)

@app.route('/register', methods=['POST'])
def register():
    """회원 등록 처리"""
    username = request.form.get('username', '').strip()
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    
    # 1. 필수값 체크
    if not username:
        flash("❌ 회원 ID는 필수 입력값입니다.", "danger")
        return redirect(url_for('index'))
    if not name:
        flash("❌ 이름은 필수 입력값입니다.", "danger")
        return redirect(url_for('index'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 2. 중복 ID 체크
    cursor.execute("SELECT id FROM members WHERE username = ?", (username,))
    if cursor.fetchone():
        flash(f"❌ '{username}'은(는) 이미 존재하는 ID입니다. 다른 ID를 입력해주세요.", "danger")
        conn.close()
        return redirect(url_for('index'))
        
    # 3. 데이터 저장
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    email_val = email if email else None
    phone_val = phone if phone else None
    
    try:
        cursor.execute("""
            INSERT INTO members (username, name, email, phone, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (username, name, email_val, phone_val, created_at))
        conn.commit()
        flash(f"🎉 {name}({username}) 회원 등록이 성공적으로 완료되었습니다!", "success")
    except sqlite3.Error as e:
        flash(f"❌ 오류가 발생했습니다: {e}", "danger")
    finally:
        conn.close()
        
    return redirect(url_for('index'))

@app.route('/delete/<username>', methods=['POST'])
def delete(username):
    """회원 삭제 처리"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 해당 회원 존재 여부 확인
    cursor.execute("SELECT name FROM members WHERE username = ?", (username,))
    row = cursor.fetchone()
    
    if not row:
        flash(f"❌ ID가 '{username}'인 회원을 찾을 수 없습니다.", "danger")
        conn.close()
        return redirect(url_for('index'))
        
    name = row[0]
    
    try:
        cursor.execute("DELETE FROM members WHERE username = ?", (username,))
        conn.commit()
        flash(f"🗑️ {name} 회원의 정보가 정상적으로 삭제되었습니다.", "success")
    except sqlite3.Error as e:
        flash(f"❌ 삭제 중 오류가 발생했습니다: {e}", "danger")
    finally:
        conn.close()
        
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
