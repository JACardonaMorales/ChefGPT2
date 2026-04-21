###Guía Pruebas
1. curl http://chefgpt-api-alb-696677446.us-east-1.elb.amazonaws.com
Salida esperada: {"status": "ok", "service": "RabbitMQ Logger API"}
2. Enviar logs (POST /logs)
Envía 3 mensajes distintos para tener datos en MongoDB:

bash
curl -X POST http://chefgpt-api-alb-696677446.us-east-1.elb.amazonaws.com/logs \
  -H "Content-Type: application/json" \
  -d '{"message": "Primer log de prueba"}'

curl -X POST http://chefgpt-api-alb-696677446.us-east-1.elb.amazonaws.com/logs \
  -H "Content-Type: application/json" \
  -d '{"message": "Segundo log desde la API"}'

curl -X POST http://chefgpt-api-alb-696677446.us-east-1.elb.amazonaws.com/logs \
  -H "Content-Type: application/json" \
  -d '{"message": "Tercer log - pipeline completo"}'
  
  Salida esperada: {"status":"sent","message":"Primer log de prueba"}{"status":"sent","message":"Segundo log desde la API"}{"status":"sent","message":"Tercer log - pipeline completo"}

3. Verificar que el Worker guardó en MongoDB (GET /logs)
bash
curl http://chefgpt-api-alb-696677446.us-east-1.elb.amazonaws.com/logs
Respuesta esperada:

json
{
  "total": 3,
  "logs": [
    {"message": "Primer log de prueba", "timestamp": null},
    {"message": "Segundo log desde la API", "timestamp": null},
    {"message": "Tercer log - pipeline completo", "timestamp": null}
  ]
}

4. Load Balancer (opcional)
for i in {1..10}; do
  curl -s -X POST http://<ALB-DNS>/logs \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"Load balancer test $i\"}"
  echo ""
done

curl http://chefgpt-api-alb-696677446.us-east-1.elb.amazonaws.com/logs | python3 -m json.tool
El total debe ser 13 (los 3 anteriores + 10 nuevos). Muestra balanceo de carga en acción.

5. Limpiar y volver a probar (DELETE /logs)
bash
curl -X DELETE http://chefgpt-api-alb-696677446.us-east-1.elb.amazonaws.com/logs
Respuesta esperada:

json
{"deleted": 13}
Confirma que quedó vacío:

bash
curl http://chefgpt-api-alb-696677446.us-east-1.elb.amazonaws.com/logs
json
{"total": 0, "logs": []}
Demuestra el CRUD completo de la API.