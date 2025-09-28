#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from models import db, ContractSignature
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def update_signature():
    """서명 레코드 업데이트"""
    with app.app_context():
        try:
            # 계약서 17의 SELLER 서명 찾기
            signature = ContractSignature.query.filter_by(
                contract_id=17,
                role='SELLER'
            ).first()
            
            if signature:
                # 이미지 경로 설정
                signature.image_path = "uploads/signatures/17/seller.png"
                signature.signed_at = datetime.utcnow()
                signature.ip = "127.0.0.1"
                signature.ua = "Test User Agent"
                
                db.session.commit()
                print(f"✓ Updated signature {signature.id} with image path")
                print(f"  Image path: {signature.image_path}")
                print(f"  Signed at: {signature.signed_at}")
            else:
                print("❌ SELLER signature not found for contract 17")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    update_signature()



