# Tu Nuevo Hogar: base de información

Información del negocio para alimentar el bot de WhatsApp. Este archivo solo contiene datos; no
describe cómo debe comportarse el bot.

**Fecha de corte:** 5 de octubre de 2026.

## Cómo leer este archivo

- **Todo es contenido de demostración.** La empresa, los precios, la dirección, los teléfonos, las
  personas y los testimonios son ficticios.
- Cada dato viene de una de dos fuentes, y cada apartado lo indica:
  - **[Sitio]** Está publicado en la página web. Su fuente es `src/data/site.ts`; si cambia ahí,
    hay que actualizarlo aquí.
  - **[Adicional]** No está en la página. Se escribió para que el bot pueda responder preguntas
    que el sitio no cubre. Son datos inventados, coherentes con el sitio, y **deben revisarse**
    antes de usarse con clientes reales.
- **[Calculado]** Cifras obtenidas con la misma fórmula del simulador del sitio.
- Los precios están en pesos mexicanos (MXN).

---

## 1. La empresa

**[Sitio]**

- Nombre: **Tu Nuevo Hogar**
- Giro: desarrolladora de vivienda nueva en Huichapan, Hidalgo, México.
- Oferta: casas nuevas en cuatro condominios (Tulipán, Bugambilia, Jacaranda y Cempasúchil).
- Los cuatro condominios comparten avenida, escuela y mercado. Cambian el tamaño de la casa y el
  precio.
- Formas de pago aceptadas: Infonavit, Fovissste, Cofinavit, crédito bancario y contado.
- Acompañamiento: desde la primera visita hasta la firma de escrituras.
- Lema de la página: "Aquí empieza Tu Nuevo Hogar."

**[Adicional]**

- La empresa construye y vende directamente; no cobra comisión al comprador por la asesoría ni por
  el trámite del crédito.
- Cempasúchil fue el primer condominio y Tulipán es el más reciente.

---

## 2. Contacto, horario y ubicación

**[Sitio]**

| Dato              | Valor                                                             |
| ----------------- | ----------------------------------------------------------------- |
| Centro de ventas  | Av. de los Fresnos 120, Col. El Mirador, 42400 Huichapan, Hidalgo |
| Teléfono          | 55 5550 0142 (marcación: +52 55 5550 0142)                        |
| Correo            | hola@tunuevohogar.com                                             |
| WhatsApp          | +1 (555) 160-1886                                                 |
| Enlace a WhatsApp | https://wa.me/15551601886                                         |
| Mapa              | https://www.openstreetmap.org/?mlat=20.3756&mlon=-99.6519#map=15/20.3756/-99.6519 |

Horario del centro de ventas:

| Días            | Horario         |
| --------------- | --------------- |
| Lunes a viernes | 10:00 a 19:00 h |
| Sábados         | 10:00 a 14:00 h |
| Domingos        | Cerrado         |

**Mensaje con el que llega un visitante desde el sitio.** El botón de WhatsApp de la página abre el
chat con este texto ya escrito:

> Hola, me gustaría agendar una visita

**[Adicional]**

- El centro de ventas está a la entrada de la Av. de los Fresnos; los cuatro condominios quedan a
  menos de cinco minutos caminando de ahí.
- Tiene estacionamiento gratuito para visitantes.
- Está a unos 10 minutos en auto del centro de Huichapan.
- Tiempos aproximados en auto (estimaciones por verificar): San Juan del Río, 50 minutos;
  Querétaro, 1 hora 20 minutos; Ciudad de México, 2 horas 30 minutos.
- Días festivos oficiales: el centro de ventas cierra. El horario de diciembre se confirma por
  teléfono.
- El marcador del mapa del sitio está puesto en el centro de Huichapan y es aproximado.

---

## 3. Las casas

### 3.1 Comparativo

**[Sitio]**

