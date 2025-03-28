import pandas as pd
import joblib

datos_test = [[0.181291],
              [0.035147],
              [1.000000],[0.989569],[0.988191],[-0.208158],[0.421778],[-0.098787],[0.431755],[0.835507]]

modelo = joblib.load("../modelos_prediccion/model_Corriente Motor Bomba Agua Alimentacion BFWP A (A).pkl")

# Función para hacer predicciones
def predecir_sensores(datos, model):
    # Convertir los datos a DataFrame (sin lista extra)
    df_nuevo = pd.DataFrame(datos)

    # Hacer la predicción
    prediccion = model.predict(df_nuevo)

    return prediccion

print(predecir_sensores(datos_test, modelo))
