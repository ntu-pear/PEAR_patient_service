# conftest.py
import threading
import sys
import traceback
import pytest

def dump_thread_stacks():
    for thread in threading.enumerate():
        print(f"\n--- Thread: {thread.name} --- daemon={thread.daemon}")
        if thread.ident is None:
            continue
        stack = sys._current_frames().get(thread.ident)
        if stack:
            traceback.print_stack(stack)

@pytest.fixture(scope="session", autouse=True)
def debug_threads_and_stacks():
    yield
    print("\n=== Remaining threads at pytest end ===")
    dump_thread_stacks()
