import concurrent.futures

class TimeoutError(Exception):
    """Raised when the generator does not yield within the timeout."""
    pass

class TimedGenerator:
    def __init__(self, gen, timeout):
        """
        Wrap a generator with timeout-based iteration.

        :param gen: A generator object
        :param timeout: Seconds to wait for each yield before raising TimeoutError
        """
        self._gen = gen
        self._timeout = timeout
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

    def __iter__(self):
        return self

    def __next__(self):
        """Get the next item from the generator with a timeout."""
        future = self._executor.submit(next, self._gen, None)  # None marks exhaustion
        try:
            item = future.result(timeout=self._timeout)
        except concurrent.futures.TimeoutError:
            raise TimeoutError(f"No yield within {self._timeout} seconds")

        if item is None:  # exhausted
            self._executor.shutdown(wait=False, cancel_futures=True)
            raise StopIteration
        return item

    def close(self):
        """Manually close the generator and shutdown the executor."""
        if self._gen:
            self._gen.close()
        self._executor.shutdown(wait=False, cancel_futures=True)

    def __del__(self):
        self.close()