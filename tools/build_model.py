"""Generate the generic workbook and its catalog from immutable local sources."""
from pathlib import Path
import argparse
import json
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tca_bp.model_build import build_model

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path)
    parser.add_argument('--force',action='store_true',help='Rebuild generated assets only; never modifies the reference.')
    args=parser.parse_args()
    print(json.dumps(build_model(ROOT,args.output_dir,force=args.force),ensure_ascii=False,indent=2))
    return 0

if __name__=='__main__':raise SystemExit(main())
