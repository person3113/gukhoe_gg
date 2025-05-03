from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

def get_all(db: Session, model):
    # 모델의 모든 레코드 조회
    pass

def get_by_id(db: Session, model, id: int):
    # ID로 특정 레코드 조회
    pass

def get_by_filter(db: Session, model, **filters):
    # 필터 조건으로 레코드 조회
    pass

def create(db: Session, model, obj_in):
    # 새 레코드 생성
    pass

def update(db: Session, model, id: int, obj_in):
    # 레코드 업데이트
    pass

def delete(db: Session, model, id: int):
    # 레코드 삭제
    pass