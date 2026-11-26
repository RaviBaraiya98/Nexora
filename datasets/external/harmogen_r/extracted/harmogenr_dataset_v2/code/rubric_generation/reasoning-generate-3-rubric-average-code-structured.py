import os
import time
import datetime
from typing import List, Optional, Dict
from functools import cached_property
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.outputs import ChatResult, ChatGeneration
import openai

# Set your OpenAI API key (replace with your actual key)
os.environ["OPENAI_API_KEY"] = "paste api key"

# Example rubrics to use as structural templates for code questions
example_rubric_1 = """
Pontuação Total: 33 pontos
•	Definição da Função insertValidNIF (3 pontos)
o	Descrição: A função deve ser definida com o nome insertValidNIF e não deve receber parâmetros.
o	Pontuação:
	Definição correta da função (def insertValidNIF()) (3 pontos).
	Caso o nome da função esteja incorreto ou sejam utilizados parâmetros (0 pontos).

•	Utilização de um Ciclo while para Validação Repetida (7 pontos)
o	Descrição: A estrutura de repetição deve garantir que a função continua a solicitar o NIF até que um valor válido seja introduzido.
o	Pontuação:
	Utilização correta de um laço while que assegura a repetição até obter um NIF válido (7 pontos). 
	Caso o laço while seja utilizado, mas não esteja corretamente configurado para continuar até a entrada ser válida (3 pontos).
	Se não for utilizado um laço de repetição (0 pontos).

•	Leitura do Valor do NIF (3 pontos)
o	Descrição: A leitura do NIF deve ser feita corretamente, seja usando input() para capturar uma string ou recebendo diretamente um valor int e armazenando na variável apropriada.
o	Pontuação:
	Leitura correta do NIF como string com input() ou recebido diretamente como int e armazenado apropriadamente (3 pontos).
	Se a leitura do valor for feita incorretamente ou não for realizada (0 pontos).

•	Verificação e Tratamento de Erros para Tipos Diferentes (6 pontos)
o	Descrição: Deve ser implementada uma verificação adequada de erros, seja com try...except ao converter string para int, ou com o uso de métodos como .isnumeric() para garantir que a string lida é numérica. Para valores lidos como int, a verificação de erro com try...except é necessária para garantir que a conversão foi bem-sucedida. Para valores lidos como string, a verificação deve ser realizada com .isnumeric() ou método equivalente.
o	Pontuação:
•	Implementação correta de verificação para ambos os casos (6 pontos):
o	Se for lido como int, uso de try...except para capturar possíveis exceções.
o	Se for lido como string, uso de .isnumeric() ou método equivalente para garantir que o valor é numérico.
•	A verificação está presente, mas de forma parcial (ex.: falta de try...except para int ou ausência de .isnumeric() para string) (3 pontos).
•	Ausência de verificação ou tratamento incorreto dos erros para qualquer um dos tipos (0 pontos).

•	Verificação do Comprimento (6 pontos)
o	Descrição: O NIF deve ter exatamente 9 dígitos. Para valores lidos como string, a verificação deve ser realizada utilizando a função len(). Para valores do tipo int, deve ser feita a conversão para string antes de verificar o comprimento.
o	Pontuação:
	Verificação correta para ambos os tipos (string e int), utilizando len() para string e conversão para string no caso de int (6 pontos).
	Verificação presente, mas aplicada incorretamente (ex.: usar len() diretamente em valores int sem conversão) (3 pontos).
	Ausência de verificação ou verificação incorreta (0 pontos).

•	Mensagem de Erro para NIF Inválido (5 pontos)
o	Descrição: Sempre que o NIF não for válido (ou seja, não for numérico ou não tiver 9 dígitos), deve ser apresentada uma mensagem que informe claramente o erro e solicite a inserção de um novo NIF. O texto exato da mensagem pode variar, desde que transmita a mesma ideia e mantenha o mesmo teor.
o	Pontuação:
	A mensagem é apresentada corretamente para todos os casos de NIF inválido e possui teor semelhante ao exemplo fornecido (5 pontos).
	A mensagem é apresentada, mas com inconsistências no conteúdo ou não cobre todos os casos de erro (3 pontos).
	A mensagem de erro não é apresentada ou está ausente para situações de NIF inválido (0 pontos).

•	Retorno do NIF Válido (3 pontos)
o	Descrição: A função deve retornar o NIF quando este for válido.
o	Pontuação:
	Retorno correto do NIF como um valor inteiro (int) (3 pontos).
	Caso o retorno esteja incorreto ou ausente (ex.: retornar como string) (0 pontos).
"""

