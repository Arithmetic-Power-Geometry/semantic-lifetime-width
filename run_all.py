from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from slw.experiments import run_experiments
if __name__=='__main__':
    print(run_experiments(ROOT/'results'))