| Condominio  | Precio desde | Recámaras | Baños | Construcción | Terreno | Estacionamiento  | Entrega       | Estado           |
| ----------- | ------------ | --------- | ----- | ------------ | ------- | ---------------- | ------------- | ---------------- |
| Tulipán     | $2,650,000   | 4         | 3½    | 162 m²       | 180 m²  | 2 autos, techado | Junio de 2027 | Preventa         |
| Bugambilia  | $1,480,000   | 3         | 2½    | 98 m²        | 105 m²  | 2 autos          | Inmediata     | Disponible       |
| Jacaranda   | $1,190,000   | 2         | 1½    | 72 m²        | 90 m²   | 1 auto           | Marzo de 2027 | Últimas 12 casas |
| Cempasúchil | $980,000     | 2         | 1     | 58 m²        | 90 m²   | 1 auto           | Inmediata     | Disponible       |

Orientación rápida:

- La más económica: **Cempasúchil**.
- La más grande y mejor equipada: **Tulipán**.
- Entrega inmediata: **Bugambilia** y **Cempasúchil**.
- Tres recámaras: **Bugambilia**. Cuatro recámaras: **Tulipán**.
- Una sola planta: **Cempasúchil**.

### 3.2 Tulipán

**[Sitio]**

- Descripción: la casa más amplia y mejor equipada, con roof garden y acabados de piedra y madera.
- Precio desde: $2,650,000
- 4 recámaras, 3½ baños
- Construcción: 162 m². Terreno: 180 m².
- Estacionamiento: 2 autos, techado
- Estado: preventa. Entrega: junio de 2027.
- Amenidades del condominio:
  - Casa club con alberca
  - Gimnasio
  - Roof garden privado
  - Acceso con tarjeta y vigilancia las 24 horas
- Promoción vigente: "Roof garden equipado" (ver sección 4).

**[Adicional]**

- Dos niveles más roof garden en la azotea.
- Planta baja: sala, comedor, cocina con isla, medio baño, cuarto de lavado y una recámara con baño
  completo.
- Planta alta: recámara principal con vestidor y baño completo, dos recámaras que comparten un baño
  completo, y estancia de televisión.
- Incluye: cocina integral con cubierta de granito, clósets en las cuatro recámaras, calentador
  solar, cisterna y preparación para aire acondicionado.
- Condominio de 36 casas. Al tratarse de preventa, todavía hay casas para elegir ubicación.
- No hay casa muestra todavía. En el centro de ventas se enseñan los planos, la maqueta y las
  muestras de acabados.
- Cuota de mantenimiento estimada: $1,800 al mes.

### 3.3 Bugambilia

**[Sitio]**

- Descripción: casas de dos niveles frente al parque central del condominio.
- Precio desde: $1,480,000
- 3 recámaras, 2½ baños
- Construcción: 98 m². Terreno: 105 m².
- Estacionamiento: 2 autos
- Estado: disponible. Entrega: inmediata.
- Amenidades del condominio:
  - Parque central con juegos
  - Caseta con vigilancia las 24 horas
  - Ciclopista interior
  - Salón de usos múltiples
- Tiene casa muestra de tres recámaras, incluida en el recorrido.
- Promociones vigentes: "Escrituración sin costo" y "Aparta con $5,000" (ver sección 4).

**[Adicional]**

- Planta baja: sala, comedor, cocina, medio baño y patio de servicio.
- Planta alta: recámara principal con baño completo y dos recámaras que comparten un baño completo.
- Incluye: tarja y preparación para cocina integral, calentador de paso y tinaco. La cocina
  integral y los clósets no están incluidos.
- Condominio de 120 casas; quedan 28 disponibles.
- Cuota de mantenimiento estimada: $650 al mes.

### 3.4 Jacaranda

**[Sitio]**

- Descripción: casas con balcón en una privada de 64 viviendas.
- Precio desde: $1,190,000
- 2 recámaras, 1½ baños
- Construcción: 72 m². Terreno: 90 m².
- Estacionamiento: 1 auto
- Estado: últimas 12 casas. Entrega: marzo de 2027.
- Amenidades del condominio:
  - Área de asadores
  - Cancha de usos múltiples
  - Acceso controlado
  - Huerto comunitario
- Tiene casa muestra, incluida en el recorrido.
- Promociones vigentes: "Cocina integral incluida" y "Aparta con $5,000" (ver sección 4).

**[Adicional]**