example_rubric_2 = """
Pontuação Total: 90 pontos

a) Função preencherSalarios - Definição da função preencherSalarios (Total: 10 pontos)

• **Descrição**: O estudante deve definir corretamente a função preencherSalarios com os parâmetros corretos.
• **Pontuação**:
  ○ Definição correta da função com nome exato e parâmetros corretos (float salarios[], int numFuncionarios) (8 pontos).
  ○ Inclusão da estrutura básica da função (abertura e fechamento de chaves) (2 pontos).
  ○ Definição parcialmente correta (nome correto mas parâmetros incorretos) (4 pontos).
  ○ Definição incorreta ou ausência da função (0 pontos).

b) Função preencherSalarios - Preenchimento do array (Total: 25 pontos)

• **Utilização de ciclo for** (10 pontos):
  ○ Implementação correta do ciclo for para percorrer o array de 0 até numFuncionarios - 1 (10 pontos).
  ○ Implementação parcial ou com pequenos erros (5 pontos).
  ○ Implementação incorreta ou ausência do ciclo for (0 pontos).

• **Mensagem de solicitação** (8 pontos):
  ○ Apresentação da mensagem exatamente no formato solicitado (8 pontos).
  ○ Mensagem apresentada mas com formato ligeiramente diferente (4 pontos).
  ○ Mensagem ausente ou completamente incorreta (0 pontos).

• **Leitura e armazenamento dos salários** (7 pontos):
  ○ Leitura correta do input e armazenamento no array na posição correta (7 pontos).
  ○ Leitura realizada mas com problemas no armazenamento (3 pontos).
  ○ Leitura ou armazenamento ausentes ou incorretos (0 pontos).
"""

# Custom Chat Model class for OpenAI
class CustomChatOpenAI(BaseChatModel):
    model_name: str
    temperature: float = 1.0  # Set default temperature to 1.0

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True

    def __init__(self, model_name: str, temperature: float = 1.0):
        super().__init__(model_name=model_name, temperature=temperature)

    @cached_property
    def client(self):
        return openai.Client()

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> ChatResult:
        message_dicts = []
        for m in messages:
            if isinstance(m, HumanMessage):
                role = "user"
            elif isinstance(m, AIMessage):
                role = "assistant"
            elif isinstance(m, SystemMessage):
                role = "system"
            else:
                role = "user"
            message_dicts.append({
                "role": role,
                "content": m.content
            })

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=message_dicts,
            temperature=self.temperature,
            stop=stop,
            **kwargs
        )

        message = AIMessage(content=response.choices[0].message.content)
        gen = ChatGeneration(message=message)
        return ChatResult(generations=[gen])

    @property
    def _llm_type(self) -> str:
        return "custom_openai_chat"

