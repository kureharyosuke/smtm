from datetime import datetime, timedelta
import pandas as pd
from smtm import Config
from smtm.data.data_repository import DataRepository

def initialize_database():
    # 데이터베이스 설정
    Config.simulation_source = "binance"
    repo = DataRepository("smtm.db", interval=60, source=Config.simulation_source)
    
    # 데이터 파일 경로
    data_files = {
        "BTC": "../../data/BTC_USDT_1h_20240329_20250329.csv",
        "ETH": "../../data/ETH_USDT_1h_20240329_20250329.csv",
        "XRP": "../../data/XRP_USDT_1h_20240329_20250329.csv"
    }
    
    # 각 통화별로 데이터 로드 및 저장
    for currency, file_path in data_files.items():
        print(f"Loading data for {currency} from {file_path}")
        
        try:
            # CSV 파일 읽기
            df = pd.read_csv(file_path)
            print(f"CSV columns: {df.columns.tolist()}")
            
            # 데이터베이스에 저장
            for _, row in df.iterrows():
                data = {
                    "market": f"{currency}USDT",
                    "date_time": datetime.fromtimestamp(row["time"] / 1000).strftime("%Y-%m-%dT%H:%M:%S"),
                    "opening_price": float(row["open"]),
                    "high_price": float(row["high"]),
                    "low_price": float(row["low"]),
                    "closing_price": float(row["close"]),
                    "acc_price": float(row["volume"] * row["close"]),  # 거래량 * 종가
                    "acc_volume": float(row["volume"])
                }
                repo.save_data(data)
            
            print(f"Saved data for {currency}")
        except Exception as e:
            print(f"Error processing {currency}: {str(e)}")

if __name__ == "__main__":
    initialize_database() 