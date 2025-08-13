import pytest, threading

@pytest.fixture(scope="session", autouse=True)
def debug_threads_at_end():
    yield
    print("\n=== Remaining threads at pytest end ===")
    for t in threading.enumerate():
        print(f"{t.name} (daemon={t.daemon})")