# Prompt for generating detailed rubric from structured criteria for code questions
PONTUACAO_RULES_PROMPT_TEMPLATE = """
Você é um assistente de avaliação de respostas a questões de programação. A sua tarefa é gerar as regras de pontuação detalhadas para cada critério estruturado, garantindo que a soma dos pontos atribuídos às mini regras (subcritérios) seja exatamente igual à pontuação total do critério. As regras devem ser formuladas de forma geral e aplicável a questões de código.

Para cada critério, siga estas orientações:
1. Identifique os componentes essenciais que o aluno deve demonstrar no código.
2. Divida o critério em mini regras que cubram todos os elementos essenciais do código.
3. Atribua pontos a cada mini regra de forma que, ao somá-los, se obtenha o total definido para o critério.
4. Se o critério for de implementação binária (por exemplo, definição correta de uma função), defina apenas duas regras:
   - Implementação correta: atribua a pontuação total.
   - Implementação incorreta ou ausência da implementação: 0 pontos.
5. Se o critério for de implementação parcial (por exemplo, algoritmos ou estruturas de controle), defina:
   - Implementação completa: atribua a pontuação total, indicando que o aluno implementou todos os componentes essenciais.
   - Implementação parcial: IMPORTANTE - Para implementações parciais, especifique EXATAMENTE quantos pontos são atribuídos para cada componente individual correto, de modo que o avaliador possa somar os pontos de acordo com os componentes que o aluno implementou corretamente. Por exemplo, se a implementação parcial vale 15 pontos no total, divida claramente: "ciclo for correto (5 pontos)", "mensagem formatada corretamente (5 pontos)", "armazenamento correto (5 pontos)".
   - Implementação incorreta ou ausência da implementação: 0 pontos.
6. Use uma linguagem clara, objetiva e técnica, sem adicionar requisitos além do que o critério exige.
7. Verifique a estrutura básica da função (abertura e fechamento de chaves) como um subcritério essencial, atribuindo uma pontuação máxima de 1 ponto para isso em cada critério relacionado à definição ou implementação de funções.
8. Penalização por elementos desnecessários ou errados: Para cada critério, defina uma penalização entre -5% a -20% dos pontos desse critério se o aluno adicionar elementos que alterem o comportamento esperado ou introduzam confusão na resposta.

Exemplo para critério binário:
Critério: "Definição da função calculateAverage" (Total: 5 pontos)
- Definição correta da função com nome exato e parâmetros corretos: 5 pontos.
- Definição incorreta ou ausência da função: 0 pontos.
- Penalização: -1 ponto (20%) se a função incluir elementos desnecessários que possam confundir a interpretação do código.

Exemplo para critério com implementação parcial:
Critério: "Implementação do algoritmo de ordenação" (Total: 15 pontos)
- Implementação completa: o aluno implementa corretamente o algoritmo de ordenação, incluindo inicialização (15 pontos).
- Implementação parcial (até 10 pontos):
  * Inicialização correta das variáveis (3 pontos)
  * Loop externo implementado corretamente (3 pontos)
  * Loop interno implementado corretamente (2 pontos)
  * Condição de troca implementada corretamente (2 pontos)
- Implementação incorreta ou ausência do algoritmo: 0 pontos.
- Penalização: até -3 pontos (20%) pela inclusão de código desnecessário ou incorreto que não comprometa totalmente a funcionalidade mas introduza confusão.

A sua resposta deve apresentar, para cada critério, uma lista de mini regras que, juntas, somem exatamente à pontuação total do critério.

### Reasoning ###
Por favor, analise cada critério e divida-o em mini regras seguindo as orientações acima. Para cada mini regra, atribua uma pontuação proporcional à sua importância, garantindo que, ao somar todas as mini regras de um critério, o total seja igual à pontuação definida para esse critério.

### Final Answer ###
Forneça as regras de pontuação para cada critério estruturado, organizadas em mini regras com pontuações específicas.
"""

# Prompt for consensus rubric creation
CONSENSUS_RUBRIC_PROMPT = """
Você é um especialista em avaliação educacional e está a analisar múltiplas versões de rubricas de avaliação para uma mesma questão de programação. A sua tarefa é criar uma única rubrica consensual de alta qualidade, combinando os melhores elementos de cada versão.

Questão: {question_text}
Pontuação Total: {question_total_score} pontos

Critérios estruturados:
{structured_criteria_formatted}

Aqui estão exemplos de rubricas bem estruturadas para OUTRAS questões (use-as apenas como exemplos de formato e abordagem, NÃO para conteúdo):

EXEMPLO 1:
{example_rubric_1}

EXEMPLO 2:
{example_rubric_2}

Rubricas para analisar:

RUBRICA 1:
{rubric_1}

RUBRICA 2:
{rubric_2}

RUBRICA 3:
{rubric_3}

Para criar a rubrica consensual, siga estas orientações:
1. Identifique os critérios que aparecem consistentemente em todas as rubricas
2. Selecione as descrições mais claras e completas de cada critério
3. Certifique-se de que a estrutura seja hierárquica e bem organizada
4. Mantenha o formato consistente com os exemplos fornecidos
5. Verifique se cada critério tem sua pontuação atribuída conforme especificado na lista de critérios estruturados
6. Certifique-se de que a soma total de pontos é exatamente {question_total_score}
7. Certifique-se de que a rubrica cubra todos os aspectos essenciais da questão
8. Mantenha descrições detalhadas para níveis de pontuação completa, parcial e nula
9. Para critérios relacionados à implementação de código:
   - Verifique a estrutura básica (abertura/fecho de funções, correto uso de parênteses/chaves)
   - Avalie a correspondência entre o código implementado e a especificação fornecida
   - Inclua subcritérios específicos para verificação de sintaxe, lógica e funcionalidade
10. IMPORTANTE: Para implementações parciais, atribua pontuações específicas para cada componente individual que pode ser avaliado separadamente. Por exemplo, se a implementação parcial de um ciclo vale 15 pontos no total, especifique claramente: "ciclo for correto (5 pontos)", "mensagem formatada corretamente (5 pontos)", "armazenamento correto (5 pontos)". Isso permitirá uma avaliação consistente quando o aluno implementar apenas alguns aspectos corretamente.

Por favor, forneça uma rubrica consensual final que seja clara, abrangente e justa para avaliar as respostas dos estudantes.
"""

