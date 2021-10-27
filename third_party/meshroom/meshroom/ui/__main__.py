import signal
import sys
import os

dir_path = __file__
dir_path = os.path.dirname(dir_path)
dir_path = os.path.dirname(dir_path)
dir_path = os.path.dirname(dir_path)
sys.path.append(dir_path)
import meshroom

if __name__ == "__main__":
    meshroom.setupEnvironment()

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    from meshroom.ui.app import MeshroomApp
    app = MeshroomApp(sys.argv)
    app.exec_()
