#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
브랜드 매칭 파일 처리 모듈
"""

import pandas as pd
import os
import logging
from typing import List, Dict
from datetime import datetime
import shutil

logger = logging.getLogger(__name__)

class BrandFileProcessor:
    """브랜드 매칭용 파일 처리기"""
    
    def __init__(self):
        self.uploads_dir = "uploads"
        self.results_dir = "results" 
        self.ensure_directories()
    
    def ensure_directories(self):
        """필요한 디렉토리 생성"""
        for directory in [self.uploads_dir, self.results_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                logger.info(f"디렉토리 생성: {directory}")
    
    def save_uploaded_file(self, file, original_filename: str) -> str:
        """업로드된 파일 저장"""
        try:
            # 안전한 파일명 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{timestamp}_{original_filename}"
            file_path = os.path.join(self.uploads_dir, safe_filename)
            
            # 파일 저장
            file.save(file_path)
            logger.info(f"파일 저장 완료: {file_path}")
            
            return file_path
            
        except Exception as e:
            logger.error(f"파일 저장 실패: {e}")
            raise e
    
    def read_excel_file(self, file_path: str) -> pd.DataFrame:
        """엑셀 파일 읽기"""
        try:
            # 다양한 엑셀 형식 지원
            if file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path, engine='openpyxl')
            elif file_path.endswith('.xls'):
                df = pd.read_excel(file_path, engine='xlrd')
            else:
                raise ValueError(f"지원되지 않는 파일 형식: {file_path}")
            
            logger.info(f"엑셀 파일 읽기 완료: {file_path} ({len(df)}행, {len(df.columns)}열)")
            return df
            
        except Exception as e:
            logger.error(f"엑셀 파일 읽기 실패 ({file_path}): {e}")
            raise e
    
    def combine_excel_files(self, file_paths: List[str]) -> pd.DataFrame:
        """여러 엑셀 파일을 하나로 합치기"""
        try:
            combined_df = pd.DataFrame()
            
            for file_path in file_paths:
                if os.path.exists(file_path):
                    df = self.read_excel_file(file_path)
                    
                    # 컬럼 수가 다른 경우 처리
                    if combined_df.empty:
                        combined_df = df.copy()
                    else:
                        # 컬럼 수를 맞춤
                        max_cols = max(len(combined_df.columns), len(df.columns))
                        
                        # combined_df 컬럼 수 조정
                        while len(combined_df.columns) < max_cols:
                            combined_df[f'Col_{len(combined_df.columns)}'] = ''
                        
                        # df 컬럼 수 조정  
                        while len(df.columns) < max_cols:
                            df[f'Col_{len(df.columns)}'] = ''
                        
                        # 컬럼명 통일
                        df.columns = combined_df.columns
                        
                        # 데이터 결합
                        combined_df = pd.concat([combined_df, df], ignore_index=True)
                    
                    logger.info(f"파일 결합: {file_path}")
                else:
                    logger.warning(f"파일이 존재하지 않음: {file_path}")
            
            logger.info(f"파일 결합 완료: 총 {len(combined_df)}행")
            return combined_df
            
        except Exception as e:
            logger.error(f"파일 결합 실패: {e}")
            raise e
    
    def get_uploaded_files(self) -> List[Dict]:
        """업로드된 파일 목록 조회"""
        try:
            files = []
            
            if os.path.exists(self.uploads_dir):
                for filename in os.listdir(self.uploads_dir):
                    if filename.endswith(('.xlsx', '.xls')):
                        file_path = os.path.join(self.uploads_dir, filename)
                        file_info = {
                            'filename': filename,
                            'path': file_path,
                            'size': os.path.getsize(file_path),
                            'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
                        }
                        files.append(file_info)
            
            # 수정일 기준 역순 정렬
            files.sort(key=lambda x: x['modified'], reverse=True)
            
            return files
            
        except Exception as e:
            logger.error(f"업로드 파일 목록 조회 실패: {e}")
            return []
    
    def delete_uploaded_file(self, filename: str) -> bool:
        """업로드된 파일 삭제"""
        try:
            file_path = os.path.join(self.uploads_dir, filename)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"파일 삭제 완료: {file_path}")
                return True
            else:
                logger.warning(f"삭제할 파일이 존재하지 않음: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"파일 삭제 실패: {e}")
            return False
    
    def clear_uploaded_files(self) -> bool:
        """모든 업로드 파일 삭제"""
        try:
            if os.path.exists(self.uploads_dir):
                for filename in os.listdir(self.uploads_dir):
                    file_path = os.path.join(self.uploads_dir, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                
                logger.info("모든 업로드 파일 삭제 완료")
                return True
            
            return True
            
        except Exception as e:
            logger.error(f"업로드 파일 전체 삭제 실패: {e}")
            return False
    
    def save_result_file(self, df: pd.DataFrame, base_filename: str = "브랜드매칭결과") -> str:
        """결과 파일 저장"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{base_filename}_{timestamp}.xlsx"
            file_path = os.path.join(self.results_dir, filename)
            
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Sheet2 탭에 저장
                df.to_excel(writer, sheet_name='Sheet2', index=False)
                
                # 컬럼 너비 조정
                worksheet = writer.sheets['Sheet2']
                for i, column in enumerate(df.columns, 1):
                    column_letter = chr(64 + i) if i <= 26 else f"A{chr(64 + i - 26)}"
                    worksheet.column_dimensions[column_letter].width = 15
            
            logger.info(f"결과 파일 저장 완료: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"결과 파일 저장 실패: {e}")
            raise e
    
    def get_file_stats(self) -> Dict:
        """파일 통계 정보"""
        try:
            uploaded_files = self.get_uploaded_files()
            
            stats = {
                'uploaded_count': len(uploaded_files),
                'total_size': sum(f['size'] for f in uploaded_files),
                'latest_upload': uploaded_files[0]['modified'] if uploaded_files else None
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"파일 통계 조회 실패: {e}")
            return {'uploaded_count': 0, 'total_size': 0, 'latest_upload': None} 