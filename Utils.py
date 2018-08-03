def printWhenExecuting(fn):
    def fn2(self):
        print('Doing', fn.__name__, '...')
        fn(self)
        print('Done with', fn.__name__, '.')

    return fn2