def format_structured_criteria(structured_criteria: Dict[str, int]) -> str:
    """Convert structured criteria dictionary to formatted string"""
    formatted = ""
    for criterion, points in structured_criteria.items():
        formatted += f"- {criterion} ({points} pontos)\n"
    return formatted

def generate_rubric(question_text, structured_criteria, examples, context, question_total_score, llm):
    """Generate a single rubric using the provided model and pre-defined criteria"""
    
    # Format structured criteria for the prompt
    structured_criteria_formatted = "\n".join([f"{key} ({value} pontos)" for key, value in structured_criteria.items()])
    
    combined_prompt_template = PromptTemplate.from_template("""
Utilize as informações abaixo para gerar as regras de pontuação para cada critério estruturado da questão de programação.

Aqui estão exemplos de rubricas bem estruturadas para OUTRAS questões (use-as apenas como exemplos de formato e abordagem, NÃO para conteúdo):

Exemplo 1:
{example_rubric_1}

Exemplo 2:
{example_rubric_2}

Questão:
{question_text}

Contexto do Curso:
{context}

Critérios Estruturados:
{structured_criteria_formatted}

Exemplo(s) de Resposta:
{examples}

Pontuação Total da Questão:
{question_total_score}

Prompt para Regras de Pontuação:
{pontuacao_rules_prompt_template}

Agora, utilizando APENAS a questão atual e mantendo uma ESTRUTURA semelhante (mas com conteúdo completamente diferente e relevante para a questão atual), gere regras de pontuação detalhadas para CADA um dos critérios estruturados listados.
""")
    
    combined_chain = RunnableSequence(combined_prompt_template | llm | StrOutputParser())
    
    response = combined_chain.invoke({
        "question_text": question_text,
        "structured_criteria_formatted": structured_criteria_formatted,
        "pontuacao_rules_prompt_template": PONTUACAO_RULES_PROMPT_TEMPLATE,
        "context": context,
        "examples": examples,
        "question_total_score": question_total_score,
        "example_rubric_1": example_rubric_1,
        "example_rubric_2": example_rubric_2
    })
    
    # Extract final answer
    try:
        reasoning_section, answer_section = response.split("### Final Answer ###")
        final_answer = answer_section.strip()
    except ValueError:
        print("Warning: Model did not follow expected format for rubric.")
        final_answer = response.strip()
    
    return final_answer

def generate_consensus_rubric(question_text, structured_criteria, question_total_score, rubrics, llm_consensus):
    """Generate a consensus rubric from multiple candidate rubrics"""
    structured_criteria_formatted = format_structured_criteria(structured_criteria)
    
    consensus_template = PromptTemplate.from_template(CONSENSUS_RUBRIC_PROMPT)
    consensus_chain = RunnableSequence(consensus_template | llm_consensus | StrOutputParser())
    
    response = consensus_chain.invoke({
        "question_text": question_text,
        "question_total_score": question_total_score,
        "structured_criteria_formatted": structured_criteria_formatted,
        "example_rubric_1": example_rubric_1,
        "example_rubric_2": example_rubric_2,
        "rubric_1": rubrics[0],
        "rubric_2": rubrics[1],
        "rubric_3": rubrics[2]
    })
    
    return response

