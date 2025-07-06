# Advanced Project: DevOps AI Assistant Dashboard
# Combines Streamlit + Linux + Docker + Agentic AI + ML in one full-stack dashboard

import streamlit as st
import paramiko
import docker
import openai
import psutil
import subprocess
import pandas as pd
import platform

# ------------------ CONFIGURATION ------------------
openai.api_key = "YOUR_OPENAI_API_KEY"
DOCKER_CLIENT = docker.from_env()
LINUX_HOST = "your.server.ip"
SSH_USER = "your_ssh_user"
SSH_KEY_PATH = "/path/to/private/key.pem"

# ------------------ HELPER FUNCTIONS ------------------
def run_ssh_command(command):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(LINUX_HOST, username=SSH_USER, key_filename=SSH_KEY_PATH)
        stdin, stdout, stderr = ssh.exec_command(command)
        return stdout.read().decode(), stderr.read().decode()
    except Exception as e:
        return str(e), ""

def get_system_info():
    return {
        "OS": platform.system(),
        "CPU Usage": f"{psutil.cpu_percent()}%",
        "Memory Usage": f"{psutil.virtual_memory().percent}%",
        "Disk Usage": f"{psutil.disk_usage('/').percent}%"
    }

def list_docker_containers():
    try:
        containers = DOCKER_CLIENT.containers.list(all=True)
        return [(c.name, c.status, c.image.tags) for c in containers]
    except Exception as e:
        return [("Docker Error", str(e), [])]

def openai_agent(prompt):
    try:
        res = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a DevOps AI assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"AI Error: {str(e)}"

# ------------------ STREAMLIT UI ------------------
st.set_page_config("DevOps AI Assistant Dashboard", layout="wide")
st.title("🚀 DevOps AI Assistant Dashboard")

# --- System Info Section ---
st.subheader("🔍 System Metrics")
system_info = get_system_info()
col1, col2, col3, col4 = st.columns(4)
col1.metric("OS", system_info['OS'])
col2.metric("CPU Usage", system_info['CPU Usage'])
col3.metric("Memory Usage", system_info['Memory Usage'])
col4.metric("Disk Usage", system_info['Disk Usage'])

# --- Docker Containers ---
st.subheader("🐳 Docker Container Status")
containers = list_docker_containers()
container_df = pd.DataFrame(containers, columns=["Name", "Status", "Image"])
st.dataframe(container_df, use_container_width=True)

# --- Linux Command Executor ---
st.subheader("🖥️ Remote Linux Command Execution")
cmd = st.text_input("Enter shell command to execute on remote Linux server:")
if st.button("Execute"):
    output, error = run_ssh_command(cmd)
    st.text_area("Output", output, height=200)
    if error:
        st.error(f"Error: {error}")

# --- Agentic AI Assistant ---
st.subheader("🤖 Ask DevOps AI Assistant")
ai_input = st.text_area("Ask me anything about Linux, Docker, Logs, or Commands:")
if st.button("Get Help from AI"):
    ai_response = openai_agent(ai_input)
    st.markdown("### 💡 AI Response")
    st.success(ai_response)

# --- Footer ---
st.markdown("---")
st.caption("Made with ❤️ by Sayeed Firoz, combining Streamlit, Docker, Linux, OpenAI GPT-4, and ML logic")
