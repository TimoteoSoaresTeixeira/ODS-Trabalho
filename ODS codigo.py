import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

# =============================================================================
# FUNÇÃO AUXILIAR DE INPUT
# =============================================================================
def obter_input_numerico(pergunta, max_val):
    """Pede um número ao usuário e garante que é válido."""
    while True:
        try:
            valor_str = input(pergunta)
            valor_int = int(valor_str)
            if 0 <= valor_int <= max_val:
                return valor_int
            else:
                print(f" [Erro] Valor inválido. Digite entre 0 e {max_val}.")
        except ValueError:
            print(" [Erro] Por favor, digite apenas um número inteiro.")

# =============================================================================
# FUNÇÃO AUXILIAR PARA INTERPRETAR O TERMO LINGUÍSTICO
# =============================================================================
def obter_termo_dominante(variavel_antecedente, valor_entrada, nomes_termos):
    """
    Verifica matematicamente qual termo (ex: 'ruim', 'bom') tem maior
    grau de pertinência para o valor digitado.
    """
    melhor_termo = "Desconhecido"
    maior_pertinencia = -1.0
    
    for termo in nomes_termos:
        # Pega a função matemática do termo (os pontos do triângulo)
        mf = variavel_antecedente[termo].mf
        # Calcula o grau de pertinência (0 a 1)
        pertinencia = fuzz.interp_membership(variavel_antecedente.universe, mf, valor_entrada)
        
        if pertinencia > maior_pertinencia:
            maior_pertinencia = pertinencia
            melhor_termo = termo
            
    return melhor_termo.upper()

# =============================================================================
# ETAPA 1, 2 e 3: BASE LÓGICA (MANTIDA ORIGINAL)
# =============================================================================
# Definição das variáveis
tempo_atividade = ctrl.Antecedent(np.arange(0, 61, 1), 'tempo_atividade')
consistencia_renda = ctrl.Antecedent(np.arange(0, 11, 1), 'consistencia_renda')
historico_pagamento = ctrl.Antecedent(np.arange(0, 11, 1), 'historico_pagamento')
nivel_risco = ctrl.Consequent(np.arange(0, 101, 1), 'nivel_risco')

# Funções de Pertinência
tempo_atividade['novo'] = fuzz.trimf(tempo_atividade.universe, [0, 0, 12])
tempo_atividade['recente'] = fuzz.trimf(tempo_atividade.universe, [6, 18, 36])
tempo_atividade['estabelecido'] = fuzz.trimf(tempo_atividade.universe, [24, 60, 60])

for var in [consistencia_renda, historico_pagamento]:
    var['ruim'] = fuzz.trimf(var.universe, [0, 0, 4])
    var['razoavel'] = fuzz.trimf(var.universe, [2, 5, 8])
    var['bom'] = fuzz.trimf(var.universe, [6, 10, 10])

nivel_risco['baixo'] = fuzz.trimf(nivel_risco.universe, [0, 25, 50])
nivel_risco['medio'] = fuzz.trimf(nivel_risco.universe, [30, 50, 70])
nivel_risco['alto'] = fuzz.trimf(nivel_risco.universe, [50, 75, 100])

# Regras
regra1 = ctrl.Rule(historico_pagamento['ruim'] | consistencia_renda['ruim'], nivel_risco['alto'])
regra2 = ctrl.Rule(tempo_atividade['estabelecido'] & historico_pagamento['bom'] & consistencia_renda['bom'], nivel_risco['baixo'])
regra3 = ctrl.Rule(tempo_atividade['recente'] & historico_pagamento['razoavel'], nivel_risco['medio'])
regra4 = ctrl.Rule(historico_pagamento['bom'] & consistencia_renda['razoavel'], nivel_risco['baixo'])

sistema_controle = ctrl.ControlSystem([regra1, regra2, regra3, regra4])
simulacao_risco = ctrl.ControlSystemSimulation(sistema_controle)

