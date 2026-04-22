import pandas as pd
from db import supabase

url = "https://docs.google.com/spreadsheets/d/1v4hCcuQN_kiN8o0uC-ClMC-vN0seJpgzCEAYt3pGaB8/export?format=csv&gid=767032110"

df = pd.read_csv(url)

print(df.head())