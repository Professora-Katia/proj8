import subprocess

# Iniciar o Flask
flask = subprocess.Popen(["python", "app.py"])

# Iniciar o Streamlit
streamlit_est=subprocess.Popen(["python", "-m", "streamlit", "run", "appS.py"])
streamlit_op = subprocess.Popen(["python", "-m", "streamlit", "run", "appPO.py"])

try:
    flask.wait()
    streamlit_est.wait()
    streamlit_op.wait()
except KeyboardInterrupt:
    flask.terminate()
    streamlit_est.terminate()
    streamlit_op.terminate()

# python starserver.py