- Las 12 casas que quedan son la última etapa de la privada. Las etapas anteriores ya están
  entregadas y habitadas.
- Planta baja: sala, comedor, cocina, medio baño y patio de servicio.
- Planta alta: dos recámaras, un baño completo y balcón en la recámara principal.
- Incluye: calentador de paso y tinaco. Con la promoción vigente, también cocina integral, tarja y
  parrilla de cuatro quemadores.
- Cuota de mantenimiento estimada: $450 al mes.

### 3.5 Cempasúchil

**[Sitio]**

- Descripción: casas de una planta con terraza en la azotea. La opción de menor precio.
- Precio desde: $980,000
- 2 recámaras, 1 baño
- Construcción: 58 m². Terreno: 90 m².
- Estacionamiento: 1 auto
- Estado: disponible. Entrega: inmediata.
- Amenidades del condominio:
  - Jardín vecinal
  - Acceso controlado
  - Terraza en azotea
- No tiene promoción vigente.

**[Adicional]**

- Una sola planta: sala comedor, cocina, dos recámaras, un baño completo y patio de servicio.
  Escalera exterior a la terraza de la azotea.
- La estructura está preparada para ampliar con un segundo nivel, con permiso del condominio y del
  municipio.
- Incluye: tarja, calentador de paso y tinaco. La cocina integral y los clósets no están incluidos.
- Condominio de 80 casas; quedan 9 disponibles.
- No tiene casa muestra amueblada; se visita una casa terminada.
- Cuota de mantenimiento estimada: $350 al mes.

---

## 4. Promociones

**[Sitio]** Las promociones no son acumulables y aplican solo a las casas y fechas indicadas.

| Promoción                | Aplica a               | En qué consiste                                                                                                      | Vigencia                                                          |
| ------------------------ | ---------------------- | -------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| Roof garden equipado     | Tulipán                | Las primeras 10 casas de la preventa se entregan con pérgola, asador y jardineras ya instalados en la azotea.         | Hasta el 15 de diciembre de 2026 o hasta agotar las 10 casas      |
| Escrituración sin costo  | Bugambilia             | La empresa cubre los gastos notariales si el cliente firma su contrato de compraventa este otoño.                     | Hasta el 30 de noviembre de 2026                                  |
| Cocina integral incluida | Jacaranda              | Las últimas 12 casas se entregan con cocina integral, tarja y parrilla de cuatro quemadores ya instaladas.            | Hasta agotar existencias                                          |
| Aparta con $5,000        | Bugambilia y Jacaranda | Se congela el precio de lista durante 30 días mientras se autoriza el crédito. Si no se autoriza, se devuelve.        | Hasta el 31 de octubre de 2026                                    |

Cempasúchil no tiene promoción vigente.

**[Adicional]**

- "No acumulables" significa que una misma casa solo puede llevar una promoción. En Bugambilia se
  elige entre "Escrituración sin costo" y "Aparta con $5,000"; en Jacaranda, entre "Cocina integral
  incluida" y "Aparta con $5,000".
- "Escrituración sin costo" cubre honorarios del notario y derechos de registro. No cubre el
  avalúo ni las comisiones que cobre la institución que otorga el crédito.

---

## 5. Créditos y formas de pago

### 5.1 Tipos de crédito

**[Sitio]**

| Crédito   | Para quién                                           | Qué ofrece la empresa                                                                       |
| --------- | ---------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| Infonavit | Quien cotiza en el IMSS                              | Se puede sumar el crédito al de la pareja, un familiar o un amigo para alcanzar más monto.   |
| Fovissste | Quien trabaja para el gobierno y cotiza en el ISSSTE | Se revisa el puntaje y se arma el expediente con el cliente, sin costo.                      |
| Bancario  | Quien trabaja por su cuenta o busca un monto mayor   | Se compara la oferta de varios bancos y se recomienda la más conveniente.                    |
| Cofinavit | Quien no alcanza solo con su crédito Infonavit       | Infonavit pone una parte y un banco la otra, en un solo trámite.                             |

- También se acepta **pago de contado**.
- Si el cliente no sabe qué crédito le corresponde, se revisa en unos diez minutos con su número
  de seguridad social.
