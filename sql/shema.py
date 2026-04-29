import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# 환경 변수 로드 (.env 파일이 같은 경로에 있어야 합니다)
load_dotenv()

# DB 접속 정보 설정
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", 3306)
DB_DATABASE = os.getenv("DB_DATABASE")

# 1. 서버 접속을 위한 베이스 URL (데이터베이스 이름 제외)
BASE_DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}"
# 2. 특정 데이터베이스 접속을 위한 URL
TARGET_DB_URL = f"{BASE_DB_URL}/{DB_DATABASE}"

def migrate_parquet_to_mysql():
    # [STEP 1] 데이터베이스 생성 (존재하지 않을 경우)
    try:
        temp_engine = create_engine(BASE_DB_URL)
        with temp_engine.connect() as conn:
            # MySQL에서는 DB 이름에 하이픈(-) 등이 있을 수 있으므로 백틱(`)으로 감싸는 것이 안전합니다.
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{DB_DATABASE}`"))
            print(f"Step 1: Database '{DB_DATABASE}' is ready (created or already exists).")
        temp_engine.dispose()
    except Exception as e:
        print(f"Error during database creation: {e}")
        return

    # [STEP 2] 실제 데이터를 넣을 엔진 생성
    engine = create_engine(TARGET_DB_URL)

    # 파일 경로 설정 (기존에 작성하신 로컬 경로 유지)
    files = {
        'category_saturation': r'C:\Users\Playdata\Desktop\SKN29-2nd-1Team\data\processed\category_saturation.parquet',
        'trending_snapshots': r'C:\Users\Playdata\Desktop\SKN29-2nd-1Team\data\processed\trending_snapshots.parquet',
        'video_trending_events': r'C:\Users\Playdata\Desktop\SKN29-2nd-1Team\data\processed\video_trending_events.parquet'
    }

    # [STEP 3] 데이터 삽입 루프
    for table_name, file_path in files.items():
        try:
            # 파일 존재 여부 확인
            if not os.path.exists(file_path):
                print(f"Warning: File not found at {file_path}. Skipping...")
                continue

            print(f"Processing {table_name}...")
            df = pd.read_parquet(file_path)
            
            # 데이터 삽입 (if_exists='replace'는 테이블을 삭제 후 새로 생성함)
            df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
            print(f"Successfully uploaded {table_name} to MySQL.")
            
        except Exception as e:
            print(f"Error processing {table_name}: {e}")

if __name__ == "__main__":
    migrate_parquet_to_mysql()