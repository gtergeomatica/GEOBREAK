import os
import requests
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go

# Variabile d'ambiente per il backend; se non definita, usa il default
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Recuperiamo la lista dei sensori dalla API all'avvio dell'app
try:
    response = requests.get(f"{BACKEND_URL}/sensors")
    sensors = response.json()
except Exception as e:
    print("Errore nel recupero dei sensori:", e)
    sensors = []

# Costruiamo le opzioni per il dropdown usando l'id e il nome del sensore
dropdown_options = []
for sensor in sensors:
    if isinstance(sensor, dict):
        dropdown_options.append({
            'label': f"{sensor.get('id', 'N/D')} - {sensor.get('name', 'Senza nome')}",
            'value': sensor.get('id')
        })
    else:
        print("Formato sensore inatteso:", sensor)


# Inizializziamo l'app Dash utilizzando un tema Bootstrap moderno
external_stylesheets = [dbc.themes.FLATLY]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "GEOBREAK"

# Layout della dashboard
app.layout = dbc.Container([
    dbc.Row(
        dbc.Col(
            html.H1("GEOBREAK", className="text-center text-primary my-4"),
            width=12
        )
    ),
    dbc.Row(
        dbc.Col(
            dcc.Dropdown(
                id='sensor-dropdown',
                options=dropdown_options,
                placeholder="Seleziona un sensore",
                style={'width': '100%'}
            ),
            width=6, className="mb-4 offset-md-3 text-center"
        )
    ),
    dbc.Row(
        dbc.Col(
            dcc.Graph(id='sensor-graph', config={'displayModeBar': False}),
            width=12
        )
    ),
    # Aggiornamento automatico ogni 2 secondi
    dcc.Interval(id='interval-component', interval=2000, n_intervals=0),
    # Conserviamo in memoria lo storico dei dati per il sensore selezionato
    dcc.Store(id='sensor-store', data={"sensor_id": None, "timestamps": [], "values": []})
], fluid=True)

# Callback per aggiornare il grafico in tempo reale
@app.callback(
    Output('sensor-store', 'data'),
    Output('sensor-graph', 'figure'),
    Input('interval-component', 'n_intervals'),
    State('sensor-dropdown', 'value'),
    State('sensor-store', 'data'),
)
def update_graph(n_intervals, sensor_id, store_data):
    # Se non è stato selezionato alcun sensore, restituisco un grafico vuoto
    if sensor_id is None:
        return store_data, go.Figure(data=[], layout=go.Layout(template='plotly_white'))
    
    # Se l'utente ha cambiato il sensore, ripuliamo lo storico
    if store_data.get("sensor_id") != sensor_id:
        store_data = {"sensor_id": sensor_id, "timestamps": [], "values": []}

    # Effettuiamo una richiesta all'API per ottenere i dati aggiornati del sensore
    try:
        res = requests.get(f"{BACKEND_URL}/sensors/{sensor_id}")
        sensor = res.json()
        # Preleviamo il timestamp e il valore dal sensore
        timestamp = sensor.get('timestamp')
        value = sensor.get('value')
        store_data["timestamps"].append(timestamp)
        store_data["values"].append(value)
    except Exception as e:
        print("Errore nel recupero del sensore:", e)

    # Creiamo il grafico con stile moderno
    fig = go.Figure(
        data=go.Scatter(
            x=store_data["timestamps"],
            y=store_data["values"],
            mode='lines+markers',
            line=dict(color='royalblue', width=2),
            marker=dict(size=6)
        )
    )
    fig.update_layout(
        title=f"Sensor {sensor_id} in tempo reale",
        xaxis_title="Timestamp",
        yaxis_title="Valore",
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return store_data, fig

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
