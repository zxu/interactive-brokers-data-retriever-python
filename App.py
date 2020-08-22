import collections
import logging
import threading
import time
import pandas as pd

from ibapi.common import TickerId, BarData
from ibapi.utils import iswrapper

from Client import Client
from Utils import printWhenExecuting
from Wrapper import Wrapper


class App(Wrapper, Client):
    done: bool

    def __init__(self, event: threading.Event):
        Wrapper.__init__(self)
        Client.__init__(self, wrapper=self)
        self.started = False
        self.nextValidOrderId = None
        self.permId2ord = {}
        self.reqId2nErr = collections.defaultdict(int)
        self.globalCancelOnly = False
        self.simplePlaceOid = None
        self.event = event
        self.df = pd.DataFrame(columns=["reqId", "bar.date", "bar.open",
                                        "bar.high", "bar.low", "bar.close", "bar.volume",
                                        "bar.barCount", "bar.average"])
        self.idx = -1

    def dumpTestCoverageSituation(self):
        for clntMeth in sorted(self.clntMeth2callCount.keys()):
            logging.debug("ClntMeth: %-30s %6d" % (clntMeth,
                                                   self.clntMeth2callCount[clntMeth]))

        for wrapMeth in sorted(self.wrapMeth2callCount.keys()):
            logging.debug("WrapMeth: %-30s %6d" % (wrapMeth,
                                                   self.wrapMeth2callCount[wrapMeth]))

    def dumpReqAnsErrSituation(self):
        logging.debug("%s\t%s\t%s\t%s" % ("ReqId", "#Req", "#Ans", "#Err"))
        for reqId in sorted(self.reqId2nReq.keys()):
            nReq = self.reqId2nReq.get(reqId, 0)
            nAns = self.reqId2nAns.get(reqId, 0)
            nErr = self.reqId2nErr.get(reqId, 0)
            logging.debug("%d\t%d\t%s\t%d" % (reqId, nReq, nAns, nErr))

    @iswrapper
    def connectAck(self):
        if self.asynchronous:
            self.startApi()

    @iswrapper
    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)

        logging.debug("setting nextValidOrderId: %d", orderId)
        self.nextValidOrderId = orderId

        self.event.set()

    def keyboardInterrupt(self):
        self.stop()
        time.sleep(1)
        self.done = True
        self.event.set()

    def stop(self):
        print("Executing cancels")
        self.historicalDataRequests_cancel()
        self.event.set()

    def nextOrderId(self):
        oid = self.nextValidOrderId
        self.nextValidOrderId += 1
        return oid

    @iswrapper
    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        if errorCode not in (2104, 2106, 366):
            super().error(reqId, errorCode, errorString)
            print("Error. Id: ", reqId, " Code: ", errorCode, " Msg: ", errorString)
        if errorCode == 321 or errorCode == 200:
            self.historicalDataRequests_cancel()
            self.event.set()

    @iswrapper
    def winError(self, text: str, lastError: int):
        super().winError(text, lastError)

    @printWhenExecuting
    def historicalDataRequests_cancel(self):
        # Canceling historical data requests
        self.cancelHistoricalData(4101)

    @iswrapper
    def historicalData(self, reqId: int, bar: BarData):
        print("HistoricalData. ", reqId, " Date:", bar.date, "Open:", bar.open,
              "High:", bar.high, "Low:", bar.low, "Close:", bar.close, "Volume:", bar.volume,
              "Count:", bar.barCount, "WAP:", bar.average)

        self.idx = self.idx + 1
        self.df.loc[self.idx] = [reqId, bar.date, bar.open,
                                                bar.high, bar.low, bar.close, bar.volume,
                                                bar.barCount, bar.average]

    @iswrapper
    def historicalDataEnd(self, reqId: int, start: str, end: str):
        super().historicalDataEnd(reqId, start, end)
        print("HistoricalDataEnd ", reqId, "from", start, "to", end)

        self.event.set()

        self.df.to_csv('historical.csv')
        self.df = self.df[0:0]
        self.idx = -1

    @iswrapper
    def historicalDataUpdate(self, reqId: int, bar: BarData):
        print("HistoricalDataUpdate. ", reqId, " Date:", bar.date, "Open:", bar.open,
              "High:", bar.high, "Low:", bar.low, "Close:", bar.close, "Volume:", bar.volume,
              "Count:", bar.barCount, "WAP:", bar.average)

        self.idx = self.idx + 1
        self.df.loc[self.idx] = [reqId, bar.date, bar.open,
                                                bar.high, bar.low, bar.close, bar.volume,
                                                bar.barCount, bar.average]
