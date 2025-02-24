# lean_manufacturing.py
import simpy
import random

RANDOM_SEED = 42
NUM_ITEMS = 20

# Tempos base (em minutos) para cada etapa do processo
PROCESSING_TIMES = {
    "recebimento": 3,      # Não agrega valor
    "montagem": 5,         # Agrega valor
    "transporte": 2,       # Não agrega valor
    "inspecao": 3,         # Agrega valor
    "embalagem": 2         # Não agrega valor
}

FAILURE_RATE = 0.2  # Probabilidade de falha na inspeção de qualidade (20%)

def item_process(env, name, assembly, inspection, packaging, results):
    """Simula o processamento de um item na linha de produção."""
    start_time = env.now
    value_added_time = 0

    # Recebimento de matéria-prima (não agrega valor)
    yield env.timeout(PROCESSING_TIMES["recebimento"])

    # Montagem (valor agregado)
    with assembly.request() as req:
        yield req
        yield env.timeout(PROCESSING_TIMES["montagem"])
        value_added_time += PROCESSING_TIMES["montagem"]

    # Transporte interno (não agrega valor)
    yield env.timeout(PROCESSING_TIMES["transporte"])

    # Inspeção de Qualidade (valor agregado)
    with inspection.request() as req:
        yield req
        yield env.timeout(PROCESSING_TIMES["inspecao"])
        value_added_time += PROCESSING_TIMES["inspecao"]

        # Verifica se houve falha na inspeção – se sim, realiza retrabalho (na montagem)
        if random.random() < FAILURE_RATE:
            with assembly.request() as req2:
                yield req2
                yield env.timeout(PROCESSING_TIMES["montagem"])
                value_added_time += PROCESSING_TIMES["montagem"]

    # Embalagem (não agrega valor)
    with packaging.request() as req:
        yield req
        yield env.timeout(PROCESSING_TIMES["embalagem"])

    total_time = env.now - start_time
    results.append((name, total_time, value_added_time))

def run_simulation():
    print("Simulação Lean Manufacturing")
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    # Criação dos recursos que representam as estações da linha de produção
    assembly = simpy.Resource(env, capacity=1)
    inspection = simpy.Resource(env, capacity=1)
    packaging = simpy.Resource(env, capacity=1)
    results = []

    # Processo de chegada de itens (intervalo de 1 minuto entre itens)
    for i in range(NUM_ITEMS):
        env.process(item_process(env, f"Item_{i+1}", assembly, inspection, packaging, results))
        # Intervalo entre chegadas (simula um item a cada 1 minuto)
        env.timeout(1)

    # Executa a simulação por tempo suficiente para processar todos os itens
    env.run(until=100)

    # Exibe os resultados da simulação
    total_lead_time = sum(t for _, t, _ in results)
    total_value_added = sum(v for _, _, v in results)
    print("\nResultados:")
    for name, t, v in results:
        print(f"{name}: Tempo total = {t:.2f} min, Tempo valor agregado = {v:.2f} min")
    print(f"\nTempo médio total: {total_lead_time/NUM_ITEMS:.2f} min")
    print(f"Tempo médio valor agregado: {total_value_added/NUM_ITEMS:.2f} min")
    efficiency = 100 * (total_value_added / total_lead_time)
    print(f"Relação valor agregado/tempo total: {efficiency:.2f}%")

if __name__ == "__main__":
    run_simulation()
