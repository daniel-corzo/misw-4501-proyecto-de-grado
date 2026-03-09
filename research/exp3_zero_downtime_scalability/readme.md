## 2. Resultados y Decisión Arquitectónica

* **Fecha de ejecución:** 26 de Febrero de 2026
* **Ejecutado por:** Equipo de Arquitectura
* **Resultado empírico:** Durante el incremento de carga simulando 3.600 usuarios concurrentes, el sistema alcanzó una tasa sostenida de **902.1 RPS**. En ese momento, se adicionaron dinámicamente nuevos nodos al clúster. Contrario a los resultados esperados (100% de éxito), se registró una **tasa de fallos del 61%**. 
  El riesgo técnico identificado en la hipótesis se materializó: aunque el mecanismo de *Service Discovery* local identificó las nuevas instancias, el balanceador de carga (Nginx) comenzó a enrutar tráfico inmediatamente hacia contenedores cuyo microservicio (FastAPI) aún estaba en proceso de inicialización (*Cold Start*). Esto provocó el rechazo de las conexiones activas y la degradación del servicio, refutando la viabilidad de un balanceo Zero-Downtime sin mecanismos de verificación de estado a nivel de aplicación.
* **Decisión Arquitectónica:** Dado que la estrategia de escalabilidad básica falló en garantizar la continuidad de las transacciones, se determina que la arquitectura de producción en AWS ECS (Elastic Container Service) no puede depender únicamente de la instanciación de la tarea a nivel de cómputo. Se establece como requisito arquitectónico estricto la configuración de Health Checks a nivel de Target Group en el Application Load Balancer (ALB), en conjunto con los Health Checks en la Task Definition de ECS.
Esta táctica asegurará que el ALB retenga el tráfico y no lo envíe hacia las nuevas tareas (tasks) levantadas por el Service Auto Scaling hasta que la aplicación reporte explícitamente estar lista (ej. retornando HTTP 200 en un endpoint /health tras cumplir con los Healthy Thresholds configurados), mitigando la pérdida de peticiones y garantizando el cumplimiento de la historia de arquitectura

### Evidencia Gráfica

![Falla del experimento](assets/failure.png)
*Figura 1: Evidencia de falla del experimento*