def save_to_file(content, prefix="rubric"):
    """Save content to a markdown file with timestamp as name"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_code_structured_{timestamp}.md"
    
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)
    
    print(f"Content saved to {filename}")
    return filename

def main():
    # Dados da questão
    question_text = """
Pretende-se implementar um programa em C++ que permita:
    a)	Criar uma árvore binária de pesquisa (BST) com os seguintes valores: {28, 14, 37, 6, 19, 42, 3, 25, 31, 48}. Deverá ser usada uma função inserirNodo, e a raiz deve ser corretamente inicializado com NULL.
    b)	Implementar as seguintes funções:
        •	bool existe(nodo* raiz, int valor) - devolve verdadeiro se o valor existir na árvore, e falso caso contrário (pesquisa recursiva).
        •	void imprimirFolhas(nodo* raiz) - imprime no ecrã os valores de todos os nós folha da árvore (nós sem filhos).
        •	int somaValores(nodo* raiz) - calcula recursivamente e retorna a soma total dos valores de todos os nós da árvore.

Nota: A estrutura da árvore deve usar a seguinte definição:
struct nodo {
    int dados;
    nodo* esq;
    nodo* dir;
};
"""
    
    # Pre-defined structured criteria (already provided)
    structured_criteria = {
        "Definição da Estrutura nodo e Implementação da Função inserirNodo": 20,
        "Criação e População da Árvore na Função main (ou equivalente)": 15,
        "Implementação da Função existe (Recursiva)": 20,
        "Implementação da Função imprimirFolhas": 15,
        "Implementação da Função somaValores (Recursiva)": 20
    }
    
    question_total_score = sum(structured_criteria.values())
    
    examples = """
*** exemplo 1 ****
#include <iostream>
using namespace std;

struct nodo {
    int dados;
    nodo* esq;
    nodo* dir;
};

nodo* novoNodo(int num) {
    nodo* novo = new nodo;
    novo->dados = num;
    novo->esq = NULL;
    novo->dir = NULL;
    return novo;
}

nodo* inserirNodo(nodo* raiz, int num) {
    if (raiz == NULL) return novoNodo(num);
    if (num <= raiz->dados)
        raiz->esq = inserirNodo(raiz->esq, num);
    else
        raiz->dir = inserirNodo(raiz->dir, num);
    return raiz;
}

bool existe(nodo* raiz, int valor) {
    if (raiz == NULL) return false;
    if (raiz->dados == valor) return true;
    if (valor < raiz->dados)
        return existe(raiz->esq, valor);
    else
        return existe(raiz->dir, valor);
}

void imprimirFolhas(nodo* raiz) {
    if (raiz == NULL) return;
    if (raiz->esq == NULL && raiz->dir == NULL)
        cout << raiz->dados << " ";
    imprimirFolhas(raiz->esq);
    imprimirFolhas(raiz->dir);
}

int somaValores(nodo* raiz) {
    if (raiz == NULL) return 0;
    return raiz->dados + somaValores(raiz->esq) + somaValores(raiz->dir);
}

int main() {
    nodo* root = NULL;

    // Inserir os valores na árvore
    int valores[] = {28, 14, 37, 6, 19, 42, 3, 25, 31, 48};
    for (int i = 0; i < 10; i++) {
        root = inserirNodo(root, valores[i]);
    }

    // Testar se o valor 42 existe
    cout << "\nO valor 42 existe? ";
    cout << (existe(root, 42) ? "Sim" : "Nao") << endl;

    // Imprimir folhas
    cout << "\nFolhas da arvore: ";
    imprimirFolhas(root);
    cout << endl;

    // Soma de todos os valores
    cout << "\nSoma total dos valores: " << somaValores(root) << endl;

    return 0;
}
*** fim exemplo 1 ***

*** exemplo 2 ****
#include <iostream>
using namespace std;

struct nodo {
    int dados;
    nodo* esq;
    nodo* dir;
};

