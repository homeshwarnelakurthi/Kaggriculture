from pathlib import Path
import json
R=Path(__file__).resolve().parents[2];W=Path(__file__).parent
(W/'candidate.py').write_text((R/'outputs/v48/main.py').read_text()+'\n'+(W/'extension.py').read_text())
(W/'screen.json').write_text(json.dumps({'candidates':{'v50':str(W/'candidate.py'),'v48':str(R/'outputs/v48/main.py')},'opponents':{'wide':str(R/'work/v46/wide.py'),'v47':str(R/'outputs/v47/main.py')}}))
