from window_manager import single


def test_second_acquire_fails_while_the_first_holds(tmp_path):
    path = tmp_path / "run.lock"
    first = single.acquire(path)
    assert first is not None
    assert single.acquire(path) is None
    first.close()
    second = single.acquire(path)
    assert second is not None
    second.close()


def test_holder_pid_reports_the_running_instance(tmp_path):
    import os

    path = tmp_path / "run.lock"
    assert single.holder_pid(path) is None
    handle = single.acquire(path)
    assert single.holder_pid(path) == os.getpid()
    handle.close()
    assert single.holder_pid(path) is None