# =============================================================================
# ETAPA 4 e 5: INTERFACE (ATUALIZADA COM COLUNAS DE TEXTO)
# =============================================================================
def main():
    while True:
        print("\n" + "="*60)
        print("   ANÁLISE DE RISCO DE MICROCRÉDITO (ODS 1) - SIMULADOR   ")
        print("="*60)
        print("Responda para avaliar o perfil:\n")

        # Coleta
        val_tempo = obter_input_numerico(" 1. Tempo de atividade (meses) [0-60]: ", 60)
        val_renda = obter_input_numerico(" 2. Consistência da renda [0-10]:      ", 10)
        val_hist  = obter_input_numerico(" 3. Histórico de pagamentos [0-10]:    ", 10)

        # Processamento
        simulacao_risco.input['tempo_atividade'] = val_tempo
        simulacao_risco.input['consistencia_renda'] = val_renda
        simulacao_risco.input['historico_pagamento'] = val_hist
        
        try:
            simulacao_risco.compute()
            sucesso = True
        except Exception as e:
            print(f"\n[Erro Crítico] Falha no cálculo fuzzy: {e}")
            sucesso = False

        if sucesso:
            risco_numerico = simulacao_risco.output['nivel_risco']
            
            # Classificação do Risco Final
            if risco_numerico <= 16: classificacao = "Risco Muito Baixo"
            elif risco_numerico <= 33: classificacao = "Risco Baixo"
            elif risco_numerico <= 50: classificacao = "Risco Médio"
            elif risco_numerico <= 67: classificacao = "Risco Um Pouco Alto"
            elif risco_numerico <= 84: classificacao = "Risco Alto"
            else: classificacao = "Risco Muito Alto"

            print("\n" + "-"*60)
            print(f" RESULTADO FINAL: {classificacao.upper()}")
            print("-"*60)
            print(f" Score de Risco: {risco_numerico:.2f} / 100.0")
            print("="*60)

            while True:
                print("\n[OPÇÕES]")
                print("1 - Ver Gráfico do Resultado (Curva de Risco)")
                print("2 - Ver Relatório de Entradas (Colunas)")
                print("3 - Nova Simulação")
                print("4 - Sair")
                
                opcao = input("Escolha: ")

                if opcao == '1':
                    try:
                        print("Gerando gráfico...")
                        nivel_risco.view(sim=simulacao_risco)
                        plt.show()
                    except:
                        print("[Aviso] Erro ao renderizar gráfico.")
                
                elif opcao == '2':
                    # --- NOVA VISUALIZAÇÃO EM COLUNAS ---
                    print("\n" + "="*75)
                    print(f"{'RELATÓRIO DE STATUS DAS ENTRADAS':^75}")
                    print("="*75)
                    
                    # Títulos das colunas
                    t1 = "TEMPO DE ATIVIDADE"
                    t2 = "CONSISTÊNCIA RENDA"
                    t3 = "HISTÓRICO PAGTO"
                    
                    # Formatação da tabela
                    print(f"| {t1:^22} | {t2:^22} | {t3:^22} |")
                    print("-" * 75)
                    
                    # Calcula o status (Bom/Ruim/etc) baseado na maior pertinência
                    st_tempo = obter_termo_dominante(tempo_atividade, val_tempo, ['novo', 'recente', 'estabelecido'])
                    st_renda = obter_termo_dominante(consistencia_renda, val_renda, ['ruim', 'razoavel', 'bom'])
                    st_hist  = obter_termo_dominante(historico_pagamento, val_hist, ['ruim', 'razoavel', 'bom'])
                    
                    # Monta o texto dos valores
                    txt_tempo = f"{val_tempo} meses"
                    txt_renda = f"Nota {val_renda}"
                    txt_hist  = f"Nota {val_hist}"
                    
                    # Linha com os valores numéricos
                    print(f"| {txt_tempo:^22} | {txt_renda:^22} | {txt_hist:^22} |")
                    # Linha com o status (em Maiúsculo)
                    print(f"| {st_tempo:^22} | {st_renda:^22} | {st_hist:^22} |")
                    
                    print("="*75)
                    input("[Pressione Enter para voltar...]")

                elif opcao == '3':
                    plt.close('all')
                    break
                
                elif opcao == '4':
                    print("\nEncerrando...")
                    plt.close('all')
                    return
                
                else:
                    print("Opção inválida.")

if __name__ == "__main__":
    main()