nodo* novoNodo(int num) {
    nodo* novo = new nodo;
    novo->dados = num;
    novo->esq = NULL;
    novo->dir = NULL;
    return novo;
}

nodo* inserirNodo(nodo* raiz, int num) {
    if (raiz == NULL) return novoNodo(num);
    if (num <= raiz->dados)
        raiz->esq = inserirNodo(raiz->esq, num);
    else
        raiz->dir = inserirNodo(raiz->dir, num);
    return raiz;
}

// Versão alternativa da função "existe" com uso de while (iterativa)
bool existe(nodo* raiz, int valor) {
    while (raiz != NULL) {
        if (raiz->dados == valor) return true;
        if (valor < raiz->dados)
            raiz = raiz->esq;
        else
            raiz = raiz->dir;
    }
    return false;
}

// Versão alternativa de "imprimirFolhas" com mais clareza na lógica
void imprimirFolhas(nodo* raiz) {
    if (raiz != NULL) {
        if (raiz->esq == NULL && raiz->dir == NULL)
            cout << raiz->dados << " ";
        else {
            imprimirFolhas(raiz->esq);
            imprimirFolhas(raiz->dir);
        }
    }
}

// Versão alternativa de "somaValores" separando variáveis
int somaValores(nodo* raiz) {
    if (raiz == NULL) return 0;
    int somaEsq = somaValores(raiz->esq);
    int somaDir = somaValores(raiz->dir);
    return raiz->dados + somaEsq + somaDir;
}

int main() {
    nodo* root = NULL;

    // Inserir os valores na árvore individualmente
    root = inserirNodo(root, 28);
    root = inserirNodo(root, 14);
    root = inserirNodo(root, 37);
    root = inserirNodo(root, 6);
    root = inserirNodo(root, 19);
    root = inserirNodo(root, 42);
    root = inserirNodo(root, 3);
    root = inserirNodo(root, 25);
    root = inserirNodo(root, 31);
    root = inserirNodo(root, 48);

    // Testar se o valor 42 existe
    cout << "O valor 42 existe? ";
    cout << (existe(root, 42) ? "Sim" : "Nao") << endl;

    // Imprimir folhas
    cout << "\nFolhas da arvore: ";
    imprimirFolhas(root);
    cout << endl;

    // Soma de todos os valores
    cout << "\nSoma total dos valores: " << somaValores(root) << endl;

    return 0;
}
*** fim exemplo 2 ***

"""

    context = "Conteúdos e conceitos abordados nas aulas de programação em C++."

    # Initialize the models
    reasoning_model = CustomChatOpenAI(
        model_name="o3-mini",
        temperature=1.0  # Default for reasoning model
    )
    
    consensus_model = CustomChatOpenAI(
        model_name="gpt-4o-2024-11-20",
        temperature=0.1  # Low temperature for consistency
    )
    
    # Generate multiple candidate rubrics
    print("Generating candidate rubrics...")
    candidate_rubrics = []
    for i in range(3):  # Generate 3 candidate rubrics
        print(f"Generating candidate rubric {i+1}/3...")
        rubric = generate_rubric(
            question_text,
            structured_criteria,
            examples,
            context,
            question_total_score,
            reasoning_model
        )
        candidate_rubrics.append(rubric)
        # Add a small delay to ensure different outputs
        time.sleep(1)
    
    # Generate consensus rubric
    print("Generating consensus rubric...")
    consensus_rubric = generate_consensus_rubric(
        question_text,
        structured_criteria,
        question_total_score,
        candidate_rubrics,
        consensus_model
    )
    
    # Create output content
    output_content = f"""# Rubric Generation Results for Code Question

## Original Question
```cpp
{question_text}
```

## Structured Criteria
{format_structured_criteria(structured_criteria)}

## Total Points
{question_total_score}

## Example Solution
```cpp
{examples}
```

## Candidate Rubric 1
{candidate_rubrics[0]}

## Candidate Rubric 2
{candidate_rubrics[1]}

## Candidate Rubric 3
{candidate_rubrics[2]}

## Final Consensus Rubric
{consensus_rubric}
"""
    
    # Save to file
    saved_file = save_to_file(output_content)
    
    print(f"Complete process finished. Results saved to {saved_file}")

if __name__ == "__main__":
    main()