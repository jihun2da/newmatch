#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
브랜드매칭시트 API 연동 모듈 - 대용량 데이터 최적화
"""

import pandas as pd
import requests
import logging
from typing import Optional
from io import StringIO
import gc

logger = logging.getLogger(__name__)

class BrandSheetsAPI:
    """브랜드매칭시트 API를 사용한 데이터 읽기 - 메모리 최적화"""
    
    def __init__(self):
        # 브랜드매칭시트 ID
        self.brand_sheet_id = "14Pmz5-bFVPSPbfoKi5BfQWa8qVMVNDqxEQVmhT9wyuU"
        self.gid = "1834709463"  # 시트 탭 ID
        self.chunk_size = 5000  # 청크 크기 설정 (메모리 절약)
        self.preserve_data = True  # 데이터 보존 모드 (더 관대한 필터링)
        
    def read_brand_matching_data(self) -> pd.DataFrame:
        """브랜드매칭시트에서 매칭 데이터 읽기 (공개 시트) - 메모리 최적화"""
        try:
            # 공개 구글시트 CSV 다운로드 URL
            csv_url = f"https://docs.google.com/spreadsheets/d/{self.brand_sheet_id}/export?format=csv&gid={self.gid}"
            
            logger.info(f"브랜드매칭시트에서 데이터 읽기 시도: {self.brand_sheet_id}")
            logger.info(f"데이터 보존 모드: {'활성화' if self.preserve_data else '비활성화'}")
            
            # CSV 데이터 다운로드 (타임아웃 증가)
            response = requests.get(csv_url, timeout=60)
            response.raise_for_status()
            
            # 인코딩 문제 해결을 위한 다중 시도
            try:
                # 방법 1: UTF-8로 디코딩
                response.encoding = 'utf-8'
                csv_content = response.text
            except:
                try:
                    # 방법 2: 바이트를 직접 UTF-8로 디코딩
                    csv_content = response.content.decode('utf-8')
                except:
                    # 방법 3: UTF-8-SIG (BOM 포함)
                    csv_content = response.content.decode('utf-8-sig')
            
            # 메모리 효율적인 CSV 읽기
            csv_data = StringIO(csv_content)
            
            # 청크 단위로 데이터 읽기
            logger.info("대용량 데이터를 청크 단위로 처리 중...")
            chunks = []
            total_rows = 0
            
            try:
                # 전체 데이터를 한 번에 읽되, 메모리 사용량 모니터링
                df = pd.read_csv(csv_data, low_memory=True)
                total_rows = len(df)
                logger.info(f"총 {total_rows:,} 행의 원시 데이터를 읽었습니다")
                
                # 메모리 사용량이 너무 클 경우 청크 처리
                if total_rows > 20000:
                    logger.info(f"대용량 데이터 감지 ({total_rows:,}개). 청크 처리를 시작합니다.")
                    return self._process_large_dataset(df)
                else:
                    return self._process_normal_dataset(df)
                    
            except Exception as e:
                logger.error(f"데이터 읽기 실패: {e}")
                return self._get_fallback_data()
                
        except Exception as e:
            logger.error(f"브랜드매칭시트 읽기 실패: {e}")
            logger.info("폴백 데이터를 사용합니다")
            return self._get_fallback_data()
    
    def _process_large_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """대용량 데이터셋을 청크 단위로 처리"""
        try:
            logger.info("대용량 데이터 처리 모드 활성화")
            
            # 필수 컬럼 확인
            if len(df.columns) < 5:
                logger.warning("필요한 컬럼을 찾을 수 없습니다. 폴백 데이터를 사용합니다.")
                return self._get_fallback_data()
            
            processed_chunks = []
            chunk_size = self.chunk_size
            total_chunks = (len(df) + chunk_size - 1) // chunk_size
            
            logger.info(f"총 {total_chunks}개 청크로 분할하여 처리합니다 (청크당 {chunk_size:,}행)")
            
            for i in range(0, len(df), chunk_size):
                chunk_num = (i // chunk_size) + 1
                logger.info(f"청크 {chunk_num}/{total_chunks} 처리 중... ({i:,}-{min(i+chunk_size, len(df)):,}행)")
                
                chunk = df.iloc[i:i+chunk_size].copy()
                processed_chunk = self._process_chunk(chunk)
                
                if not processed_chunk.empty:
                    processed_chunks.append(processed_chunk)
                
                # 메모리 정리
                del chunk
                gc.collect()
                
                # 진행률 로깅
                if chunk_num % 5 == 0 or chunk_num == total_chunks:
                    logger.info(f"진행률: {chunk_num}/{total_chunks} ({(chunk_num/total_chunks)*100:.1f}%)")
            
            # 모든 청크 결합
            if processed_chunks:
                logger.info("청크들을 결합하는 중...")
                final_df = pd.concat(processed_chunks, ignore_index=True)
                
                # 메모리 정리
                del processed_chunks
                gc.collect()
                
                # 최종 스마트 중복 제거 및 정리
                logger.info("최종 데이터 정리 중...")
                before_dedup = len(final_df)
                
                if self.preserve_data:
                    # 관대한 중복 제거 (브랜드+상품명만으로 중복 판단)
                    final_df = final_df.drop_duplicates(subset=['브랜드', '상품명'], keep='first')
                    logger.info("관대한 중복 제거 적용 (브랜드+상품명 기준)")
                else:
                    # 엄격한 중복 제거 (브랜드+상품명+옵션입력)
                    final_df = final_df.drop_duplicates(subset=['브랜드', '상품명', '옵션입력'], keep='first')
                    logger.info("엄격한 중복 제거 적용 (브랜드+상품명+옵션 기준)")
                
                after_dedup = len(final_df)
                
                logger.info(f"중복 제거: {before_dedup:,}개 → {after_dedup:,}개 (제거된 중복: {before_dedup - after_dedup:,}개)")
                
                # 인덱스 재설정 (중요! 브랜드 인덱스 오류 방지)
                final_df = final_df.reset_index(drop=True)
                
                logger.info(f"대용량 데이터 처리 완료: {len(final_df):,}개 상품")
                return final_df
            else:
                logger.warning("처리된 데이터가 없습니다. 폴백 데이터를 사용합니다.")
                return self._get_fallback_data()
                
        except Exception as e:
            logger.error(f"대용량 데이터 처리 실패: {e}")
            return self._get_fallback_data()
    
    def _process_normal_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """일반 크기 데이터셋 처리"""
        logger.info("일반 크기 데이터셋 처리 모드")
        processed_df = self._process_chunk(df)
        
        if not processed_df.empty:
            # 스마트 중복 제거
            before_dedup = len(processed_df)
            
            if self.preserve_data:
                # 관대한 중복 제거 (브랜드+상품명만으로 중복 판단)
                processed_df = processed_df.drop_duplicates(subset=['브랜드', '상품명'], keep='first')
                logger.info("관대한 중복 제거 적용 (브랜드+상품명 기준)")
            else:
                # 엄격한 중복 제거 (브랜드+상품명+옵션입력)
                processed_df = processed_df.drop_duplicates(subset=['브랜드', '상품명', '옵션입력'], keep='first')
                logger.info("엄격한 중복 제거 적용 (브랜드+상품명+옵션 기준)")
            
            after_dedup = len(processed_df)
            
            logger.info(f"중복 제거: {before_dedup:,}개 → {after_dedup:,}개 (제거된 중복: {before_dedup - after_dedup:,}개)")
            
            # 인덱스 재설정 (중요! 브랜드 인덱스 오류 방지)
            processed_df = processed_df.reset_index(drop=True)
            
            logger.info(f"일반 데이터 처리 완료: {len(processed_df):,}개 상품")
        
        return processed_df
    
    def _process_chunk(self, chunk: pd.DataFrame) -> pd.DataFrame:
        """개별 청크 처리"""
        try:
            if len(chunk.columns) < 5:
                logger.warning(f"컬럼 수 부족: {len(chunk.columns)}개 (최소 5개 필요)")
                return pd.DataFrame()
            
            original_count = len(chunk)
            logger.info(f"청크 원시 데이터: {original_count:,}개")
            
            # 필요한 컬럼들 추출 (메모리 효율적)
            brand_data = pd.DataFrame()
            brand_data['브랜드'] = chunk.iloc[:, 0].fillna('').astype('string')  # string dtype 사용
            brand_data['상품명'] = chunk.iloc[:, 1].fillna('').astype('string')
            brand_data['중도매'] = chunk.iloc[:, 2].fillna('').astype('string')
            brand_data['공급가'] = pd.to_numeric(chunk.iloc[:, 3], errors='coerce').fillna(0).astype('float32')  # float32 사용
            brand_data['옵션입력'] = chunk.iloc[:, 4].fillna('').astype('string')
            
            # 필터링 전 데이터 상태 분석
            empty_brand = (brand_data['브랜드'].str.strip() == '').sum()
            nan_brand = (brand_data['브랜드'] == 'nan').sum()
            header_brand = (brand_data['브랜드'] == '브랜드').sum()
            empty_product = (brand_data['상품명'].str.strip() == '').sum()
            header_product = (brand_data['상품명'] == '상품명').sum()
            
            logger.info(f"필터링 전 분석 - 빈 브랜드: {empty_brand}, nan 브랜드: {nan_brand}, 헤더 브랜드: {header_brand}")
            logger.info(f"필터링 전 분석 - 빈 상품명: {empty_product}, 헤더 상품명: {header_product}")
            
            # 데이터 보존 모드에 따른 필터링
            if self.preserve_data:
                # 관대한 필터링 (데이터 보존 우선)
                mask = (
                    (brand_data['브랜드'].str.strip() != '') & 
                    (brand_data['브랜드'] != 'nan') &
                    (brand_data['브랜드'].str.lower() != '브랜드') &
                    (brand_data['상품명'].str.strip() != '') &
                    (brand_data['상품명'].str.lower() != '상품명') &
                    (~brand_data['브랜드'].isna()) &
                    (~brand_data['상품명'].isna())
                )
                logger.info("관대한 필터링 적용 (데이터 보존 우선)")
            else:
                # 엄격한 필터링 (기존 방식)
                mask = (
                    (brand_data['브랜드'].str.strip() != '') & 
                    (brand_data['브랜드'] != 'nan') &
                    (brand_data['브랜드'].str.lower() != '브랜드') &
                    (brand_data['상품명'].str.strip() != '') &
                    (brand_data['상품명'].str.lower() != '상품명') &
                    (~brand_data['브랜드'].isna()) &
                    (~brand_data['상품명'].isna()) &
                    (brand_data['공급가'] > 0)  # 공급가가 0보다 큰 경우만
                )
                logger.info("엄격한 필터링 적용")
            
            # 각 조건별 제외되는 항목 수 분석
            conditions = {
                '빈_브랜드': (brand_data['브랜드'].str.strip() == '').sum(),
                'nan_브랜드': (brand_data['브랜드'] == 'nan').sum(), 
                '헤더_브랜드': (brand_data['브랜드'].str.lower() == '브랜드').sum(),
                '빈_상품명': (brand_data['상품명'].str.strip() == '').sum(),
                '헤더_상품명': (brand_data['상품명'].str.lower() == '상품명').sum(),
                '브랜드_NA': brand_data['브랜드'].isna().sum(),
                '상품명_NA': brand_data['상품명'].isna().sum(),
            }
            
            if not self.preserve_data:
                conditions['공급가_0'] = (brand_data['공급가'] <= 0).sum()
            
            logger.info(f"필터링 조건별 제외 항목: {conditions}")
            
            brand_data = brand_data[mask]
            filtered_count = len(brand_data)
            
            logger.info(f"필터링 후: {filtered_count:,}개 (제거된 항목: {original_count - filtered_count:,}개)")
            
            # 샘플 데이터 확인 (처음 3개)
            if not brand_data.empty:
                sample_data = brand_data.head(3)[['브랜드', '상품명']].to_dict('records')
                logger.info(f"샘플 데이터: {sample_data}")
            
            # 인덱스 재설정 (중요! 브랜드 인덱스 오류 방지)
            brand_data = brand_data.reset_index(drop=True)
            
            return brand_data
            
        except Exception as e:
            logger.error(f"청크 처리 실패: {e}")
            return pd.DataFrame()
    
    def _get_fallback_data(self) -> pd.DataFrame:
        """브랜드매칭시트 읽기 실패 시 사용할 폴백 데이터"""
        fallback_data = pd.DataFrame({
            '브랜드': [
                '소예', '린도', '마마미', '로다제이', '바비',
                '보니토', '아르키드', '미미앤루', '니니벨로', '화이트스케치북',
                '키즈', '여름', '아동', '유아', '베이비'
            ],
            '상품명': [
                '테리헤어밴드', '세일러린넨바디수트', '클래식썸머셔츠', '코코넛슈트', '래쉬가드',
                '래쉬가드스윔세트', '슬립온', '티셔츠', '루비볼레로세트', '카고롱스커트',
                '래쉬가드', '원피스', '수영복', '티셔츠', '반바지'
            ],
            '옵션입력': [
                '사이즈{S,M,L}', '사이즈{80,90,100}', '사이즈{FREE}', '사이즈{S,M,L,XL}', '사이즈{5,7,9,11,13}',
                '사이즈{5,7,9,11,13}', '사이즈{150,160,170}', '사이즈{S,M,L}', '사이즈{90,100,110}', '사이즈{5,7,9,11,13}',
                '사이즈{5,7,9,11,13}', '사이즈{S,M,L}', '사이즈{90,100,110}', '사이즈{80,90,100}', '사이즈{S,M,L}'
            ],
            '공급가': [
                8000, 15000, 18000, 14000, 10000,
                20000, 30000, 12000, 16000, 8000,
                12000, 20000, 15000, 10000, 14000
            ],
            '중도매': [
                '소예패션', '린도키즈', '마마미브랜드', '로다제이', '바비브랜드',
                '보니토코리아', '아르키드', '미미앤루', '니니벨로', '화이트스케치북',
                '키즈패션', '여름브랜드', '아동복전문', '유아복몰', '베이비웨어'
            ]
        })
        
        logger.info(f"폴백 데이터 사용: {len(fallback_data)}개 상품")
        return fallback_data

# 전역 인스턴스
brand_sheets_api = BrandSheetsAPI() 