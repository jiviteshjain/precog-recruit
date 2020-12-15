#%%
import argparse
import camelot
import pandas as pd

# %%

tables = camelot.read_pdf('../../data/task-3a/EICHERMOT.pdf',
                          flavor='stream', table_areas=['310,650,595,550'])
print(tables)

# %%
display(tables[0].df)
# %%

plt = camelot.plot(tables[0], kind='text')





















# %%
raise SystemExit
tables = camelot.read_pdf('../../data/task-3a/EICHERMOT.pdf',
                          flavor='stream', table_areas=['0,570,300,500'], row_tol=14, strip_text='\n')  # Eichermot left