- Plazos disponibles en el simulador: 10, 15, 20 y 30 años.
- Enganche en el simulador: de 5 % a 50 % del precio.

### 5.2 Tasas de referencia

**[Sitio]** Son las tasas anuales precargadas en el simulador. **No son una oferta**; la tasa real
la define la institución que presta.

| Crédito   | Tasa anual de referencia |
| --------- | ------------------------ |
| Infonavit | 8.5 %                    |
| Fovissste | 6 %                      |
| Bancario  | 11 %                     |
| Cofinavit | 10.5 %                   |

### 5.3 Mensualidades estimadas

**[Calculado]** Con 10 % de enganche, plazo de 20 años, tasa fija de referencia y precio "desde".
No incluyen seguros, comisiones ni gastos de escrituración.

| Condominio  | Enganche (10 %) | Monto del crédito | Infonavit | Fovissste | Bancario | Cofinavit |
| ----------- | --------------- | ----------------- | --------- | --------- | -------- | --------- |
| Tulipán     | $265,000        | $2,385,000        | $20,698   | $17,087   | $24,618  | $23,811   |
| Bugambilia  | $148,000        | $1,332,000        | $11,559   | $9,543    | $13,749  | $13,298   |
| Jacaranda   | $119,000        | $1,071,000        | $9,294    | $7,673    | $11,055  | $10,693   |
| Cempasúchil | $98,000         | $882,000          | $7,654    | $6,319    | $9,104   | $8,806    |

Ingreso mensual sugerido para esas mensualidades. El sitio usa la regla de que la mensualidad no
pase del 30 % del ingreso:

| Condominio  | Infonavit | Fovissste | Bancario | Cofinavit |
| ----------- | --------- | --------- | -------- | --------- |
| Tulipán     | $68,992   | $56,956   | $82,059  | $79,371   |
| Bugambilia  | $38,531   | $31,810   | $45,829  | $44,328   |
| Jacaranda   | $30,981   | $25,577   | $36,849  | $35,642   |
| Cempasúchil | $25,514   | $21,063   | $30,346  | $29,352   |

Cómo cambia la mensualidad con el plazo (Infonavit, 8.5 %, 10 % de enganche):

| Condominio  | 10 años | 15 años | 20 años | 30 años |
| ----------- | ------- | ------- | ------- | ------- |
| Tulipán     | $29,571 | $23,486 | $20,698 | $18,339 |
| Bugambilia  | $16,515 | $13,117 | $11,559 | $10,242 |
| Jacaranda   | $13,279 | $10,547 | $9,294  | $8,235  |
| Cempasúchil | $10,936 | $8,685  | $7,654  | $6,782  |

Enganche según el porcentaje:

| Condominio  | 5 %      | 10 %     | 20 %     |
| ----------- | -------- | -------- | -------- |
| Tulipán     | $132,500 | $265,000 | $530,000 |
| Bugambilia  | $74,000  | $148,000 | $296,000 |
| Jacaranda   | $59,500  | $119,000 | $238,000 |
| Cempasúchil | $49,000  | $98,000  | $196,000 |

Fórmula del simulador, por si el bot necesita calcular otros casos:

```
crédito      = precio − enganche
tasa mensual = tasa anual / 100 / 12
meses        = años × 12
mensualidad  = crédito × tasa mensual / (1 − (1 + tasa mensual)^(−meses))
ingreso sugerido = mensualidad / 0.30
```

Con tasa 0 %, la mensualidad es `crédito / meses`.

### 5.4 Documentos y requisitos

**[Sitio]**

- Para la primera visita no se necesita ningún documento.
- Para precalificar el crédito: identificación oficial, CURP, número de seguridad social y
  comprobante de domicilio.

**[Adicional]** Documentos para integrar el expediente, según el crédito:

