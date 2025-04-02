import os
from smtm import (
    SimulationOperator,
    StrategyBuyAndHold,
    StrategySma0,
    StrategyRsi,
    SimulationTrader,
    SimulationDataProvider,
    Analyzer,
    Config,
)

def run_simulation(currency="BTC", strategy_type="sma"):
    # 전략 선택
    if strategy_type == "buy_and_hold":
        strategy = StrategyBuyAndHold()
    elif strategy_type == "sma":
        strategy = StrategySma0()
    elif strategy_type == "rsi":
        strategy = StrategyRsi()
    else:
        raise ValueError("Invalid strategy type")

    # 시뮬레이션 설정
    budget = 1000000  # 초기 예산 (100만원)
    interval = 60  # 거래 간격 (분)
    market = f"{currency}USDT"  # 시장 이름 (예: BTCUSDT)

    # 데이터 준비
    Config.simulation_source = "binance"  # binance 데이터 사용
    data_provider = SimulationDataProvider(currency=currency, interval=interval)
    data_provider.initialize_simulation(
        end="2024-03-29T00:00:00",  # 종료 시점
        count=8760,  # 1년치 데이터 (365일 * 24시간)
    )
    
    # 트레이더 초기화
    trader = SimulationTrader()
    trader.initialize(market, budget)
    
    # 분석기 초기화
    analyzer = Analyzer()
    analyzer.initialize(market)
    
    # 시뮬레이션 운영자 설정
    operator = SimulationOperator()
    operator.initialize(
        data_provider,
        strategy,
        trader,
        analyzer,
        budget,
    )
    
    # 시뮬레이션 실행
    operator.start()
    while operator.state == "running":
        pass
    
    # 결과 반환
    return operator.get_score(lambda x: print(f"Final Result: {x}"))

if __name__ == "__main__":
    # 테스트할 통화 쌍
    currencies = ["BTC", "ETH", "XRP"]
    strategies = ["sma", "rsi", "buy_and_hold"]
    
    for currency in currencies:
        print(f"\nTesting with {currency}")
        for strategy in strategies:
            print(f"\nStrategy: {strategy}")
            run_simulation(currency, strategy) 