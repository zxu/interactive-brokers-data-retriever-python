import argparse
import datetime
import logging
import threading

from ibapi.order_condition import *

from App import App
from Prompter import historical_data_query_options


class Worker(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.app = app

    def run(self):
        self.app.run()
        print("Worker thread [%s] finished." % threading.get_ident())


def main():
    logging.getLogger().setLevel(logging.ERROR)
    logging.debug("now is %s", datetime.datetime.now())

    cmdLineParser = argparse.ArgumentParser("api tests")
    # cmdLineParser.add_option("-c", action="store_True", dest="use_cache", default = False, help = "use the cache")
    # cmdLineParser.add_option("-f", action="store", type="string", dest="file", default="", help="the input file")
    cmdLineParser.add_argument("-p", "--port", action="store", type=int,
                               dest="port", default=7497, help="The TCP port to use")
    cmdLineParser.add_argument("-C", "--global-cancel", action="store_true",
                               dest="global_cancel", default=False,
                               help="whether to trigger a globalCancel req")
    args = cmdLineParser.parse_args()
    print("Using args", args)
    logging.debug("Using args %s", args)

    # enable logging when member vars are assigned
    from ibapi import utils
    from ibapi.order import Order
    Order.__setattr__ = utils.setattr_log
    from ibapi.contract import Contract, DeltaNeutralContract
    Contract.__setattr__ = utils.setattr_log
    DeltaNeutralContract.__setattr__ = utils.setattr_log
    from ibapi.tag_value import TagValue
    TagValue.__setattr__ = utils.setattr_log
    TimeCondition.__setattr__ = utils.setattr_log
    ExecutionCondition.__setattr__ = utils.setattr_log
    MarginCondition.__setattr__ = utils.setattr_log
    PriceCondition.__setattr__ = utils.setattr_log
    PercentChangeCondition.__setattr__ = utils.setattr_log
    VolumeCondition.__setattr__ = utils.setattr_log

    event = threading.Event()
    app = App(event)
    try:
        if args.global_cancel:
            app.globalCancelOnly = True
        app.connect("127.0.0.1", args.port, clientId=0)
        print("serverVersion:%s connectionTime:%s" % (app.serverVersion(),
                                                      app.twsConnectionTime()))

        worker = Worker(app)
        worker.start()

        print("Wait for connection to be established...")
        event.wait(5)

        while True:
            try:
                if app.done and app.isConnected():
                    app.disconnect()
                    print("Disconnecting from TWS.")
                if not app.isConnected():
                    break

                from Prompter import build_contract, choose_action

                choice = choose_action()

                if choice == 'X':
                    raise EOFError

                if choice == "H":
                    contract = build_contract()
                    parameters = historical_data_query_options()
                    event.clear()
                    app.reqHistoricalData(4101, contract, **parameters)
            except KeyboardInterrupt:
                pass
            except (EOFError, SystemExit):
                event.clear()
                app.keyboardInterrupt()
            event.wait()
    except RuntimeError:
        logging.error("Unexpected error")
    except KeyboardInterrupt:
        app.disconnect()
        print("Exiting.")
    finally:
        print("Cleaning up...")
        app.dumpTestCoverageSituation()
        app.dumpReqAnsErrSituation()
        print('GoodBye!')


if __name__ == "__main__":
    main()
