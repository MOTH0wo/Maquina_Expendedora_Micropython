from machine import I2C, Pin
from SSD1306 import SSD1306_I2C
from utime import sleep, ticks_ms, ticks_diff

# Pines de la pantalla OLED y botones
i2c = I2C(1, sda=Pin(21), scl=Pin(22))
oled = SSD1306_I2C(128, 64, i2c)

b1 = Pin(14, Pin.IN, Pin.PULL_DOWN)  # Siguiente producto
b2 = Pin(27, Pin.IN, Pin.PULL_DOWN)  # Seleccionar / Cancelar
b3 = Pin(26, Pin.IN, Pin.PULL_DOWN)  # Agregar $5
b4 = Pin(25, Pin.IN, Pin.PULL_DOWN)  # Agregar $10

# Catálogo de productos (fácil de ampliar)
PRODUCTOS = [
    {"nombre": "Agua",      "precio": 10},
    {"nombre": "Papas",     "precio": 15},
    {"nombre": "Bocadillo", "precio": 20},
    {"nombre": "Chocolate", "precio": 10},
    {"nombre": "Refresco",  "precio": 15},
]

# Constantes de estado
E_CATALOGO   = 0
E_SELECCION  = 1
E_SALDO      = 2
E_ENTREGA    = 3
E_CAMBIO     = 4

DEBOUNCE_MS = 50
TIMEOUT_MS  = 120000   # Segundos de inactividad ajustar a necesidad

# Estado global
e = E_CATALOGO
indice = 0
producto_elegido = None
saldo = 0
estado_anterior = None
ultima_actividad = ticks_ms()

# Variables para debounce
ultimo_tiempo = {b1: 0, b2: 0, b3: 0, b4: 0}
estado_prev = {b1: 0, b2: 0, b3: 0, b4: 0}


def boton_presionado(pin):
    """Detección de flanco ascendente con debounce por tiempo."""
    ahora = ticks_ms()
    if pin.value() == 1 and estado_prev[pin] == 0 and ticks_diff(ahora, ultimo_tiempo[pin]) > DEBOUNCE_MS:
        ultimo_tiempo[pin] = ahora
        estado_prev[pin] = 1
        return True
    if pin.value() == 0:
        estado_prev[pin] = 0
    return False


def leer_botones_con_prioridad():
    """
    Lee los 4 botones pero solo deja pasar UNO por ciclo, con prioridad fija
    b1 > b2 > b3 > b4. Si se presionan varios "al mismo tiempo", solo se
    atiende el de mayor prioridad y los demás se ignoran para este ciclo.
    """
    p1 = boton_presionado(b1)
    p2 = boton_presionado(b2)
    p3 = boton_presionado(b3)
    p4 = boton_presionado(b4)

    if p1:
        return True, False, False, False
    if p2:
        return False, True, False, False
    if p3:
        return False, False, True, False
    if p4:
        return False, False, False, True
    return False, False, False, False


def dibujar_pantalla():
    oled.fill(0)

    if e == E_CATALOGO:
        p = PRODUCTOS[indice]
        oled.text("{}/{}".format(indice + 1, len(PRODUCTOS)), 0, 0)
        oled.text(p["nombre"], 0, 16)
        oled.text("${}".format(p["precio"]), 0, 32)
        oled.text("B1=sig  B2=elegir", 0, 48)

    elif e == E_SELECCION:
        p = PRODUCTOS[producto_elegido]
        oled.text("Seleccionado:", 0, 0)
        oled.text(p["nombre"], 0, 16)
        oled.text("Precio: ${}".format(p["precio"]), 0, 32)
        oled.text("B3=+$5 B4=+$10", 0, 48)

    elif e == E_SALDO:
        p = PRODUCTOS[producto_elegido]
        oled.text(p["nombre"], 0, 0)
        oled.text("Saldo: ${}".format(saldo), 0, 16)
        oled.text("Falta: ${}".format(max(p["precio"] - saldo, 0)), 0, 32)
        oled.text("B2=cancelar", 0, 48)

    elif e == E_ENTREGA:
        p = PRODUCTOS[producto_elegido]
        oled.text("Pago completo!", 0, 0)
        oled.text("Entregando:", 0, 16)
        oled.text(p["nombre"], 0, 32)
        oled.text("Gracias!", 0, 48)

    elif e == E_CAMBIO:
        p = PRODUCTOS[producto_elegido]
        cambio = saldo - p["precio"]
        oled.text("Cambio: ${}".format(cambio), 0, 0)
        oled.text("Entregando:", 0, 16)
        oled.text(p["nombre"], 0, 32)
        oled.text("Gracias!", 0, 48)

    oled.show()


# Pantalla de bienvenida
oled.fill(0)
oled.text("Maquina", 0, 0)
oled.text("Expendedora", 0, 16)
oled.show()
sleep(1)

# Bucle principal
while True:
    ev1, ev2, ev3, ev4 = leer_botones_con_prioridad()

    if ev1 or ev2 or ev3 or ev4:
        ultima_actividad = ticks_ms()

    # Timeout de inactividad (solo aplica si hay una compra en curso)
    if e in (E_SELECCION, E_SALDO) and ticks_diff(ticks_ms(), ultima_actividad) > TIMEOUT_MS:
        e = E_CATALOGO
        producto_elegido = None
        saldo = 0

    else:
        # Máquina de estados
        if e == E_CATALOGO:
            if ev1:
                indice = (indice + 1) % len(PRODUCTOS)
            elif ev2:
                producto_elegido = indice
                saldo = 0
                e = E_SELECCION

        elif e == E_SELECCION:
            if ev3:
                saldo += 5
                e = E_SALDO
            elif ev4:
                saldo += 10
                e = E_SALDO

        elif e == E_SALDO:
            precio = PRODUCTOS[producto_elegido]["precio"]

            if ev2:
                e = E_CATALOGO
                producto_elegido = None
                saldo = 0
            else:
                if ev3:
                    saldo += 5
                elif ev4:
                    saldo += 10

                if ev3 or ev4:
                    if saldo == precio:
                        e = E_ENTREGA
                    elif saldo > precio:
                        e = E_CAMBIO

        elif e == E_ENTREGA:
            sleep(3)
            e = E_CATALOGO
            producto_elegido = None
            saldo = 0

        elif e == E_CAMBIO:
            sleep(3)
            e = E_CATALOGO
            producto_elegido = None
            saldo = 0

    if e != estado_anterior or ev1 or ev2 or ev3 or ev4:
        dibujar_pantalla()
        estado_anterior = e

    sleep(0.02)
