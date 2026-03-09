from locust import HttpUser, task, between

class ViajeroUser(HttpUser):
    # Simulamos el comportamiento natural: el usuario "piensa" entre 1 y 2 segundos
    wait_time = between(1.0, 2.0)

    @task
    def hacer_reserva(self):
        # Apuntamos a Nginx (puerto 80 por defecto)
        with self.client.post("/reservas", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Error {response.status_code}")