# scripts/parse_asset_excel.py
import sys
import os

# 프로젝트 루트 디렉토리 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.database import SessionLocal, engine, Base
from app.models.assetdetailed import AssetDetailed
from app.utils.excel_parser import parse_asset_excel

def init_asset_table():
    """
    AssetDetailed 테이블 생성
    """
    # models.assetdetailed.py에 정의된 테이블 생성
    from sqlalchemy import inspect
    
    inspector = inspect(engine)
    if 'assets_detailed' not in inspector.get_table_names():
        print("assets_detailed 테이블이 없습니다. 테이블을 생성합니다...")
        # AssetDetailed 모델에 해당하는 테이블 생성
        AssetDetailed.__table__.create(engine, checkfirst=True)
        print("assets_detailed 테이블 생성 완료")
    else:
        print("assets_detailed 테이블이 이미 존재합니다.")

def display_legislator_assets(db, legislator_name):
    """
    특정 의원의 모든 자산 정보를 출력
    
    Args:
        db: 데이터베이스 세션
        legislator_name: 국회의원 이름
    """
    assets = db.query(AssetDetailed).filter(AssetDetailed.name == legislator_name).all()
    
    if not assets:
        print(f"'{legislator_name}' 의원의 자산 정보를 찾을 수 없습니다.")
        return
    
    print(f"\n===== '{legislator_name}' 의원의 자산 정보 ({len(assets)}건) =====")
    
    # 총 자산 계산
    total_asset = sum(asset.asset_current for asset in assets if asset.asset_current is not None)
    
    print(f"총 자산: {total_asset:,}천원 (약 {total_asset/100000:.1f}억원)")
    print("\n- 자산 상세 내역:")
    
    # 자산 유형별 분류
    asset_by_category = {}
    
    for asset in assets:
        category = asset.asset_category
        if category not in asset_by_category:
            asset_by_category[category] = []
        asset_by_category[category].append(asset)
    
    # 자산 유형별로 출력
    for category, items in asset_by_category.items():
        category_total = sum(item.asset_current for item in items if item.asset_current is not None)
        print(f"\n[{category}] - 총액: {category_total:,}천원")
        
        for idx, item in enumerate(items, 1):
            # 자산 유형의 상세 정보 출력
            print(f"  {idx}. {item.asset_type} - {item.asset_current:,}천원")
            print(f"     소유: {item.relation_to_self}, 소재지: {item.location}")
            if item.area_sqm:
                print(f"     면적: {item.area_sqm}")
            if item.rights_detail:
                print(f"     권리사항: {item.rights_detail}")
            if item.asset_increase > 0 or item.asset_decrease > 0:
                print(f"     변동: {'+' if item.asset_increase > 0 else ''}{item.asset_increase:,}천원 "
                      f"{'-' if item.asset_decrease > 0 else ''}{item.asset_decrease:,}천원")
            if item.reason_for_change:
                print(f"     변동사유: {item.reason_for_change}")
            print()

def parse_asset_files():
    """
    data/excel/asset 폴더의 재산 엑셀 파일을 파싱하여 DB에 저장
    """
    # DB 세션 생성
    db = SessionLocal()
    try:
        # 파일 경로 설정
        asset_dir = os.path.join('data', 'excel', 'asset')
        
        # 지정된 파일명 확인
        expected_file = 'asset_2025_03.xlsx'
        file_path = os.path.join(asset_dir, expected_file)
        
        if not os.path.exists(file_path):
            print(f"파일을 찾을 수 없습니다: {file_path}")
            # 디렉토리 내의 다른 엑셀 파일 확인
            excel_files = [f for f in os.listdir(asset_dir) if f.endswith('.xlsx') or f.endswith('.xls')]
            if excel_files:
                print(f"대신 다음 엑셀 파일을 찾았습니다: {excel_files}")
                # 첫 번째 찾은 파일 사용
                file_path = os.path.join(asset_dir, excel_files[0])
                print(f"파일 사용: {file_path}")
            else:
                print(f"디렉토리에 엑셀 파일이 없습니다: {asset_dir}")
                return
        
        # 파일 파싱 및 DB 저장
        processed_count = parse_asset_excel(file_path, db)
        
        if processed_count > 0:
            print(f"총 {processed_count}개의 재산 상세 데이터를 처리했습니다.")
            
            # 데이터가 저장된 의원 목록 조회
            legislators = db.query(AssetDetailed.name).distinct().all()
            legislator_names = [row[0] for row in legislators]
            
            if legislator_names:
                print(f"\n다음 {len(legislator_names)}명의 의원 데이터가 저장되었습니다:")
                for i, name in enumerate(sorted(legislator_names), 1):
                    print(f"{i}. {name}")
                
                # 특정 의원의 데이터 조회 여부 확인
                view_legislator = input("\n특정 의원의 상세 정보를 조회하시겠습니까? (의원명 입력 또는 n): ")
                if view_legislator.lower() != 'n':
                    # 입력된 이름과 가장 비슷한 의원 찾기
                    closest_match = None
                    for name in legislator_names:
                        if view_legislator in name:
                            closest_match = name
                            break
                    
                    if closest_match:
                        display_legislator_assets(db, closest_match)
                    else:
                        print(f"'{view_legislator}' 이름을 가진 의원을 찾을 수 없습니다.")
            else:
                print("저장된 의원 데이터가, 없습니다.")
        
    except Exception as e:
        print(f"재산 데이터 처리 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    # 테이블 초기화
    init_asset_table()
    
    # 기존 데이터 확인
    db = SessionLocal()
    existing_count = db.query(AssetDetailed).count()
    
    if existing_count > 0:
        print(f"이미 {existing_count}개의 재산 상세 데이터가 있습니다.")
        
        # 저장된 의원 리스트 출력
        legislators = db.query(AssetDetailed.name).distinct().all()
        legislator_names = [row[0] for row in legislators]
        
        print(f"총 {len(legislator_names)}명의 의원 데이터가 저장되어 있습니다:")
        for i, name in enumerate(sorted(legislator_names), 1):
            print(f"{i}. {name}")
        
        action = input("작업을 선택하세요:\n1. 특정 의원 정보 조회\n2. 모든 데이터 삭제 후 다시 파싱\n3. 기존 데이터 유지하고 추가 파싱\n선택: ")
        
        if action == '1':
            legislator_name = input("조회할 의원 이름을 입력하세요: ")
            display_legislator_assets(db, legislator_name)
            db.close()
            sys.exit(0)
        elif action == '2':
            # 모든 데이터 삭제
            db.query(AssetDetailed).delete()
            db.commit()
            print("모든 데이터가 삭제되었습니다.")
        elif action != '3':
            print("작업이 취소되었습니다.")
            db.close()
            sys.exit(0)
    
    db.close()
    
    # 파싱 진행
    parse_asset_files()