| Documento                                       | Infonavit | Fovissste | Bancario | Cofinavit |
| ----------------------------------------------- | --------- | --------- | -------- | --------- |
| Identificación oficial vigente                  | Sí        | Sí        | Sí       | Sí        |
| CURP                                            | Sí        | Sí        | Sí       | Sí        |
| Acta de nacimiento                              | Sí        | Sí        | Sí       | Sí        |
| RFC                                             | Sí        | Sí        | Sí       | Sí        |
| Comprobante de domicilio (no mayor a 3 meses)   | Sí        | Sí        | Sí       | Sí        |
| Número de seguridad social                      | Sí        | No        | No       | Sí        |
| Último talón de pago                            | No        | Sí        | No       | No        |
| Comprobantes de ingresos de los últimos 3 meses | No        | No        | Sí       | Sí        |
| Estados de cuenta de los últimos 3 meses        | No        | No        | Sí       | Sí        |
| Acta de matrimonio, si aplica                   | Sí        | Sí        | Sí       | Sí        |

- Infonavit pide una puntuación mínima para otorgar crédito (1,080 puntos al momento de escribir
  esto; por verificar). El asesor de crédito la consulta con el número de seguridad social.
- Quien trabaja por su cuenta puede comprobar ingresos con declaraciones fiscales y estados de
  cuenta.
- La precalificación no tiene costo ni compromete a comprar.

---

## 6. Proceso de compra

**[Adicional]** Pasos habituales:

1. **Visita.** Recorrido por las casas muestra, unos 40 minutos.
2. **Precalificación.** El asesor de crédito revisa cuánto presta la institución. Sin costo.
3. **Apartado.** Se elige la casa y se paga el apartado para reservarla.
4. **Integración del expediente.** Se entregan los documentos de la sección 5.4.
5. **Avalúo y autorización del crédito.** De 3 a 6 semanas, según la institución.
6. **Firma de escrituras ante notario.** La acompaña el área de titulación.
7. **Entrega de la casa.** Recorrido de revisión y entrega de llaves.

Apartado:

| Condominio                           | Apartado regular | Con la promoción "Aparta con $5,000"       |
| ------------------------------------ | ---------------- | ------------------------------------------ |
| Bugambilia y Jacaranda               | $10,000          | $5,000, hasta el 31 de octubre de 2026     |
| Cempasúchil                          | $10,000          | No aplica                                  |
| Tulipán                              | $25,000          | No aplica                                  |

- El apartado regular reserva la casa y congela el precio 15 días. Con la promoción, 30 días.
- El apartado se toma a cuenta del enganche.
- Se devuelve completo si el crédito no se autoriza.
- Se paga con transferencia o tarjeta. No se recibe efectivo.

**[Sitio]** Gastos además del precio de la casa: los de escrituración, que son honorarios del
notario, impuestos, derechos de registro y avalúo. Cambian según la casa y el crédito; la empresa
entrega el cálculo por escrito antes de la firma.

**[Adicional]** Como referencia, los gastos de escrituración suelen estar entre 5 % y 8 % del valor
de la casa.

---

## 7. Visitas y citas

**[Sitio]**

- La cita no es obligatoria, pero con cita un asesor espera al cliente a la hora elegida.
- El recorrido dura unos 40 minutos.
- Incluye las casas muestra de Bugambilia y Jacaranda.
- No hace falta llevar documentos.
- Se hace dentro del horario del centro de ventas (sección 2).

Datos que el formulario del sitio pide para agendar. Sirven de referencia para lo que el bot
necesita recabar:

| Dato                       | Obligatorio | Reglas en el sitio                                                    |
| -------------------------- | ----------- | --------------------------------------------------------------------- |
| Nombre                     | Sí          | De 3 a 80 caracteres; solo letras, espacios, puntos, guiones y apóstrofos |
| Teléfono                   | Sí          | Exactamente 10 dígitos                                                |
| Condominio de interés      | No          | Tulipán, Bugambilia, Jacaranda, Cempasúchil o "Todavía no lo sé"      |
| Medio de contacto          | Sí          | Llamada o WhatsApp                                                    |
| Comentario                 | No          | Hasta 300 caracteres                                                  |
| Aceptar aviso de privacidad | Sí         | Sin aceptarlo no se agenda                                            |

El formulario no pide día ni hora; el equipo los confirma después por el medio elegido.

**[Adicional]**

