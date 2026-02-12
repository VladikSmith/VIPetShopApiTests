from http.client import responses

import allure
import jsonschema
import pytest
import requests

from .schemas.store_schema import STORE_SCHEMA
from .schemas.store_schema import INVENTORY_SCHEMA
from .conftest import create_order

BASE_URL = 'http://5.181.109.28:9090/api/v3'


@allure.feature('Store')
class TestStore:
    @allure.title('Размещение заказа')
    def test_placing_order(self):
        with allure.step('Отправка запроса на размещение заказа'):
            payload = {
                "id": 1,
                "petId": 1,
                "quantity": 1,
                "status": "placed",
                "complete": True
            }
            response = requests.post(f'{BASE_URL}/store/order', json=payload)
            response_json = response.json()

        with allure.step('Проверка статуса ответа и валидация JSON-схемы'):
            assert response.status_code == 200, 'Код не совпадает с ожидаемым'
            jsonschema.validate(response_json, STORE_SCHEMA)

        with allure.step('Проверка параметров заказа в ответе'):
            assert response_json['id'] == payload['id'], 'id заказа не совпадает'
            assert response_json['petId'] == payload['petId'], 'id питомца не совпадает'
            assert response_json['quantity'] == payload['quantity'], 'количество не совпадает'
            assert response_json['status'] == payload['status'], 'статус не совпадает'
            assert response_json['complete'] == payload['complete'], 'завершенность не совпадает'

    @allure.title('Получение информации о заказе по ID')
    def test_get_order_by_id(self, create_order):
        with allure.step('Получение ID созданного заказа'):
            order_id = create_order['id']

        with allure.step('Отправка запроса для получения информации о заказе по ID'):
            response = requests.get(f'{BASE_URL}/store/order/{order_id}')

        with allure.step('Проверка статуса ответа'):
            assert response.status_code == 200, 'Код не совпадает с ожидаемым'

        with allure.step('Проверка параметров заказа'):
            assert response.json()['id'] == create_order['id']
            assert response.json()['petId'] == create_order['petId']
            assert response.json()['quantity'] == create_order['quantity']
            assert response.json()['status'] == create_order['status']
            assert response.json()['complete'] == create_order['complete']

    @allure.title('Удаление заказа по ID')
    def test_delete_order_by_id(self, create_order):
        with allure.step('Получение ID созданного заказа'):
            order_id = create_order['id']

        with allure.step('Отправка запроса на удаление заказа по ID'):
            response = requests.delete(f'{BASE_URL}/store/order/{order_id}')

        with allure.step('Проверка статуса ответа'):
            assert response.status_code == 200, 'Код не совпадает с ожидаемым'

        with allure.step('Отправка запроса на получение информации заказа по ID'):
            response = requests.get(f'{BASE_URL}/store/order/{order_id}')

        with allure.step('Проверка статуса ответа'):
            assert response.status_code == 404, 'Код не совпадает с ожидаемым'

    @allure.title('Попытка получить информацию о несуществующем заказе')
    def test_delete_nonexistent_order(self):
        response = requests.get(f'{BASE_URL}/store/order/99999')

        with allure.step('Проверка статуса ответа'):
            assert response.status_code == 404, 'Код не совпадает с ожидаемым'

        with allure.step('Проверка текстового содержимого ответа'):
            assert response.text == 'Order not found'

    @allure.title('Получение инвентаря магазина')
    def test_get_inventory(self):
        response = requests.get(f'{BASE_URL}/store/inventory')

        with allure.step('Проверка статуса ответа и валидация JSON схемы'):
            assert response.status_code == 200
            jsonschema.validate(response.json(), INVENTORY_SCHEMA)
