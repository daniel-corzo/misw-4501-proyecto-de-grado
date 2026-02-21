from locust import HttpUser, task, between

class ViajeroAgresivo(HttpUser):
    # Sin tiempo de espera: el usuario virtual disparará peticiones como ametralladora
    wait_time = between(0.0, 0.0)

    @task
    def saturar_busqueda(self):
        # Hacemos la petición e interceptamos la respuesta
        with self.client.get("/buscar", catch_response=True) as response:
            if response.status_code == 200:
                # Petición procesada normalmente (debería tardar ~500ms)
                response.success()
            elif response.status_code == 429:
                # El Rate Limiter nos bloqueó. Para el experimento, esto es un ÉXITO.
                # (Debería responder en ~2ms, liberando al servidor)
                response.success()
            else:
                # Cualquier otro código (ej. 500, 502) es un fallo real
                response.failure(f"Fallo real del sistema: {response.status_code}")