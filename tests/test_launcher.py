from contextlib import contextmanager
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


@contextmanager
def wait_for_windows_process(pid):
    """Pin the live server handle before shutdown, then wait for actual process exit.

    Removing state.json signals server cleanup, but Python can still hold its
    working directory open until final interpreter teardown. Windows will not
    delete that directory while it is held. No delay or ignored cleanup errors.
    """
    if os.name != 'nt':
        yield
        return
    import ctypes
    from ctypes import wintypes

    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.WaitForSingleObject.argtypes = (wintypes.HANDLE, wintypes.DWORD)
    kernel.WaitForSingleObject.restype = wintypes.DWORD
    kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
    kernel.CloseHandle.restype = wintypes.BOOL
    handle = kernel.OpenProcess(0x00100000, False, pid)  # SYNCHRONIZE only
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        yield
        result = kernel.WaitForSingleObject(handle, 10000)
        if result == 0xFFFFFFFF:
            raise ctypes.WinError(ctypes.get_last_error())
        if result != 0:  # WAIT_OBJECT_0
            raise AssertionError('Test server did not exit within 10 seconds')
    finally:
        kernel.CloseHandle(handle)


class LauncherTests(unittest.TestCase):
    def test_fresh_start_reuse_and_shutdown_in_path_with_spaces(self):
        # Repeat the lifecycle to exercise the intermittent Windows teardown race.
        for attempt in range(5):
            with self.subTest(attempt=attempt):
                self.check_lifecycle()

    def check_lifecycle(self):
        with tempfile.TemporaryDirectory(prefix='transkript test ') as directory:
            root = Path(directory)
            shutil.copyfile(ROOT / 'start.py', root / 'start.py')
            shutil.copytree(ROOT / 'app', root / 'app', ignore=shutil.ignore_patterns('__pycache__'))
            http = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            state = None
            try:
                for _ in range(2):
                    subprocess.run([sys.executable, str(root / 'start.py'), '--no-open'], check=True, timeout=30)
                    current = json.loads((root / '.runtime/state.json').read_text(encoding='utf-8'))
                    if state:
                        self.assertEqual(current, state)
                    state = current
                request = urllib.request.Request(f"http://127.0.0.1:{state['port']}/health", headers={'X-Session': state['token']})
                with http.open(request, timeout=5) as response:
                    self.assertEqual(json.load(response)['version'], '1.0.2')
            finally:
                if state:
                    # Acquire the handle while the process is definitely alive;
                    # a PID-only poll after shutdown could observe a reused PID.
                    with wait_for_windows_process(state['pid']):
                        request = urllib.request.Request(f"http://127.0.0.1:{state['port']}/shutdown", data=b'{}', headers={'X-Session': state['token'], 'Content-Type': 'application/json'})
                        with http.open(request, timeout=5) as response:
                            self.assertTrue(json.load(response)['ok'])
                        for _ in range(100):
                            if not (root / '.runtime/state.json').exists():
                                break
                            time.sleep(.05)
                        self.assertFalse((root / '.runtime/state.json').exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
