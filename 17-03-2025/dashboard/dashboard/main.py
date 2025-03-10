import os
import requests
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go

# Variabile d'ambiente per il backend; se non definita, usa il default
BACKEND_URL = os.getenv("BASE_BACKEND_URL", "http://localhost:8000")

# Recuperiamo la lista dei sensori dalla API all'avvio dell'app
try:
    response = requests.get(f"{BACKEND_URL}/sensors")
    sensors = response.json()
except Exception as e:
    print("Errore nel recupero dei sensori:", e)
    sensors = []

# Costruiamo le opzioni per il dropdown raggruppando per nome (evitiamo duplicati)
dropdown_options = []
sensor_names = set()
for sensor in sensors:
    if isinstance(sensor, dict):
        sensor_name = sensor.get('name', 'Senza nome')
        if sensor_name not in sensor_names:
            sensor_names.add(sensor_name)
            dropdown_options.append({
                'label': sensor_name,
                'value': sensor_name  # Usare il nome come identificatore
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
    # Aggiornamento automatico ogni 2 secondi per il grafico
    dcc.Interval(id='interval-component', interval=2000, n_intervals=0),
    # Aggiornamento automatico ogni 5 secondi per il dropdown
    dcc.Interval(id='dropdown-interval', interval=5000, n_intervals=0),
    # Conserviamo in memoria lo storico dei dati per il sensore selezionato, utilizzando il nome
    dcc.Store(id='sensor-store', data={"sensor_name": None, "timestamps": [], "values": []})
], fluid=True)

# Callback per aggiornare il grafico in tempo reale
@app.callback(
    Output('sensor-store', 'data'),
    Output('sensor-graph', 'figure'),
    Input('interval-component', 'n_intervals'),
    State('sensor-dropdown', 'value'),
    State('sensor-store', 'data'),
)
def update_graph(n_intervals, sensor_name, store_data):
    # Se non è stato selezionato alcun sensore, restituisco un grafico vuoto
    if sensor_name is None:
        return store_data, go.Figure(data=[], layout=go.Layout(template='plotly_white'))
    
    # Se l'utente ha cambiato sensore (nome), ripuliamo lo storico
    if store_data.get("sensor_name") != sensor_name:
        store_data = {"sensor_name": sensor_name, "timestamps": [], "values": []}

    try:
        # Effettuiamo una richiesta al nuovo endpoint passando il nome del sensore
        res = requests.get(f"{BACKEND_URL}/sensors/by_name/{sensor_name}")
        sensor_data = res.json()  # Ci aspettiamo una lista di record
        # Ordiniamo la lista in base al timestamp (opzionale, se non già ordinata)
        sensor_data.sort(key=lambda record: record.get('timestamp'))
        
        # Aggiorniamo lo store con tutti i record ricevuti
        store_data["timestamps"] = [record.get("timestamp") for record in sensor_data]
        store_data["values"] = [record.get("value") for record in sensor_data]
    except Exception as e:
        print("Errore nel recupero del sensore:", e)

    # Creiamo il grafico con i dati aggiornati
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
        title=f"Sensor {sensor_name} in tempo reale",
        xaxis_title="Timestamp",
        yaxis_title="Valore",
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return store_data, fig

# Callback per aggiornare le opzioni del dropdown (anche qui raggruppando per nome)
@app.callback(
    Output('sensor-dropdown', 'options'),
    Input('dropdown-interval', 'n_intervals')
)
def update_dropdown(n_intervals):
    print("---------------------------- aggiornamento dropdown")
    try:
        response = requests.get(f"{BACKEND_URL}/sensors")
        sensors = response.json()
    except Exception as e:
        print("Errore nel recupero dei sensori:", e)
        sensors = []
    options = []
    sensor_names = set()
    for sensor in sensors:
        if isinstance(sensor, dict):
            sensor_name = sensor.get('name', 'Senza nome')
            if sensor_name not in sensor_names:
                sensor_names.add(sensor_name)
                options.append({
                    'label': sensor_name,
                    'value': sensor_name
                })
        else:
            print("Formato sensore inatteso:", sensor)
    
    return options

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
