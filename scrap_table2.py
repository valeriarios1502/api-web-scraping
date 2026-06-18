import requests
import boto3
import uuid

def lambda_handler(event, context):
    # URL de la página web que contiene la tabla
    url = "https://ultimosismo.igp.gob.pe/api/ultimo-sismo/ajaxb/2026"

    # Realizar la solicitud HTTP a la página web
    response = requests.get(url)
    if response.status_code != 200:
        return {
            'statusCode': response.status_code,
            'body': 'Error al acceder a la página web'
        }

    data = response.json()

    # Guardar los datos en DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('TablaWebScrapingSismos')


     # Eliminar todos los elementos existentes antes de insertar los nuevos
    scan = table.scan()
    with table.batch_writer() as batch:
        for each in scan['Items']:
            batch.delete_item(Key={'id': each['id']})
 
    # Insertar los nuevos datos, mapeando los campos relevantes
    rows = []
    with table.batch_writer() as batch:
        for sismo in data:
            row = {
                'id': str(uuid.uuid4()),  # uuid
                'codigo': sismo.get('codigo'),
                'referencia': sismo.get('referencia'),
                'magnitud': sismo.get('magnitud'),
                'fecha_local': sismo.get('fecha_local'),
                'hora_local': sismo.get('hora_local'),
                'latitud': sismo.get('latitud'),
                'longitud': sismo.get('longitud'),
                'profundidad': sismo.get('profundidad'),
                'intensidad': sismo.get('intensidad'),
                'numero_reporte': sismo.get('numero_reporte'),
                'reporte_acelerometrico_pdf': sismo.get('reporte_acelerometrico_pdf'),
            }
            batch.put_item(Item=row)
            rows.append(row)

    # Retornar el resultado como JSON
    return {
        'statusCode': 200,
        'body': rows
    }
