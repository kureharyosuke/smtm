"""시뮬레이션에 사용되는 모듈들을 연동하여 시뮬레이션을 운영"""

import time
from datetime import datetime
from .log_manager import LogManager
from .operator import Operator


class SimulationOperator(Operator):
    """
    각 모듈을 연동해 시뮬레이션을 진행하는 클래스
    """

    def __init__(self):
        super().__init__()
        self.logger = LogManager.get_logger(__class__.__name__)
        self.turn = 0
        self.end = "2020-12-20T16:23:00"
        self.count = 0
        self.budget = 0
        self.last_report = None

    def initialize(
        self,
        data_provider,
        strategy,
        trader,
        analyzer,
        end=None,
        count=100,
        budget=500,
    ):
        """
        시뮬레이션에 사용될 각 모듈을 전달 받아 초기화를 진행한다

        end: 언제까지의 거래기간 정보를 사용할 것인지에 대한 날짜 시간 정보 yyyy-MM-dd HH:mm:ss
        count: 사용될 거래 정도 갯수
        budget: 사용될 예산
        """
        if self.state is not None:
            return

        self.data_provider = data_provider
        self.strategy = strategy
        self.trader = trader
        self.analyzer = analyzer
        self.state = "ready"
        self.strategy.initialize(budget)
        self.analyzer.initialize(trader.get_account_info, True)

        if end is not None:
            self.end = end
        self.count = count
        self.budget = budget
        end_str = self.end.replace(" ", "T")
        end_str = end_str.replace(":", "")
        self.tag = datetime.now().strftime("%Y%m%d-%H%M%S") + "-simulation"

        try:
            data_provider.initialize_from_server(end=end, count=count)
            trader.initialize(end=end, count=count, budget=budget)
        except (AttributeError, UserWarning) as msg:
            self.state = None
            self.logger.error(f"initialize fail: {msg}")
            return

    def _excute_trading(self, task):
        """자동 거래를 실행 후 타이머를 실행한다

        simulation_terminated 상태는 시뮬레이션에만 존재하는 상태로서 시뮬레이션이 끝났으나
        Operator는 중지되지 않은 상태. Operator의 시작과 중지는 외부부터 실행되어야 한다.
        """
        self.logger.info(
            f"##################### trading is started : {self.turn + 1} / {int(self.count) - 1}"
        )
        self.is_timer_running = False
        try:
            trading_info = self.data_provider.get_info()
            self.strategy.update_trading_info(trading_info)
            self.analyzer.put_trading_info(trading_info)

            def send_request_callback(result):
                self.logger.debug("send_request_callback is called")
                if result["msg"] == "game-over":
                    self.last_report = self.analyzer.create_report(tag=self.tag)
                    self.state = "simulation_terminated"
                    return
                self.strategy.update_result(result)
                self.analyzer.put_result(result)

            target_request = self.strategy.get_request()

            if target_request is not None:
                self.trader.send_request(target_request, send_request_callback)
                self.analyzer.put_request(target_request)
        except AttributeError:
            self.logger.error("excuting fail")

        self.turn += 1
        self.logger.debug("##################### trading is completed")
        self._start_timer()
        return True

    def get_score(self, callback):
        """현재 수익률을 인자로 전달받은 콜백함수를 통해 전달한다
        시뮬레이션이 종료된 경우 마지막 수익률 전달한다

        Returns:
        (
            start_budget: 시작 자산
            final_balance: 최종 자산
            cumulative_return : 기준 시점부터 누적 수익률
            price_change_ratio: 기준 시점부터 보유 종목별 가격 변동률 딕셔너리
        )
        """

        if self.state != "running":
            self.logger.debug(f"already terminated return last report")
            callback(self.last_report["summary"])
            return

        def get_and_return_score(task):
            try:
                task["callback"](self.analyzer.get_return_report())
            except TypeError:
                self.logger.error("invalid callback")

        self.worker.post_task({"runnable": get_and_return_score, "callback": callback})

    def start(self):
        if self.state != "ready":
            return False
        try:
            self.analyzer.make_start_point()
        except AttributeError:
            self.logger.error("make start point fail")
        return super().start()
