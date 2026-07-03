# Maquina_Expendedora_Micropython

Simulador de máquina expendedora controlada por una máquina de estados finita (FSM), desarrollado en MicroPython para un microcontrolador con pantalla OLED SSD1306 y botones físicos.

## Características

- Catálogo de productos navegable (fácil de ampliar, solo edita la lista `PRODUCTOS`).
- Selección de producto y acumulación de saldo con dos denominaciones ($5 / $10).
- Cálculo automático de cambio cuando el pago excede el precio.
- Cancelación de compra en cualquier momento (botón B2 durante la acumulación de saldo).
- Timeout de inactividad: si el usuario abandona una compra a medias, la máquina se resetea sola tras un tiempo configurable.
- Lectura de botones no bloqueante con debounce por tiempo (sin `sleep()` que congele el microcontrolador).
- Redibujado de pantalla solo cuando hay cambios, para evitar parpadeo innecesario.

## Hardware necesario

| Componente | Cantidad | Notas |
|---|---|---|
| Microcontrolador compatible con MicroPython (ESP32, Raspberry Pi Pico, etc.) | 1 | Pines I2C configurables |
| Pantalla OLED SSD1306 128x64 | 1 | Comunicación I2C |
| Pulsador (botón) | 4 | Con resistencia pull-down |
| Cables / protoboard | — | Para las conexiones |

## Conexiones

| Pin lógico | GPIO | Función |
|---|---|---|
| SDA (I2C) | 21 | Pantalla OLED |
| SCL (I2C) | 22 | Pantalla OLED |
| Botón 1 | 14 | Siguiente producto |
| Botón 2 | 27 | Seleccionar / Cancelar |
| Botón 3 | 26 | Agregar $5 |
| Botón 4 | 25 | Agregar $10 |

> Ajusta los números de pin en el código (`Pin(14, ...)`, etc.) según tu placa específica.

## Instalación

1. Flashea tu microcontrolador con el firmware de MicroPython correspondiente a tu placa.
2. Descarga la libreria para la pantalla OLED. (Revisar requeriments)
3. Copia `main.py` (el archivo principal de este repositorio) también a la raíz.
4. Conecta el hardware según la tabla de [Conexiones](#conexiones).
5. Reinicia el microcontrolador. El programa arranca automáticamente si el archivo se llama `main.py`.

## Uso

1. **Catálogo:** usa B1 para navegar entre productos, B2 para seleccionar el que se muestra en pantalla.
2. **Pago:** con el producto seleccionado, usa B3 (+$5) o B4 (+$10) para acumular saldo.
3. **Cancelar:** durante la acumulación de saldo, B2 cancela la compra y regresa al catálogo.
4. **Entrega:** al alcanzar o superar el precio, la máquina muestra el mensaje de entrega (y el cambio, si aplica) y regresa sola al catálogo.
5. **Inactividad:** si dejas una compra a medias sin tocar ningún botón, la máquina se cancela automáticamente después de `TIMEOUT_MS` (configurable en el código, por defecto 15 segundos).

## Configuración rápida

Algunas constantes al inicio del archivo principal que puedes ajustar sin tocar el resto del código:

```python
PRODUCTOS = [
    {"nombre": "Agua",      "precio": 10},
    {"nombre": "Papas",     "precio": 15},
    # agrega más productos aquí
]

DEBOUNCE_MS = 50      # tiempo de rechazo de rebote mecánico de botones
TIMEOUT_MS  = 15000   # tiempo de inactividad antes de cancelar una compra
```
## 🤝 Contribuciones

Si encuentras algún error o quieres mejorar el proyecto, abre un issue o pull request.