- Las citas se dan cada hora en punto. Última cita: 18:00 de lunes a viernes y 13:00 los sábados.
- Se puede ir con niños y acompañantes.
- Tulipán y Cempasúchil no tienen casa muestra amueblada. Tulipán se presenta con planos y
  maqueta; en Cempasúchil se visita una casa terminada.
- Para reagendar o cancelar basta avisar por WhatsApp o por teléfono.

---

## 8. Equipo

**[Sitio]** A quién corresponde cada tema:

| Persona                | Puesto                         | Temas                                                 |
| ---------------------- | ------------------------------ | ----------------------------------------------------- |
| Mariana Robles Ortega  | Directora comercial            | Precios, disponibilidad y fechas de entrega           |
| Héctor Villaseñor Paz  | Asesor de crédito              | Precalificación Infonavit o Fovissste                 |
| Daniela Cruz Montiel   | Asesora de ventas, Bugambilia  | Recorridos por la casa muestra de tres recámaras      |
| Iván Sandoval Rey      | Asesor de ventas, Jacaranda    | Las 12 casas que quedan y su ubicación en la privada  |
| Paola Guerrero Luna    | Titulación y escrituras        | Notaría, avalúo y firma de escrituras                 |
| Ernesto Maldonado Ríos | Atención posventa              | Garantías y detalles después de la entrega            |

**[Adicional]**

- Tulipán y Cempasúchil no tienen un asesor de ventas propio; los atiende Mariana Robles Ortega.
- Héctor Villaseñor Paz también orienta sobre Cofinavit y crédito bancario.

---

## 9. Entrega, garantías y posventa

**[Sitio]**

- Fechas de entrega: Tulipán, junio de 2027; Bugambilia, inmediata; Jacaranda, marzo de 2027;
  Cempasúchil, inmediata. La fecha queda escrita en el contrato.
- Las casas tienen garantía. Cubre estructura, instalaciones e impermeabilización, con los plazos
  que marca el contrato.
- Los reportes los recibe el área de atención posventa.

**[Adicional]**

- "Entrega inmediata" significa que la casa está terminada. Se entrega al firmar escrituras, lo que
  suele tomar de 4 a 8 semanas desde el apartado, según el crédito.
- Plazos de garantía de referencia: estructura, 5 años; impermeabilización, 2 años; instalaciones
  hidráulicas, eléctricas y de gas, 1 año; acabados, 3 meses.
- La garantía no cubre daños por modificaciones hechas por el propietario ni por falta de
  mantenimiento.
- Los reportes de posventa se atienden en un máximo de 5 días hábiles.

---

## 10. Vida en los condominios

**[Adicional]**

- **Servicios.** Agua potable, drenaje, electricidad y alumbrado en todos los condominios. Gas LP
  con tanque estacionario. Hay cobertura de internet por fibra óptica; la contratación corre por
  cuenta del propietario.
- **Seguridad.** Tulipán y Bugambilia tienen vigilancia las 24 horas. Jacaranda y Cempasúchil
  tienen acceso controlado con pluma y cámaras.
- **Mascotas.** Se permiten. En áreas comunes deben ir con correa.
- **Mantenimiento.** La cuota mensual cubre vigilancia, limpieza y cuidado de áreas comunes.
  Cuotas estimadas: Tulipán, $1,800; Bugambilia, $650; Jacaranda, $450; Cempasúchil, $350.
- **Ampliaciones y remodelaciones.** Se permiten con autorización de la administración del
  condominio. No se puede cambiar el color de la fachada.
- **Renta.** El propietario puede rentar su casa. No se permiten rentas por noche.
- **Cerca.** Escuela primaria y mercado sobre la misma avenida.
- **Estacionamiento de visitas.** Hay cajones para visitantes en cada condominio.

---

## 11. Preguntas frecuentes

**[Sitio]**

**¿Necesito cita para ver las casas muestra?**
No es obligatoria, pero con cita un asesor te espera a la hora que elijas. El recorrido dura unos
40 minutos y se hace dentro del horario del centro de ventas.

**¿Qué documentos necesito para empezar?**
Para la primera visita, ninguno. Para precalificar tu crédito te pediremos identificación oficial,
CURP, número de seguridad social y un comprobante de domicilio.

