import subprocess,time,httpx,os
from core.models import Scenario
for key in ['HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','http_proxy','https_proxy','all_proxy']:os.environ.pop(key,None)
procs=[]
try:
 for name,port in [('master',8001),('simulation',8002),('appraisal',8003),('portfolio',8004)]:
  procs.append(subprocess.Popen(['python','-m','uvicorn',f'services.{name}:app','--port',str(port)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL))
 for port in range(8001,8005):
  for attempt in range(100):
   try:
    assert httpx.get(f'http://127.0.0.1:{port}/health',trust_env=False).status_code==200;break
   except Exception:time.sleep(.1)
  else:raise RuntimeError('service did not start')
 r=httpx.post('http://127.0.0.1:8003/v1/appraise',json=Scenario().model_dump(),timeout=30);r.raise_for_status();assert 'appraisal' in r.json()
 assert httpx.get('http://127.0.0.1:8001/v1/master/lcs').json()['version']=='demo-1'
 os.environ['SERVICE_MODE']='remote'
 from streamlit.testing.v1 import AppTest
 at=AppTest.from_file(os.path.abspath('app.py'),default_timeout=30).run();assert not at.exception
 at.button[0].click().run();assert not at.exception and len(at.metric)==4
 at.button[1].click().run();assert not at.exception
 print('Four live services and remote Streamlit simulation/portfolio workflows passed')
finally:
 for p in procs:p.terminate()
 for p in procs:p.wait(timeout=10)
