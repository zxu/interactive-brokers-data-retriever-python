from prompt_toolkit import PromptSession, HTML
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.styles import Style

style = Style.from_dict({
    'completion-menu.completion': 'bg:#008888 #ffffff',
    'completion-menu.completion.current': 'bg:#00aaaa #000000',
    'scrollbar.background': 'bg:#88aaaa',
    'scrollbar.button': 'bg:#222222',
    'eg': '#FFFFFF bg:#454545 bold'
})


class Question:
    def __init__(self, title, attribute, possible_answers):
        self.title = title
        self.attribute = attribute
        self.possible_answers = possible_answers

    def ask(self):
        session = PromptSession()
        completer = WordCompleter(self.possible_answers, ignore_case=True)
        return session.prompt(HTML(self.title + ': '), completer=completer, style=style).strip()


def choose_action():
    """
    Create a `PromptSession` object for the user to choose the 'main action', i.e.,
    loading historical data, retrieve real-time data, etc.
    """
    bindings = KeyBindings()

    @bindings.add('h')
    @bindings.add('H')
    def historical(event):
        session.default_buffer.text = 'h'
        event.app.exit(result='H')

    @bindings.add('r')
    @bindings.add('R')
    def realtime(event):
        session.default_buffer.text = 'r'
        event.app.exit(result='R')

    @bindings.add(Keys.Any)
    def _(event):
        event.app.exit(result='X')

    print('\r')
    print('\r')
    print('\r')
    print('===================================')
    print('    Welcome to Market Data Tool    ')
    print('===================================')
    print('\r')

    prompt_string = '{:20}{:30}\r'.format('<b>H</b> -', 'Historical data')
    prompt_string += '{:20}{:30}\r'.format('<b>R</b> -', 'Real-time data')
    prompt_string += '{:20}{:30}\r\r'.format('<b>Other keys</b> -', 'Exit')
    prompt_string += 'Please make your choice: '

    session = PromptSession(HTML(prompt_string), key_bindings=bindings)
    return session.prompt()


def build_contract():
    from ibapi.contract import Contract

    contract = Contract()
    questions = [
        Question('Security symbol', 'symbol', ['SPX', 'SPY', 'AMZN']),
        Question('Security type', 'secType', ['IND', 'STK', 'FUND']),
        Question('Currency', 'currency', ['USD', 'AUD', 'EUR']),
        Question('Exchange', 'exchange', ['CBOE', 'ISLAND']),
    ]

    print('\r')
    print('What contract are we interested in?')
    print('\r')
    for question in questions:
        while True:
            try:
                answer = question.ask()
                break
            except KeyboardInterrupt:
                pass
        setattr(contract, question.attribute, answer)

        print(contract)
    return contract


def historical_data_query_options():
    questions = [
        Question('End datetime, e.g., <eg>20160127 23:59:59</eg>', 'endDateTime', []),
        Question('Duration, e.g., <eg>5 D</eg>, <eg>1 M</eg>, <eg>1 Y</eg>', 'durationStr', []),
        Question('Bar size, e.g., <eg>5 mins</eg>, <eg>1 hour</eg>, <eg>1 day</eg>', 'barSizeSetting',
                 ['5 mins', '10 mins', '15 mins', '20 mins', '30 mins',
                  '1 hour', '2 hours', '3 hours', '4 hours', '8 hours',
                  '1 day', '1 week', '1 month']),
        Question('What to show, e.g., <eg>TRADES</eg>, <eg>MIDPOINT</eg>, <eg>BID</eg>, <eg>ASK</eg>', 'whatToShow',
                 ['TRADES', 'MIDPOINT', 'BID', 'ASK'])
    ]

    print('\r')
    print('Now please make some choices on the query.')
    print('\r')

    parameters = dict()
    for question in questions:
        while True:
            try:
                answer = question.ask()
                break
            except KeyboardInterrupt:
                pass
        parameters.update({question.attribute: answer})

    # print(parameters)

    parameters.update({'useRTH': 1, 'formatDate': 1, 'keepUpToDate': False, 'chartOptions': []})
    return parameters
