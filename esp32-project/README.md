# Monitor de Enchentes com ESP32

## Sobre o Projeto

Este projeto implementa um sistema de monitoramento de enchentes utilizando um ESP32, sensor de temperatura e umidade DHT22 e sensor ultrassônico HC-SR04. O sistema utiliza os dados dos sensores para prever possíveis riscos de enchente.

## Ambiente de Simulação

Estamos utilizando o emulador [Wokwi](https://wokwi.com/) para simular o funcionamento do ESP32 e seus componentes.

### Limitações do Ambiente

O Wokwi tem limitações para rodar o TensorFlow Lite e o EloquentTinyML, bibliotecas comumente utilizadas para machine learning em microcontroladores. Por esse motivo, criamos uma função que simula o modelo de predição, que retorna um score de 0 a 1, onde 1 é entendido como risco de enchente.

```cpp
float run_model_simulado(float h, float t) {
  // Simulação do modelo de machine learning
  // Retorna um valor entre 0 e 1, onde 1 indica alto risco de enchente
  // ...
}
```

## Componentes Utilizados

- ESP32
- Sensor de temperatura e umidade DHT22
- Display LCD 16x2
- Sensor ultrassônico HC-SR04 (para medir o nível da água)

## Demonstração

![Demonstração do Sistema](demo-esp32.gif)

## Como Executar

1. Acesse o [Wokwi](https://wokwi.com/)
2. Importe os arquivos do projeto
3. Clique em "Start Simulation" para executar

## Funcionalidades

- Monitoramento em tempo real da temperatura e umidade
- Alerta quando a temperatura está muito alta ou muito baixa
- Previsão de risco de enchente baseada nos dados dos sensores 