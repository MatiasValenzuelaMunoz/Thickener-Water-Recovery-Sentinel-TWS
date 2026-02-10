import pandas as pd

df = pd.read_parquet("data/processed/thickener_timeseries.parquet")

# ¿cuántos eventos caen dentro de régimen FLOC?
ev_in_floc = df[(df["event_now"]==1) & (df["Regime"]=="FLOC")]
print("events_in_floc_points:", len(ev_in_floc))

# distribución event_type durante eventos
print(df[df["event_now"]==1]["event_type"].value_counts(normalize=True))

# diagnóstico del umbral: cuánto vale floc_c durante eventos en FLOC
# (no guardamos floc_c; como proxy, mira déficit efectivo)
# df["floc_deficit_proxy"] = ...  # si quieres, lo agrego como columna persistente.