**¿Cuándo me entregan la casa?**
Depende del condominio. Tulipán, junio de 2027; Bugambilia, inmediata; Jacaranda, marzo de 2027;
Cempasúchil, inmediata. La fecha queda escrita en tu contrato.

**¿Cuánto tengo que dar de enganche?**
Depende de tu crédito y de la casa. En el simulador de la página puedes probar desde 5 % y ver cómo
cambia la mensualidad; el monto definitivo lo confirma la institución que te presta.

**¿Puedo juntar mi crédito con el de otra persona?**
Sí. Infonavit permite sumar tu crédito al de tu pareja, un familiar o un amigo. Nuestro asesor de
crédito revisa los dos casos y te dice cuánto alcanzan juntos.

**¿Qué gastos hay además del precio de la casa?**
Los de escrituración: honorarios del notario, impuestos, derechos de registro y avalúo. Cambian
según la casa y el crédito, así que te entregamos el cálculo por escrito antes de que firmes.

**¿Puedo pagar de contado?**
Sí. Además de Infonavit, Fovissste, Cofinavit y crédito bancario, aceptamos pago de contado.

**¿Las casas tienen garantía?**
Sí. Cubre estructura, instalaciones e impermeabilización, con los plazos que marca tu contrato. Los
reportes los recibe nuestra área de atención posventa.

**[Adicional]**

**¿Cuál es la casa más barata?**
Cempasúchil, desde $980,000. Tiene 2 recámaras y 1 baño en una planta, con entrega inmediata.

**¿Qué casas puedo ocupar ya?**
Bugambilia y Cempasúchil tienen entrega inmediata.

**¿Los precios son fijos?**
Son precios "desde" y pueden cambiar sin previo aviso. El precio se congela al pagar el apartado.

**¿Cuánto cuesta el apartado?**
$10,000 en Bugambilia, Jacaranda y Cempasúchil, y $25,000 en Tulipán. Hasta el 31 de octubre de
2026, Bugambilia y Jacaranda se apartan con $5,000.

**¿Me devuelven el apartado si no me autorizan el crédito?**
Sí, completo.

**¿Puedo usar mi crédito Infonavit si ya lo usé una vez?**
Infonavit ofrece un segundo crédito a quien ya terminó de pagar el primero. El asesor de crédito
revisa cada caso.

**¿Puedo comprar si trabajo por mi cuenta?**
Sí, con crédito bancario o de contado.

**¿Puedo comprar si vivo fuera de México?**
Sí. La firma de escrituras se puede hacer con un poder notarial.

**¿Cobran por la asesoría o el trámite del crédito?**
No.

**¿Aceptan mascotas?**
Sí, en los cuatro condominios.

**¿Las casas incluyen cocina integral?**
Tulipán la incluye. Jacaranda la incluye con la promoción vigente. Bugambilia y Cempasúchil se
entregan con tarja y preparación para instalarla.

**¿Puedo ampliar la casa después?**
Sí, con autorización de la administración. Cempasúchil está preparada para un segundo nivel.

**¿Hay casa muestra de todos los condominios?**
De Bugambilia y Jacaranda. Tulipán se presenta con planos y maqueta, y en Cempasúchil se visita una
casa terminada.

**¿Atienden los domingos?**
No. El centro de ventas abre de lunes a viernes de 10:00 a 19:00 y los sábados de 10:00 a 14:00.

---

## 12. Testimonios

**[Sitio]** No hay testimonios de Tulipán porque está en preventa y todavía no vive nadie ahí.

| Familia                 | Condominio  | Testimonio                                                                                   |
| ----------------------- | ----------- | -------------------------------------------------------------------------------------------- |
| Familia Ortiz Bañuelos  | Bugambilia  | Pagamos renta nueve años. Hoy la mensualidad es casi la misma y la casa es nuestra.           |
| Familia Peña Salgado    | Cempasúchil | Héctor juntó nuestros dos créditos Infonavit. Solos no habríamos sabido que se podía.         |
| Familia Lara Quintero   | Jacaranda   | Mis hijos salen en bici dentro del condominio. Eso era justo lo que buscábamos.               |
| Familia Hernández Solís | Bugambilia  | Nos entregaron la casa en la fecha que decía el contrato. Con dos niños, eso valía oro.       |
| Rocío Medina Tapia      | Cempasúchil | Compré sola, con mi crédito Infonavit. Paola me explicó cada papel antes de firmar.           |
| Familia Ríos Camacho    | Jacaranda   | El huerto comunitario lo cuidamos entre vecinos. Ya cosechamos jitomate y chile.              |
| Familia Aguilar Nava    | Bugambilia  | Tenemos el parque enfrente. Mi mamá sale a caminar cada mañana sin cruzar una sola calle.     |
| Jorge y Lucía Cabrera   | Cempasúchil | Convertimos la azotea en terraza. Ahí festejamos el primer cumpleaños de nuestra hija.        |
| Familia Domínguez Vera  | Jacaranda   | Salió una gotera con la primera lluvia. Ernesto mandó a repararla esa misma semana.           |
| Familia Zamora Pineda   | Bugambilia  | Trabajo desde casa y la tercera recámara es mi oficina. Ya no pago un coworking.              |

---

## 13. Aviso de privacidad

**[Sitio]** Es un borrador de ejemplo, no un texto legal revisado. Última actualización: 4 de
octubre de 2026.

- **Quién es responsable de los datos.** Tu Nuevo Hogar, con domicilio en Av. de los Fresnos 120,
  Col. El Mirador, 42400 Huichapan, Hidalgo.
- **Qué datos se piden.** Nombre, teléfono, condominio de interés, medio de contacto preferido y
  el comentario que la persona quiera dejar.
- **Para qué se usan.** Para contactar a la persona, agendar su visita y darle información de las
  casas y de su crédito. No se usan para nada más sin pedirlo antes.
- **Con quién se comparten.** Con nadie fuera de Tu Nuevo Hogar, salvo que una autoridad lo exija
  conforme a la ley.
- **Derechos.** La persona puede pedir acceso a sus datos, corregirlos, cancelarlos u oponerse a su
  uso (derechos ARCO), y retirar su consentimiento, escribiendo a hola@tunuevohogar.com.
- **Cambios.** Si el aviso cambia, se publica la nueva versión en la página con su fecha de
  actualización.

---

## 14. Avisos y límites

**[Sitio]**

- Las ilustraciones del sitio son representativas.
- Precios, medidas y promociones pueden cambiar sin previo aviso. La información vigente se
  confirma en el centro de ventas.
- El simulador es un cálculo ilustrativo con tasa fija. No incluye seguros, comisiones ni gastos de
  escrituración, y no es una oferta de crédito.
- Las promociones no son acumulables y aplican solo a las casas y fechas indicadas.

**[Adicional]**

- La autorización de un crédito depende de la institución que lo otorga, no de Tu Nuevo Hogar.
- Las cuotas de mantenimiento son estimadas y las fija la administración de cada condominio.

---

## 15. Glosario

**[Adicional]**

- **Apartado.** Pago que reserva una casa y congela su precio por un tiempo.
- **Avalúo.** Dictamen del valor de la casa que pide la institución antes de prestar.
- **Casa muestra.** Casa terminada y amueblada que se usa para los recorridos.
- **Cofinavit.** Esquema en el que Infonavit presta una parte y un banco la otra.
- **Contado.** Pago del precio completo sin crédito.
- **Enganche.** Parte del precio que el comprador paga con sus propios recursos; el resto lo cubre
  el crédito.
- **Escrituración.** Firma ante notario que hace al comprador dueño legal de la casa.
- **Fovissste.** Fondo de vivienda para trabajadores del Estado que cotizan en el ISSSTE.
- **Infonavit.** Instituto que otorga créditos de vivienda a trabajadores que cotizan en el IMSS.
- **NSS.** Número de seguridad social, asignado por el IMSS.
- **Precalificación.** Consulta previa del monto que una institución puede prestar.
- **Preventa.** Venta de casas que todavía están en construcción.
- **Roof garden.** Azotea acondicionada como terraza o jardín.
- **Unir créditos.** Sumar el crédito Infonavit de dos personas para comprar una sola casa.
